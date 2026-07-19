import uuid
from django.db import models
from apps.base_models import BaseModel, SoftDeleteModel


class Theme(BaseModel):
    """
    Dynamic frontend display customization entries (look and feel).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Aesthetic theme name (e.g., Calm Amber, Slate Twilight).")
    colors = models.JSONField(help_text="Custom palette mappings (e.g., {'primary': '#F59E0B'}).")
    is_active = models.BooleanField(default=False, help_text="Is current custom theme active?")

    class Meta:
        db_table = "themes"
        verbose_name = "Theme"
        verbose_name_plural = "Themes"

    def __str__(self):
        return self.name


class PlatformSetting(models.Model):
    """
    Flexible dynamic administrative platform settings stored in JSON format.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, unique=True, help_text="Unique configuration setting key name.")
    value = models.JSONField(help_text="Arbitrary JSON settings document.")
    description = models.TextField(blank=True, null=True, help_text="Short description outlining setting's purpose.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platform_settings"
        verbose_name = "Platform Setting"
        verbose_name_plural = "Platform Settings"

    def __str__(self):
        return self.key


class DashboardWidget(models.Model):
    """
    Configures metric grids and dynamic panels shown in the control center dynamically.
    The metrics queries, display order, colors, and permissions are loaded completely from here.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, help_text="Visual heading (e.g., Total Students)")
    metric_type = models.CharField(
        max_length=30,
        choices=[
            ("DB_COUNT", "Database Count Query"),
            ("DB_SUM", "Database Sum/Aggregate Query"),
            ("TELEMETRY_RATE", "Telemetry Event Rate"),
            ("STATIC_VALUE", "Fixed Parameter"),
        ],
        default="DB_COUNT"
    )
    query_target = models.CharField(
        max_length=255, 
        help_text="Specifies target entity or SQL aggregate routine (e.g., lms.CourseStructure.count)"
    )
    color_scheme = models.CharField(max_length=50, default="indigo", help_text="Tailwind display scheme color class")
    icon_name = models.CharField(max_length=50, default="Activity", help_text="Lucide icon identifier name")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    required_role = models.CharField(max_length=100, default="role-super-admin")

    class Meta:
        db_table = "control_dashboard_widgets"
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"
        ordering = ["display_order"]


class AdministrativeTask(models.Model):
    """
    Pending actions or ledger operations requiring supervisor digital signatures and override signals.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=[
            ("PAYOUT_APPROVAL", "Payout Approval"),
            ("SYLLABUS_AUDIT", "Syllabus Audit Check"),
            ("CERTIFICATE_SIGNING", "Certificate Signing"),
            ("USER_SUSPENSION", "Account Verification"),
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending Approval"),
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected"),
            ("EXECUTED", "Executed"),
        ],
        default="PENDING"
    )
    payload = models.JSONField(default=dict, blank=True, help_text="Metadata or specific action parameters.")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "control_administrative_tasks"
        verbose_name = "Administrative Task"
        verbose_name_plural = "Administrative Tasks"
        ordering = ["-created_at"]


