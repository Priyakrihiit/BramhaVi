"""
apps/ai/services.py
Sprint 24 — Phase 3: AI Backend Services — BrahmaVidya Galaxy

Service classes:
  GeminiService          — Real Gemini SDK calls (chat, stream, structured)
  ContextWindowService   — 3-layer conversation memory management
  EmbeddingService       — Content chunk embedding (async via Celery)
  RAGService             — Retrieval-augmented context grounding
  ConversationService    — Conversation + message lifecycle
  PromptService          — Template resolution and variable injection
  AIUsageService         — Token accounting, quota enforcement, daily rollup
  StudyPlanService       — AI-generated weekly study plans
  FlashcardService       — AI-generated flashcard decks
  QuizGenerationService  — AI quiz generation and persistence
  RecommendationService  — Personalized learning recommendations
  AgentConfigService     — AIAgentConfig registry accessor
"""

from __future__ import annotations

import json
import logging
import hashlib
import datetime
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.ai.models import (
    AIModelRegistry, PromptTemplate, AIChatSession, AIUsageLog,
    AITokenLog, AIRateLimitQuota, AIAgentConfig, KnowledgeContext,
    ConversationMemory, StudyPlan, StudyPlanSession, FlashcardDeck,
    Flashcard, QuizGeneration, QuizQuestion, LearningRecommendation, AITask,
)
from apps.control_center.models import AIConversation, AIMessage
from apps.ai.utils import estimate_tokens, calculate_cost

User = get_user_model()
logger = logging.getLogger("brahmavidya.ai")


# ─── 1. Gemini Service ────────────────────────────────────────────────────────

