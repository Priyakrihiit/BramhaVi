"""
Student Dashboard FilterSets — BrahmaVidya Galaxy
Sprint 20: Filters enabling query-parameter-based search and filters.
"""

from __future__ import annotations

import django_filters
from django_filters import rest_framework as df_filters

from apps.student.models import (
    Bookmark, StudentNote, StudyGoal,
    StudySession, StudyCalendarEvent, LearningReminder,
)


class BookmarkFilter(df_filters.FilterSet):
    """
    FilterSet for the Bookmark model.
    """
    content_type = django_filters.CharFilter(
        field_name="content_type",
        lookup_expr="exact"
    )
    content_id = django_filters.UUIDFilter(
        field_name="content_id"
    )
    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains"
    )

    class Meta:
        model = Bookmark
        fields = ["content_type", "content_id", "title"]


class StudentNoteFilter(df_filters.FilterSet):
    """
    FilterSet for the StudentNote model.
    """
    node = django_filters.NumberFilter(
        field_name="node__id"
    )
    is_pinned = django_filters.BooleanFilter(
        field_name="is_pinned"
    )
    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains"
    )
    content = django_filters.CharFilter(
        field_name="content",
        lookup_expr="icontains"
    )
    tag = django_filters.CharFilter(
        method="filter_by_tag",
        label="Filter notes having this tag"
    )

    class Meta:
        model = StudentNote
        fields = ["node", "is_pinned", "title", "content"]

    def filter_by_tag(self, queryset, name, value):
        if not value:
            return queryset
        # Search tag inside the tags JSONField array
        return queryset.filter(tags__contains=value)


class StudyGoalFilter(df_filters.FilterSet):
    """
    FilterSet for the StudyGoal model.
    """
    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="exact"
    )
    enrollment = django_filters.NumberFilter(
        field_name="enrollment__id"
    )
    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains"
    )
    target_date_before = django_filters.DateFilter(
        field_name="target_date",
        lookup_expr="lte"
    )
    target_date_after = django_filters.DateFilter(
        field_name="target_date",
        lookup_expr="gte"
    )

    class Meta:
        model = StudyGoal
        fields = ["status", "enrollment", "title"]


class StudySessionFilter(df_filters.FilterSet):
    """
    FilterSet for the StudySession model.
    """
    node = django_filters.NumberFilter(
        field_name="node__id"
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active"
    )
    started_after = django_filters.DateTimeFilter(
        field_name="started_at",
        lookup_expr="gte"
    )
    started_before = django_filters.DateTimeFilter(
        field_name="started_at",
        lookup_expr="lte"
    )

    class Meta:
        model = StudySession
        fields = ["node", "is_active"]


class StudyCalendarEventFilter(df_filters.FilterSet):
    """
    FilterSet for the StudyCalendarEvent model.
    """
    event_type = django_filters.CharFilter(
        field_name="event_type",
        lookup_expr="exact"
    )
    is_completed = django_filters.BooleanFilter(
        field_name="is_completed"
    )
    starts_after = django_filters.DateTimeFilter(
        field_name="starts_at",
        lookup_expr="gte"
    )
    starts_before = django_filters.DateTimeFilter(
        field_name="starts_at",
        lookup_expr="lte"
    )

    class Meta:
        model = StudyCalendarEvent
        fields = ["event_type", "is_completed"]


class LearningReminderFilter(df_filters.FilterSet):
    """
    FilterSet for the LearningReminder model.
    """
    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="exact"
    )
    is_recurring = django_filters.BooleanFilter(
        field_name="is_recurring"
    )
    remind_after = django_filters.DateTimeFilter(
        field_name="remind_at",
        lookup_expr="gte"
    )
    remind_before = django_filters.DateTimeFilter(
        field_name="remind_at",
        lookup_expr="lte"
    )

    class Meta:
        model = LearningReminder
        fields = ["status", "is_recurring"]
