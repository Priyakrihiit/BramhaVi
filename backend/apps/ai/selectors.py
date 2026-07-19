"""
apps/ai/selectors.py
Sprint 24 — Phase 3: AI ORM Query Selectors — BrahmaVidya Galaxy

Pure read-only query functions grouped by domain.
All functions use cache-aside pattern (Redis → DB fallback).
Never perform writes — that belongs to services.py.
"""

from __future__ import annotations

import datetime
import logging

from django.db.models import QuerySet, Sum, Count, Avg, Q
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model

from apps.ai.models import (
    AIModelRegistry, PromptTemplate, AIChatSession, AIUsageLog,
    AITokenLog, AIAgentConfig, KnowledgeContext, ConversationMemory,
    StudyPlan, StudyPlanSession, FlashcardDeck, Flashcard,
    QuizGeneration, QuizQuestion, LearningRecommendation, AITask,
)
from apps.control_center.models import AIConversation, AIMessage

User = get_user_model()
logger = logging.getLogger("brahmavidya.ai")


# ─── Conversation Selectors ────────────────────────────────────────────────────

class ConversationSelector:

    @staticmethod
    def get_user_conversations(user, search: str = "") -> QuerySet:
        """Returns all non-deleted conversations for a user, optional title search."""
        qs = AIConversation.objects.filter(user=user).order_by("-updated_at")
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    @staticmethod
    def get_conversation(conversation_id: str, user=None) -> AIConversation | None:
        try:
            qs = AIConversation.objects.filter(id=conversation_id)
            if user:
                qs = qs.filter(user=user)
            return qs.select_related("user").get()
        except AIConversation.DoesNotExist:
            return None

    @staticmethod
    def get_messages(conversation: AIConversation, page_size: int = 50) -> QuerySet:
        return (
            AIMessage.objects.filter(conversation=conversation)
            .order_by("created_at")[:page_size]
        )

    @staticmethod
    def get_conversation_memory(conversation: AIConversation) -> ConversationMemory | None:
        try:
            return ConversationMemory.objects.get(conversation=conversation)
        except ConversationMemory.DoesNotExist:
            return None

    @staticmethod
    def get_conversation_stats(user) -> dict:
        """Returns aggregate conversation stats for a user."""
        cache_key = f"bvg:ai:conv_stats:{user.id}"
        try:
            cached = cache.get(cache_key)
            if cached:
                return cached
        except Exception:
            pass

        convs = AIConversation.objects.filter(user=user)
        total = convs.count()
        messages_count = AIMessage.objects.filter(conversation__user=user).count()

        data = {
            "total_conversations": total,
            "total_messages": messages_count,
            "avg_messages_per_conversation": round(messages_count / total, 1) if total else 0,
        }
        try:
            cache.set(cache_key, data, 300)
        except Exception:
            pass
        return data


# ─── Prompt Template Selectors ────────────────────────────────────────────────

class PromptTemplateSelector:

    @staticmethod
    def get_all_active(category: str = "", public_only: bool = True) -> QuerySet:
        qs = PromptTemplate.objects.filter(is_active=True)
        if public_only:
            qs = qs.filter(is_public=True)
        if category:
            qs = qs.filter(category=category)
        return qs.order_by("-usage_count", "title")

    @staticmethod
    def get_by_id(template_id: str) -> PromptTemplate | None:
        try:
            return PromptTemplate.objects.get(id=template_id, is_active=True)
        except PromptTemplate.DoesNotExist:
            return None

    @staticmethod
    def get_favorites(user) -> QuerySet:
        return PromptTemplate.objects.filter(owner=user, is_favorite=True, is_active=True)

    @staticmethod
    def get_categories() -> list[str]:
        return list(
            PromptTemplate.objects.filter(is_active=True)
            .values_list("category", flat=True)
            .distinct()
            .order_by("category")
        )


# ─── AI Model Registry Selectors ──────────────────────────────────────────────

class AIModelSelector:

    @staticmethod
    def get_all_active() -> QuerySet:
        cache_key = "bvg:ai:model_registry"
        try:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            pass
        qs = AIModelRegistry.objects.filter(is_active=True).order_by("-is_default", "name")
        try:
            cache.set(cache_key, qs, 600)
        except Exception:
            pass
        return qs

    @staticmethod
    def get_default() -> AIModelRegistry | None:
        try:
            return AIModelRegistry.objects.get(is_default=True, is_active=True)
        except AIModelRegistry.DoesNotExist:
            return AIModelRegistry.objects.filter(is_active=True).first()