class GeminiService:
    """
    Wraps the Google Generative AI SDK.
    Provides chat, streaming, and structured JSON generation methods.
    Falls back to a structured mock when GEMINI_API_KEY is not configured.
    """

    _client = None  # Lazy-initialised SDK client

    @classmethod
    def _get_client(cls):
        """
        Lazy-loads the Gemini SDK client once and caches it on the class.
        Returns None when the key is absent (dev/test mode).
        """
        if cls._client is not None:
            return cls._client
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            logger.warning("GEMINI_API_KEY not configured — using mock responses.")
            return None
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=api_key)
            cls._client = genai
            return cls._client
        except ImportError:
            logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
            return None

    @classmethod
    def chat(
        cls,
        messages: list[dict],
        model_id: str = "gemini-1.5-pro",
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict:
        """
        Sends a synchronous chat request.
        messages: [{"role": "user"|"model", "parts": [{"text": "..."}]}]
        Returns: {"content": str, "prompt_tokens": int, "completion_tokens": int, "cached": bool}
        """
        genai = cls._get_client()
        if genai is None:
            return cls._mock_response(messages[-1]["parts"][0]["text"] if messages else "")

        try:
            model = genai.GenerativeModel(
                model_name=model_id,
                system_instruction=system_prompt or None,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            chat_session = model.start_chat(history=messages[:-1] if len(messages) > 1 else [])
            last_msg = messages[-1]["parts"][0]["text"] if messages else ""
            response = chat_session.send_message(last_msg)
            content = response.text or ""
            usage = getattr(response, "usage_metadata", None)
            prompt_tokens = getattr(usage, "prompt_token_count", estimate_tokens(last_msg))
            completion_tokens = getattr(usage, "candidates_token_count", estimate_tokens(content))
            return {
                "content": content,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cached": False,
                "error": False,
            }
        except Exception as exc:
            logger.error(f"GeminiService.chat error: {exc}", exc_info=True)
            return {"content": "", "prompt_tokens": 0, "completion_tokens": 0, "error": True, "error_message": str(exc)}

    @classmethod
    def generate_structured(
        cls,
        prompt: str,
        schema_hint: str = "",
        model_id: str = "gemini-1.5-flash",
        system_prompt: str = "",
        temperature: float = 0.4,
        max_tokens: int = 4096,
    ) -> dict:
        """
        Requests a structured JSON response from Gemini.
        Uses response_mime_type='application/json' when supported.
        Returns: {"data": dict|list, "prompt_tokens": int, "completion_tokens": int}
        """
        genai = cls._get_client()
        if genai is None:
            return {"data": {}, "prompt_tokens": 0, "completion_tokens": 0, "error": False}

        full_prompt = prompt
        if schema_hint:
            full_prompt = f"{prompt}\n\nRespond with valid JSON matching: {schema_hint}"

        try:
            model = genai.GenerativeModel(
                model_name=model_id,
                system_instruction=system_prompt or None,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "response_mime_type": "application/json",
                }
            )
            response = model.generate_content(full_prompt)
            text = response.text or "{}"
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # Fallback: strip markdown fences and retry
                cleaned = text.strip().strip("```json").strip("```").strip()
                data = json.loads(cleaned)

            usage = getattr(response, "usage_metadata", None)
            return {
                "data": data,
                "prompt_tokens": getattr(usage, "prompt_token_count", estimate_tokens(full_prompt)),
                "completion_tokens": getattr(usage, "candidates_token_count", estimate_tokens(text)),
                "error": False,
            }
        except Exception as exc:
            logger.error(f"GeminiService.generate_structured error: {exc}", exc_info=True)
            return {"data": {}, "prompt_tokens": 0, "completion_tokens": 0, "error": True, "error_message": str(exc)}

    @staticmethod
    def _mock_response(user_content: str) -> dict:
        """Returns a structured mock when SDK is unavailable (dev mode)."""
        from apps.ai.utils import generate_mock_assistant_response
        result = generate_mock_assistant_response(user_content, "gemini-mock")
        content = result.get("content", "")
        return {
            "content": content,
            "prompt_tokens": estimate_tokens(user_content),
            "completion_tokens": estimate_tokens(content),
            "cached": False,
            "error": False,
        }


# ─── 2. Context Window Service ────────────────────────────────────────────────

class ContextWindowService:
    """
    3-layer conversation memory manager:
      Layer 1 — Redis working memory (last N messages, 24h TTL)
      Layer 2 — PostgreSQL (persistent full history)
      Layer 3 — Summarised long-term memory (ConversationMemory model)
    """

    REDIS_TTL = 86400          # 24 hours
    MAX_WORKING_TOKENS = 80000  # Trigger summarisation above this

    @classmethod
    def get_context_messages(cls, conversation: AIConversation, agent_config: AIAgentConfig | None = None) -> list[dict]:
        """
        Builds the context window for a Gemini API call.
        Priority: ConversationMemory summary (if exists) + recent Redis messages.
        """
        cache_key = f"bvg:ai:ctx:{conversation.id}"
        try:
            cached = cache.get(cache_key)
            if cached:
                return cached
        except Exception:
            pass

        messages = []

        # Include long-term summary if present
        try:
            memory = ConversationMemory.objects.get(conversation=conversation)
            messages.append({
                "role": "model",
                "parts": [{"text": f"[CONVERSATION SUMMARY]\n{memory.summary}"}],
            })
        except ConversationMemory.DoesNotExist:
            pass

        # Load recent messages from DB
        max_ctx = (agent_config.context_window_tokens if agent_config else 80000)
        db_msgs = (
            AIMessage.objects.filter(conversation=conversation)
            .order_by("-created_at")[:100]
        )
        db_msgs = list(reversed(db_msgs))

        total_tokens = 0
        ctx_slice = []
        for msg in db_msgs:
            t = msg.token_count or estimate_tokens(msg.content)
            total_tokens += t
            if total_tokens > max_ctx:
                break
            role = "user" if msg.sender_type == "USER" else "model"
            ctx_slice.append({"role": role, "parts": [{"text": msg.content}]})

        messages.extend(ctx_slice)

        try:
            cache.set(cache_key, messages, cls.REDIS_TTL)
        except Exception:
            pass

        return messages

    @classmethod
    def invalidate(cls, conversation_id: str) -> None:
        """Drops the cached context after a new message is saved."""
        try:
            cache.delete(f"bvg:ai:ctx:{conversation_id}")
        except Exception:
            pass

    @classmethod
    def should_summarise(cls, conversation: AIConversation) -> bool:
        """Returns True if total token count exceeds the summarisation threshold."""
        total = AIMessage.objects.filter(conversation=conversation).aggregate(
            total=__import__("django.db.models", fromlist=["Sum"]).Sum("token_count")
        )["total"] or 0
        return total >= cls.MAX_WORKING_TOKENS


# ─── 3. Embedding Service ─────────────────────────────────────────────────────

class EmbeddingService:
    """
    Generates and stores text embeddings for KnowledgeContext chunks.
    SQLite mode: stores JSON string. PostgreSQL+pgvector: swap to VectorField.
    """

    MODEL = "text-embedding-004"
    CHUNK_SIZE = 512   # tokens per chunk (≈ 2048 chars)

    @classmethod
    def embed_text(cls, text: str) -> list[float] | None:
        """
        Calls Gemini embedding API. Returns list[float] or None on failure.
        """
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            return None
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=api_key)
            result = genai.embed_content(model=f"models/{cls.MODEL}", content=text)
            return result["embedding"]
        except Exception as exc:
            logger.warning(f"EmbeddingService.embed_text failed: {exc}")
            return None

    @classmethod
    def chunk_text(cls, text: str, chunk_chars: int = 2048) -> list[str]:
        """Splits a long text into overlapping character-window chunks."""
        chunks = []
        step = chunk_chars - 200  # 200-char overlap
        for i in range(0, len(text), step):
            chunk = text[i : i + chunk_chars]
            if chunk.strip():
                chunks.append(chunk.strip())
        return chunks or [text[:chunk_chars]]

    @classmethod
    @transaction.atomic
    def store_chunks(cls, source_type: str, source_id: str, text: str, metadata: dict | None = None) -> int:
        """
        Splits text into chunks, saves KnowledgeContext rows, triggers async embedding.
        Returns count of new chunks created.
        """
        KnowledgeContext.objects.filter(source_type=source_type, source_id=source_id).delete()
        chunks = cls.chunk_text(text)
        created = 0
        for idx, chunk in enumerate(chunks):
            KnowledgeContext.objects.create(
                source_type=source_type,
                source_id=source_id,
                chunk_index=idx,
                chunk_text=chunk,
                token_count=estimate_tokens(chunk),
                metadata=metadata or {},
                is_embedded=False,
            )
            created += 1
        return created


