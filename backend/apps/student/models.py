"""
Student Dashboard Models — BrahmaVidya Galaxy
Sprint 20: New models extending the LMS for the Student Portal.

DO NOT modify existing models in apps.lms, apps.users, or any other app.
All new tables live exclusively in this app.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.base_models import BaseModel, SoftDeleteModel


# ─── Content Type Choices ─────────────────────────────────────────────────────

class ContentType(models.TextChoices):
    LESSON      = "LESSON",   "Lesson"
    ARTICLE     = "ARTICLE",  "Article"
    TUTORIAL    = "TUTORIAL", "Tutorial"
    VIDEO       = "VIDEO",    "Video"
    BOOK        = "BOOK",     "Book"
    QUIZ        = "QUIZ",     "Quiz"
    EXAM        = "EXAM",     "Exam"
    LIVE_CLASS  = "LIVE_CLASS", "Live Class"


# ─── 1. Learning History ──────────────────────────────────────────────────────

class LearningHistory(BaseModel):
    """
    Auditable log of every lesson visit/access by a student.
    Fires on lesson load and records time spent.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_history",
        help_text="Student who accessed the content."
    )
    node = models.ForeignKey(
        "lms.CourseStructure",
        on_delete=models.CASCADE,
        related_name="history_records",
        help_text="The curriculum node (lesson/topic) accessed."
    )
    enrollment = models.ForeignKey(
        "lms.StudentEnrollment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history_records",
        help_text="The enrollment context this visit belongs to."
    )
    duration_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Seconds spent on this content during this visit."
    )
    completed = models.BooleanField(
        default=False,
        help_text="Did the student mark this node complete during this visit?"
    )
    accessed_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Timestamp when access began."
    )

    class Meta:
        db_table = "student_learning_history"
        verbose_name = "Learning History"
        verbose_name_plural = "Learning Histories"
        ordering = ["-accessed_at"]
        indexes = [
            models.Index(fields=["student", "-accessed_at"], name="idx_hist_student_date"),
            models.Index(fields=["student", "node"], name="idx_hist_student_node"),
        ]

    def __str__(self):
        return f"{self.student.email} → {self.node.title} at {self.accessed_at:%Y-%m-%d %H:%M}"


# ─── 2. Continue Learning ─────────────────────────────────────────────────────

class ContinueLearning(BaseModel):
    """
    Stores the last-accessed lesson position for each student enrollment,
    enabling the "Continue Learning" resume feature.
    One record per (student, enrollment) pair — upserted on every lesson access.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="continue_learning_records",
        help_text="Student learner."
    )
    enrollment = models.ForeignKey(
        "lms.StudentEnrollment",
        on_delete=models.CASCADE,
        related_name="continue_learning_record",
        help_text="The course enrollment this position belongs to."
    )
    last_node = models.ForeignKey(
        "lms.CourseStructure",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="continue_learning_records",
        help_text="Last accessed curriculum node."
    )
    last_accessed_at = models.DateTimeField(
        auto_now=True,
        help_text="Auto-updated timestamp of last access."
    )
    position_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Video playback position in seconds (if applicable)."
    )

    class Meta:
        db_table = "student_continue_learning"
        verbose_name = "Continue Learning"
        verbose_name_plural = "Continue Learning Records"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "enrollment"],
                name="uq_continue_learning_student_enrollment"
            )
        ]
        indexes = [
            models.Index(fields=["student", "-last_accessed_at"], name="idx_continue_student_date"),
        ]

    def __str__(self):
        return f"{self.student.email} → {self.enrollment.course.title} (last: {self.last_node})"


# ─── 3. Bookmark ─────────────────────────────────────────────────────────────

class Bookmark(BaseModel):
    """
    Student-created bookmarks for any type of content (polymorphic via JSON ref).
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookmarks",
        help_text="Student who bookmarked the content."
    )
    content_type = models.CharField(
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.LESSON,
        help_text="Type of bookmarked content."
    )
    content_id = models.UUIDField(
        help_text="UUID of the bookmarked entity (lesson ID, article ID, etc.)."
    )
    title = models.CharField(
        max_length=255,
        help_text="Display title of the bookmarked content (snapshot at time of bookmark)."
    )
    source_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Parent context name (course title, CMS section name, etc.)."
    )
    url_path = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        help_text="Direct navigation path to the bookmarked content."
    )
    note = models.TextField(
        blank=True,
        null=True,
        help_text="Optional student note attached to this bookmark."
    )

    class Meta:
        db_table = "student_bookmarks"
        verbose_name = "Bookmark"
        verbose_name_plural = "Bookmarks"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "content_type", "content_id"],
                name="uq_bookmark_student_content"
            )
        ]
        indexes = [
            models.Index(fields=["student", "content_type"], name="idx_bookmark_student_type"),
        ]

    def __str__(self):
        return f"[{self.content_type}] {self.title} (by {self.student.email})"


