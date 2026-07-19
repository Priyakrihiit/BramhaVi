"""
Teacher Portal FilterSets — BrahmaVidya Galaxy
Sprint 21: Query filters enabling dynamic index filtering for dashboard panels.
"""

from __future__ import annotations

import django_filters
from django_filters import rest_framework as df_filters

from apps.teacher.models import (
    Batch, Attendance, TeacherAnnouncement, TeacherSchedule,
    TeachingGoal, TeacherEarning, TeacherCertificate, TeacherActivityLog
)


class BatchFilter(df_filters.FilterSet):
    """FilterSet for the cohort Batch model."""
    course = django_filters.NumberFilter(field_name="course__id")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Batch
        fields = ["course", "is_active", "name"]


class AttendanceFilter(df_filters.FilterSet):
    """FilterSet for Attendance logging records."""
    session = django_filters.NumberFilter(field_name="session__id")
    live_class = django_filters.UUIDFilter(field_name="live_class__id")
    student = django_filters.NumberFilter(field_name="student__id")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = Attendance
        fields = ["session", "live_class", "student", "status"]


class TeacherAnnouncementFilter(df_filters.FilterSet):
    """FilterSet for announcements bulletin board."""
    course = django_filters.NumberFilter(field_name="course__id")
    teacher = django_filters.NumberFilter(field_name="teacher__id")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = TeacherAnnouncement
        fields = ["course", "teacher", "title"]


class TeacherScheduleFilter(df_filters.FilterSet):
    """FilterSet for teacher agenda activities."""
    teacher = django_filters.NumberFilter(field_name="teacher__id")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    start_time_after = django_filters.DateTimeFilter(field_name="start_time", lookup_expr="gte")
    end_time_before = django_filters.DateTimeFilter(field_name="end_time", lookup_expr="lte")

    class Meta:
        model = TeacherSchedule
        fields = ["teacher", "status"]


class TeachingGoalFilter(df_filters.FilterSet):
    """FilterSet for professional KPI targets."""
    teacher = django_filters.NumberFilter(field_name="teacher__id")
    target_metric = django_filters.CharFilter(field_name="target_metric", lookup_expr="exact")
    is_completed = django_filters.BooleanFilter(field_name="is_completed")

    class Meta:
        model = TeachingGoal
        fields = ["teacher", "target_metric", "is_completed"]


class TeacherEarningFilter(df_filters.FilterSet):
    """FilterSet for revenue ledger logs."""
    teacher = django_filters.NumberFilter(field_name="teacher__id")
    course = django_filters.NumberFilter(field_name="course__id")
    earning_type = django_filters.CharFilter(field_name="earning_type", lookup_expr="exact")

    class Meta:
        model = TeacherEarning
        fields = ["teacher", "course", "earning_type"]


class TeacherCertificateFilter(df_filters.FilterSet):
    """FilterSet for verified credentials listings."""
    teacher = django_filters.NumberFilter(field_name="teacher__id")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = TeacherCertificate
        fields = ["teacher", "title"]


class TeacherActivityLogFilter(df_filters.FilterSet):
    """FilterSet for audit records."""
    teacher = django_filters.NumberFilter(field_name="teacher__id")
    action = django_filters.CharFilter(field_name="action", lookup_expr="exact")

    class Meta:
        model = TeacherActivityLog
        fields = ["teacher", "action"]
