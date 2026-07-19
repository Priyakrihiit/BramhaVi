import uuid
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from apps.base_models import BaseModel, SoftDeleteModel


class CourseNodeType(models.TextChoices):
    """
    Valid logical level categories in the curriculum adjacency tree.
    """
    PROGRAM = "PROGRAM", "Program"
    SUBJECT = "SUBJECT", "Subject"
    COURSE = "COURSE", "Course"
    CHAPTER = "CHAPTER", "Chapter"
    TOPIC = "TOPIC", "Topic"
    SUBTOPIC = "SUBTOPIC", "Subtopic"
    LESSON = "LESSON", "Lesson"


class CourseStructure(SoftDeleteModel):
    """
    Unified table powering the hierarchical curriculum tree (Program to Lesson).
    """
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text="Self-referential link pointing to parent node in adjacency list."
    )
    node_type = models.CharField(
        max_length=20,
        choices=CourseNodeType.choices,
        help_text="The tier layer classifier of this curriculum unit."
    )
    title = models.CharField(max_length=255, help_text="Header display title.")
    slug = models.CharField(max_length=255, help_text="URL slug identifier.")
    description = models.TextField(blank=True, null=True, help_text="Detailed description of content unit.")
    display_order = models.IntegerField(default=0, help_text="Sequential sorting index under the same parent.")
    metadata = models.JSONField(
        default=dict,
        help_text="Flexible dynamic settings (e.g., video URL, duration, attachment details)."
    )

    class Meta:
        db_table = "course_structures"
        verbose_name = "Course Structure"
        verbose_name_plural = "Course Structures"
        indexes = [
            models.Index(fields=["parent"], name="idx_course_struct_parent"),
            GinIndex(fields=["metadata"], name="idx_course_struct_meta_gin")
        ]

    def __str__(self):
        return f"[{self.node_type}] {self.title}"


class LearningProgress(SoftDeleteModel):
    """
    Tracks precise user progress metrics and completion status across curriculum nodes.
    """
    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="learning_progress",
        help_text="Enrolled student user."
    )
    node = models.ForeignKey(
        CourseStructure,
        on_delete=models.CASCADE,
        related_name="progress_records",
        help_text="Associated syllabus block node."
    )
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Completion ratio of child lessons under this node."
    )
    is_completed = models.BooleanField(default=False, help_text="Has student successfully achieved 100% completion?")
    last_accessed_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp of complete milestone.")

    class Meta:
        db_table = "learning_progress"
        verbose_name = "Learning Progress"
        verbose_name_plural = "Learning Progresses"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "node"],
                name="uq_learning_progress_student_node"
            )
        ]
        indexes = [
            models.Index(
                fields=["student", "node"],
                condition=models.Q(is_completed=False),
                name="idx_learning_progress_active"
            )
        ]

    def __str__(self):
        return f"{self.student.email} -> {self.node.title} ({self.progress_percentage}%)"