# ─── 4. Student Note ──────────────────────────────────────────────────────────

class StudentNote(SoftDeleteModel):
    """
    Rich in-lesson notes created by students, linked to a specific curriculum node.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_notes",
        help_text="Note author (student)."
    )
    node = models.ForeignKey(
        "lms.CourseStructure",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_notes",
        help_text="Linked curriculum node (lesson context)."
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional note title/heading."
    )
    content = models.TextField(
        help_text="Note body (supports markdown)."
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of tag strings for filtering/search."
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pin this note to the top of the notes list."
    )

    class Meta:
        db_table = "student_notes"
        verbose_name = "Student Note"
        verbose_name_plural = "Student Notes"
        ordering = ["-is_pinned", "-updated_at"]
        indexes = [
            models.Index(fields=["student", "-updated_at"], name="idx_note_student_date"),
        ]

    def __str__(self):
        return f"Note by {self.student.email}: {self.title or self.content[:50]}"


# ─── 5. Study Goal ────────────────────────────────────────────────────────────

class StudyGoal(SoftDeleteModel):
    """
    Personal study goals set by students with targets and progress tracking.
    """
    class GoalStatus(models.TextChoices):
        ACTIVE      = "ACTIVE",     "Active"
        COMPLETED   = "COMPLETED",  "Completed"
        ABANDONED   = "ABANDONED",  "Abandoned"
        PAUSED      = "PAUSED",     "Paused"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_goals",
        help_text="Goal-setting student."
    )
    enrollment = models.ForeignKey(
        "lms.StudentEnrollment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_goals",
        help_text="Optional linked course enrollment."
    )
    title = models.CharField(
        max_length=255,
        help_text="Goal description (e.g., 'Complete React Course')."
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed goal notes."
    )
    target_date = models.DateField(
        help_text="Target completion date."
    )
    daily_target_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Daily study time target in minutes."
    )
    status = models.CharField(
        max_length=20,
        choices=GoalStatus.choices,
        default=GoalStatus.ACTIVE,
        db_index=True,
        help_text="Current goal lifecycle status."
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when goal was marked completed."
    )
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Auto-calculated completion percentage."
    )

    class Meta:
        db_table = "student_study_goals"
        verbose_name = "Study Goal"
        verbose_name_plural = "Study Goals"
        ordering = ["target_date", "-created_at"]
        indexes = [
            models.Index(fields=["student", "status"], name="idx_goal_student_status"),
        ]

    def __str__(self):
        return f"{self.student.email}: {self.title} ({self.status})"


# ─── 6. Study Session ─────────────────────────────────────────────────────────

class StudySession(BaseModel):
    """
    Timed study sessions representing focused learning blocks.
    Used to calculate daily/weekly study time accurately.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_sessions",
        help_text="Session participant (student)."
    )
    node = models.ForeignKey(
        "lms.CourseStructure",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_sessions",
        help_text="Curriculum node being studied (if applicable)."
    )
    started_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Session start timestamp."
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Session end timestamp. Null = active session."
    )
    duration_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Computed duration of the session in seconds."
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether the study session is currently ongoing."
    )
    xp_earned = models.PositiveIntegerField(
        default=0,
        help_text="XP points awarded for this session."
    )

    class Meta:
        db_table = "student_study_sessions"
        verbose_name = "Study Session"
        verbose_name_plural = "Study Sessions"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["student", "-started_at"], name="idx_session_student_date"),
            models.Index(fields=["student", "is_active"], name="idx_session_active"),
        ]

    def __str__(self):
        return f"Session by {self.student.email} at {self.started_at:%Y-%m-%d %H:%M} ({self.duration_seconds}s)"

    def end_session(self):
        """Convenience method to close an active session."""
        self.ended_at = timezone.now()
        self.is_active = False
        if self.started_at:
            delta = self.ended_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
        self.save(update_fields=["ended_at", "is_active", "duration_seconds", "updated_at"])


