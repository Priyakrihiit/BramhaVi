import uuid
from django.db import models
from apps.base_models import BaseModel, SoftDeleteModel


class TeacherProfile(SoftDeleteModel):
    """
    Extends user profiles specifically for academic teachers and instructors.
    """
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        help_text="The core user account associated with this instructor profile."
    )
    bio = models.TextField(blank=True, null=True, help_text="Biographical text and professional background.")
    qualifications = models.JSONField(default=list, help_text="Academic degrees, credentials, and achievements.")
    specialties = models.JSONField(default=list, help_text="Primary subjects, domains, or skills of expertise.")
    experience_years = models.IntegerField(default=0, help_text="Total years of teaching experience.")
    is_verified = models.BooleanField(default=False, help_text="True if credentials have been verified by system admins.")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00, help_text="Aggregated course evaluation rating (1.00 - 5.00).")

    class Meta:
        db_table = "teacher_profiles"
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"

    def __str__(self):
        return f"Profile of Teacher: {self.user.email}"


class TeacherAnalytics(BaseModel):
    """
    Caches historical aggregates of teacher instructional performance metrics.
    """
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_analytics",
        help_text="Instructor user context."
    )
    total_students_taught = models.IntegerField(default=0, help_text="Sum of enrolled students across all assigned classes.")
    average_course_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, help_text="Averaged student rating.")
    total_teaching_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0.0, help_text="Total elapsed hours hosting live sessions.")
    assignment_completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Percentage of student submissions reviewed.")
    period_start = models.DateField(auto_now_add=True, help_text="Beginning of the evaluated period.")
    period_end = models.DateField(auto_now=True, help_text="End of the evaluated period.")

    class Meta:
        db_table = "teacher_analytics"
        verbose_name = "Teacher Analytics"
        verbose_name_plural = "Teacher Analytics Reports"

    def __str__(self):
        return f"Analytics for {self.teacher.email} ({self.period_start} to {self.period_end})"


class TeachingSession(SoftDeleteModel):
    """
    Represents active tutoring or mentoring sessions scheduled outside of curriculum lectures.
    """
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teaching_sessions",
        help_text="Instructor hosting this specific learning block."
    )
    title = models.CharField(max_length=255, help_text="Name or purpose of this tutorial session.")
    session_type = models.CharField(
        max_length=50,
        default="OFFICE_HOURS",
        choices=[
            ("OFFICE_HOURS", "Office Hours"),
            ("MENTORING", "1-on-1 Mentoring"),
            ("GROUP_REVIEW", "Group Review Class")
        ],
        help_text="Classification structure of the session."
    )
    start_time = models.DateTimeField(help_text="Session launch timestamp.")
    end_time = models.DateTimeField(help_text="Session closing timestamp.")
    meeting_link = models.CharField(max_length=512, blank=True, null=True, help_text="Virtual meeting URL (e.g., Google Meet, Zoom).")
    notes = models.TextField(blank=True, null=True, help_text="Session agenda or meeting highlights.")

    class Meta:
        db_table = "teaching_sessions"
        verbose_name = "Teaching Session"
        verbose_name_plural = "Teaching Sessions"

    def __str__(self):
        return f"{self.title} ({self.get_session_type_display()} by {self.teacher.email})"


class Batch(SoftDeleteModel):
    """
    Cohorts grouping students into distinct schedules and course timelines.
    """
    course = models.ForeignKey(
        "lms.CourseStructure",
        on_delete=models.CASCADE,
        related_name="teacher_batches",
        limit_choices_to={"node_type": "COURSE"},
        help_text="Syllabus course map associated with this cohort."
    )
    name = models.CharField(max_length=255, help_text="Cohort tag identifiers (e.g., 'Winter 2026 Batch Alpha').")
    start_date = models.DateField(help_text="Cohort start schedule.")
    end_date = models.DateField(help_text="Cohort conclusion schedule.")
    instructors = models.ManyToManyField(
        "users.User",
        related_name="assigned_batches",
        help_text="Certified educators assigned to instruct this batch cohort."
    )
    is_active = models.BooleanField(default=True, help_text="Whether this cohort is currently active.")

    class Meta:
        db_table = "batches"
        verbose_name = "Cohort Batch"
        verbose_name_plural = "Cohort Batches"

    def __str__(self):
        return f"{self.name} — {self.course.title}"


