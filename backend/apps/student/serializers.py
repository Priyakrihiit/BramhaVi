"""
Student Dashboard Serializers — BrahmaVidya Galaxy
Sprint 20: Model Serializers for all Student Portal models.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.student.models import (
    LearningHistory, ContinueLearning, Bookmark,
    StudentNote, StudyGoal, StudySession,
    StudyCalendarEvent, DailyProgress, WeeklyProgress,
    MonthlyProgress, LearningStreak, Achievement,
    StudentAchievement, StudentPreference, RecentlyViewedLesson,
    LearningReminder
)


class LearningHistorySerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    node_title = serializers.ReadOnlyField(source="node.title")
    node_type = serializers.ReadOnlyField(source="node.node_type")

    class Meta:
        model = LearningHistory
        fields = [
            "id", "student", "student_email", "node", "node_title", "node_type",
            "enrollment", "duration_seconds", "completed", "accessed_at", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "accessed_at", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class ContinueLearningSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    course_title = serializers.ReadOnlyField(source="enrollment.course.title")
    last_node_title = serializers.ReadOnlyField(source="last_node.title")

    class Meta:
        model = ContinueLearning
        fields = [
            "id", "student", "student_email", "enrollment", "course_title",
            "last_node", "last_node_title", "last_accessed_at", "position_seconds", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "last_accessed_at", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class BookmarkSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")

    class Meta:
        model = Bookmark
        fields = [
            "id", "student", "student_email", "content_type", "content_id",
            "title", "source_name", "url_path", "note", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class StudentNoteSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    node_title = serializers.ReadOnlyField(source="node.title")

    class Meta:
        model = StudentNote
        fields = [
            "id", "student", "student_email", "node", "node_title",
            "title", "content", "tags", "is_pinned", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]

    def validate_content(self, value):
        from apps.student.validators import validate_note_length
        try:
            validate_note_length(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class StudyGoalSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    course_title = serializers.ReadOnlyField(source="enrollment.course.title")

    class Meta:
        model = StudyGoal
        fields = [
            "id", "student", "student_email", "enrollment", "course_title",
            "title", "description", "target_date", "daily_target_minutes",
            "status", "completed_at", "progress_percentage", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "completed_at", "progress_percentage", "created_at", "updated_at"]

    def validate_target_date(self, value):
        from apps.student.validators import validate_goal_dates
        try:
            validate_goal_dates(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class StudySessionSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    node_title = serializers.ReadOnlyField(source="node.title")

    class Meta:
        model = StudySession
        fields = [
            "id", "student", "student_email", "node", "node_title",
            "started_at", "ended_at", "duration_seconds", "is_active", "xp_earned", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "duration_seconds", "xp_earned", "created_at", "updated_at"]

    def validate_duration_seconds(self, value):
        from apps.student.validators import validate_session_duration
        try:
            validate_session_duration(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class StudyCalendarEventSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    node_title = serializers.ReadOnlyField(source="node.title")

    class Meta:
        model = StudyCalendarEvent
        fields = [
            "id", "student", "student_email", "title", "description", "event_type",
            "starts_at", "ends_at", "all_day", "node", "node_title", "color", "is_completed",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class DailyProgressSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")

    class Meta:
        model = DailyProgress
        fields = [
            "id", "student", "student_email", "date", "study_minutes",
            "lessons_completed", "xp_earned", "lessons_accessed", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]


class WeeklyProgressSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")

    class Meta:
        model = WeeklyProgress
        fields = [
            "id", "student", "student_email", "week_start", "study_minutes",
            "lessons_completed", "xp_earned", "goal_minutes", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]


class MonthlyProgressSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")

    class Meta:
        model = MonthlyProgress
        fields = [
            "id", "student", "student_email", "year", "month", "study_minutes",
            "lessons_completed", "courses_completed", "xp_earned", "badges_earned", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]


class LearningStreakSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")

    class Meta:
        model = LearningStreak
        fields = [
            "id", "student", "student_email", "current_streak", "longest_streak",
            "last_studied_date", "streak_start_date", "total_study_days", "total_xp", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = [
            "id", "code", "title", "description", "category",
            "icon_url", "xp_reward", "criteria", "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentAchievementSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    achievement_title = serializers.ReadOnlyField(source="achievement.title")
    achievement_description = serializers.ReadOnlyField(source="achievement.description")
    achievement_category = serializers.ReadOnlyField(source="achievement.category")
    achievement_xp_reward = serializers.ReadOnlyField(source="achievement.xp_reward")

    class Meta:
        model = StudentAchievement
        fields = [
            "id", "student", "student_email", "achievement", "achievement_title",
            "achievement_description", "achievement_category", "achievement_xp_reward",
            "progress_value", "is_unlocked", "unlocked_at", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "is_unlocked", "unlocked_at", "created_at", "updated_at"]


class StudentPreferenceSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")

    class Meta:
        model = StudentPreference
        fields = [
            "id", "student", "student_email", "sidebar_collapsed", "dashboard_layout",
            "daily_goal_minutes", "weekly_goal_minutes", "preferred_study_time",
            "show_streak_on_nav", "show_wallet_on_nav", "email_weekly_report", "extra", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class RecentlyViewedLessonSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    node_title = serializers.ReadOnlyField(source="node.title")

    class Meta:
        model = RecentlyViewedLesson
        fields = [
            "id", "student", "student_email", "node", "node_title", "viewed_at"
        ]
        read_only_fields = ["id", "student", "viewed_at"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class LearningReminderSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source="student.email")
    node_title = serializers.ReadOnlyField(source="node.title")

    class Meta:
        model = LearningReminder
        fields = [
            "id", "student", "student_email", "title", "message", "remind_at",
            "node", "node_title", "status", "is_recurring", "recurrence_rule",
            "snooze_until", "sent_at", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "student", "sent_at", "created_at", "updated_at"]

    def validate_remind_at(self, value):
        from apps.student.validators import validate_reminder_time
        try:
            validate_reminder_time(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


# ─── NESTED SERIALIZERS ──────────────────────────────────────────────────────

class NestedBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ["id", "content_type", "content_id", "title", "created_at"]


class NestedStudentNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentNote
        fields = ["id", "title", "is_pinned", "updated_at"]


class NestedStudyGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyGoal
        fields = ["id", "title", "progress_percentage", "status"]


class NestedStudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = ["id", "started_at", "duration_seconds", "xp_earned"]


class NestedStudentAchievementSerializer(serializers.ModelSerializer):
    achievement_title = serializers.ReadOnlyField(source="achievement.title")
    class Meta:
        model = StudentAchievement
        fields = ["id", "achievement_title", "is_unlocked", "unlocked_at"]


# ─── READ & WRITE SERIALIZERS ────────────────────────────────────────────────

class BookmarkReadSerializer(BookmarkSerializer):
    pass


class BookmarkWriteSerializer(BookmarkSerializer):
    pass


class StudentNoteReadSerializer(StudentNoteSerializer):
    pass


class StudentNoteWriteSerializer(StudentNoteSerializer):
    pass


class StudyGoalReadSerializer(StudyGoalSerializer):
    pass


class StudyGoalWriteSerializer(StudyGoalSerializer):
    pass


class StudyCalendarEventReadSerializer(StudyCalendarEventSerializer):
    pass


class StudyCalendarEventWriteSerializer(StudyCalendarEventSerializer):
    pass


class StudySessionReadSerializer(StudySessionSerializer):
    pass


class StudySessionWriteSerializer(StudySessionSerializer):
    pass


class StudentPreferenceReadSerializer(StudentPreferenceSerializer):
    pass


class StudentPreferenceWriteSerializer(StudentPreferenceSerializer):
    pass


# ─── GENERAL ALIASES FOR COMPLIANCE ─────────────────────────────────────────

class GoalSerializer(StudyGoalSerializer):
    pass


class NoteSerializer(StudentNoteSerializer):
    pass


class PreferenceSerializer(StudentPreferenceSerializer):
    pass


# ─── PROGRESS & STATISTICS SERIALIZERS ───────────────────────────────────────

class ProgressSerializer(serializers.Serializer):
    daily = DailyProgressSerializer(many=True, required=False)
    weekly = WeeklyProgressSerializer(many=True, required=False)
    monthly = MonthlyProgressSerializer(many=True, required=False)
    streak = LearningStreakSerializer(required=False)


class StudentStatisticsSerializer(serializers.Serializer):
    total_study_minutes = serializers.FloatField(default=0.0)
    total_lessons_completed = serializers.IntegerField(default=0)
    total_xp_earned = serializers.IntegerField(default=0)
    daily_average_minutes = serializers.FloatField(default=0.0)
    peak_streak = serializers.IntegerField(default=0)


class StatisticsSerializer(StudentStatisticsSerializer):
    pass


# ─── CALENDAR SERIALIZERS ───────────────────────────────────────────────────

class CalendarSerializer(serializers.Serializer):
    id = serializers.CharField()
    source = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    event_type = serializers.CharField()
    starts_at = serializers.CharField()
    ends_at = serializers.CharField(allow_null=True, required=False)
    all_day = serializers.BooleanField()
    color = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    is_completed = serializers.BooleanField()
    node_id = serializers.IntegerField(allow_null=True, required=False)


# ─── DASHBOARD SERIALIZERS ───────────────────────────────────────────────────

class DashboardStreakSerializer(serializers.Serializer):
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    total_study_days = serializers.IntegerField()
    total_xp = serializers.IntegerField()


class DashboardTodayStatsSerializer(serializers.Serializer):
    study_minutes = serializers.FloatField()
    lessons_completed = serializers.IntegerField()
    xp_earned = serializers.IntegerField()
    lessons_accessed = serializers.IntegerField()


class DashboardWeeklyStatsSerializer(serializers.Serializer):
    study_minutes = serializers.FloatField()
    lessons_completed = serializers.IntegerField()
    xp_earned = serializers.IntegerField()
    goal_minutes = serializers.IntegerField()


class DashboardBookmarkSerializer(serializers.Serializer):
    id = serializers.CharField()
    content_type = serializers.CharField()
    content_id = serializers.CharField()
    title = serializers.CharField()
    source_name = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    url_path = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    created_at = serializers.CharField()


class DashboardRecentViewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    node_id = serializers.IntegerField()
    title = serializers.CharField()
    node_type = serializers.CharField()
    viewed_at = serializers.CharField()


class DashboardActiveSessionSerializer(serializers.Serializer):
    id = serializers.CharField()
    node_id = serializers.IntegerField(allow_null=True, required=False)
    node_title = serializers.CharField(allow_null=True, required=False)
    started_at = serializers.CharField()


class DashboardSerializer(serializers.Serializer):
    streak = DashboardStreakSerializer()
    today_stats = DashboardTodayStatsSerializer()
    weekly_stats = DashboardWeeklyStatsSerializer()
    active_goals_count = serializers.IntegerField()
    bookmarks = DashboardBookmarkSerializer(many=True)
    recently_viewed = DashboardRecentViewSerializer(many=True)
    active_session = DashboardActiveSessionSerializer(allow_null=True)


class StudentDashboardSummarySerializer(DashboardSerializer):
    pass