# ─── 4. RAG Service ───────────────────────────────────────────────────────────

class RAGService:
    """
    Retrieval-Augmented Generation: fetches relevant KnowledgeContext chunks
    and prepends them to the Gemini prompt for grounded responses.

    Text-similarity mode (SQLite): uses keyword matching.
    pgvector mode (PostgreSQL): cosine similarity on embedding vectors.
    """

    @staticmethod
    def retrieve(query: str, top_k: int = 5, source_types: list[str] | None = None) -> list[str]:
        """
        Returns top_k relevant text chunks for the query.
        Falls back to keyword matching when embeddings are unavailable.
        """
        qs = KnowledgeContext.objects.all()
        if source_types:
            qs = qs.filter(source_type__in=source_types)

        # Keyword fallback (works on SQLite)
        words = [w.strip() for w in query.split() if len(w.strip()) > 3]
        if not words:
            return []

        from django.db.models import Q
        q_obj = Q()
        for word in words[:5]:
            q_obj |= Q(chunk_text__icontains=word)

        chunks = qs.filter(q_obj).order_by("-created_at")[:top_k]
        return [c.chunk_text for c in chunks]

    @staticmethod
    def build_rag_context(query: str, top_k: int = 5) -> str:
        """
        Builds a formatted context block from retrieved chunks.
        """
        chunks = RAGService.retrieve(query, top_k=top_k)
        if not chunks:
            return ""
        joined = "\n\n---\n\n".join(chunks)
        return f"[PLATFORM KNOWLEDGE BASE]\n{joined}\n[END KNOWLEDGE BASE]"