class Attendance(BaseModel):
    """
    Logs student attendance records for synchronous virtual events and class meetings.
    """
    session = models.ForeignKey(
        TeachingSession,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        null=True,
        blank=True,
        help_text="Associated special teaching session, if applicable."
    )
    live_class = models.ForeignKey(
        "lms.LiveClass",
        on_delete=models.CASCADE,
        related_name="teacher_attendance_records",
        null=True,
        blank=True,
        help_text="Associated curriculum Live Class stream, if applicable."
    )
    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_portal_attendance",
        help_text="Attending student recipient."
    )
    joined_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when user logged into stream.")
    left_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when user disconnected.")
    status = models.CharField(
        max_length=50,
        default="ABSENT",
        choices=[
            ("PRESENT", "Present"),
            ("ABSENT", "Absent"),
            ("LATE", "Late"),
            ("EXCUSED", "Excused")
        ],
        help_text="Attendance certification state."
    )

    class Meta:
        db_table = "attendances"
        verbose_name = "Attendance Log"
        verbose_name_plural = "Attendance Logs"

    def __str__(self):
        event_name = self.live_class.title if self.live_class else (self.session.title if self.session else "Session")
        return f"{self.student.email} Attendance: {self.status} for {event_name}"


class QuestionCategory(BaseModel):
    """
    Provides standard taxonomic tags and topics to organize item banks.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Display identifier tag (e.g., 'Metaphysics', 'Ethics').")
    description = models.TextField(blank=True, null=True, help_text="Topic context overview.")

    class Meta:
        db_table = "question_categories"
        verbose_name = "Question Category"
        verbose_name_plural = "Question Categories"

    def __str__(self):
        return self.name


class QuestionDifficulty(BaseModel):
    """
    Defines complexity weight tiers to calibrate exam evaluations.
    """
    level = models.CharField(max_length=50, unique=True, help_text="Tier identifier (e.g., 'EASY', 'MEDIUM', 'HARD', 'EXPERT').")
    multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0, help_text="Grade weighting multiplier.")

    class Meta:
        db_table = "question_difficulties"
        verbose_name = "Question Difficulty Tier"
        verbose_name_plural = "Question Difficulty Tiers"

    def __str__(self):
        return f"{self.level} (Weight: {self.multiplier}x)"


class TeachingCalendar(BaseModel):
    """
    Schedules recurring availability templates for teacher calendar synchronizations.
    """
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teaching_calendars",
        help_text="Sustaining instructor."
    )
    day_of_week = models.IntegerField(
        choices=[
            (1, "Monday"),
            (2, "Tuesday"),
            (3, "Wednesday"),
            (4, "Thursday"),
            (5, "Friday"),
            (6, "Saturday"),
            (7, "Sunday")
        ],
        help_text="Target weekly schedule pattern day."
    )
    start_time = models.TimeField(help_text="Availability onset.")
    end_time = models.TimeField(help_text="Availability closure.")
    recurrence_rule = models.CharField(max_length=255, default="WEEKLY", help_text="Standard recurrence ruleset.")

    class Meta:
        db_table = "teaching_calendars"
        verbose_name = "Teaching Calendar Slot"
        verbose_name_plural = "Teaching Calendar Slots"

    def __str__(self):
        return f"Recurring Slot: {self.get_day_of_week_display()} {self.start_time}-{self.end_time} (Teacher: {self.teacher.email})"


class TeacherAnnouncement(SoftDeleteModel):
    """
    Broadcasts bulletins, alerts, and instructions from teachers to associated course groups.
    """
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_announcements",
        help_text="Broadcasting instructor."
    )
    course = models.ForeignKey(
        "lms.CourseStructure",
        on_delete=models.CASCADE,
        related_name="teacher_announcements",
        limit_choices_to={"node_type": "COURSE"},
        help_text="Target course cohort destination."
    )
    title = models.CharField(max_length=255, help_text="Alert headline header.")
    content = models.TextField(help_text="Message text body.")
    published_at = models.DateTimeField(auto_now_add=True, help_text="Dispatch timestamp.")

    class Meta:
        db_table = "teacher_announcements"
        verbose_name = "Teacher Announcement"
        verbose_name_plural = "Teacher Announcements"

    def __str__(self):
        return f"Announcement '{self.title}' (Course: {self.course.title})"


class TeacherSchedule(BaseModel):
    """
    Tracks administrative and calendar actions scheduled specifically by teachers.
    """
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_schedules",
        help_text="Assigned educator."
    )
    title = models.CharField(max_length=255, help_text="Agenda description headline.")
    description = models.TextField(blank=True, null=True, help_text="Detailed objective criteria.")
    start_time = models.DateTimeField(help_text="Launch execution time.")
    end_time = models.DateTimeField(help_text="Scheduled closure time.")
    status = models.CharField(
        max_length=50,
        default="PENDING",
        choices=[
            ("PENDING", "Pending"),
            ("IN_PROGRESS", "In Progress"),
            ("COMPLETED", "Completed"),
            ("CANCELLED", "Cancelled")
        ],
        help_text="Task fulfillment state."
    )

    class Meta:
        db_table = "teacher_schedules"
        verbose_name = "Teacher Schedule Item"
        verbose_name_plural = "Teacher Schedule Items"

    def __str__(self):
        return f"Schedule: {self.title} ({self.status}) for {self.teacher.email}"


class TeachingGoal(BaseModel):
    """
    Maintains professional development KPIs, certification trackers, or syllabus progress targets.
    """
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teaching_goals",
        help_text="Educator chasing target."
    )
    title = models.CharField(max_length=255, help_text="KPI goal definition.")
    description = models.TextField(blank=True, null=True, help_text="Fulfillment guidelines.")
    target_metric = models.CharField(
        max_length=100,
        choices=[
            ("STUDENT_RATING", "Student Evaluation Score"),
            ("CLASSES_HELD", "Total Live Classes Handled"),
            ("GRADED_COUNT", "Grading Submissions Answered"),
            ("COURSE_COMPLETE", "Cohort Course Completion Rate")
        ],
        help_text="Target indicator classifier."
    )
    target_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Goal target threshold value.")
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Active achievement score.")
    deadline = models.DateField(null=True, blank=True, help_text="Goal expiration target date.")
    is_completed = models.BooleanField(default=False, help_text="True if target has been satisfied.")

    class Meta:
        db_table = "teaching_goals"
        verbose_name = "Teaching Goal"
        verbose_name_plural = "Teaching Goals"

    def __str__(self):
        return f"Goal: {self.title} ({self.current_value}/{self.target_value}) for {self.teacher.email}"


class TeacherEarning(BaseModel):
    """
    Tracks revenue shares, grading bonuses, and payout credits awarded to educators.
    """
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_earnings",
        help_text="Earning instructor recipient."
    )
    course = models.ForeignKey(
        "lms.CourseStructure",
        on_delete=models.CASCADE,
        related_name="teacher_earnings",
        null=True,
        blank=True,
        help_text="Source course yielding split revenue, if applicable."
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Financial credit value awarded.")
    points = models.IntegerField(default=0, help_text="Points ledger credits awarded.")
    earning_type = models.CharField(
        max_length=50,
        default="REVENUE_SHARE",
        choices=[
            ("REVENUE_SHARE", "Course Purchase Split"),
            ("GRADING_BONUS", "Assignment Evaluation Premium"),
            ("LECTURE_PAYMENT", "Live Streaming Hours Fee"),
            ("SYSTEM_AWARD", "Direct Administrative Incentive")
        ],
        help_text="Financial allocation classifier."
    )
    description = models.TextField(blank=True, null=True, help_text="Descriptive transaction ledger context.")
    recorded_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when earnings ledger locked.")

    class Meta:
        db_table = "teacher_earnings"
        verbose_name = "Teacher Earning Entry"
        verbose_name_plural = "Teacher Earning Entries"

    def __str__(self):
        return f"${self.amount} ({self.earning_type}) credited to {self.teacher.email}"


class TeacherWallet(BaseModel):
    """
    Stores payment configurations and tracks active payout accounts and ledger balances.
    """
    teacher = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_wallet",
        help_text="The instructor associated with this finance vault."
    )
    payout_method = models.CharField(
        max_length=100,
        default="STRIPE",
        choices=[
            ("STRIPE", "Stripe Connect Direct"),
            ("PAYPAL", "PayPal Business Transfer"),
            ("BANK", "Direct ACH Wire Draft")
        ],
        help_text="Active financial payout method."
    )
    payout_address = models.CharField(max_length=255, blank=True, null=True, help_text="Routing bank address, card, or PayPal email.")
    balance_points = models.IntegerField(default=0, help_text="Aggregated balance points.")
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Withdrawable financial balance.")
    last_payout_at = models.DateTimeField(null=True, blank=True, help_text="Most recent completed withdrawal transaction.")

    class Meta:
        db_table = "teacher_wallets"
        verbose_name = "Teacher Financial Wallet"
        verbose_name_plural = "Teacher Financial Wallets"

    def __str__(self):
        return f"Wallet of {self.teacher.email} — Balance: ${self.balance_amount}"


class TeacherCertificate(SoftDeleteModel):
    """
    Tracks certification milestones earned by teachers from external registries or admin reviews.
    """
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_certificates",
        help_text="Educator recipient."
    )
    title = models.CharField(max_length=255, help_text="Certification name (e.g., 'Advanced Vedanta Instruction').")
    issuer = models.CharField(max_length=255, help_text="Academic board body verifying credentials.")
    issued_date = models.DateField(help_text="Validation launch date.")
    expiry_date = models.DateField(null=True, blank=True, help_text="Credential expiration date, if applicable.")
    verification_url = models.CharField(max_length=512, blank=True, null=True, help_text="Public certificate validation page link.")

    class Meta:
        db_table = "teacher_certificates"
        verbose_name = "Teacher Certificate"
        verbose_name_plural = "Teacher Certificates"

    def __str__(self):
        return f"{self.title} for {self.teacher.email}"


class TeacherAchievement(BaseModel):
    """
    Rewards milestones earned by teachers within the BrahmaVidya system.
    """
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_achievements",
        help_text="Instructing recipient."
    )
    title = models.CharField(max_length=255, help_text="Achievement name (e.g., 'Guru of the Month').")
    description = models.TextField(blank=True, null=True, help_text="Narrative outlining why badge was awarded.")
    unlocked_at = models.DateTimeField(auto_now_add=True, help_text="Awarded timestamp.")
    badge_icon = models.CharField(max_length=100, default="award", help_text="Visually distinct award icon marker.")

    class Meta:
        db_table = "teacher_achievements"
        verbose_name = "Teacher Achievement Badge"
        verbose_name_plural = "Teacher Achievement Badges"

    def __str__(self):
        return f"{self.title} Badge — {self.teacher.email}"


class TeacherNotificationPreference(BaseModel):
    """
    Enables instructors to toggle alert channels and thresholds.
    """
    teacher = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_notification_preference",
        help_text="Configuring educator."
    )
    email_on_submission = models.BooleanField(default=True, help_text="Email alert immediately when a student submits an assignment.")
    email_on_discussion = models.BooleanField(default=True, help_text="Email alert when a student posts comments in active lessons.")
    sms_on_urgent = models.BooleanField(default=False, help_text="SMS notifications for system-critical cancellations.")
    push_on_live_class = models.BooleanField(default=True, help_text="In-app browser push reminders before launching live class streams.")

    class Meta:
        db_table = "teacher_notification_preferences"
        verbose_name = "Teacher Notification Preference"
        verbose_name_plural = "Teacher Notification Preferences"

    def __str__(self):
        return f"Notification Preferences for {self.teacher.email}"


class TeacherActivityLog(BaseModel):
    """
    Maintains a secure, auditable record of instructor interactions across curriculum, grading, and finance.
    """
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_activity_logs",
        help_text="Operating educator."
    )
    action = models.CharField(max_length=100, help_text="Coded trigger keyword (e.g., 'GRADED_ASSIGNMENT', 'CURATED_LESSON').")
    details = models.TextField(blank=True, null=True, help_text="Description of exact payload modifications.")
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="Client IP routing reference.")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Logged execution timestamp.")

    class Meta:
        db_table = "teacher_activity_logs"
        verbose_name = "Teacher Audit Log Entry"
        verbose_name_plural = "Teacher Audit Log Entries"

    def __str__(self):
        return f"[{self.timestamp}] {self.teacher.email} performed: {self.action}"