class Assignment(models.Model):
    """
    Syllabus Lesson Assignment criteria prompts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(
        CourseStructure,
        on_delete=models.CASCADE,
        related_name="assignments",
        limit_choices_to={"node_type": CourseNodeType.LESSON},
        help_text="Target Lesson node."
    )
    title = models.CharField(max_length=255, help_text="Assignment heading.")
    instructions = models.TextField(help_text="Detailed grading guidelines and prompt criteria.")
    max_points = models.IntegerField(default=100, help_text="Max grading point capacity.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "assignments"
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self):
        return self.title


class AssignmentSubmission(SoftDeleteModel):
    """
    Student assignment uploads, feedback, and grading records.
    """
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
        help_text="Linked assignment criteria."
    )
    student = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="assignment_submissions",
        help_text="Submitting student user."
    )
    submission_payload = models.JSONField(help_text="Tracks text essay essay inputs and attachment storage URLs.")
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Awarded score by instructor."
    )
    feedback = models.TextField(blank=True, null=True, help_text="Instructor feedback notations.")
    graded_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="graded_assignment_submissions",
        help_text="Grading instructor user."
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when grade was finalized.")

    class Meta:
        db_table = "assignment_submissions"
        verbose_name = "Assignment Submission"
        verbose_name_plural = "Assignment Submissions"

    def __str__(self):
        return f"Submission {self.id} for {self.assignment.title} (Student: {self.student.email})"


class PracticeSession(SoftDeleteModel):
    """
    Tracks quick quiz mock testing session histories.
    """
    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="practice_sessions",
        help_text="Student participant."
    )
    course = models.ForeignKey(
        CourseStructure,
        on_delete=models.CASCADE,
        related_name="practice_sessions",
        help_text="Linked Course curriculum node."
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Achieved percentage score."
    )
    session_data = models.JSONField(help_text="Tracks given student answers and correct keys.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "practice_sessions"
        verbose_name = "Practice Session"
        verbose_name_plural = "Practice Sessions"

    def __str__(self):
        return f"Session {self.id} (Student: {self.student.email}, Score: {self.score})"


class Project(SoftDeleteModel):
    """
    Large scale capstone project constraints linked to a Course unit.
    """
    course = models.ForeignKey(
        CourseStructure,
        on_delete=models.CASCADE,
        related_name="projects",
        help_text="Parent Course node."
    )
    title = models.CharField(max_length=255, help_text="Project theme title.")
    description = models.TextField(help_text="Comprehensive requirements description.")
    requirements = models.JSONField(default=list, help_text="Serialized checklist array of deliverables.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "projects"
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title


class Exam(models.Model):
    """
    Primary milestone examinations required for official course certification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        CourseStructure,
        on_delete=models.CASCADE,
        related_name="exams",
        help_text="Parent Course node."
    )
    title = models.CharField(max_length=255, help_text="Exam heading title.")
    passing_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=70.00,
        help_text="Score percentage threshold required to pass."
    )
    duration_minutes = models.IntegerField(default=60, help_text="Time allowance for complete attempt.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exams"
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self):
        return self.title


class QuestionBank(SoftDeleteModel):
    """
    Master repository of system questions linked to subjects/courses.
    """
    course = models.ForeignKey(
        CourseStructure,
        on_delete=models.CASCADE,
        related_name="questions",
        help_text="Subject or Course node context of questions."
    )
    question_text = models.TextField(help_text="Prompt question text.")
    question_type = models.CharField(
        max_length=50,
        default="MULTIPLE_CHOICE",
        help_text="Classification model of input layout."
    )
    options = models.JSONField(default=list, help_text="List of choices.")
    correct_answers = models.JSONField(default=list, help_text="Answer evaluation key indexes.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "question_banks"
        verbose_name = "Question Bank"
        verbose_name_plural = "Question Banks"

    def __str__(self):
        return f"Question {self.id} on {self.course.title}"


class ExamQuestion(models.Model):
    """
    Bridge joining Exams to specific QuestionBank elements.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="exam_questions", help_text="Associated exam.")
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name="exam_questions", help_text="Linked question bank node.")

    class Meta:
        db_table = "exam_questions"
        verbose_name = "Exam Question"
        verbose_name_plural = "Exam Questions"
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "question"],
                name="uq_exam_questions_exam_question"
            )
        ]

    def __str__(self):
        return f"{self.exam.title} Question: {self.question.id}"


class ExamAttempt(SoftDeleteModel):
    """
    Represents a student's active or completed exam attempt.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="exam_attempts",
        help_text="Student participant."
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="attempts",
        help_text="Linked exam."
    )
    answers = models.JSONField(default=dict, help_text="Dictionary of question responses: {question_id: selected_options_list}")
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Calculated percentage score."
    )
    passed = models.BooleanField(default=False, help_text="Whether score meets passing threshold.")
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp of submission.")
    status = models.CharField(
        max_length=50,
        default="STARTED",
        help_text="State of attempt: STARTED, SUBMITTED, TIMED_OUT"
    )

    class Meta:
        db_table = "exam_attempts"
        verbose_name = "Exam Attempt"
        verbose_name_plural = "Exam Attempts"

    def __str__(self):
        return f"Attempt {self.id} on {self.exam.title} (Student: {self.student.email}, Passed: {self.passed})"


