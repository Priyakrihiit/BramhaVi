"""
apps/ai/validators.py
Sprint 24 — Phase 3: AI Input Validators — BrahmaVidya Galaxy

Validates all incoming API inputs before they reach services.
Raises django.core.exceptions.ValidationError with structured messages.
"""

from __future__ import annotations

import re
from django.core.exceptions import ValidationError


# ─── Constants ────────────────────────────────────────────────────────────────

ALLOWED_MODEL_IDS = {
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.0-pro",
    "gemini-pro",
}

ALLOWED_AGENT_TYPES = {
    "tutor", "explainer", "quiz", "assignment", "code",
    "roadmap", "notes", "flashcards", "doubt", "study_planner",
    "resume", "interview", "teacher", "analytics", "general",
}

ALLOWED_QUESTION_TYPES = {"MCQ", "TRUE_FALSE", "SHORT_ANSWER", "FILL_BLANK", "MIXED"}
ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
ALLOWED_CARD_TYPES = {"TERM_DEFINITION", "Q_A", "CLOZE", "CONCEPT_MAP"}
ALLOWED_EXPORT_FORMATS = {"markdown", "text", "json"}
ALLOWED_LEARNING_PACES = {"slow", "moderate", "fast"}
ALLOWED_LEARNING_STYLES = {"VISUAL", "READING", "PRACTICE"}
ALLOWED_NOTE_FORMATS = {"CORNELL", "OUTLINE", "MINDMAP", "SUMMARY", "BULLETS"}
ALLOWED_CODE_MODES = {"COMPLETE", "EXPLAIN", "DEBUG", "REVIEW", "REFACTOR", "TEST"}

MAX_MESSAGE_LENGTH = 32_000     # ~8k tokens
MAX_PROMPT_TEMPLATE_LENGTH = 64_000
MAX_SOURCE_TEXT_LENGTH = 100_000
MAX_TOPIC_LENGTH = 500
MAX_TITLE_LENGTH = 255
MAX_GOAL_LENGTH = 2_000


# ─── Chat / Message Validators ────────────────────────────────────────────────

def validate_chat_message(content: str) -> None:
    """Validates a single AI chat message payload."""
    if not content or not content.strip():
        raise ValidationError("Message content cannot be empty.")
    if len(content) > MAX_MESSAGE_LENGTH:
        raise ValidationError(
            f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters "
            f"(current: {len(content)})."
        )


def validate_model_id(model_id: str) -> None:
    """Validates that the requested model is registered and active."""
    if not model_id:
        return  # use default
    from apps.ai.models import AIModelRegistry
    exists = AIModelRegistry.objects.filter(model_id=model_id, is_active=True).exists()
    if not exists and model_id not in ALLOWED_MODEL_IDS:
        raise ValidationError(
            f"Model '{model_id}' is not available. "
            f"Allowed: {sorted(ALLOWED_MODEL_IDS)}."
        )


def validate_agent_type(agent_type: str) -> None:
    if agent_type not in ALLOWED_AGENT_TYPES:
        raise ValidationError(
            f"Unknown agent type '{agent_type}'. "
            f"Allowed: {sorted(ALLOWED_AGENT_TYPES)}."
        )


def validate_conversation_title(title: str) -> None:
    if not title or not title.strip():
        raise ValidationError("Conversation title cannot be empty.")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError(f"Title exceeds {MAX_TITLE_LENGTH} characters.")


# ─── Prompt Template Validators ───────────────────────────────────────────────

def validate_prompt_template(data: dict) -> None:
    """Validates a PromptTemplate create/update payload."""
    title = data.get("title", "")
    prompt_text = data.get("prompt_text", "")

    if not title or not title.strip():
        raise ValidationError("Prompt template title is required.")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError(f"Title exceeds {MAX_TITLE_LENGTH} characters.")
    if not prompt_text or not prompt_text.strip():
        raise ValidationError("Prompt text is required.")
    if len(prompt_text) > MAX_PROMPT_TEMPLATE_LENGTH:
        raise ValidationError(f"Prompt text exceeds {MAX_PROMPT_TEMPLATE_LENGTH} characters.")

    # Validate variable syntax {{variable_name}}
    variables = data.get("variables", [])
    if variables:
        for var in variables:
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", str(var)):
                raise ValidationError(
                    f"Invalid variable name '{var}'. Use snake_case identifiers."
                )

    # Check that all listed variables appear in the prompt_text
    for var in variables:
        placeholder = f"{{{{{var}}}}}"
        if placeholder not in prompt_text:
            raise ValidationError(
                f"Variable '{{{{ {var} }}}}' listed but not found in prompt_text."
            )


