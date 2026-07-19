"""
Teacher Portal Serializers — BrahmaVidya Galaxy
Sprint 21: Model and standard serializers for all Teacher Portal models and outputs.
"""

from __future__ import annotations

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.teacher.models import (
    TeacherProfile, TeacherAnalytics, TeachingSession, Batch, Attendance,
    QuestionCategory, QuestionDifficulty, TeachingCalendar, TeacherAnnouncement,
    TeacherSchedule, TeachingGoal, TeacherEarning, TeacherWallet,
    TeacherCertificate, TeacherAchievement, TeacherNotificationPreference,
    TeacherActivityLog
)
from apps.lms.models import CourseStructure, Assignment, AssignmentSubmission, LiveClass

User = get_user_model()


# ─── TEACHER PROFILE & SYSTEM PREFERENCES ─────────────────────────────────────

class TeacherProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = TeacherProfile
        fields = [
            "id", "user", "user_email", "bio", "qualifications", "specialties",
            "experience_years", "is_verified", "rating", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "user", "is_verified", "rating", "created_at", "updated_at"]

    def validate_experience_years(self, value):
        from apps.teacher.validators import validate_positive_experience
        try:
            validate_positive_experience(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value


class TeacherProfileReadSerializer(TeacherProfileSerializer):
    pass


class TeacherProfileWriteSerializer(TeacherProfileSerializer):
    pass


class TeacherNotificationPreferenceSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")

    class Meta:
        model = TeacherNotificationPreference
        fields = [
            "id", "teacher", "teacher_email", "email_on_submission", "email_on_discussion",
            "sms_on_urgent", "push_on_live_class", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "created_at", "updated_at"]


# ─── FINANCE & PAYOUT LEDGER ──────────────────────────────────────────────────

class TeacherWalletSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")

    class Meta:
        model = TeacherWallet
        fields = [
            "id", "teacher", "teacher_email", "payout_method", "payout_address",
            "balance_points", "balance_amount", "last_payout_at", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "balance_points", "balance_amount", "last_payout_at", "created_at", "updated_at"]

    def validate(self, attrs):
        payout_method = attrs.get("payout_method")
        payout_address = attrs.get("payout_address")
        if payout_method and payout_address:
            from apps.teacher.validators import validate_payout_address
            try:
                validate_payout_address(payout_method, payout_address)
            except Exception as e:
                raise serializers.ValidationError(str(e))
        return attrs


class TeacherEarningSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = TeacherEarning
        fields = [
            "id", "teacher", "teacher_email", "course", "course_title", "amount",
            "points", "earning_type", "description", "recorded_at", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "recorded_at", "created_at", "updated_at"]


# ─── SCHEDULE & CALENDAR DYNAMICS ─────────────────────────────────────────────

class TeachingSessionSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")

    class Meta:
        model = TeachingSession
        fields = [
            "id", "teacher", "teacher_email", "title", "session_type",
            "start_time", "end_time", "meeting_link", "notes", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "created_at", "updated_at"]

    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Session start time must precede end time.")
        return attrs


class TeachingCalendarSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")
    day_of_week_display = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = TeachingCalendar
        fields = [
            "id", "teacher", "teacher_email", "day_of_week", "day_of_week_display",
            "start_time", "end_time", "recurrence_rule", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "created_at", "updated_at"]

    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Availability start time must precede end time.")
        return attrs


class TeacherScheduleSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")

    class Meta:
        model = TeacherSchedule
        fields = [
            "id", "teacher", "teacher_email", "title", "description",
            "start_time", "end_time", "status", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "created_at", "updated_at"]

    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Schedule item start time must precede end time.")
        return attrs


# ─── COHORT & COURSE MANAGEMENTS ──────────────────────────────────────────────

class BatchSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")
    instructors_list = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = [
            "id", "course", "course_title", "name", "start_date", "end_date",
            "instructors", "instructors_list", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_instructors_list(self, obj) -> list[dict]:
        return [{"id": inst.id, "email": inst.email} for inst in obj.instructors.all()]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date:
            from apps.teacher.validators import validate_batch_dates
            try:
                validate_batch_dates(start_date, end_date)
            except Exception as e:
                raise serializers.ValidationError(str(e))
        return attrs


class TeacherAnnouncementSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = TeacherAnnouncement
        fields = [
            "id", "teacher", "teacher_email", "course", "course_title",
            "title", "content", "published_at", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "published_at", "created_at", "updated_at"]


# ─── LESSON SERIALIZERS ───────────────────────────────────────────────────────

class CourseStructureLessonSerializer(serializers.ModelSerializer):
    """Serializer representing lessons/syllabus structures inside CourseStructure."""
    parent_title = serializers.ReadOnlyField(source="parent.title")

    class Meta:
        model = CourseStructure
        fields = [
            "id", "parent", "parent_title", "node_type", "title", "slug",
            "description", "display_order", "metadata", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "node_type", "slug", "created_at", "updated_at"]


# ─── ASSIGNMENTS & GRADING ────────────────────────────────────────────────────

class AssignmentSerializer(serializers.ModelSerializer):
    lesson_title = serializers.ReadOnlyField(source="lesson.title")

    class Meta:
        model = Assignment
        fields = [
            "id", "lesson", "lesson_title", "title", "instructions", "max_points", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    assignment_title = serializers.ReadOnlyField(source="assignment.title")
    student_email = serializers.ReadOnlyField(source="student.email")
    graded_by_email = serializers.ReadOnlyField(source="graded_by.email")

    class Meta:
        model = AssignmentSubmission
        fields = [
            "id", "assignment", "assignment_title", "student", "student_email",
            "submission_payload", "grade", "feedback", "graded_by", "graded_by_email",
            "submitted_at", "graded_at", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "submitted_at", "graded_by", "graded_at", "created_at", "updated_at"]

    def validate_grade(self, value):
        if value is not None:
            from apps.teacher.validators import validate_grade_score
            max_points = 100
            if self.instance and self.instance.assignment:
                max_points = self.instance.assignment.max_points
            try:
                validate_grade_score(float(value), max_points)
            except Exception as e:
                raise serializers.ValidationError(str(e))
        return value


# ─── QUIZ ASSESSMENT BANK ─────────────────────────────────────────────────────

class QuestionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = ["id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuestionDifficultySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionDifficulty
        fields = ["id", "level", "multiplier", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_multiplier(self, value):
        from apps.teacher.validators import validate_multiplier
        try:
            validate_multiplier(float(value))
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value


# ─── ATTENDANCE CERTIFICATION ─────────────────────────────────────────────────

class AttendanceSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    session_title = serializers.ReadOnlyField(source="session.title")
    live_class_title = serializers.ReadOnlyField(source="live_class.title")

    class Meta:
        model = Attendance
        fields = [
            "id", "session", "session_title", "live_class", "live_class_title",
            "student", "student_email", "joined_at", "left_at", "status", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ─── ANALYTICS AND PERFORMANCE ────────────────────────────────────────────────

class TeacherAnalyticsSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")

    class Meta:
        model = TeacherAnalytics
        fields = [
            "id", "teacher", "teacher_email", "total_students_taught", "average_course_rating",
            "total_teaching_hours", "assignment_completion_rate", "period_start", "period_end",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "period_start", "period_end", "created_at", "updated_at"]


class EnrollmentStatsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    completed_students = serializers.IntegerField()
    completion_percentage = serializers.FloatField()


class PerformanceStatsSerializer(serializers.Serializer):
    average_exam_score = serializers.FloatField()
    average_assignment_grade = serializers.FloatField()
    total_assignment_submissions = serializers.IntegerField()
    pending_evaluations = serializers.IntegerField()


class CoursePerformanceReportSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    enrollment_stats = EnrollmentStatsSerializer()
    performance_stats = PerformanceStatsSerializer()


# ─── CREDENTIALS & ACHIEVEMENTS ───────────────────────────────────────────────

class TeacherCertificateSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")

    class Meta:
        model = TeacherCertificate
        fields = [
            "id", "teacher", "teacher_email", "title", "issuer",
            "issued_date", "expiry_date", "verification_url", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "created_at", "updated_at"]


class TeacherAchievementSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")

    class Meta:
        model = TeacherAchievement
        fields = [
            "id", "teacher", "teacher_email", "title", "description",
            "unlocked_at", "badge_icon", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "unlocked_at", "created_at", "updated_at"]


class TeachingGoalSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")

    class Meta:
        model = TeachingGoal
        fields = [
            "id", "teacher", "teacher_email", "title", "description", "target_metric",
            "target_value", "current_value", "deadline", "is_completed", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "is_completed", "created_at", "updated_at"]


# ─── AUDITING ─────────────────────────────────────────────────────────────────

class TeacherActivityLogSerializer(serializers.ModelSerializer):
    teacher_email = serializers.ReadOnlyField(source="teacher.email")

    class Meta:
        model = TeacherActivityLog
        fields = [
            "id", "teacher", "teacher_email", "action", "details",
            "ip_address", "timestamp", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "teacher", "timestamp", "created_at", "updated_at"]


# ─── INTEGRATED DASHBOARD TIMELINE & METRICS ──────────────────────────────────

class DashboardMetricsSerializer(serializers.Serializer):
    total_active_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    pending_evaluations = serializers.IntegerField()
    mtd_earnings = serializers.FloatField()
    average_rating = serializers.FloatField()


class DashboardTimelineItemSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.CharField()
    title = serializers.CharField()
    course_title = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    time = serializers.CharField()
    duration = serializers.IntegerField()
    link = serializers.CharField(allow_blank=True, required=False, allow_null=True)


class TeacherDashboardSummarySerializer(serializers.Serializer):
    metrics = DashboardMetricsSerializer()
    schedule_timeline = DashboardTimelineItemSerializer(many=True)
    last_cached_at = serializers.DateTimeField()