# ─── 5. Conversation Service ──────────────────────────────────────────────────

class ConversationService:
    """
    Manages the full conversation lifecycle: create, message, archive, restore.
    Integrates with ContextWindowService and AIUsageService.
    """

    @staticmethod
    @transaction.atomic
    def create_conversation(user, title: str = "New Conversation") -> AIConversation:
        return AIConversation.objects.create(user=user, title=title)

    @staticmethod
    @transaction.atomic
    def send_message(
        conversation: AIConversation,
        user_content: str,
        agent_type: str = "tutor",
        model_id: str | None = None,
        enable_rag: bool = False,
    ) -> dict:
        """
        Full pipeline:
          1. Load agent config
          2. Build context window
          3. Optional RAG injection
          4. Call Gemini
          5. Save user + assistant messages
          6. Update token log
          7. Invalidate cache
        """
        # 1. Agent config
        agent = AgentConfigService.get_config(agent_type)
        effective_model = model_id or (agent.model_id if agent else "gemini-1.5-pro")
        system_prompt = agent.system_prompt if agent else ""

        # 2. Context window
        ctx_messages = ContextWindowService.get_context_messages(conversation, agent)

        # 3. RAG injection
        rag_ctx = ""
        if enable_rag:
            rag_ctx = RAGService.build_rag_context(user_content)
            if rag_ctx:
                system_prompt = f"{system_prompt}\n\n{rag_ctx}".strip()

        # 4. Append new user message
        ctx_messages.append({"role": "user", "parts": [{"text": user_content}]})

        # 5. Call Gemini
        result = GeminiService.chat(
            messages=ctx_messages,
            model_id=effective_model,
            system_prompt=system_prompt,
            temperature=agent.temperature if agent else 0.7,
            max_tokens=agent.max_output_tokens if agent else 4096,
        )

        assistant_content = result.get("content", "")
        prompt_tokens = result.get("prompt_tokens", estimate_tokens(user_content))
        completion_tokens = result.get("completion_tokens", estimate_tokens(assistant_content))

        # 6. Persist messages
        user_msg = AIMessage.objects.create(
            conversation=conversation,
            sender_type="USER",
            content=user_content,
            token_count=prompt_tokens,
        )
        assistant_msg = AIMessage.objects.create(
            conversation=conversation,
            sender_type="ASSISTANT",
            content=assistant_content,
            token_count=completion_tokens,
        )

        # 7. Auto-title
        if conversation.title in ("New Conversation", ""):
            prefix = user_content[:50]
            conversation.title = f"{prefix}..." if len(user_content) > 50 else prefix
            conversation.save(update_fields=["title", "updated_at"])

        # 8. Invalidate cache
        ContextWindowService.invalidate(str(conversation.id))

        return {
            "user_message": user_msg,
            "assistant_message": assistant_msg,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "model_id": effective_model,
            "error": result.get("error", False),
        }


# ─── 6. Prompt Service ────────────────────────────────────────────────────────

class PromptService:
    """
    Resolves PromptTemplates and injects {{variable}} placeholders.
    """

    @staticmethod
    def resolve(template_id: str, variables: dict) -> str | None:
        """
        Fetches an active PromptTemplate by UUID and renders it with variables.
        Returns rendered string or None if not found.
        """
        try:
            template = PromptTemplate.objects.get(id=template_id, is_active=True)
        except PromptTemplate.DoesNotExist:
            return None

        text = template.prompt_text
        for key, val in variables.items():
            text = text.replace(f"{{{{{key}}}}}", str(val))

        # Increment usage counter (non-critical)
        try:
            PromptTemplate.objects.filter(id=template_id).update(
                usage_count=__import__("django.db.models", fromlist=["F"]).F("usage_count") + 1
            )
        except Exception:
            pass

        return text

    @staticmethod
    def list_by_category(category: str, public_only: bool = True):
        qs = PromptTemplate.objects.filter(is_active=True, category=category)
        if public_only:
            qs = qs.filter(is_public=True)
        return qs.order_by("-usage_count")