def validate_prompt_variables(variables: dict, template_variables: list[str]) -> None:
    """Validates that required template variables are provided."""
    missing = [v for v in template_variables if v not in variables]
    if missing:
        raise ValidationError(f"Missing required prompt variables: {missing}.")


# ─── Quiz Generation Validators ───────────────────────────────────────────────

def validate_quiz_generation_request(data: dict) -> None:
    """Validates AI quiz generation request payload."""
    topic = data.get("topic", "")
    source_text = data.get("source_text", "")
    question_count = data.get("question_count", 10)
    difficulty = data.get("difficulty", "medium")
    question_type = data.get("question_type", "MCQ")

    if not topic or not topic.strip():
        raise ValidationError("Quiz topic is required.")
    if len(topic) > MAX_TOPIC_LENGTH:
        raise ValidationError(f"Topic exceeds {MAX_TOPIC_LENGTH} characters.")

    if source_text and len(source_text) > MAX_SOURCE_TEXT_LENGTH:
        raise ValidationError(f"Source text exceeds {MAX_SOURCE_TEXT_LENGTH} characters.")

    if not isinstance(question_count, int) or not (1 <= question_count <= 50):
        raise ValidationError("question_count must be an integer between 1 and 50.")

    if difficulty not in ALLOWED_DIFFICULTIES:
        raise ValidationError(f"difficulty must be one of: {sorted(ALLOWED_DIFFICULTIES)}.")

    if question_type not in ALLOWED_QUESTION_TYPES:
        raise ValidationError(f"question_type must be one of: {sorted(ALLOWED_QUESTION_TYPES)}.")


# ─── Flashcard Validators ─────────────────────────────────────────────────────

def validate_flashcard_generation_request(data: dict) -> None:
    """Validates AI flashcard deck generation request payload."""
    topic = data.get("topic", "")
    source_text = data.get("source_text", "")
    card_count = data.get("card_count", 15)
    card_type = data.get("card_type", "TERM_DEFINITION")

    if not topic or not topic.strip():
        raise ValidationError("Flashcard topic is required.")
    if len(topic) > MAX_TOPIC_LENGTH:
        raise ValidationError(f"Topic exceeds {MAX_TOPIC_LENGTH} characters.")

    if source_text and len(source_text) > MAX_SOURCE_TEXT_LENGTH:
        raise ValidationError(f"Source text exceeds {MAX_SOURCE_TEXT_LENGTH} characters.")

    if not isinstance(card_count, int) or not (5 <= card_count <= 100):
        raise ValidationError("card_count must be between 5 and 100.")

    if card_type not in ALLOWED_CARD_TYPES:
        raise ValidationError(f"card_type must be one of: {sorted(ALLOWED_CARD_TYPES)}.")


def validate_flashcard_review(data: dict) -> None:
    """Validates a flashcard review submission."""
    correct = data.get("correct")
    if correct is None or not isinstance(correct, bool):
        raise ValidationError("'correct' field must be a boolean (true/false).")


# ─── Study Plan Validators ────────────────────────────────────────────────────

