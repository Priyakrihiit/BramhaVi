"""
apps/ai/filters.py
Sprint 24 — Phase 3: AI Query Parameter Filters — BrahmaVidya Galaxy

FilterSets enabling query-parameter-based search and filter logic.
"""

from __future__ import annotations

import django_filters
from django_filters import rest_framework as df_filters

from apps.ai.models import (
    PromptTemplate, StudyPlan, FlashcardDeck, Flashcard,
    QuizGeneration, LearningRecommendation, AIUsageLog, AITask,
)


class PromptTemplateFilter(df_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category", lookup_expr="exact")
    is_public = django_filters.BooleanFilter(field_name="is_public")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = PromptTemplate
        fields = ["category", "is_public", "title"]


class StudyPlanFilter(df_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")
    week_start_after = django_filters.DateFilter(field_name="week_start", lookup_expr="gte")
    week_start_before = django_filters.DateFilter(field_name="week_start", lookup_expr="lte")

    class Meta:
        model = StudyPlan
        fields = ["is_active"]


class FlashcardDeckFilter(df_filters.FilterSet):
    topic = django_filters.CharFilter(field_name="topic", lookup_expr="icontains")
    card_type = django_filters.CharFilter(field_name="card_type", lookup_expr="exact")
    lesson_id = django_filters.CharFilter(field_name="lesson_id", lookup_expr="exact")
    course_id = django_filters.CharFilter(field_name="course_id", lookup_expr="exact")

    class Meta:
        model = FlashcardDeck
        fields = ["topic", "card_type", "lesson_id", "course_id"]


class FlashcardFilter(df_filters.FilterSet):
    leitner_box = django_filters.NumberFilter(field_name="leitner_box")
    next_review_before = django_filters.DateFilter(field_name="next_review_date", lookup_expr="lte")

    class Meta:
        model = Flashcard
        fields = ["leitner_box"]


class QuizGenerationFilter(df_filters.FilterSet):
    difficulty = django_filters.CharFilter(field_name="difficulty", lookup_expr="exact")
    question_type = django_filters.CharFilter(field_name="question_type", lookup_expr="exact")
    lesson_id = django_filters.CharFilter(field_name="lesson_id", lookup_expr="exact")
    course_id = django_filters.CharFilter(field_name="course_id", lookup_expr="exact")

    class Meta:
        model = QuizGeneration
        fields = ["difficulty", "question_type", "lesson_id", "course_id"]


class LearningRecommendationFilter(df_filters.FilterSet):
    recommendation_type = django_filters.CharFilter(field_name="recommendation_type", lookup_expr="exact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = LearningRecommendation
        fields = ["recommendation_type", "status"]


class AIUsageLogFilter(df_filters.FilterSet):
    feature = django_filters.CharFilter(field_name="feature", lookup_expr="exact")
    model_id = django_filters.CharFilter(field_name="model_id", lookup_expr="exact")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")

    class Meta:
        model = AIUsageLog
        fields = ["feature", "model_id"]


class AITaskFilter(df_filters.FilterSet):
    task_type = django_filters.CharFilter(field_name="task_type", lookup_expr="exact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = AITask
        fields = ["task_type", "status"]