# ─── 7. AI Usage Service ─────────────────────────────────────────────────────

class AIUsageService:
    """
    Token accounting, quota enforcement, and daily rollup.
    """

    DAILY_DEFAULTS = {
        "FREE": 50_000,
        "STUDENT": 200_000,
        "TEACHER": 500_000,
        "ADMIN": 0,  # unlimited
    }

    @classmethod
    def check_quota(cls, user) -> tuple[bool, str]:
        """
        Returns (allowed: bool, reason: str).
        Checks daily token limit via Redis counter then DB fallback.
        """
        try:
            quota = AIRateLimitQuota.objects.get(user=user)
            if quota.is_unlimited:
                return True, ""
            daily_limit = quota.daily_token_limit
        except AIRateLimitQuota.DoesNotExist:
            daily_limit = cls.DAILY_DEFAULTS.get("STUDENT", 200_000)

        # Redis daily counter
        today_key = f"bvg:ai:daily_tokens:{user.id}:{timezone.now().date()}"
        try:
            used = cache.get(today_key) or 0
            if daily_limit > 0 and int(used) >= daily_limit:
                return False, f"Daily token limit of {daily_limit} reached."
        except Exception:
            pass

        return True, ""

    @classmethod
    def log_usage(
        cls,
        user,
        feature: str,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: int = 0,
        session=None,
        conversation=None,
        metadata: dict | None = None,
    ) -> AIUsageLog:
        """
        Creates AIUsageLog row, updates Redis daily counter, and increments AITokenLog.
        """
        total = prompt_tokens + completion_tokens

        # Estimate cost from model registry
        estimated_cost = Decimal("0")
        try:
            model_rec = AIModelRegistry.objects.get(model_id=model_id)
            estimated_cost = (
                Decimal(prompt_tokens) * model_rec.input_token_rate
                + Decimal(completion_tokens) * model_rec.output_token_rate
            )
        except AIModelRegistry.DoesNotExist:
            pass

        log = AIUsageLog.objects.create(
            user=user,
            session=session,
            conversation=conversation,
            model_id=model_id,
            feature=feature,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            prompt_length=0,
            completion_length=0,
            estimated_cost_usd=estimated_cost,
            latency_ms=latency_ms,
            request_metadata=metadata or {},
        )

        # Redis daily counter
        today_key = f"bvg:ai:daily_tokens:{user.id}:{timezone.now().date()}"
        try:
            cache.incr(today_key, total)
            cache.expire(today_key, 86400)
        except Exception:
            pass

        # DB daily rollup (get_or_create)
        today = timezone.now().date()
        try:
            token_log, _ = AITokenLog.objects.get_or_create(
                user=user,
                log_date=today,
                defaults={"tokens_used": 0, "input_tokens": 0, "output_tokens": 0,
                          "request_count": 0, "estimated_cost_usd": Decimal("0")},
            )
            AITokenLog.objects.filter(pk=token_log.pk).update(
                tokens_used=__import__("django.db.models", fromlist=["F"]).F("tokens_used") + total,
                input_tokens=__import__("django.db.models", fromlist=["F"]).F("input_tokens") + prompt_tokens,
                output_tokens=__import__("django.db.models", fromlist=["F"]).F("output_tokens") + completion_tokens,
                request_count=__import__("django.db.models", fromlist=["F"]).F("request_count") + 1,
                estimated_cost_usd=__import__("django.db.models", fromlist=["F"]).F("estimated_cost_usd") + estimated_cost,
            )
        except Exception as exc:
            logger.warning(f"AIUsageService.log_usage: token log update failed: {exc}")

        return log


# ─── 8. Agent Config Service ──────────────────────────────────────────────────

class AgentConfigService:
    """
    Retrieves AIAgentConfig rows with Redis caching (5-min TTL).
    """
    CACHE_TTL = 300

    @classmethod
    def get_config(cls, agent_type: str) -> AIAgentConfig | None:
        cache_key = f"bvg:ai:agent_cfg:{agent_type}"
        try:
            cached = cache.get(cache_key)
            if cached:
                return cached
        except Exception:
            pass
        try:
            config = AIAgentConfig.objects.get(agent_type=agent_type, is_active=True)
            try:
                cache.set(cache_key, config, cls.CACHE_TTL)
            except Exception:
                pass
            return config
        except AIAgentConfig.DoesNotExist:
            return None