# ─── 7. Study Calendar Event ──────────────────────────────────────────────────

class StudyCalendarEvent(BaseModel):
    """
    Student-created calendar events: study blocks, reminders, self-set deadlines.
    Complements the system-generated events (exams, live classes, assignments).
    """
    class EventType(models.TextChoices):
        STUDY_BLOCK = "STUDY_BLOCK", "Study Block"
        REMINDER    = "REMINDER",    "Reminder"
        DEADLINE    = "DEADLINE",    "Self-set Deadline"
        MILESTONE   = "MILESTONE",   "Milestone"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calendar_events",
        help_text="Calendar owner (student)."
    )
    title = models.CharField(max_length=255, help_text="Event title.")
    description = models.TextField(blank=True, null=True, help_text="Optional event notes.")
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.STUDY_BLOCK,
        db_index=True
    )
    starts_at = models.DateTimeField(db_index=True, help_text="Event start datetime.")
    ends_at = models.DateTimeField(null=True, blank=True, help_text="Event end datetime.")
    all_day = models.BooleanField(default=False, help_text="Is this an all-day event?")
    node = models.ForeignKey(
        "lms.CourseStructure",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calendar_events",
        help_text="Optional linked curriculum node."
    )
    color = models.CharField(
        max_length=20,
        default="indigo",
        help_text="Display colour key for the calendar UI."
    )
    is_completed = models.BooleanField(default=False, help_text="Was this event completed?")

    class Meta:
        db_table = "student_calendar_events"
        verbose_name = "Study Calendar Event"
        verbose_name_plural = "Study Calendar Events"
        ordering = ["starts_at"]
        indexes = [
            models.Index(fields=["student", "starts_at"], name="idx_cal_student_date"),
        ]

    def __str__(self):
        return f"[{self.event_type}] {self.title} ({self.starts_at:%Y-%m-%d})"


# ─── 8. Daily Progress ────────────────────────────────────────────────────────

class DailyProgress(models.Model):
    """
    Pre-aggregated daily study statistics per student.
    Computed by a nightly Celery task or updated in real-time via signals.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_progress",
        help_text="Student learner."
    )
    date = models.DateField(db_index=True, help_text="The date this record covers.")
    study_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Total minutes studied on this date."
    )
    lessons_completed = models.PositiveIntegerField(
        default=0,
        help_text="Number of lessons completed on this date."
    )
    xp_earned = models.PositiveIntegerField(
        default=0,
        help_text="Total XP earned on this date."
    )
    lessons_accessed = models.PositiveIntegerField(
        default=0,
        help_text="Total lesson accesses (including revisits)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_daily_progress"
        verbose_name = "Daily Progress"
        verbose_name_plural = "Daily Progress Records"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "date"],
                name="uq_daily_progress_student_date"
            )
        ]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["student", "-date"], name="idx_daily_student_date"),
        ]

    def __str__(self):
        return f"{self.student.email} on {self.date}: {self.study_minutes}min, {self.lessons_completed} lessons"


# ─── 9. Weekly Progress ───────────────────────────────────────────────────────

class WeeklyProgress(models.Model):
    """
    Pre-aggregated weekly study statistics per student.
    week_start is always a Monday.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="weekly_progress",
        help_text="Student learner."
    )
    week_start = models.DateField(db_index=True, help_text="Monday date of this ISO week.")
    study_minutes = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    goal_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Total target study minutes for the week (from active goals)."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_weekly_progress"
        verbose_name = "Weekly Progress"
        verbose_name_plural = "Weekly Progress Records"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "week_start"],
                name="uq_weekly_progress_student_week"
            )
        ]
        ordering = ["-week_start"]

    def __str__(self):
        return f"{self.student.email} week of {self.week_start}: {self.study_minutes}min"


# ─── 10. Monthly Progress ─────────────────────────────────────────────────────

