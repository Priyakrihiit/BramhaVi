"""
apps/ai/models.py
Sprint 24 — Phase 2: AI Learning Platform Database Models

DESIGN RULES:
- DO NOT duplicate AIConversation, AIMessage, AIFeedback (already in control_center/models.py)
- SQLite-compatible fields only (USE_SQLITE=True is the default)
- Inherit from BaseModel (UUID pk, created_at, updated_at) or SoftDeleteModel
- All db_table names prefixed with "ai_" to avoid collisions
"""

import uuid
from django.db import models
from django.conf import settings
from apps.base_models import BaseModel, SoftDeleteModel


# ─── 1. AI Model Registry ─────────────────────────────────────────────────────

class AIModelRegistry(BaseModel):
    """
    Persistent registry of all AI models available on the platform.
    Migrated from ai_store.json 'models' dict to PostgreSQL/SQLite.
    """
    MODEL_PROVIDER_CHOICES = [
        ("Gemini", "Gemini"),
        ("GPT", "GPT"),
        ("Claude", "Claude"),
        ("Open Source Models", "Open Source Models"),
        ("Other", "Other"),
    ]
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DISABLED", "Disabled"),
        ("DEPRECATED", "Deprecated"),
    ]

    model_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Canonical model identifier (e.g. 'gemini-1.5-pro', 'gpt-4o')."
    )
    name = models.CharField(max_length=255, help_text="Human-readable display name.")
    provider = models.CharField(
        max_length=50,
        choices=MODEL_PROVIDER_CHOICES,
        default="Gemini",
        help_text="API provider name."
    )
    context_window = models.IntegerField(
        default=128000,
        help_text="Maximum input context tokens supported."
    )
    max_output_tokens = models.IntegerField(
        default=4096,
        help_text="Maximum generation output tokens."
    )
    default_temperature = models.FloatField(
        default=0.7,
        help_text="Default sampling temperature (0.0–2.0)."
    )
    input_token_rate = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        default=0.0,
        help_text="Cost per input token in USD."
    )
    output_token_rate = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        default=0.0,
        help_text="Cost per output token in USD."
    )
    supports_streaming = models.BooleanField(default=True)
    supports_function_calling = models.BooleanField(default=False)
    supports_vision = models.BooleanField(default=False)
    supports_grounding = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    is_default = models.BooleanField(
        default=False,
        help_text="Exactly one model should be default at a time."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )
    capabilities = models.JSONField(
        default=dict,
        blank=True,
        help_text="Arbitrary capability flags and metadata dict."
    )

    class Meta:
        db_table = "ai_model_registry"
        verbose_name = "AI Model"
        verbose_name_plural = "AI Model Registry"
        ordering = ["-is_default", "name"]

    def __str__(self):
        return f"{self.name} ({self.provider})"


# ─── 2. AI Prompt Template ────────────────────────────────────────────────────