class SystemAuditLog(models.Model):
    """
    Immutable secure log stream capturing database mutations with JSON state snapshots.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="system_audits",
        help_text="User actor responsible for modification."
    )
    action_type = models.CharField(max_length=100, help_text="Mutation action name (e.g., ROLE_MODIFIED).")
    target_table = models.CharField(max_length=100, help_text="Physical database table modified.")
    before_state = models.JSONField(blank=True, null=True, help_text="State snapshot prior to modification.")
    after_state = models.JSONField(blank=True, null=True, help_text="State snapshot subsequent to modification.")
    ip_address = models.CharField(max_length=45, blank=True, null=True, help_text="IP address of executing system client.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_audit_logs"
        verbose_name = "System Audit Log"
        verbose_name_plural = "System Audit Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Audit {self.id} -> {self.action_type}"


class ActivityLog(models.Model):
    """
    Diagnostic operational logs recording user sessions activity (page visits, logins, clicks).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="activity_logs",
        help_text="Active user session performer."
    )
    event = models.CharField(max_length=255, help_text="Event classification title (e.g., USER_LOGIN).")
    details = models.JSONField(default=dict, blank=True, help_text="Additional event context parameters.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity_logs"
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Activity {self.id} -> {self.event}"


class AnalyticsEvent(models.Model):
    """
    High-velocity performance reporting telemetry logs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analytics_events",
        help_text="Active user logging metric."
    )
    metric_name = models.CharField(max_length=100, help_text="Telemetry identifier (e.g., video_playback_sec).")
    metric_value = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        blank=True,
        null=True,
        help_text="Numeric telemetry quantity."
    )
    context_data = models.JSONField(default=dict, blank=True, help_text="Dynamic telemetry details payload.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_events"
        verbose_name = "Analytics Event"
        verbose_name_plural = "Analytics Events"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Telemetry {self.metric_name} ({self.metric_value})"


class AIConversation(SoftDeleteModel):
    """
    Dynamic thread containers for student dialog sessions with Vidya AI.
    """
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="ai_conversations",
        help_text="Owner user dialog participant."
    )
    title = models.CharField(max_length=255, default="New Conversation", help_text="Custom name of discussion thread.")

    class Meta:
        db_table = "ai_conversations"
        verbose_name = "AI Conversation"
        verbose_name_plural = "AI Conversations"

    def __str__(self):
        return f"AI Thread: {self.title} (User: {self.user.email})"


class AIMessage(BaseModel):
    """
    Saves prompt questions and generated AI model completions under thread sessions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="Parent discussion session thread."
    )
    sender_type = models.CharField(
        max_length=20,
        choices=[
            ("USER", "User Prompt"),
            ("ASSISTANT", "Assistant Response")
        ],
        help_text="Classifier tag indicating prompt vs model output."
    )
    content = models.TextField(help_text="Raw or markdown text content.")
    token_count = models.IntegerField(default=0, help_text="Token diagnostics tracking count.")

    class Meta:
        db_table = "ai_messages"
        verbose_name = "AI Message"
        verbose_name_plural = "AI Messages"

    def __str__(self):
        return f"Msg {self.id} in Thread {self.conversation.id}"


class AIFeedback(models.Model):
    """
    Thumbs up/down user feedback rating flags on specific Vidya completions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.OneToOneField(
        AIMessage,
        on_delete=models.CASCADE,
        related_name="feedback",
        help_text="Target message feedback rating target."
    )
    is_positive = models.BooleanField(help_text="True representing Thumbs Up, False representing Thumbs Down.")
    feedback_text = models.TextField(blank=True, null=True, help_text="Additional qualitative textual review.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_feedback"
        verbose_name = "AI Feedback"
        verbose_name_plural = "AI Feedbacks"

    def __str__(self):
        return f"Feedback for Msg {self.message.id} (Positive: {self.is_positive})"


class MediaFile(BaseModel):
    """
    Tracks uploads of images, videos, documents, books, and certificates.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="media_files",
        help_text="User who uploaded the file."
    )
    file_name = models.CharField(max_length=255, help_text="Original file name.")
    file_url = models.CharField(max_length=512, help_text="Fully qualified URL or storage key.")
    file_type = models.CharField(
        max_length=100,
        help_text="MIME type classification (e.g. image/png, video/mp4, application/pdf)."
    )
    file_size = models.BigIntegerField(help_text="Size of file in bytes.")
    purpose = models.CharField(
        max_length=50,
        choices=[
            ("AVATAR", "User Profile Picture"),
            ("COVER", "User Profile Cover"),
            ("COURSE_FILE", "LMS Lesson File"),
            ("BOOK_FILE", "Store E-Book File"),
            ("CERTIFICATE", "Syllabus Certificate File"),
        ],
        default="COURSE_FILE"
    )
    version = models.IntegerField(default=1, help_text="File version increments.")

    class Meta:
        db_table = "media_files"
        verbose_name = "Media File"
        verbose_name_plural = "Media Files"

    def __str__(self):
        return f"{self.file_name} (v{self.version})"