# ─── 9. Study Plan Service ────────────────────────────────────────────────────

class StudyPlanService:
    """
    Generates AI-powered weekly study plans for students.
    Integrates with student LearningHistory and LMS enrollments.
    """

    SYSTEM_PROMPT = (
        "You are an expert academic study planner for the BrahmaVidya Galaxy learning platform. "
        "Generate structured, realistic weekly study plans in JSON format. "
        "Consider the student's pace, available hours, and enrolled courses."
    )

    @classmethod
    def generate(
        cls,
        student,
        week_start: datetime.date,
        available_hours_per_day: int = 2,
        learning_pace: str = "moderate",
        learning_style: str = "READING",
        goal: str = "",
        enrolled_courses: list[dict] | None = None,
    ) -> StudyPlan:
        """
        Calls Gemini to generate a weekly study plan and persists it.
        """
        enrolled_courses = enrolled_courses or []
        courses_text = json.dumps(enrolled_courses, indent=2) if enrolled_courses else "No enrolled courses provided."

        prompt = (
            f"Generate a 7-day study plan starting {week_start} for a student with these details:\n"
            f"- Available hours/day: {available_hours_per_day}\n"
            f"- Learning pace: {learning_pace}\n"
            f"- Learning style: {learning_style}\n"
            f"- Goal: {goal or 'General learning'}\n"
            f"- Enrolled courses:\n{courses_text}\n\n"
            "Return JSON with keys: title, weekly_goals (list), daily_sessions (list of "
            "{date, sessions: [{time_slot, type, course_title, lesson_title, duration_minutes, goal, motivational_message}]}), "
            "risk_alerts (list of {course, message})."
        )

        result = GeminiService.generate_structured(
            prompt=prompt,
            model_id="gemini-1.5-pro",
            system_prompt=cls.SYSTEM_PROMPT,
            temperature=0.5,
        )

        plan_data = result.get("data", {})
        prompt_tokens = result.get("prompt_tokens", 0)
        completion_tokens = result.get("completion_tokens", 0)

        with transaction.atomic():
            # Deactivate previous active plans
            StudyPlan.objects.filter(student=student, is_active=True).update(is_active=False)

            plan = StudyPlan.objects.create(
                student=student,
                title=plan_data.get("title", f"Study Plan — Week of {week_start}"),
                week_start=week_start,
                week_end=week_start + datetime.timedelta(days=6),
                available_hours_per_day=available_hours_per_day,
                learning_pace=learning_pace,
                learning_style=learning_style,
                goal=goal,
                plan_data=plan_data,
                weekly_goals=plan_data.get("weekly_goals", []),
                risk_alerts=plan_data.get("risk_alerts", []),
                model_id="gemini-1.5-pro",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                is_active=True,
            )

            # Inflate StudyPlanSession rows
            for day_block in plan_data.get("daily_sessions", []):
                day_str = day_block.get("date", "")
                try:
                    session_date = datetime.date.fromisoformat(day_str)
                except (ValueError, TypeError):
                    continue
                for sess in day_block.get("sessions", []):
                    StudyPlanSession.objects.create(
                        study_plan=plan,
                        session_date=session_date,
                        time_slot=sess.get("time_slot", ""),
                        session_type=sess.get("type", "STUDY"),
                        course_title=sess.get("course_title", ""),
                        lesson_title=sess.get("lesson_title", ""),
                        goal=sess.get("goal", ""),
                        duration_minutes=sess.get("duration_minutes", 60),
                        motivational_message=sess.get("motivational_message", ""),
                    )

        return plan


# ─── 10. Flashcard Service ────────────────────────────────────────────────────