class Certificate(SoftDeleteModel):
    """
    Cryptographically secured verified course completion transcripts.
    """
    user = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="certificates",
        help_text="Graduate student recipient."
    )
    course = models.ForeignKey(
        CourseStructure,
        on_delete=models.RESTRICT,
        related_name="certificates",
        help_text="Completed course module."
    )
    certificate_url = models.CharField(max_length=512, blank=True, null=True, help_text="Cloud storage storage path of certificate PDF.")
    signature_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text="Cryptographic SHA-256 validation identifier signature."
    )
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "certificates"
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"
        indexes = [
            models.Index(fields=["signature_hash"], name="idx_certificates_hash")
        ]

    def __str__(self):
        return f"Certificate {self.signature_hash[:8]}... (User: {self.user.email})"


class Badge(SoftDeleteModel):
    """
    Playful achievement milestone tags for student gamification loops.
    """
    title = models.CharField(max_length=100, unique=True, help_text="Visually distinct badge title.")
    description = models.TextField(blank=True, null=True, help_text="Details of how to earn badge.")
    icon_url = models.CharField(max_length=512, blank=True, null=True, help_text="Creative badge icon vector SVG path URL.")
    criteria = models.JSONField(default=dict, help_text="JSON structure configuration outlining triggers.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "badges"
        verbose_name = "Badge"
        verbose_name_plural = "Badges"

    def __str__(self):
        return self.title


class UserBadge(SoftDeleteModel):
    """
    Bridge mapping unlocked Badges to User accounts.
    """
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="user_badges", help_text="Recipient user.")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="user_badges", help_text="Unlocked badge.")
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_badges"
        verbose_name = "User Badge"
        verbose_name_plural = "User Badges"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "badge"],
                name="uq_user_badges_user_badge"
            )
        ]

    def __str__(self):
        return f"{self.user.email} unlocked {self.badge.title}"


class TeacherApplication(BaseModel):
    """
    Employment recruitment applications submitted by candidate instructors.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="teacher_applications",
        help_text="Applying candidate user."
    )
    resume_url = models.CharField(max_length=512, blank=True, null=True, help_text="Cloud storage storage URL of CV.")
    experience_summary = models.TextField(help_text="Detailed overview of instruction background.")
    subjects_requested = models.JSONField(
        default=list,
        help_text="Serialized list of topics the candidate seeks to instruct."
    )
    status = models.CharField(
        max_length=50,
        default="PENDING",
        choices=[
            ("PENDING", "Pending"),
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected")
        ],
        help_text="Recruitment processing status."
    )
    reviewed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviewed_teacher_applications",
        help_text="Supervising administrator reviewer user."
    )

    class Meta:
        db_table = "teacher_applications"
        verbose_name = "Teacher Application"
        verbose_name_plural = "Teacher Applications"

    def __str__(self):
        return f"Application {self.id} (User: {self.user.email}, Status: {self.status})"


class TeacherClass(BaseModel):
    """
    Linkages mapping authorized instructors to active scheduled student courses.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="classes",
        help_text="Instructing teacher user."
    )
    course = models.ForeignKey(
        CourseStructure,
        on_delete=models.RESTRICT,
        related_name="teacher_classes",
        limit_choices_to={"node_type": CourseNodeType.COURSE},
        help_text="Assigned Course."
    )
    schedule_info = models.JSONField(help_text="Serialized agenda configurations (calendar, times, recurrence).")
    is_active = models.BooleanField(default=True, help_text="Is current scheduled class active?")

    class Meta:
        db_table = "teacher_classes"
        verbose_name = "Teacher Class"
        verbose_name_plural = "Teacher Classes"

    def __str__(self):
        return f"Class {self.id} ({self.course.title} -> Teacher: {self.teacher.email})"


class StudentEnrollment(SoftDeleteModel):
    """
    Registries mapping students to active Course structures.
    """
    student = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="enrollments",
        help_text="Learner student user."
    )
    course = models.ForeignKey(
        CourseStructure,
        on_delete=models.RESTRICT,
        related_name="enrollments",
        limit_choices_to={"node_type": CourseNodeType.COURSE},
        help_text="Target registered Course."
    )
    status = models.CharField(
        max_length=50,
        default="ACTIVE",
        choices=[
            ("ACTIVE", "Active"),
            ("COMPLETED", "Completed"),
            ("CANCELLED", "Cancelled")
        ],
        help_text="Status of educational enrollment."
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_enrollments"
        verbose_name = "Student Enrollment"
        verbose_name_plural = "Student Enrollments"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="uq_student_enrollments_student_course"
            )
        ]

    def __str__(self):
        return f"Enrollment {self.id} (Student: {self.student.email} -> Course: {self.course.title})"