class MonthlyProgress(models.Model):
    """
    Pre-aggregated monthly study statistics per student.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monthly_progress",
        help_text="Student learner."
    )
    year = models.PositiveSmallIntegerField(db_index=True, help_text="Calendar year.")
    month = models.PositiveSmallIntegerField(db_index=True, help_text="Calendar month (1–12).")
    study_minutes = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    courses_completed = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    badges_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_monthly_progress"
        verbose_name = "Monthly Progress"
        verbose_name_plural = "Monthly Progress Records"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "year", "month"],
                name="uq_monthly_progress_student_ym"
            )
        ]
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.student.email} {self.year}-{self.month:02d}: {self.study_minutes}min"


# ─── 11. Learning Streak ──────────────────────────────────────────────────────

class LearningStreak(models.Model):
    """
    Tracks consecutive study days (streak) per student.
    One record per student — upserted daily via Celery.
    """
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_streak",
        help_text="Streak-tracking student."
    )
    current_streak = models.PositiveIntegerField(
        default=0,
        help_text="Current consecutive active-study-day count."
    )
    longest_streak = models.PositiveIntegerField(
        default=0,
        help_text="Historical best streak count."
    )
    last_studied_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="The most recent date the student had any study activity."
    )
    streak_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Start date of the current streak."
    )
    total_study_days = models.PositiveIntegerField(
        default=0,
        help_text="All-time total number of distinct study days."
    )
    total_xp = models.PositiveIntegerField(
        default=0,
        help_text="Lifetime accumulated XP points."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_learning_streaks"
        verbose_name = "Learning Streak"
        verbose_name_plural = "Learning Streaks"

    def __str__(self):
        return f"{self.student.email}: {self.current_streak} day streak (best: {self.longest_streak})"


# ─── 12. Achievement ──────────────────────────────────────────────────────────

class Achievement(BaseModel):
    """
    Extended achievement catalog (beyond lms.Badge).
    Supports progress-based achievements (e.g., "Study 100 hours total").
    """
    class AchievementCategory(models.TextChoices):
        STREAK      = "STREAK",     "Streak"
        COMPLETION  = "COMPLETION", "Completion"
        SPEED       = "SPEED",      "Speed"
        CONSISTENCY = "CONSISTENCY","Consistency"
        SOCIAL      = "SOCIAL",     "Social"
        SPECIAL     = "SPECIAL",    "Special"

    code = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique achievement identifier (e.g., STREAK_7_DAYS)."
    )
    title = models.CharField(max_length=255, help_text="Achievement display title.")
    description = models.TextField(help_text="How to earn this achievement.")
    category = models.CharField(
        max_length=20,
        choices=AchievementCategory.choices,
        default=AchievementCategory.COMPLETION,
        db_index=True
    )
    icon_url = models.CharField(max_length=512, blank=True, null=True)
    xp_reward = models.PositiveIntegerField(default=0, help_text="XP awarded on unlock.")
    criteria = models.JSONField(
        default=dict,
        help_text="Machine-readable unlock criteria (e.g., {'streak_days': 7})."
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "student_achievements"
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
        ordering = ["category", "xp_reward"]

    def __str__(self):
        return f"[{self.category}] {self.title} (+{self.xp_reward} XP)"


class StudentAchievement(BaseModel):
    """
    Bridge mapping earned Achievements to students with progress tracking.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_achievements",
        help_text="Achievement recipient."
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name="student_achievements",
        help_text="Earned achievement."
    )
    progress_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Current progress toward the achievement target."
    )
    is_unlocked = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Has the student fully unlocked this achievement?"
    )
    unlocked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of unlock."
    )

    class Meta:
        db_table = "student_achievement_records"
        verbose_name = "Student Achievement"
        verbose_name_plural = "Student Achievements"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "achievement"],
                name="uq_student_achievement"
            )
        ]

    def __str__(self):
        return f"{self.student.email} → {self.achievement.title} ({'✓' if self.is_unlocked else '…'})"


# ─── 13. Student Preference ───────────────────────────────────────────────────