class PromptTemplate(SoftDeleteModel):
    """
    Versioned, categorized prompt templates powering all AI features.
    Migrated from ai_store.json 'prompts' dict to SQLite/PostgreSQL.
    """
    CATEGORY_CHOICES = [
        ("Education", "Education"),
        ("Programming", "Programming"),
        ("Resume", "Resume"),
        ("Portfolio", "Portfolio"),
        ("Career", "Career"),
        ("Translation", "Translation"),
        ("Business", "Business"),
        ("Marketing", "Marketing"),
        ("Blog Writing", "Blog Writing"),
        ("Research", "Research"),
        ("Mathematics", "Mathematics"),
        ("Science", "Science"),
        ("Tutoring", "Tutoring"),
        ("Code", "Code"),
        ("Planning", "Planning"),
        ("Analytics", "Analytics"),
        ("Teacher", "Teacher"),
        ("Interview", "Interview"),
        ("Other", "Other"),
    ]

    title = models.CharField(max_length=255, help_text="Short display title for the prompt.")
    description = models.TextField(blank=True, default="", help_text="What this prompt does.")
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="Education",
        db_index=True
    )
    system_prompt = models.TextField(
        blank=True,
        default="",
        help_text="System instruction injected before user messages."
    )
    prompt_text = models.TextField(help_text="Main prompt body. Supports {{variable}} placeholders.")
    variables = models.JSONField(
        default=list,
        blank=True,
        help_text="List of variable names expected in prompt_text e.g. ['student_name', 'lesson_content']."
    )
    model_id = models.CharField(
        max_length=100,
        default="gemini-1.5-pro",
        help_text="Preferred model for this prompt."
    )
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=4096)
    version = models.CharField(max_length=20, default="1.0.0")
    is_active = models.BooleanField(default=True, db_index=True)
    is_public = models.BooleanField(default=True, db_index=True)
    is_favorite = models.BooleanField(default=False)
    usage_count = models.PositiveIntegerField(default=0, help_text="Times this template has been used.")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prompt_templates",
        help_text="User who owns this template (null = platform-level)."
    )

    class Meta:
        db_table = "ai_prompt_templates"
        verbose_name = "Prompt Template"
        verbose_name_plural = "Prompt Templates"
        ordering = ["-is_favorite", "-usage_count", "title"]
        indexes = [
            models.Index(fields=["category", "is_active"], name="idx_prompt_cat_active"),
            models.Index(fields=["is_public", "is_active"], name="idx_prompt_pub_active"),
        ]

    def __str__(self):
        return f"[{self.category}] {self.title} v{self.version}"


# ─── 3. AI Chat Session ───────────────────────────────────────────────────────

class AIChatSession(BaseModel):
    """
    Tracks individual chat sessions (start/end/device/model used).
    Migrated from ai_store.json 'sessions' dict to SQLite/PostgreSQL.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_chat_sessions",
        help_text="User who initiated the session."
    )
    conversation = models.ForeignKey(
        "control_center.AIConversation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_sessions",
        help_text="Linked conversation thread (if any)."
    )
    model_id = models.CharField(
        max_length=100,
        default="gemini-1.5-pro",
        help_text="AI model used for this session."
    )
    feature_used = models.CharField(
        max_length=100,
        default="tutor",
        db_index=True,
        help_text="Feature type: tutor, quiz, explain, code, etc."
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    device = models.CharField(max_length=100, blank=True, default="Desktop")
    browser = models.CharField(max_length=100, blank=True, default="")
    language = models.CharField(max_length=10, default="en")
    timezone = models.CharField(max_length=50, default="UTC")
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "ai_chat_sessions"
        verbose_name = "AI Chat Session"
        verbose_name_plural = "AI Chat Sessions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="idx_session_user_date"),
            models.Index(fields=["feature_used", "-created_at"], name="idx_session_feature_date"),
        ]

    def __str__(self):
        return f"Session {self.id} | {self.user_id} | {self.feature_used}"


# ─── 4. AI Usage Log ──────────────────────────────────────────────────────────

class AIUsageLog(BaseModel):
    """
    Immutable per-request AI usage record.
    Migrated from ai_store.json 'usage_tracking' list to SQLite/PostgreSQL.
    Used for billing, quota enforcement, and analytics.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_usage_logs",
        help_text="User who triggered the AI request."
    )
    session = models.ForeignKey(
        AIChatSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usage_logs",
        help_text="Linked chat session."
    )
    conversation = models.ForeignKey(
        "control_center.AIConversation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usage_logs",
        help_text="Linked conversation (if applicable)."
    )
    model_id = models.CharField(max_length=100, db_index=True)
    feature = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Feature identifier: tutor, quiz, explain, code, roadmap, etc."
    )
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    prompt_length = models.PositiveIntegerField(default=0, help_text="Character count of prompt.")
    completion_length = models.PositiveIntegerField(default=0, help_text="Character count of completion.")
    estimated_cost_usd = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=0.0,
        help_text="Estimated USD cost for this request."
    )
    latency_ms = models.PositiveIntegerField(default=0, help_text="End-to-end request latency in ms.")
    cached = models.BooleanField(default=False, help_text="Was this response served from cache?")
    error = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, default="")
    language = models.CharField(max_length=10, default="en")
    request_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context: course_id, lesson_id, etc."
    )

    class Meta:
        db_table = "ai_usage_logs"
        verbose_name = "AI Usage Log"
        verbose_name_plural = "AI Usage Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="idx_usage_user_date"),
            models.Index(fields=["feature", "-created_at"], name="idx_usage_feature_date"),
            models.Index(fields=["model_id", "-created_at"], name="idx_usage_model_date"),
        ]

    def __str__(self):
        return f"Usage {self.id} | {self.feature} | {self.total_tokens} tokens"