class ProjectSubmission(SoftDeleteModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="project_submissions")
    submission_payload = models.JSONField(help_text="Tracks text essay essay inputs and attachment storage URLs.")

    class Meta:
        db_table = "project_submissions"
        verbose_name = "Project Submission"
        verbose_name_plural = "Project Submissions"

    def __str__(self):
        return f"ProjectSubmission {self.id} (Project: {self.project.title}, Student: {self.student.email})"


class LiveClass(BaseModel):
    """
    Schedules interactive streaming lectures linked to course curriculum topics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        CourseStructure,
        on_delete=models.CASCADE,
        related_name="live_classes",
        limit_choices_to={"node_type": CourseNodeType.COURSE},
        help_text="Assigned Course."
    )
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="live_classes",
        help_text="Instructing teacher user."
    )
    title = models.CharField(max_length=255, help_text="Header title of the live class.")
    scheduled_at = models.DateTimeField(help_text="Date and time of stream launch.")
    duration_minutes = models.IntegerField(help_text="Stream target duration in minutes.")
    stream_url = models.CharField(max_length=512, blank=True, null=True, help_text="Live stream RTMP/WebRTC entry link.")
    
    # Extensions for Sprint 22
    status = models.CharField(
        max_length=20, 
        default="SCHEDULED", 
        choices=[("SCHEDULED", "Scheduled"), ("LIVE", "Live"), ("COMPLETED", "Completed")],
        help_text="Active lifecycle stage of live class event."
    )
    meeting_id = models.CharField(max_length=255, blank=True, null=True, help_text="External WebRTC channel/room ID.")

    class Meta:
        db_table = "live_classes"
        verbose_name = "Live Class"
        verbose_name_plural = "Live Classes"

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class LiveSession(BaseModel):
    """
    Tracks execution and activation instances of live class broadcasts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "live_sessions"


class MeetingParticipant(BaseModel):
    """
    Logs active viewer presence status logs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="meeting_participations")
    role = models.CharField(max_length=50, default="ATTENDEE", choices=[("PRESENTER", "Presenter"), ("ATTENDEE", "Attendee")])
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "live_meeting_participants"


class Recording(BaseModel):
    """
    Stores archived stream recording resources.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="recordings")
    video_url = models.URLField(max_length=512)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "live_recordings"


class Whiteboard(BaseModel):
    """
    Stores drawings and shapes coordinates serialized logs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="whiteboards")
    canvas_data = models.TextField(help_text="Serialized JSON drawing commands")

    class Meta:
        db_table = "live_whiteboards"


class ChatMessage(BaseModel):
    """
    Logs live chat messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="chat_messages")
    sender = models.ForeignKey("users.User", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "live_chat_messages"


class Poll(BaseModel):
    """
    Interactive questions created by instructors.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="polls")
    creator = models.ForeignKey("users.User", on_delete=models.CASCADE)
    question = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "live_polls"


class PollOption(BaseModel):
    """
    Option answers mapping to specific Polls.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=255)

    class Meta:
        db_table = "live_poll_options"


class PollVote(BaseModel):
    """
    User votes mapping.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name="votes")
    voter = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "live_poll_votes"


class BreakoutRoom(BaseModel):
    """
    Decoupled sub-room partitions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="breakout_rooms")
    name = models.CharField(max_length=100)
    meeting_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "live_breakout_rooms"


class CalendarEvent(BaseModel):
    """
    Calendar schedule mapping.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="live_calendar_events")
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="calendar_syncs")
    event_title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        db_table = "live_calendar_events"


class Reminder(BaseModel):
    """
    User-gated launch alerts queue.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="live_reminders")
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="reminders")
    remind_at = models.DateTimeField()
    is_sent = models.BooleanField(default=False)

    class Meta:
        db_table = "live_reminders"


class MeetingAnalytics(BaseModel):
    """
    Post-stream aggregation dashboard analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="analytics_reports")
    total_participants = models.IntegerField(default=0)
    average_engagement_score = models.FloatField(default=0.0)
    peak_concurrent_users = models.IntegerField(default=0)

    class Meta:
        db_table = "live_meeting_analytics"
