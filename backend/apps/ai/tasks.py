"""
apps/ai/tasks.py
Sprint 24 — Phase 3: AI Celery Background Tasks — BrahmaVidya Galaxy

Background tasks for embedding calculation, conversation summarization,
and asynchronous task orchestration.
"""

from __future__ import annotations

import logging
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.ai.models import AITask, KnowledgeContext, ConversationMemory
from apps.ai.services import EmbeddingService, GeminiService
from apps.control_center.models import AIConversation, AIMessage

logger = logging.getLogger("brahmavidya.ai.tasks")


@shared_task(
    bind=True,
    acks_late=True,
    queue="ai-default",
    name="apps.ai.tasks.async_embed_context_task",
)
def async_embed_context_task(self, chunk_id: str) -> dict:
    """
    Asynchronously generates and saves embeddings for a single KnowledgeContext chunk.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Generating embedding for KnowledgeContext {chunk_id}")
    
    # Track task state if registered
    AITask.objects.filter(celery_task_id=task_id).update(
        status="RUNNING",
        started_at=timezone.now()
    )

    try:
        chunk = KnowledgeContext.objects.get(id=chunk_id)
        embedding = EmbeddingService.embed_text(chunk.chunk_text)
        if embedding:
            chunk.embedding = embedding
            chunk.is_embedded = True
            chunk.save(update_fields=["embedding", "is_embedded", "updated_at"])
            
            AITask.objects.filter(celery_task_id=task_id).update(
                status="SUCCESS",
                completed_at=timezone.now(),
                result_data={"status": "success", "chunk_id": chunk_id}
            )
            return {"status": "success", "chunk_id": chunk_id}
        else:
            AITask.objects.filter(celery_task_id=task_id).update(
                status="FAILURE",
                completed_at=timezone.now(),
                error_message="Embedding generator returned empty vector."
            )
            return {"status": "failed", "reason": "No embedding generated"}
    except Exception as exc:
        logger.error(f"[{task_id}] Error in async_embed_context_task: {exc}", exc_info=True)
        AITask.objects.filter(celery_task_id=task_id).update(
            status="FAILURE",
            completed_at=timezone.now(),
            error_message=str(exc)
        )
        raise self.retry(exc=exc, countdown=30)


@shared_task(
    bind=True,
    acks_late=True,
    queue="ai-default",
    name="apps.ai.tasks.summarize_conversation_task",
)
def summarize_conversation_task(self, conversation_id: str) -> dict:
    """
    Asynchronously generates a conversation summary when context length limit is reached.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Generating summary for conversation {conversation_id}")
    
    AITask.objects.filter(celery_task_id=task_id).update(
        status="RUNNING",
        started_at=timezone.now()
    )

    try:
        conv = AIConversation.objects.get(id=conversation_id)
        messages = AIMessage.objects.filter(conversation=conv).order_by("created_at")
        history_text = "\n".join([f"{m.sender_type}: {m.content}" for m in messages])
        
        prompt = (
            "Please summarize the following educational chat conversation context in detail. "
            "Capture all key topics discussed, student doubts, and explanations provided so far:\n\n"
            f"{history_text}"
        )
        
        result = GeminiService.chat(
            messages=[{"role": "user", "parts": [{"text": prompt}]}],
            model_id="gemini-1.5-flash",
            system_prompt="You are a helpful teaching assistant summarising learning history.",
        )
        
        summary = result.get("content", "")
        if summary:
            with transaction.atomic():
                memory, created = ConversationMemory.objects.get_or_create(
                    conversation=conv,
                    defaults={"summary": summary, "last_summarized_at": timezone.now()}
                )
                if not created:
                    memory.summary = summary
                    memory.last_summarized_at = timezone.now()
                    memory.save(update_fields=["summary", "last_summarized_at", "updated_at"])
            
            AITask.objects.filter(celery_task_id=task_id).update(
                status="SUCCESS",
                completed_at=timezone.now(),
                result_data={"status": "success", "summary_preview": summary[:100]}
            )
            return {"status": "success", "summary_preview": summary[:100]}
        else:
            AITask.objects.filter(celery_task_id=task_id).update(
                status="FAILURE",
                completed_at=timezone.now(),
                error_message="Empty summary returned by model."
            )
            return {"status": "failed", "reason": "Empty summary returned"}
    except Exception as exc:
        logger.error(f"[{task_id}] Error in summarize_conversation_task: {exc}", exc_info=True)
        AITask.objects.filter(celery_task_id=task_id).update(
            status="FAILURE",
            completed_at=timezone.now(),
            error_message=str(exc)
        )
        raise self.retry(exc=exc, countdown=60)
