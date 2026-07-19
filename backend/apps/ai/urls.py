"""
apps/ai/urls.py
Sprint 24 — Phase 4: AI Endpoints Router — BrahmaVidya Galaxy

Maps routing paths to Conversation History, AI Chat, Prompt Templates,
Flashcards, Quizzes, Recommendations, and custom generation features.
"""

from __future__ import annotations

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.ai.views import (
    ConversationViewSet, PromptTemplateViewSet, FlashcardDeckViewSet,
    FlashcardViewSet, QuizGenerationViewSet, RecommendationViewSet, AIFeatureViewSet,
)

router = DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversation")
router.register("prompts", PromptTemplateViewSet, basename="prompt")
router.register("flashcards/decks", FlashcardDeckViewSet, basename="flashcard-deck")
router.register("flashcards", FlashcardViewSet, basename="flashcard")
router.register("quizzes", QuizGenerationViewSet, basename="quiz")
router.register("recommendations", RecommendationViewSet, basename="recommendation")
router.register("features", AIFeatureViewSet, basename="feature")

app_name = "ai"

urlpatterns = [
    path("", include(router.urls)),
]
