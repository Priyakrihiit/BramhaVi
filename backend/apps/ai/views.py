"""
apps/ai/views.py
Sprint 24 — Phase 4: AI ViewSets — BrahmaVidya Galaxy

ViewSets exposing Django REST APIs for:
  - AI Chat & Conversation History
  - Prompt Templates CRUD
  - Flashcard Decks Generation & Leitner spaced repetition reviews
  - Quiz Generation & retrieving questions
  - Study Plan Generation & Session tracking
  - Learning Recommendations
  - Custom AI generators: Lesson Explanation, Summarised Notes, Assignments, and Roadmaps
"""

from __future__ import annotations

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.ai.models import (
    PromptTemplate, StudyPlan, StudyPlanSession, FlashcardDeck, Flashcard,
    QuizGeneration, QuizQuestion, LearningRecommendation, AIUsageLog, AITask,
)
from apps.control_center.models import AIConversation, AIMessage
from apps.ai.serializers import (
    PromptTemplateSerializer, StudyPlanSerializer, StudyPlanSessionSerializer,
    FlashcardDeckSerializer, FlashcardSerializer, QuizGenerationSerializer,
    QuizQuestionSerializer, LearningRecommendationSerializer, ConversationSerializer,
    MessageSerializer, AIUsageLogSerializer, AITaskSerializer,
)
from apps.ai.permissions import IsOwnerOrAdmin, IsStudentUser
from apps.ai.services import (
    ConversationService, QuizGenerationService, FlashcardService,
    StudyPlanService, RecommendationService, GeminiService, AIUsageService,
)
from apps.ai.selectors import (
    ConversationSelector, PromptTemplateSelector, StudyPlanSelector,
    FlashcardSelector, QuizSelector, RecommendationSelector,
)
from apps.ai.validators import (
    validate_chat_message, validate_quiz_generation_request,
    validate_flashcard_generation_request, validate_flashcard_review,
    validate_study_plan_request, validate_explain_request,
    validate_notes_request, validate_code_request,
)

logger = logging.getLogger("brahmavidya.ai.views")