class StudentPreference(models.Model):
    """
    Per-student dashboard layout and behaviour preferences.
    OneToOne with User — created on first dashboard visit.
    """
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_preference",
        help_text="Preference owner."
    )
    sidebar_collapsed = models.BooleanField(
        default=False,
        help_text="Whether the sidebar should render collapsed by default."
    )
    dashboard_layout = models.CharField(
        max_length=20,
        choices=[
            ("COMFORTABLE", "Comfortable"),
            ("COMPACT",     "Compact"),
            ("MINIMAL",     "Minimal"),
        ],
        default="COMFORTABLE"
    )
    daily_goal_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Personal daily study target in minutes."
    )
    weekly_goal_minutes = models.PositiveIntegerField(
        default=300,
        help_text="Personal weekly study target in minutes."
    )
    preferred_study_time = models.CharField(
        max_length=20,
        choices=[
            ("MORNING",   "Morning (6–12)"),
            ("AFTERNOON", "Afternoon (12–18)"),
            ("EVENING",   "Evening (18–22)"),
            ("NIGHT",     "Night (22–6)"),
            ("FLEXIBLE",  "Flexible"),
        ],
        default="FLEXIBLE"
    )
    show_streak_on_nav = models.BooleanField(default=True)
    show_wallet_on_nav = models.BooleanField(default=True)
    email_weekly_report = models.BooleanField(
        default=True,
        help_text="Receive weekly progress report via email."
    )
    extra = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible extension settings for future preferences."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_preferences"
        verbose_name = "Student Preference"
        verbose_name_plural = "Student Preferences"

    def __str__(self):
        return f"Preferences for {self.student.email}"


# ─── 14. Recently Viewed Lesson ───────────────────────────────────────────────

class RecentlyViewedLesson(models.Model):
    """
    LRU (least-recently-used) ring buffer of the last N lessons viewed per student.
    Capped at 20 entries per student via a post-save signal.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recently_viewed",
        help_text="Student viewer."
    )
    node = models.ForeignKey(
        "lms.CourseStructure",
        on_delete=models.CASCADE,
        related_name="recently_viewed_by",
        help_text="Viewed curriculum node."
    )
    viewed_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text="Auto-updated on each view (upsert pattern)."
    )

    class Meta:
        db_table = "student_recently_viewed"
        verbose_name = "Recently Viewed Lesson"
        verbose_name_plural = "Recently Viewed Lessons"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "node"],
                name="uq_recently_viewed_student_node"
            )
        ]
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.student.email} viewed {self.node.title} at {self.viewed_at:%Y-%m-%d %H:%M}"


# ─── 15. Learning Reminder ────────────────────────────────────────────────────

class LearningReminder(BaseModel):
    """
    Scheduled study reminder notifications set by students.
    Processed by the Celery beat scheduler to fire at remind_at.
    """
    class ReminderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT    = "SENT",    "Sent"
        SNOOZED = "SNOOZED", "Snoozed"
        CANCELLED = "CANCELLED", "Cancelled"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_reminders",
        help_text="Reminder recipient."
    )
    title = models.CharField(max_length=255, help_text="Reminder headline.")
    message = models.TextField(blank=True, null=True, help_text="Optional reminder body text.")
    remind_at = models.DateTimeField(
        db_index=True,
        help_text="Scheduled datetime to fire the reminder."
    )
    node = models.ForeignKey(
        "lms.CourseStructure",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminders",
        help_text="Optional linked lesson to jump to when reminder fires."
    )
    status = models.CharField(
        max_length=20,
        choices=ReminderStatus.choices,
        default=ReminderStatus.PENDING,
        db_index=True
    )
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.JSONField(
        default=dict,
        blank=True,
        help_text="Recurrence configuration (e.g., {'frequency': 'DAILY', 'days': ['MON','WED','FRI']})."
    )
    snooze_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If snoozed, new fire datetime."
    )
    sent_at = models.DateTimeField(null=True, blank=True, help_text="Actual delivery timestamp.")

    class Meta:
        db_table = "student_learning_reminders"
        verbose_name = "Learning Reminder"
        verbose_name_plural = "Learning Reminders"
        ordering = ["remind_at"]
        indexes = [
            models.Index(fields=["student", "remind_at", "status"], name="idx_rem_student_date_status"),
            models.Index(fields=["remind_at", "status"], name="idx_reminder_global_schedule"),
        ]

    def __str__(self):
        return f"Reminder for {self.student.email}: '{self.title}' at {self.remind_at}"