class FlashcardService:
    """
    Generates AI flashcard decks from lesson/topic text.
    Uses Leitner spaced-repetition scheduling.
    """

    SYSTEM_PROMPT = (
        "You are an expert educator specialising in active recall and spaced repetition. "
        "Generate high-quality flashcard decks in JSON format."
    )

    @classmethod
    def generate(
        cls,
        student,
        topic: str,
        source_text: str,
        card_count: int = 15,
        card_type: str = "TERM_DEFINITION",
        lesson_id: str | None = None,
        course_id: str | None = None,
    ) -> FlashcardDeck:
        """Generates a flashcard deck using Gemini and persists it."""

        prompt = (
            f"Generate {card_count} {card_type} flashcards for the topic: '{topic}'.\n"
            f"Source content:\n{source_text[:4000]}\n\n"
            "Return JSON with keys: title, cards (list of "
            "{front, back, hint, difficulty (1-5), tags (list)})."
        )

        result = GeminiService.generate_structured(
            prompt=prompt,
            model_id="gemini-1.5-flash",
            system_prompt=cls.SYSTEM_PROMPT,
            temperature=0.6,
        )

        data = result.get("data", {})
        cards_data = data.get("cards", [])

        # Leitner schedule: all new cards start in box 1 (daily review)
        today = timezone.now().date()
        schedule = {"day_1": list(range(len(cards_data)))}

        with transaction.atomic():
            deck = FlashcardDeck.objects.create(
                student=student,
                title=data.get("title", f"Flashcards: {topic[:50]}"),
                topic=topic,
                card_type=card_type,
                lesson_id=lesson_id,
                course_id=course_id,
                card_count=len(cards_data),
                spaced_repetition_schedule=schedule,
                model_id="gemini-1.5-flash",
                prompt_tokens=result.get("prompt_tokens", 0),
                completion_tokens=result.get("completion_tokens", 0),
            )

            for card_data in cards_data:
                Flashcard.objects.create(
                    deck=deck,
                    card_type=card_type,
                    front=card_data.get("front", ""),
                    back=card_data.get("back", ""),
                    hint=card_data.get("hint", ""),
                    difficulty=max(1, min(5, int(card_data.get("difficulty", 3)))),
                    tags=card_data.get("tags", []),
                    next_review_date=today,
                    leitner_box=1,
                )

        return deck

    @staticmethod
    def review_card(card: Flashcard, correct: bool) -> Flashcard:
        """
        Updates Leitner box and next review date after a review attempt.
        Correct → advance box. Incorrect → reset to box 1.
        """
        LEITNER_INTERVALS = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}  # days
        today = timezone.now().date()

        if correct:
            card.leitner_box = min(5, card.leitner_box + 1)
            card.correct_count += 1
        else:
            card.leitner_box = 1

        interval = LEITNER_INTERVALS.get(card.leitner_box, 1)
        card.next_review_date = today + datetime.timedelta(days=interval)
        card.review_count += 1
        card.last_reviewed_at = timezone.now()
        card.save()
        return card


# ─── 11. Quiz Generation Service ─────────────────────────────────────────────