# ─── Usage & Token Selectors ──────────────────────────────────────────────────

class AIUsageSelector:

    @staticmethod
    def get_user_usage(user, days: int = 30) -> QuerySet:
        since = timezone.now() - datetime.timedelta(days=days)
        return (
            AIUsageLog.objects.filter(user=user, created_at__gte=since)
            .order_by("-created_at")
        )

    @staticmethod
    def get_daily_token_summary(user, days: int = 30) -> list[dict]:
        since = timezone.now().date() - datetime.timedelta(days=days)
        return list(
            AITokenLog.objects.filter(user=user, log_date__gte=since)
            .order_by("-log_date")
            .values("log_date", "tokens_used", "input_tokens", "output_tokens",
                    "request_count", "estimated_cost_usd")
        )

    @staticmethod
    def get_usage_by_feature(user, days: int = 30) -> list[dict]:
        since = timezone.now() - datetime.timedelta(days=days)
        return list(
            AIUsageLog.objects.filter(user=user, created_at__gte=since)
            .values("feature")
            .annotate(
                total_requests=Count("id"),
                total_tokens=Sum("total_tokens"),
                avg_latency=Avg("latency_ms"),
            )
            .order_by("-total_tokens")
        )

    @staticmethod
    def get_platform_usage_summary(days: int = 7) -> dict:
        """Admin: platform-wide usage summary."""
        cache_key = f"bvg:ai:platform_usage:{days}"
        try:
            cached = cache.get(cache_key)
            if cached:
                return cached
        except Exception:
            pass

        since = timezone.now() - datetime.timedelta(days=days)
        agg = AIUsageLog.objects.filter(created_at__gte=since).aggregate(
            total_requests=Count("id"),
            total_tokens=Sum("total_tokens"),
            total_cost=Sum("estimated_cost_usd"),
            avg_latency=Avg("latency_ms"),
            unique_users=Count("user", distinct=True),
        )
        data = {
            "period_days": days,
            "total_requests": agg["total_requests"] or 0,
            "total_tokens": agg["total_tokens"] or 0,
            "total_cost_usd": float(agg["total_cost"] or 0),
            "avg_latency_ms": int(agg["avg_latency"] or 0),
            "unique_users": agg["unique_users"] or 0,
        }
        try:
            cache.set(cache_key, data, 300)
        except Exception:
            pass
        return data


# ─── Study Plan Selectors ─────────────────────────────────────────────────────

class StudyPlanSelector:

    @staticmethod
    def get_active_plan(student) -> StudyPlan | None:
        return StudyPlan.objects.filter(student=student, is_active=True).first()

    @staticmethod
    def get_student_plans(student) -> QuerySet:
        return StudyPlan.objects.filter(student=student).order_by("-week_start")

    @staticmethod
    def get_plan_sessions(plan: StudyPlan, date: datetime.date | None = None) -> QuerySet:
        qs = StudyPlanSession.objects.filter(study_plan=plan).order_by("session_date", "time_slot")
        if date:
            qs = qs.filter(session_date=date)
        return qs

    @staticmethod
    def get_today_sessions(student) -> QuerySet:
        today = timezone.now().date()
        plan = StudyPlan.objects.filter(student=student, is_active=True).first()
        if not plan:
            return StudyPlanSession.objects.none()
        return StudyPlanSession.objects.filter(study_plan=plan, session_date=today).order_by("time_slot")

    @staticmethod
    def get_completion_stats(plan: StudyPlan) -> dict:
        sessions = StudyPlanSession.objects.filter(study_plan=plan)
        total = sessions.count()
        completed = sessions.filter(is_completed=True).count()
        return {
            "total_sessions": total,
            "completed_sessions": completed,
            "completion_rate": round(completed / total * 100, 1) if total else 0.0,
        }


# ─── Flashcard Selectors ──────────────────────────────────────────────────────