class ConversationViewSet(viewsets.ModelViewSet):
    """
    Exposes conversation history CRUD and chat message generation.
    """
    queryset = AIConversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return ConversationSelector.get_user_conversations(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get", "post"])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        if request.method == "GET":
            msgs = ConversationSelector.get_messages(conversation)
            serializer = MessageSerializer(msgs, many=True)
            return Response(serializer.data)
        
        elif request.method == "POST":
            content = request.data.get("content")
            validate_chat_message(content)
            
            agent_type = request.data.get("agent_type", "tutor")
            model_id = request.data.get("model_id")
            enable_rag = request.data.get("enable_rag", False)
            
            # Quota Check
            allowed, reason = AIUsageService.check_quota(request.user)
            if not allowed:
                return Response({"detail": reason}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            res = ConversationService.send_message(
                conversation=conversation,
                user_content=content,
                agent_type=agent_type,
                model_id=model_id,
                enable_rag=enable_rag
            )
            
            # Log usage
            AIUsageService.log_usage(
                user=request.user,
                feature="chat",
                model_id=res["model_id"],
                prompt_tokens=res["prompt_tokens"],
                completion_tokens=res["completion_tokens"],
                conversation=conversation
            )
            
            return Response({
                "user_message": MessageSerializer(res["user_message"]).data,
                "assistant_message": MessageSerializer(res["assistant_message"]).data
            }, status=status.HTTP_201_CREATED)


class PromptTemplateViewSet(viewsets.ModelViewSet):
    """
    Exposes CRUD for prompt templates.
    """
    queryset = PromptTemplate.objects.all()
    serializer_class = PromptTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        category = self.request.query_params.get("category", "")
        return PromptTemplateSelector.get_all_active(category=category, public_only=True)


class FlashcardDeckViewSet(viewsets.ModelViewSet):
    """
    Exposes Flashcard Decks API.
    """
    queryset = FlashcardDeck.objects.all()
    serializer_class = FlashcardDeckSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return FlashcardSelector.get_student_decks(self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=False, methods=["post"])
    def generate(self, request):
        validate_flashcard_generation_request(request.data)
        
        # Quota Check
        allowed, reason = AIUsageService.check_quota(request.user)
        if not allowed:
            return Response({"detail": reason}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        deck = FlashcardService.generate(
            student=request.user,
            topic=request.data["topic"],
            source_text=request.data.get("source_text", ""),
            card_count=request.data.get("card_count", 15),
            card_type=request.data.get("card_type", "TERM_DEFINITION"),
            lesson_id=request.data.get("lesson_id"),
            course_id=request.data.get("course_id")
        )
        
        # Log usage
        AIUsageService.log_usage(
            user=request.user,
            feature="flashcards",
            model_id=deck.model_id,
            prompt_tokens=deck.prompt_tokens,
            completion_tokens=deck.completion_tokens
        )
        
        return Response(FlashcardDeckSerializer(deck).data, status=status.HTTP_201_CREATED)


class FlashcardViewSet(viewsets.ModelViewSet):
    """
    Exposes reviews for flashcards.
    """
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        card = self.get_object()
        validate_flashcard_review(request.data)
        updated_card = FlashcardService.review_card(card, request.data["correct"])
        return Response(FlashcardSerializer(updated_card).data)


class QuizGenerationViewSet(viewsets.ModelViewSet):
    """
    Exposes Quiz Generation APIs.
    """
    queryset = QuizGeneration.objects.all()
    serializer_class = QuizGenerationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return QuizSelector.get_user_quizzes(self.request.user)

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)

    @action(detail=False, methods=["post"])
    def generate(self, request):
        validate_quiz_generation_request(request.data)

        # Quota Check
        allowed, reason = AIUsageService.check_quota(request.user)
        if not allowed:
            return Response({"detail": reason}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        quiz = QuizGenerationService.generate(
            generated_by=request.user,
            topic=request.data["topic"],
            source_text=request.data.get("source_text", ""),
            question_count=request.data.get("question_count", 10),
            difficulty=request.data.get("difficulty", "medium"),
            question_type=request.data.get("question_type", "MCQ"),
            lesson_id=request.data.get("lesson_id"),
            course_id=request.data.get("course_id")
        )
        
        # Log usage
        AIUsageService.log_usage(
            user=request.user,
            feature="quiz",
            model_id=quiz.model_id,
            prompt_tokens=quiz.prompt_tokens,
            completion_tokens=quiz.completion_tokens
        )
        
        return Response(QuizGenerationSerializer(quiz).data, status=status.HTTP_201_CREATED)


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Exposes personalized Recommendations.
    """
    queryset = LearningRecommendation.objects.all()
    serializer_class = LearningRecommendationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return RecommendationSelector.get_all_for_student(self.request.user)

    @action(detail=False, methods=["post"])
    def refresh(self, request):
        recs = RecommendationService.generate_for_student(request.user)
        return Response(LearningRecommendationSerializer(recs, many=True).data)


class AIFeatureViewSet(viewsets.ViewSet):
    """
    Endpoint mapping for ad-hoc generation tasks:
      - Lesson Explanation
      - Summarised Notes
      - Assignments
      - Roadmaps
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="explain")
    def explain_lesson(self, request):
        validate_explain_request(request.data)
        
        # Quota Check
        allowed, reason = AIUsageService.check_quota(request.user)
        if not allowed:
            return Response({"detail": reason}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        content = request.data["content"]
        level = request.data.get("level", "intermediate")
        
        prompt = f"Explain the following academic concept in clear details suitable for a {level}-level student:\n\n{content}"
        res = GeminiService.chat(
            messages=[{"role": "user", "parts": [{"text": prompt}]}],
            model_id="gemini-1.5-flash",
            system_prompt="You are an encouraging tutor explaining complex concepts simply."
        )
        
        # Log usage
        AIUsageService.log_usage(
            user=request.user,
            feature="explain",
            model_id="gemini-1.5-flash",
            prompt_tokens=res.get("prompt_tokens", 0),
            completion_tokens=res.get("completion_tokens", 0)
        )
        
        return Response({
            "explanation": res["content"],
            "model_id": "gemini-1.5-flash"
        })

    @action(detail=False, methods=["post"], url_path="notes/generate")
    def generate_notes(self, request):
        validate_notes_request(request.data)
        
        # Quota Check
        allowed, reason = AIUsageService.check_quota(request.user)
        if not allowed:
            return Response({"detail": reason}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        content = request.data["content"]
        fmt = request.data.get("format", "SUMMARY")
        
        prompt = f"Summarize the following content using the academic formatting style '{fmt}':\n\n{content}"
        res = GeminiService.chat(
            messages=[{"role": "user", "parts": [{"text": prompt}]}],
            model_id="gemini-1.5-flash",
            system_prompt="You are a study notes organizer. Respond with highly structured markdown notes."
        )
        
        # Log usage
        AIUsageService.log_usage(
            user=request.user,
            feature="notes",
            model_id="gemini-1.5-flash",
            prompt_tokens=res.get("prompt_tokens", 0),
            completion_tokens=res.get("completion_tokens", 0)
        )
        
        return Response({
            "notes": res["content"],
            "format": fmt
        })

    @action(detail=False, methods=["post"], url_path="roadmap")
    def generate_roadmap(self, request):
        # Quota Check
        allowed, reason = AIUsageService.check_quota(request.user)
        if not allowed:
            return Response({"detail": reason}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        topic = request.data.get("topic")
        if not topic:
            return Response({"detail": "topic is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        prompt = f"Create a comprehensive step-by-step learning roadmap for: '{topic}'. Include major milestones, recommended study resources, and estimated timeframes."
        res = GeminiService.chat(
            messages=[{"role": "user", "parts": [{"text": prompt}]}],
            model_id="gemini-1.5-pro",
            system_prompt="You are an expert curriculum designer. Produce clean markdown learning roadmaps."
        )
        
        # Log usage
        AIUsageService.log_usage(
            user=request.user,
            feature="roadmap",
            model_id="gemini-1.5-pro",
            prompt_tokens=res.get("prompt_tokens", 0),
            completion_tokens=res.get("completion_tokens", 0)
        )
        
        return Response({
            "roadmap": res["content"],
            "topic": topic
        })

    @action(detail=False, methods=["post"], url_path="assignment/generate")
    def generate_assignment(self, request):
        # Quota Check
        allowed, reason = AIUsageService.check_quota(request.user)
        if not allowed:
            return Response({"detail": reason}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        topic = request.data.get("topic")
        difficulty = request.data.get("difficulty", "medium")
        if not topic:
            return Response({"detail": "topic is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        prompt = f"Design a rigorous academic assignment on the topic '{topic}' at a '{difficulty}' level. Include objective tasks, subjective questions, a grading rubric, and learning objectives."
        res = GeminiService.chat(
            messages=[{"role": "user", "parts": [{"text": prompt}]}],
            model_id="gemini-1.5-pro",
            system_prompt="You are an academic course developer. Output high-quality markdown assignment templates."
        )
        
        # Log usage
        AIUsageService.log_usage(
            user=request.user,
            feature="assignment",
            model_id="gemini-1.5-pro",
            prompt_tokens=res.get("prompt_tokens", 0),
            completion_tokens=res.get("completion_tokens", 0)
        )
        
        return Response({
            "assignment": res["content"],
            "topic": topic,
            "difficulty": difficulty
        })