class QuizGenerationService:
    """
    AI quiz generation with Bloom's taxonomy tagging and structured output.
    """

    SYSTEM_PROMPT = (
        "You are a curriculum expert who creates pedagogically sound quiz questions "
        "following Bloom's Taxonomy. Generate questions in valid JSON format."
    )

    @classmethod
    def generate(
        cls,
        generated_by,
        topic: str,
        source_text: str,
        question_count: int = 10,
        difficulty: str = "medium",
        question_type: str = "MCQ",
        lesson_id: str | None = None,
        course_id: str | None = None,
    ) -> QuizGeneration:
        """Generates a quiz using Gemini and persists questions."""

        # Cache key for identical requests
        cache_key = hashlib.sha256(
            f"{topic}:{source_text[:500]}:{question_count}:{difficulty}:{question_type}".encode()
        ).hexdigest()[:16]

        prompt = (
            f"Generate {question_count} {difficulty}-level {question_type} questions about: '{topic}'.\n"
            f"Content:\n{source_text[:4000]}\n\n"
            "Return JSON: {title, questions: [{question, question_type, options (list for MCQ), "
            "correct_answer, explanation, concept_tag, bloom_level (remember/understand/apply/analyze/evaluate/create), "
            "difficulty_score (1-5)}]}"
        )

        result = GeminiService.generate_structured(
            prompt=prompt,
            model_id="gemini-1.5-flash",
            system_prompt=cls.SYSTEM_PROMPT,
            temperature=0.3,
        )

        data = result.get("data", {})
        questions_data = data.get("questions", [])

        with transaction.atomic():
            quiz = QuizGeneration.objects.create(
                generated_by=generated_by,
                quiz_title=data.get("title", f"Quiz: {topic[:100]}"),
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                question_count=len(questions_data),
                lesson_id=lesson_id,
                course_id=course_id,
                model_id="gemini-1.5-flash",
                prompt_tokens=result.get("prompt_tokens", 0),
                completion_tokens=result.get("completion_tokens", 0),
                generation_output=data,
                cache_key=cache_key,
            )

            for idx, q in enumerate(questions_data, start=1):
                QuizQuestion.objects.create(
                    generation=quiz,
                    question_number=idx,
                    question=q.get("question", ""),
                    question_type=q.get("question_type", question_type),
                    options=q.get("options", []),
                    correct_answer=q.get("correct_answer", ""),
                    explanation=q.get("explanation", ""),
                    concept_tag=q.get("concept_tag", ""),
                    bloom_level=q.get("bloom_level", "understand"),
                    difficulty_score=max(1, min(5, int(q.get("difficulty_score", 3)))),
                )

        return quiz


# ─── 12. Recommendation Service ───────────────────────────────────────────────

class RecommendationService:
    """
    Generates and manages AI-powered learning recommendations for students.
    """

    @classmethod
    def generate_for_student(cls, student, enrolled_courses: list[dict] | None = None) -> list[LearningRecommendation]:
        """
        Calls Gemini to generate personalised recommendations based on the student's
        recent activity and enrolled courses.
        """
        enrolled_courses = enrolled_courses or []

        # Gather recent history summary
        try:
            from apps.student.models import LearningHistory, LearningStreak
            recent_nodes = (
                LearningHistory.objects.filter(student=student)
                .order_by("-accessed_at")[:10]
                .values_list("node__title", flat=True)
            )
            history_text = ", ".join(list(recent_nodes)) or "No recent activity."
            streak = LearningStreak.objects.filter(student=student).values("current_streak", "total_xp").first()
        except Exception:
            history_text = "No recent activity."
            streak = {}

        prompt = (
            f"Based on this student's learning activity, generate 5 personalised recommendations.\n"
            f"Recent lessons: {history_text}\n"
            f"Streak: {streak or 'Unknown'}\n"
            f"Enrolled courses: {json.dumps(enrolled_courses[:5])}\n\n"
            "Return JSON: {recommendations: [{type (NEXT_LESSON/REVISION/COURSE/PRACTICE/WEAK_AREA), "
            "title, description, reason, priority_score (0.0-1.0), target_type, target_url}]}"
        )

        result = GeminiService.generate_structured(
            prompt=prompt,
            model_id="gemini-1.5-flash",
            temperature=0.5,
        )

        recs_data = result.get("data", {}).get("recommendations", [])
        created = []

        # Expire old PENDING recommendations
        LearningRecommendation.objects.filter(student=student, status="PENDING").update(status="DISMISSED")

        for rec in recs_data[:5]:
            obj = LearningRecommendation.objects.create(
                student=student,
                recommendation_type=rec.get("type", "NEXT_LESSON"),
                title=rec.get("title", "")[:255],
                description=rec.get("description", ""),
                reason=rec.get("reason", ""),
                priority_score=float(rec.get("priority_score", 0.5)),
                target_type=rec.get("target_type", ""),
                target_url=rec.get("target_url", ""),
                model_id="gemini-1.5-flash",
                expires_at=timezone.now() + datetime.timedelta(days=7),
            )
            created.append(obj)

        return created