class FlashcardSelector:

    @staticmethod
    def get_student_decks(student) -> QuerySet:
        return FlashcardDeck.objects.filter(student=student, is_active=True).order_by("-created_at")

    @staticmethod
    def get_deck(deck_id: str, student=None) -> FlashcardDeck | None:
        try:
            qs = FlashcardDeck.objects.filter(id=deck_id, is_active=True)
            if student:
                qs = qs.filter(student=student)
            return qs.get()
        except FlashcardDeck.DoesNotExist:
            return None

    @staticmethod
    def get_due_cards(student, date: datetime.date | None = None) -> QuerySet:
        """Returns cards due for review today or earlier."""
        due_date = date or timezone.now().date()
        decks = FlashcardDeck.objects.filter(student=student, is_active=True).values_list("id", flat=True)
        return (
            Flashcard.objects.filter(deck_id__in=decks, next_review_date__lte=due_date)
            .select_related("deck")
            .order_by("leitner_box", "next_review_date")
        )

    @staticmethod
    def get_deck_stats(deck: FlashcardDeck) -> dict:
        cards = Flashcard.objects.filter(deck=deck)
        total = cards.count()
        reviewed = cards.filter(review_count__gt=0).count()
        avg_correct = cards.aggregate(avg=Avg("correct_count"))["avg"] or 0
        return {
            "total_cards": total,
            "reviewed_cards": reviewed,
            "unreviewed_cards": total - reviewed,
            "avg_correct_per_card": round(float(avg_correct), 2),
        }


# ─── Quiz Selectors ───────────────────────────────────────────────────────────

class QuizSelector:

    @staticmethod
    def get_user_quizzes(user) -> QuerySet:
        return QuizGeneration.objects.filter(generated_by=user).order_by("-created_at")

    @staticmethod
    def get_quiz(quiz_id: str, user=None) -> QuizGeneration | None:
        try:
            qs = QuizGeneration.objects.filter(id=quiz_id)
            if user:
                qs = qs.filter(generated_by=user)
            return qs.get()
        except QuizGeneration.DoesNotExist:
            return None

    @staticmethod
    def get_questions(quiz: QuizGeneration) -> QuerySet:
        return QuizQuestion.objects.filter(generation=quiz).order_by("question_number")

    @staticmethod
    def get_by_lesson(lesson_id: str, difficulty: str = "") -> QuerySet:
        qs = QuizGeneration.objects.filter(lesson_id=lesson_id)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        return qs.order_by("-created_at")


# ─── Recommendation Selectors ─────────────────────────────────────────────────

class RecommendationSelector:

    @staticmethod
    def get_pending(student, limit: int = 10) -> QuerySet:
        return (
            LearningRecommendation.objects.filter(
                student=student,
                status="PENDING",
            )
            .filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
            )
            .order_by("-priority_score", "-created_at")[:limit]
        )

    @staticmethod
    def get_all_for_student(student) -> QuerySet:
        return LearningRecommendation.objects.filter(student=student).order_by("-created_at")


# ─── AI Task Selectors ────────────────────────────────────────────────────────

class AITaskSelector:

    @staticmethod
    def get_task(celery_task_id: str) -> AITask | None:
        try:
            return AITask.objects.get(celery_task_id=celery_task_id)
        except AITask.DoesNotExist:
            return None

    @staticmethod
    def get_user_tasks(user, task_type: str = "") -> QuerySet:
        qs = AITask.objects.filter(triggered_by=user).order_by("-created_at")
        if task_type:
            qs = qs.filter(task_type=task_type)
        return qs

    @staticmethod
    def get_running_tasks() -> QuerySet:
        return AITask.objects.filter(status="RUNNING").order_by("-created_at")

    @staticmethod
    def get_failed_tasks(hours: int = 24) -> QuerySet:
        since = timezone.now() - datetime.timedelta(hours=hours)
        return AITask.objects.filter(status="FAILURE", created_at__gte=since).order_by("-created_at")


# ─── Knowledge Context Selectors ──────────────────────────────────────────────

class KnowledgeContextSelector:

    @staticmethod
    def get_unembedded(limit: int = 100) -> QuerySet:
        return KnowledgeContext.objects.filter(is_embedded=False).order_by("created_at")[:limit]

    @staticmethod
    def get_by_source(source_type: str, source_id: str) -> QuerySet:
        return KnowledgeContext.objects.filter(
            source_type=source_type, source_id=source_id
        ).order_by("chunk_index")

    @staticmethod
    def search_keyword(query: str, source_types: list[str] | None = None, top_k: int = 10) -> QuerySet:
        words = [w.strip() for w in query.split() if len(w.strip()) > 3]
        if not words:
            return KnowledgeContext.objects.none()
        q_obj = Q()
        for word in words[:6]:
            q_obj |= Q(chunk_text__icontains=word)
        qs = KnowledgeContext.objects.filter(q_obj)
        if source_types:
            qs = qs.filter(source_type__in=source_types)
        return qs.order_by("-created_at")[:top_k]