def validate_study_plan_request(data: dict) -> None:
    """Validates an AI study plan generation request."""
    week_start = data.get("week_start")
    hours_per_day = data.get("available_hours_per_day", 2)
    pace = data.get("learning_pace", "moderate")
    style = data.get("learning_style", "READING")
    goal = data.get("goal", "")

    if not week_start:
        raise ValidationError("week_start date is required (YYYY-MM-DD).")
    try:
        from datetime import date
        if isinstance(week_start, str):
            date.fromisoformat(week_start)
    except ValueError:
        raise ValidationError("week_start must be a valid date in YYYY-MM-DD format.")

    if not isinstance(hours_per_day, int) or not (1 <= hours_per_day <= 16):
        raise ValidationError("available_hours_per_day must be between 1 and 16.")

    if pace not in ALLOWED_LEARNING_PACES:
        raise ValidationError(f"learning_pace must be one of: {sorted(ALLOWED_LEARNING_PACES)}.")

    if style not in ALLOWED_LEARNING_STYLES:
        raise ValidationError(f"learning_style must be one of: {sorted(ALLOWED_LEARNING_STYLES)}.")

    if goal and len(goal) > MAX_GOAL_LENGTH:
        raise ValidationError(f"Goal exceeds {MAX_GOAL_LENGTH} characters.")


# ─── Content Embedding Validators ────────────────────────────────────────────

def validate_embed_request(data: dict) -> None:
    """Validates a content embedding request."""
    source_type = data.get("source_type", "")
    source_id = data.get("source_id", "")
    text = data.get("text", "")

    ALLOWED_SOURCE_TYPES = {
        "lesson", "course", "quiz_question", "student_note",
        "assignment", "ai_prompt_template", "announcement", "article",
    }

    if not source_type or source_type not in ALLOWED_SOURCE_TYPES:
        raise ValidationError(
            f"source_type must be one of: {sorted(ALLOWED_SOURCE_TYPES)}."
        )
    if not source_id:
        raise ValidationError("source_id is required.")
    if not text or not text.strip():
        raise ValidationError("text content is required for embedding.")
    if len(text) > MAX_SOURCE_TEXT_LENGTH:
        raise ValidationError(f"text exceeds {MAX_SOURCE_TEXT_LENGTH} characters.")


# ─── Code Assistant Validators ────────────────────────────────────────────────

def validate_code_request(data: dict) -> None:
    """Validates an AI code assistant request."""
    code = data.get("code", "")
    mode = data.get("mode", "EXPLAIN")
    language = data.get("language", "python")

    if not code or not code.strip():
        raise ValidationError("code is required.")
    if len(code) > 50_000:
        raise ValidationError("Code block exceeds 50,000 characters.")
    if mode not in ALLOWED_CODE_MODES:
        raise ValidationError(f"mode must be one of: {sorted(ALLOWED_CODE_MODES)}.")
    if not language or not language.strip():
        raise ValidationError("language is required.")


# ─── General AI Feature Validators ───────────────────────────────────────────

def validate_explain_request(data: dict) -> None:
    """Validates an AI lesson explainer request."""
    content = data.get("content", "")
    if not content or not content.strip():
        raise ValidationError("Content to explain is required.")
    if len(content) > MAX_SOURCE_TEXT_LENGTH:
        raise ValidationError(f"Content exceeds {MAX_SOURCE_TEXT_LENGTH} characters.")


def validate_notes_request(data: dict) -> None:
    """Validates an AI notes generation request."""
    content = data.get("content", "")
    note_format = data.get("format", "SUMMARY")
    if not content or not content.strip():
        raise ValidationError("Content for note generation is required.")
    if len(content) > MAX_SOURCE_TEXT_LENGTH:
        raise ValidationError(f"Content exceeds {MAX_SOURCE_TEXT_LENGTH} characters.")
    if note_format not in ALLOWED_NOTE_FORMATS:
        raise ValidationError(f"format must be one of: {sorted(ALLOWED_NOTE_FORMATS)}.")


def validate_feedback_payload(data: dict) -> None:
    """Validates a message feedback payload."""
    feedback_type = data.get("feedback_type", "")
    if feedback_type not in ("THUMBS_UP", "THUMBS_DOWN"):
        raise ValidationError("feedback_type must be 'THUMBS_UP' or 'THUMBS_DOWN'.")
    rating = data.get("rating")
    if rating is not None and (not isinstance(rating, int) or not (1 <= rating <= 5)):
        raise ValidationError("rating must be an integer between 1 and 5.")


def validate_export_format(fmt: str) -> None:
    if fmt not in ALLOWED_EXPORT_FORMATS:
        raise ValidationError(
            f"export format must be one of: {sorted(ALLOWED_EXPORT_FORMATS)}."
        )
