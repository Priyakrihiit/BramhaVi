"""
apps/ai/serializers.py
Sprint 24 — Phase 4: AI Model Serializers — BrahmaVidya Galaxy

Serializers transforming DB models to JSON and validating incoming request bodies.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.ai.models import (
    PromptTemplate, StudyPlan, StudyPlanSession, FlashcardDeck, Flashcard,
    QuizGeneration, QuizQuestion, LearningRecommendation, AIUsageLog, AITask,
)
from apps.control_center.models import AIConversation, AIMessage


# ─── Conversation & Chat Serializers ──────────────────────────────────────────

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversation
        fields = ["id", "user", "title", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender_role = serializers.SerializerMethodField()

    class Meta:
        model = AIMessage
        fields = ["id", "conversation", "sender_type", "sender_role", "content", "token_count", "created_at"]
        read_only_fields = ["id", "conversation", "sender_type", "sender_role", "token_count", "created_at"]

    def get_sender_role(self, obj) -> str:
        return "user" if obj.sender_type == "USER" else "assistant"


# ─── Prompt Template Serializers ──────────────────────────────────────────────

class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = [
            "id", "title", "description", "category", "system_prompt",
            "prompt_text", "variables", "is_active", "is_public",
            "usage_count", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "usage_count", "created_at", "updated_at"]


# ─── Study Plan Serializers ───────────────────────────────────────────────────

class StudyPlanSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyPlanSession
        fields = [
            "id", "session_date", "time_slot", "session_type", "course_title",
            "lesson_title", "goal", "duration_minutes", "is_completed",
            "motivational_message", "created_at"
        ]


class StudyPlanSerializer(serializers.ModelSerializer):
    sessions = StudyPlanSessionSerializer(many=True, read_only=True)

    class Meta:
        model = StudyPlan
        fields = [
            "id", "student", "title", "week_start", "week_end",
            "available_hours_per_day", "learning_pace", "learning_style",
            "goal", "weekly_goals", "risk_alerts", "is_active", "sessions",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "weekly_goals", "risk_alerts", "created_at", "updated_at"]


# ─── Flashcard Serializers ────────────────────────────────────────────────────

class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = [
            "id", "card_type", "front", "back", "hint", "difficulty",
            "tags", "next_review_date", "leitner_box", "review_count",
            "correct_count", "last_reviewed_at"
        ]
        read_only_fields = ["id", "next_review_date", "leitner_box", "review_count", "correct_count", "last_reviewed_at"]


class FlashcardDeckSerializer(serializers.ModelSerializer):
    cards = FlashcardSerializer(many=True, read_only=True)

    class Meta:
        model = FlashcardDeck
        fields = [
            "id", "student", "title", "topic", "card_type", "lesson_id",
            "course_id", "card_count", "is_active", "cards", "created_at"
        ]
        read_only_fields = ["id", "student", "card_count", "created_at"]


# ─── Quiz Generation Serializers ──────────────────────────────────────────────

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = [
            "id", "question_number", "question", "question_type", "options",
            "correct_answer", "explanation", "concept_tag", "bloom_level",
            "difficulty_score"
        ]


class QuizGenerationSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = QuizGeneration
        fields = [
            "id", "generated_by", "quiz_title", "topic", "difficulty",
            "question_type", "question_count", "lesson_id", "course_id",
            "questions", "created_at"
        ]
        read_only_fields = ["id", "generated_by", "question_count", "created_at"]


# ─── Learning Recommendation Serializers ──────────────────────────────────────

class LearningRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningRecommendation
        fields = [
            "id", "student", "recommendation_type", "title", "description",
            "reason", "priority_score", "status", "target_type", "target_url",
            "expires_at", "created_at"
        ]
        read_only_fields = ["id", "student", "created_at"]


# ─── AI Usage & Task Serializers ──────────────────────────────────────────────

class AIUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIUsageLog
        fields = [
            "id", "user", "model_id", "feature", "prompt_tokens",
            "completion_tokens", "total_tokens", "estimated_cost_usd",
            "latency_ms", "created_at"
        ]


class AITaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AITask
        fields = [
            "id", "triggered_by", "task_type", "celery_task_id", "status",
            "error_message", "started_at", "completed_at", "created_at"
        ]
