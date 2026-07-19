"""
apps/ai/signals.py
Sprint 24 — Phase 3: AI Model Signals — BrahmaVidya Galaxy

Event receivers to automate workflow hooks like async embedding generation
on new content ingestion and trigger conversation summaries.
"""

from __future__ import annotations

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ai.models import KnowledgeContext, AITask
from apps.control_center.models import AIMessage
from apps.ai.tasks import async_embed_context_task, summarize_conversation_task
from apps.ai.services import ContextWindowService

logger = logging.getLogger("brahmavidya.ai.signals")


@receiver(post_save, sender=KnowledgeContext)
def on_knowledge_context_saved(sender, instance, created, **kwargs):
    """
    Triggers async embedding calculation when a new chunk is added.
    """
    if created and not instance.is_embedded:
        logger.info(f"Triggering async embedding calculation for KnowledgeContext chunk {instance.id}")
        async_embed_context_task.delay(str(instance.id))


@receiver(post_save, sender=AIMessage)
def on_ai_message_saved(sender, instance, created, **kwargs):
    """
    Invalidates context window cache and checks if summarization is needed.
    """
    if created:
        logger.info(f"Invalidating cache and checking summary rules for conversation {instance.conversation_id}")
        # Invalidate the context window memory cache
        ContextWindowService.invalidate(str(instance.conversation_id))
        
        # Trigger async summarization if conversation size exceeds threshold
        if ContextWindowService.should_summarise(instance.conversation):
            logger.info(f"Conversation {instance.conversation_id} exceeds token limits. Triggering summary.")
            summarize_conversation_task.delay(str(instance.conversation_id))