# ─── 5. AI Token Log ──────────────────────────────────────────────────────────

class AITokenLog(BaseModel):
    """
    Fine-grained per-day token accounting per user.
    Supports quota enforcement and monthly billing rollups.
    Separate from AIUsageLog to allow fast daily aggregation queries.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_token_logs",
        help_text="User consuming tokens."
    )
    log_date = models.DateField(db_index=True, help_text="Calendar date of token consumption.")
    tokens_used = models.PositiveIntegerField(default=0, help_text="Total tokens consumed on this date.")
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    request_count = models.PositiveIntegerField(default=0, help_text="Number of AI requests on this date.")
    estimated_cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    breakdown = models.JSONField(
        default=dict,
        blank=True,
        help_text="Per-feature token breakdown e.g. {'tutor': 5000, 'quiz': 1200}."
    )

    class Meta:
        db_table = "ai_token_logs"
        verbose_name = "AI Token Log"
        verbose_name_plural = "AI Token Logs"
        ordering = ["-log_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "log_date"],
                name="uq_token_log_user_date"
            )
        ]
        indexes = [
            models.Index(fields=["user", "-log_date"], name="idx_token_log_user_date"),
        ]

    def __str__(self):
        return f"TokenLog {self.user_id} | {self.log_date} | {self.tokens_used} tokens"


# ─── 6. AI Rate Limit Quota ───────────────────────────────────────────────────

class AIRateLimitQuota(BaseModel):
    """
    Per-user token quota configuration for AI access control.
    Tiers: FREE, STUDENT, TEACHER, ADMIN.
    """
    TIER_CHOICES = [
        ("FREE", "Free"),
        ("STUDENT", "Student"),
        ("TEACHER", "Teacher"),
        ("ADMIN", "Admin — Unlimited"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_quota",
        help_text="User this quota applies to."
    )
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="STUDENT")
    daily_token_limit = models.PositiveIntegerField(
        default=200000,
        help_text="Maximum tokens per calendar day (0 = unlimited)."
    )
    monthly_token_limit = models.PositiveIntegerField(
        default=2000000,
        help_text="Maximum tokens per calendar month (0 = unlimited)."
    )
    is_unlimited = models.BooleanField(
        default=False,
        help_text="Admin override to bypass all token limits."
    )
    custom_limits = models.JSONField(
        default=dict,
        blank=True,
        help_text="Per-feature override limits e.g. {'quiz': 50000}."
    )

    class Meta:
        db_table = "ai_rate_limit_quotas"
        verbose_name = "AI Rate Limit Quota"
        verbose_name_plural = "AI Rate Limit Quotas"

    def __str__(self):
        return f"Quota [{self.tier}] {self.user_id} — {self.daily_token_limit}/day"


# ─── 7. AI Agent Config ───────────────────────────────────────────────────────

class AIAgentConfig(BaseModel):
    """
    Per-feature AI agent personality and model configuration.
    Controls which model, temperature, and system prompt each AI feature uses.
    """
    AGENT_TYPE_CHOICES = [
        ("tutor", "AI Tutor"),
        ("explainer", "AI Lesson Explainer"),
        ("quiz", "AI Quiz Generator"),
        ("assignment", "AI Assignment Generator"),
        ("code", "AI Code Assistant"),
        ("roadmap", "AI Roadmap Generator"),
        ("notes", "AI Notes Generator"),
        ("flashcards", "AI Flashcards"),
        ("doubt", "AI Doubt Solver"),
        ("study_planner", "AI Study Planner"),
        ("resume", "AI Resume Assistant"),
        ("interview", "AI Interview Assistant"),
        ("teacher", "AI Teacher Assistant"),
        ("analytics", "AI Analytics"),
        ("general", "General AI"),
    ]

    name = models.CharField(max_length=100, unique=True, help_text="Unique config identifier.")
    agent_type = models.CharField(
        max_length=50,
        choices=AGENT_TYPE_CHOICES,
        default="general",
        db_index=True
    )
    model_id = models.CharField(
        max_length=100,
        default="gemini-1.5-pro",
        help_text="Gemini model ID to use for this agent."
    )
    system_prompt = models.TextField(
        blank=True,
        default="",
        help_text="System instruction injected for this agent type."
    )
    temperature = models.FloatField(default=0.7)
    max_output_tokens = models.IntegerField(default=4096)
    context_window_tokens = models.IntegerField(
        default=120000,
        help_text="Maximum context tokens before summarization triggers."
    )
    summarization_threshold = models.IntegerField(
        default=80000,
        help_text="Token count threshold that triggers conversation summarization."
    )
    rag_top_k = models.IntegerField(
        default=5,
        help_text="Number of RAG context chunks to retrieve per request."
    )
    is_active = models.BooleanField(default=True)
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Feature-specific overrides and extra configuration."
    )

    class Meta:
        db_table = "ai_agent_configs"
        verbose_name = "AI Agent Config"
        verbose_name_plural = "AI Agent Configs"

    def __str__(self):
        return f"AgentConfig [{self.agent_type}] {self.name}"


# ─── 8. Knowledge Context ─────────────────────────────────────────────────────

class KnowledgeContext(BaseModel):
    """
    Stores text chunks from platform content (lessons, courses, notes)
    used for AI grounding and RAG retrieval.

    Note: Uses text-based similarity scoring (SQLite-compatible).
    When PostgreSQL + pgvector is available, add a VectorField column
    via a separate migration.
    """
    SOURCE_TYPE_CHOICES = [
        ("lesson", "LMS Lesson"),
        ("course", "Course Description"),
        ("quiz_question", "Quiz Question"),
        ("student_note", "Student Note"),
        ("assignment", "Assignment"),
        ("ai_prompt_template", "AI Prompt Template"),
        ("announcement", "Announcement"),
        ("article", "Article"),
    ]

    source_type = models.CharField(
        max_length=50,
        choices=SOURCE_TYPE_CHOICES,
        db_index=True,
        help_text="Type of source entity this chunk comes from."
    )
    source_id = models.UUIDField(
        db_index=True,
        help_text="UUID of the originating record (e.g. CourseStructure.id)."
    )
    chunk_index = models.PositiveIntegerField(
        default=0,
        help_text="Sequential index of this chunk within the source document."
    )
    chunk_text = models.TextField(
        help_text="Raw text content of this chunk (512-token window)."
    )
    embedding_model = models.CharField(
        max_length=100,
        default="text-embedding-004",
        help_text="Name of the model used to generate the embedding."
    )
    # Stored as JSON array string for SQLite; replace with VectorField on PostgreSQL.
    embedding_json = models.TextField(
        blank=True,
        default="",
        help_text="JSON-serialized embedding vector (1536 floats). Empty until embedded."
    )
    is_embedded = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True once the embedding_json has been populated by Celery task."
    )
    token_count = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extra context: title, course_id, lesson_id, tags, etc."
    )

    class Meta:
        db_table = "ai_knowledge_context"
        verbose_name = "Knowledge Context"
        verbose_name_plural = "Knowledge Contexts"
        ordering = ["source_type", "source_id", "chunk_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["source_type", "source_id", "chunk_index"],
                name="uq_knowledge_chunk"
            )
        ]
        indexes = [
            models.Index(fields=["source_type", "source_id"], name="idx_knowledge_source"),
            models.Index(fields=["is_embedded"], name="idx_knowledge_embedded"),
        ]

    def __str__(self):
        return f"KnowledgeChunk [{self.source_type}] {self.source_id} #{self.chunk_index}"


# ─── 9. Conversation Memory ───────────────────────────────────────────────────

class ConversationMemory(BaseModel):
    """
    Stores summarized long-term memory for AI conversations.
    Created by Celery's summarize_conversation_task when the conversation
    exceeds the token budget threshold (default: 80,000 tokens).
    """
    conversation = models.OneToOneField(
        "control_center.AIConversation",
        on_delete=models.CASCADE,
        related_name="memory",
        help_text="The conversation this memory belongs to."
    )
    summary = models.TextField(
        help_text="AI-generated summary of the conversation history (200-300 words)."
    )
    summarized_up_to_message = models.ForeignKey(
        "control_center.AIMessage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memory_checkpoint",
        help_text="The latest message included in this summary."
    )
    total_tokens_summarized = models.PositiveIntegerField(
        default=0,
        help_text="Cumulative token count of messages included in this summary."
    )
    messages_summarized = models.PositiveIntegerField(
        default=0,
        help_text="Count of messages included in this summary."
    )
    pinned_context = models.JSONField(
        default=list,
        blank=True,
        help_text="List of pinned message IDs always included in context window."
    )
    model_id = models.CharField(
        max_length=100,
        default="gemini-1.5-flash",
        help_text="Model used to generate this summary."
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Incremented each time the summary is regenerated."
    )

    class Meta:
        db_table = "ai_conversation_memory"
        verbose_name = "Conversation Memory"
        verbose_name_plural = "Conversation Memories"

    def __str__(self):
        return f"Memory for Conversation {self.conversation_id} (v{self.version})"


# ─── 10. Study Plan ───────────────────────────────────────────────────────────

class StudyPlan(SoftDeleteModel):
    """
    AI-generated weekly/monthly study plan for a student.
    Links to enrolled courses and accounts for exam dates, pace, and learning style.
    """
    LEARNING_PACE_CHOICES = [
        ("slow", "Slow"),
        ("moderate", "Moderate"),
        ("fast", "Fast"),
    ]
    LEARNING_STYLE_CHOICES = [
        ("VISUAL", "Visual"),
        ("READING", "Reading / Writing"),
        ("PRACTICE", "Practice / Hands-on"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_plans",
        help_text="Student this study plan is for."
    )
    title = models.CharField(max_length=255, default="My Study Plan")
    week_start = models.DateField(db_index=True, help_text="Monday of the week this plan covers.")
    week_end = models.DateField(null=True, blank=True)
    total_study_hours = models.PositiveIntegerField(default=0)
    available_hours_per_day = models.PositiveIntegerField(default=2)
    learning_pace = models.CharField(
        max_length=20,
        choices=LEARNING_PACE_CHOICES,
        default="moderate"
    )
    learning_style = models.CharField(
        max_length=20,
        choices=LEARNING_STYLE_CHOICES,
        default="READING"
    )
    goal = models.TextField(blank=True, default="", help_text="Student's stated learning goal.")
    plan_data = models.JSONField(
        default=dict,
        help_text="Full structured plan (daily sessions, milestones, risk alerts) as JSON."
    )
    weekly_goals = models.JSONField(
        default=list,
        blank=True,
        help_text="List of weekly goal strings."
    )
    risk_alerts = models.JSONField(
        default=list,
        blank=True,
        help_text="List of risk alert objects for falling-behind courses."
    )
    model_id = models.CharField(max_length=100, default="gemini-1.5-pro")
    is_active = models.BooleanField(default=True, db_index=True)
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "ai_study_plans"
        verbose_name = "Study Plan"
        verbose_name_plural = "Study Plans"
        ordering = ["-week_start"]
        indexes = [
            models.Index(fields=["student", "-week_start"], name="idx_study_plan_student_week"),
            models.Index(fields=["student", "is_active"], name="idx_study_plan_student_active"),
        ]

    def __str__(self):
        return f"StudyPlan: {self.student_id} | Week of {self.week_start}"


class StudyPlanSession(BaseModel):
    """
    Individual study session within a StudyPlan (one session = one lesson block).
    Created from StudyPlan.plan_data for fine-grained progress tracking.
    """
    SESSION_TYPE_CHOICES = [
        ("STUDY", "Study"),
        ("REVISION", "Revision"),
        ("PRACTICE", "Practice"),
        ("QUIZ", "Quiz"),
    ]

    study_plan = models.ForeignKey(
        StudyPlan,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text="Parent study plan."
    )
    session_date = models.DateField(db_index=True)
    time_slot = models.CharField(max_length=20, blank=True, default="", help_text="e.g. '18:00-19:30'")
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default="STUDY")
    course_id = models.UUIDField(null=True, blank=True, db_index=True)
    lesson_id = models.UUIDField(null=True, blank=True, db_index=True)
    course_title = models.CharField(max_length=255, blank=True, default="")
    lesson_title = models.CharField(max_length=255, blank=True, default="")
    goal = models.TextField(blank=True, default="")
    duration_minutes = models.PositiveIntegerField(default=60)
    is_completed = models.BooleanField(default=False, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    motivational_message = models.TextField(blank=True, default="")

    class Meta:
        db_table = "ai_study_plan_sessions"
        verbose_name = "Study Plan Session"
        verbose_name_plural = "Study Plan Sessions"
        ordering = ["session_date", "time_slot"]
        indexes = [
            models.Index(fields=["study_plan", "session_date"], name="idx_sps_plan_date"),
            models.Index(fields=["is_completed"], name="idx_sps_completed"),
        ]

    def __str__(self):
        return f"Session {self.session_date} | {self.session_type} | {self.lesson_title or 'General'}"


# ─── 11. Flashcard Deck + Flashcard ──────────────────────────────────────────

class FlashcardDeck(SoftDeleteModel):
    """
    AI-generated flashcard deck from a lesson or topic.
    Uses spaced-repetition scheduling (Leitner box system).
    """
    CARD_TYPE_CHOICES = [
        ("TERM_DEFINITION", "Term / Definition"),
        ("Q_A", "Question / Answer"),
        ("CLOZE", "Fill in the Blank"),
        ("CONCEPT_MAP", "Concept Map"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="flashcard_decks",
        help_text="Student who owns this deck."
    )
    title = models.CharField(max_length=255)
    lesson_id = models.UUIDField(null=True, blank=True, db_index=True)
    course_id = models.UUIDField(null=True, blank=True, db_index=True)
    topic = models.CharField(max_length=255, blank=True, default="")
    card_type = models.CharField(max_length=30, choices=CARD_TYPE_CHOICES, default="TERM_DEFINITION")
    card_count = models.PositiveIntegerField(default=0)
    spaced_repetition_schedule = models.JSONField(
        default=dict,
        blank=True,
        help_text="Leitner review schedule e.g. {'day_1': [0,1,2], 'day_3': [3,4]}."
    )
    model_id = models.CharField(max_length=100, default="gemini-1.5-flash")
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "ai_flashcard_decks"
        verbose_name = "Flashcard Deck"
        verbose_name_plural = "Flashcard Decks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "-created_at"], name="idx_deck_student_date"),
            models.Index(fields=["lesson_id"], name="idx_deck_lesson"),
        ]

    def __str__(self):
        return f"Deck: {self.title} ({self.card_count} cards)"


class Flashcard(BaseModel):
    """
    Individual flashcard within a FlashcardDeck.
    """
    DIFFICULTY_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1–5

    deck = models.ForeignKey(
        FlashcardDeck,
        on_delete=models.CASCADE,
        related_name="cards",
        help_text="Parent flashcard deck."
    )
    card_type = models.CharField(max_length=30, default="TERM_DEFINITION")
    front = models.TextField(help_text="Front of the card (question, term, or incomplete statement).")
    back = models.TextField(help_text="Back of the card (answer, definition, or completion).")
    hint = models.TextField(blank=True, default="")
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=3)
    tags = models.JSONField(default=list, blank=True)
    # Spaced repetition state
    next_review_date = models.DateField(null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    leitner_box = models.PositiveIntegerField(
        default=1,
        help_text="Current Leitner box (1=daily, 2=3-day, 3=weekly, etc.)."
    )
    last_reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "ai_flashcards"
        verbose_name = "Flashcard"
        verbose_name_plural = "Flashcards"
        ordering = ["deck", "difficulty"]
        indexes = [
            models.Index(fields=["deck", "next_review_date"], name="idx_card_deck_review"),
            models.Index(fields=["leitner_box"], name="idx_card_leitner"),
        ]

    def __str__(self):
        return f"Card {self.id} | Box {self.leitner_box} | {self.front[:40]}"


# ─── 12. Quiz Generation ──────────────────────────────────────────────────────

class QuizGeneration(SoftDeleteModel):
    """
    Records an AI-generated quiz (question set) from a lesson or topic.
    Stores the full generated output plus generation metadata.
    """
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]
    QUESTION_TYPE_CHOICES = [
        ("MCQ", "Multiple Choice"),
        ("TRUE_FALSE", "True / False"),
        ("SHORT_ANSWER", "Short Answer"),
        ("FILL_BLANK", "Fill in the Blank"),
        ("MIXED", "Mixed Types"),
    ]

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generated_quizzes",
        help_text="User (student or teacher) who triggered generation."
    )
    quiz_title = models.CharField(max_length=255)
    lesson_id = models.UUIDField(null=True, blank=True, db_index=True)
    course_id = models.UUIDField(null=True, blank=True, db_index=True)
    topic = models.CharField(max_length=255, blank=True, default="")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="medium")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default="MCQ")
    question_count = models.PositiveIntegerField(default=10)
    model_id = models.CharField(max_length=100, default="gemini-1.5-flash")
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    # Full structured JSON output from Gemini
    generation_output = models.JSONField(
        default=dict,
        help_text="Full structured quiz JSON as returned by Gemini."
    )
    cache_key = models.CharField(
        max_length=64,
        blank=True,
        default="",
        db_index=True,
        help_text="Redis cache key hash for this generation."
    )
    is_published = models.BooleanField(
        default=False,
        help_text="True if teacher has reviewed and published this quiz."
    )

    class Meta:
        db_table = "ai_quiz_generations"
        verbose_name = "Quiz Generation"
        verbose_name_plural = "Quiz Generations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["lesson_id", "difficulty"], name="idx_quiz_lesson_diff"),
            models.Index(fields=["generated_by", "-created_at"], name="idx_quiz_user_date"),
        ]

    def __str__(self):
        return f"Quiz: {self.quiz_title} | {self.difficulty} | {self.question_count}Q"


class QuizQuestion(BaseModel):
    """
    Individual question extracted from a QuizGeneration.
    Stored separately for reuse across multiple quizzes.
    """
    BLOOM_LEVEL_CHOICES = [
        ("remember", "Remember"),
        ("understand", "Understand"),
        ("apply", "Apply"),
        ("analyze", "Analyze"),
        ("evaluate", "Evaluate"),
        ("create", "Create"),
    ]

    generation = models.ForeignKey(
        QuizGeneration,
        on_delete=models.CASCADE,
        related_name="questions",
        help_text="Parent quiz generation."
    )
    question_number = models.PositiveIntegerField(default=1)
    question = models.TextField()
    question_type = models.CharField(max_length=20, default="MCQ")
    options = models.JSONField(
        default=list,
        blank=True,
        help_text="List of answer options for MCQ/TRUE_FALSE."
    )
    correct_answer = models.TextField(help_text="Correct answer (text or option letter).")
    explanation = models.TextField(blank=True, default="")
    concept_tag = models.CharField(max_length=255, blank=True, default="")
    bloom_level = models.CharField(
        max_length=20,
        choices=BLOOM_LEVEL_CHOICES,
        default="understand"
    )
    difficulty_score = models.PositiveIntegerField(
        default=3,
        help_text="Difficulty 1-5."
    )

    class Meta:
        db_table = "ai_quiz_questions"
        verbose_name = "Quiz Question"
        verbose_name_plural = "Quiz Questions"
        ordering = ["generation", "question_number"]
        indexes = [
            models.Index(fields=["generation", "question_number"], name="idx_qq_gen_num"),
        ]

    def __str__(self):
        return f"Q{self.question_number}: {self.question[:60]}"


# ─── 13. Learning Recommendation ─────────────────────────────────────────────

class LearningRecommendation(BaseModel):
    """
    AI-generated personalized learning recommendations for a student.
    Powered by the student's LearningHistory, progress, and goals.
    """
    RECOMMENDATION_TYPE_CHOICES = [
        ("NEXT_LESSON", "Next Lesson to Study"),
        ("REVISION", "Revision Needed"),
        ("COURSE", "Recommended Course"),
        ("RESOURCE", "External Resource"),
        ("PRACTICE", "Practice Exercise"),
        ("WEAK_AREA", "Weak Area Alert"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SHOWN", "Shown to Student"),
        ("ACCEPTED", "Accepted"),
        ("DISMISSED", "Dismissed"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_recommendations",
        help_text="Student this recommendation is for."
    )
    recommendation_type = models.CharField(
        max_length=30,
        choices=RECOMMENDATION_TYPE_CHOICES,
        default="NEXT_LESSON",
        db_index=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    reason = models.TextField(
        blank=True,
        default="",
        help_text="Why this recommendation was generated (AI explanation)."
    )
    target_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text="UUID of the recommended entity (lesson_id, course_id, etc.)."
    )
    target_type = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Type of target: 'lesson', 'course', 'resource', etc."
    )
    target_url = models.CharField(max_length=512, blank=True, default="")
    priority_score = models.FloatField(
        default=0.5,
        help_text="0.0–1.0 relevance/priority score from the AI."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True
    )
    shown_at = models.DateTimeField(null=True, blank=True)
    acted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Recommendation expiry (stale after this)."
    )
    model_id = models.CharField(max_length=100, default="gemini-1.5-flash")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "ai_learning_recommendations"
        verbose_name = "Learning Recommendation"
        verbose_name_plural = "Learning Recommendations"
        ordering = ["-priority_score", "-created_at"]
        indexes = [
            models.Index(fields=["student", "status"], name="idx_rec_student_status"),
            models.Index(fields=["student", "recommendation_type"], name="idx_rec_student_type"),
            models.Index(fields=["priority_score"], name="idx_rec_priority"),
        ]

    def __str__(self):
        return f"Rec [{self.recommendation_type}] → {self.student_id}: {self.title}"


# ─── 14. AI Task ─────────────────────────────────────────────────────────────

class AITask(BaseModel):
    """
    Tracks Celery async AI tasks dispatched by the platform.
    Enables task status polling, result retrieval, and failure auditing.
    """
    TASK_TYPE_CHOICES = [
        ("embed_content", "Embed Content Chunk"),
        ("batch_embed_lessons", "Batch Embed Lessons"),
        ("summarize_conversation", "Summarize Conversation"),
        ("generate_study_plan", "Generate Study Plan"),
        ("generate_flashcards", "Generate Flashcard Deck"),
        ("generate_quiz", "Generate Quiz"),
        ("generate_report", "Generate Analytics Report"),
        ("index_ai_item", "Index AI Item in Search"),
        ("notify_ai_event", "Notify AI Event"),
        ("log_usage", "Log AI Usage"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("SUCCESS", "Success"),
        ("FAILURE", "Failure"),
        ("REVOKED", "Revoked"),
        ("RETRY", "Retrying"),
    ]

    celery_task_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Celery task UUID returned by .delay() or .apply_async()."
    )
    task_type = models.CharField(
        max_length=50,
        choices=TASK_TYPE_CHOICES,
        default="other",
        db_index=True
    )
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_tasks",
        help_text="User who triggered this task (null for system tasks)."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True
    )
    input_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Task input arguments for debugging."
    )
    result_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Task output or result summary."
    )
    error_message = models.TextField(blank=True, default="")
    retry_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "ai_tasks"
        verbose_name = "AI Task"
        verbose_name_plural = "AI Tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["task_type", "status"], name="idx_aitask_type_status"),
            models.Index(fields=["triggered_by", "-created_at"], name="idx_aitask_user_date"),
            models.Index(fields=["status", "-created_at"], name="idx_aitask_status_date"),
        ]

    def __str__(self):
        return f"AITask [{self.task_type}] {self.celery_task_id[:8]} — {self.status}"
