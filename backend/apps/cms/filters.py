"""
CMS FilterSets - BrahmaVidya Galaxy
Sprint 15 — Enterprise CMS Extension

Purpose:
    django-filter FilterSet classes for every CMS content type.
    ViewSets set `filterset_class = <FilterSet>` to enable structured,
    type-safe filtering from URL query parameters.

Design rules:
    - Every FilterSet defines only the fields its ViewSet actually exposes.
    - Custom filters (method=) are used for M2M lookups (category, tag),
      cross-field range queries (date_from/date_to), and boolean convenience
      filters (has_workflow, is_overdue).
    - `CharFilter(lookup_expr="icontains")` for partial text matching.
    - `UUIDFilter` for exact-match UUID FK lookups.
    - `DateTimeFilter` for scheduled_at / published_at range queries.
    - `OrderingFilter` exposes only the fields intended to be orderable.
    - No raw SQL in any filter method — pure ORM.
    - All FilterSets are importable individually; no circular imports.

Usage example (in a ViewSet):
    from apps.cms.filters import ArticleFilter

    class ArticleViewSet(viewsets.ModelViewSet):
        filterset_class = ArticleFilter
        # search_fields handled by DRF SearchFilter (set in settings globally)
        search_fields = ["title", "excerpt", "body"]
        ordering_fields = ["published_at", "created_at", "views_count", "title"]
        ordering = ["-published_at"]

URL query parameter examples:
    GET /api/v1/cms/articles/?title=django
    GET /api/v1/cms/articles/?status=draft&is_featured=true
    GET /api/v1/cms/articles/?category_slug=technology&tag_slug=python
    GET /api/v1/cms/articles/?published_after=2026-01-01&published_before=2026-07-01
    GET /api/v1/cms/articles/?author=<uuid>&ordering=-views_count
    GET /api/v1/cms/articles/?search=django+orm&page=2&page_size=10
"""

from __future__ import annotations

import django_filters
from django_filters import rest_framework as df_filters

from apps.cms.models import (
    Article, Blog, Page, Tutorial, FAQ,
    Category, Tag, Author, MediaFile, Folder,
    WorkflowState, PublishSchedule, CMSRedirect,
    CMSAuditTrail, CMSSearchIndex,
)


# ─────────────────────────────────────────────────────────────────────────────
# Shared ordering choices
# ─────────────────────────────────────────────────────────────────────────────

COMMON_DATE_ORDERINGS = [
    "created_at", "-created_at",
    "updated_at", "-updated_at",
]

CONTENT_ORDERINGS = [
    "title", "-title",
    "published_at", "-published_at",
    "created_at", "-created_at",
    "updated_at", "-updated_at",
    "views_count", "-views_count",
]


# ─────────────────────────────────────────────────────────────────────────────
# ArticleFilter
# ─────────────────────────────────────────────────────────────────────────────

class ArticleFilter(df_filters.FilterSet):
    """
    FilterSet for the Article model.

    Supports filtering by:
        title           — partial, case-insensitive (icontains)
        slug            — partial, case-insensitive (icontains)
        author          — exact UUID match against author FK
        category_slug   — filter articles in a specific category by slug (M2M)
        tag_slug        — filter articles with a specific tag by slug (M2M)
        status          — exact match ("draft", "review", "approved", "published", etc.)
        is_published    — boolean exact match
        is_featured     — boolean exact match
        content_type    — exact match ("article", "news", "legal", etc.)
        published_after — articles published on or after this datetime
        published_before — articles published on or before this datetime
        has_workflow    — custom: True → only articles with an active workflow item
        ordering        — field ordering via OrderingFilter
    """

    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Title contains"
    )
    slug = django_filters.CharFilter(
        field_name="slug",
        lookup_expr="icontains",
        label="Slug contains"
    )
    author = django_filters.UUIDFilter(
        field_name="author__id",
        label="Author UUID"
    )
    cms_author = django_filters.UUIDFilter(
        field_name="cms_author__id",
        label="CMS Author profile UUID"
    )
    category_slug = django_filters.CharFilter(
        method="filter_by_category_slug",
        label="Category slug (M2M)"
    )
    tag_slug = django_filters.CharFilter(
        method="filter_by_tag_slug",
        label="Tag slug (M2M)"
    )
    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=[
            ("draft",     "Draft"),
            ("submitted", "Submitted"),
            ("review",    "Review"),
            ("approved",  "Approved"),
            ("published", "Published"),
            ("scheduled", "Scheduled"),
            ("archived",  "Archived"),
            ("rejected",  "Rejected"),
        ],
        label="Workflow status"
    )
    content_type = django_filters.CharFilter(
        field_name="content_type",
        lookup_expr="exact",
        label="Content type"
    )
    is_published = django_filters.BooleanFilter(
        field_name="is_published",
        label="Is published"
    )
    is_featured = django_filters.BooleanFilter(
        field_name="is_featured",
        label="Is featured"
    )
    is_pinned = django_filters.BooleanFilter(
        field_name="is_pinned",
        label="Is pinned"
    )
    published_after = django_filters.DateTimeFilter(
        field_name="published_at",
        lookup_expr="gte",
        label="Published on or after (ISO 8601)"
    )
    published_before = django_filters.DateTimeFilter(
        field_name="published_at",
        lookup_expr="lte",
        label="Published on or before (ISO 8601)"
    )
    created_after = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte",
        label="Created on or after (YYYY-MM-DD)"
    )
    created_before = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte",
        label="Created on or before (YYYY-MM-DD)"
    )
    has_workflow = django_filters.BooleanFilter(
        method="filter_has_workflow",
        label="Has active workflow item"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("title",        "title"),
            ("published_at", "published_at"),
            ("created_at",   "created_at"),
            ("updated_at",   "updated_at"),
            ("views_count",  "views_count"),
            ("likes_count",  "likes_count"),
        ),
        label="Order by field"
    )

    class Meta:
        model = Article
        fields = [
            "title", "slug", "author", "cms_author",
            "category_slug", "tag_slug", "status", "content_type",
            "is_published", "is_featured", "is_pinned",
            "published_after", "published_before",
            "created_after", "created_before",
            "has_workflow",
        ]

    def filter_by_category_slug(self, queryset, name, value):
        """
        Filter articles that belong to a category with the given slug.
        Adds distinct() to prevent duplicate rows from the M2M JOIN.
        """
        if not value:
            return queryset
        return queryset.filter(categories__slug=value).distinct()

    def filter_by_tag_slug(self, queryset, name, value):
        """
        Filter articles that have a tag with the given slug.
        Adds distinct() to prevent duplicate rows from the M2M JOIN.
        """
        if not value:
            return queryset
        return queryset.filter(tags__slug=value).distinct()

    def filter_has_workflow(self, queryset, name, value):
        """
        Filter articles that have at least one WorkflowState record.

        True  → only articles with an active workflow item.
        False → only articles with no workflow item.
        """
        from django.db.models import Exists, OuterRef
        has_workflow_sq = WorkflowState.objects.filter(article=OuterRef("pk"))
        queryset = queryset.annotate(_has_wf=Exists(has_workflow_sq))
        return queryset.filter(_has_wf=value)


# ─────────────────────────────────────────────────────────────────────────────
# BlogFilter
# ─────────────────────────────────────────────────────────────────────────────

class BlogFilter(df_filters.FilterSet):
    """
    FilterSet for the Blog model.

    Supports:
        title           — partial icontains
        slug            — partial icontains
        author          — exact UUID
        is_published    — boolean
        published_after — datetime gte
        published_before — datetime lte
        ordering        — title, published_at, created_at
    """

    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Title contains"
    )
    slug = django_filters.CharFilter(
        field_name="slug",
        lookup_expr="icontains",
        label="Slug contains"
    )
    author = django_filters.UUIDFilter(
        field_name="author__id",
        label="Author UUID"
    )
    is_published = django_filters.BooleanFilter(
        field_name="is_published",
        label="Is published"
    )
    published_after = django_filters.DateTimeFilter(
        field_name="published_at",
        lookup_expr="gte",
        label="Published on or after"
    )
    published_before = django_filters.DateTimeFilter(
        field_name="published_at",
        lookup_expr="lte",
        label="Published on or before"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("title",        "title"),
            ("published_at", "published_at"),
            ("created_at",   "created_at"),
            ("updated_at",   "updated_at"),
        ),
        label="Order by"
    )

    class Meta:
        model = Blog
        fields = [
            "title", "slug", "author",
            "is_published",
            "published_after", "published_before",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# PageFilter
# ─────────────────────────────────────────────────────────────────────────────

class PageFilter(df_filters.FilterSet):
    """
    FilterSet for the Page model (visual page builder).

    Supports:
        title           — partial icontains
        slug            — partial icontains
        is_published    — boolean
        author          — exact UUID
        created_after   — date filter
        created_before  — date filter
        ordering        — title, created_at, updated_at
    """

    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Title contains"
    )
    slug = django_filters.CharFilter(
        field_name="slug",
        lookup_expr="icontains",
        label="Slug contains"
    )
    is_published = django_filters.BooleanFilter(
        field_name="is_published",
        label="Is published"
    )
    author = django_filters.UUIDFilter(
        field_name="author__id",
        label="Author UUID"
    )
    created_after = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte",
        label="Created on or after"
    )
    created_before = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte",
        label="Created on or before"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("title",      "title"),
            ("created_at", "created_at"),
            ("updated_at", "updated_at"),
        ),
        label="Order by"
    )

    class Meta:
        model = Page
        fields = [
            "title", "slug", "is_published", "author",
            "created_after", "created_before",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# CategoryFilter
# ─────────────────────────────────────────────────────────────────────────────

class CategoryFilter(df_filters.FilterSet):
    """
    FilterSet for the Category hierarchical taxonomy model.

    Supports:
        name            — partial icontains
        slug            — partial icontains
        parent          — exact UUID of parent category
        is_root         — custom: True → only root categories (parent IS NULL)
        is_active       — boolean
        ordering        — name, display_order
    """

    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Name contains"
    )
    slug = django_filters.CharFilter(
        field_name="slug",
        lookup_expr="icontains",
        label="Slug contains"
    )
    parent = django_filters.UUIDFilter(
        field_name="parent__id",
        label="Parent category UUID"
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
        label="Is active"
    )
    is_root = django_filters.BooleanFilter(
        method="filter_is_root",
        label="Is root category (no parent)"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("name",          "name"),
            ("display_order", "display_order"),
            ("created_at",    "created_at"),
        ),
        label="Order by"
    )

    class Meta:
        model = Category
        fields = ["name", "slug", "parent", "is_active", "is_root"]

    def filter_is_root(self, queryset, name, value):
        """
        True  → categories with no parent (root nodes).
        False → categories that have a parent (non-root).
        """
        if value is True:
            return queryset.filter(parent__isnull=True)
        if value is False:
            return queryset.filter(parent__isnull=False)
        return queryset


# ─────────────────────────────────────────────────────────────────────────────
# TagFilter
# ─────────────────────────────────────────────────────────────────────────────

class TagFilter(df_filters.FilterSet):
    """
    FilterSet for the Tag flat taxonomy model.

    Supports:
        name            — partial icontains
        slug            — partial icontains
        min_usage       — usage_count >= value
        ordering        — name, usage_count
    """

    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Name contains"
    )
    slug = django_filters.CharFilter(
        field_name="slug",
        lookup_expr="icontains",
        label="Slug contains"
    )
    min_usage = django_filters.NumberFilter(
        field_name="usage_count",
        lookup_expr="gte",
        label="Minimum usage count"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("name",        "name"),
            ("usage_count", "usage_count"),
        ),
        label="Order by"
    )

    class Meta:
        model = Tag
        fields = ["name", "slug", "min_usage"]


# ─────────────────────────────────────────────────────────────────────────────
# MediaFilter
# ─────────────────────────────────────────────────────────────────────────────

class MediaFilter(df_filters.FilterSet):
    """
    FilterSet for the MediaFile library model.

    Supports:
        file_type       — exact: "image", "video", "audio", "document", "other"
        uploader        — exact UUID of uploader user
        original_filename — partial icontains
        is_public       — boolean
        min_size_kb     — file_size_bytes >= value * 1024
        max_size_kb     — file_size_bytes <= value * 1024
        uploaded_after  — created_at >= datetime
        uploaded_before — created_at <= datetime
        ordering        — created_at, file_size_bytes, original_filename
    """

    file_type = django_filters.ChoiceFilter(
        field_name="file_type",
        choices=[
            ("image",    "Image"),
            ("video",    "Video"),
            ("audio",    "Audio"),
            ("document", "Document"),
            ("other",    "Other"),
        ],
        label="File type"
    )
    uploader = django_filters.UUIDFilter(
        field_name="uploader__id",
        label="Uploader UUID"
    )
    original_filename = django_filters.CharFilter(
        field_name="original_filename",
        lookup_expr="icontains",
        label="Filename contains"
    )
    is_public = django_filters.BooleanFilter(
        field_name="is_public",
        label="Is public"
    )
    min_size_kb = django_filters.NumberFilter(
        method="filter_min_size_kb",
        label="Minimum file size (KB)"
    )
    max_size_kb = django_filters.NumberFilter(
        method="filter_max_size_kb",
        label="Maximum file size (KB)"
    )
    uploaded_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
        label="Uploaded on or after"
    )
    uploaded_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
        label="Uploaded on or before"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("created_at",       "created_at"),
            ("file_size_bytes",  "file_size_bytes"),
            ("original_filename","original_filename"),
        ),
        label="Order by"
    )

    class Meta:
        model = MediaFile
        fields = [
            "file_type", "uploader", "original_filename",
            "is_public", "min_size_kb", "max_size_kb",
            "uploaded_after", "uploaded_before",
        ]

    def filter_min_size_kb(self, queryset, name, value):
        """Filter files larger than the given kilobyte threshold."""
        try:
            return queryset.filter(file_size_bytes__gte=int(value) * 1024)
        except (ValueError, TypeError):
            return queryset

    def filter_max_size_kb(self, queryset, name, value):
        """Filter files smaller than the given kilobyte threshold."""
        try:
            return queryset.filter(file_size_bytes__lte=int(value) * 1024)
        except (ValueError, TypeError):
            return queryset


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowFilter
# ─────────────────────────────────────────────────────────────────────────────

class WorkflowFilter(df_filters.FilterSet):
    """
    FilterSet for the WorkflowState model.

    Supports:
        status          — exact choice filter
        assigned_to     — exact UUID of assigned reviewer
        article         — exact UUID of related article
        is_overdue      — custom: True → due_date < now AND due_date is not NULL
        due_before      — due_date <= datetime
        due_after       — due_date >= datetime
        ordering        — created_at, due_date, status
    """

    status = django_filters.MultipleChoiceFilter(
        field_name="status",
        choices=[
            ("draft",     "Draft"),
            ("submitted", "Submitted"),
            ("review",    "Review"),
            ("approved",  "Approved"),
            ("published", "Published"),
            ("scheduled", "Scheduled"),
            ("archived",  "Archived"),
            ("rejected",  "Rejected"),
        ],
        label="Workflow status (multi-select: ?status=review&status=submitted)"
    )
    assigned_to = django_filters.UUIDFilter(
        field_name="assigned_to__id",
        label="Assigned reviewer UUID"
    )
    article = django_filters.UUIDFilter(
        field_name="article__id",
        label="Article UUID"
    )
    is_overdue = django_filters.BooleanFilter(
        method="filter_is_overdue",
        label="Is overdue (past due_date)"
    )
    due_before = django_filters.DateTimeFilter(
        field_name="due_date",
        lookup_expr="lte",
        label="Due on or before"
    )
    due_after = django_filters.DateTimeFilter(
        field_name="due_date",
        lookup_expr="gte",
        label="Due on or after"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("due_date",   "due_date"),
            ("status",     "status"),
        ),
        label="Order by"
    )

    class Meta:
        model = WorkflowState
        fields = [
            "status", "assigned_to", "article",
            "is_overdue", "due_before", "due_after",
        ]

    def filter_is_overdue(self, queryset, name, value):
        """
        True  → workflow items where due_date is in the past (non-null).
        False → workflow items that are not overdue (due in the future, or no due_date).
        """
        from django.utils import timezone
        from django.db.models import Q
        now = timezone.now()
        if value is True:
            return queryset.filter(due_date__lt=now, due_date__isnull=False)
        if value is False:
            return queryset.filter(
                Q(due_date__gte=now) | Q(due_date__isnull=True)
            )
        return queryset



# ─────────────────────────────────────────────────────────────────────────────
# PublishScheduleFilter
# ─────────────────────────────────────────────────────────────────────────────

class PublishScheduleFilter(df_filters.FilterSet):
    """
    FilterSet for the PublishSchedule model.

    Supports:
        content_type    — exact choice: "article", "blog", "page"
        status          — exact choice: "pending", "processing", "published", "failed", "cancelled"
        scheduled_by    — exact UUID of scheduling user
        scheduled_after — scheduled_at >= datetime
        scheduled_before — scheduled_at <= datetime
        is_upcoming     — custom: True → pending schedules in the future
        ordering        — scheduled_at, created_at, status
    """

    content_type = django_filters.ChoiceFilter(
        field_name="content_type",
        choices=[
            ("article", "Article"),
            ("blog",    "Blog"),
            ("page",    "Page"),
        ],
        label="Content type"
    )
    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=[
            ("pending",    "Pending"),
            ("processing", "Processing"),
            ("published",  "Published"),
            ("failed",     "Failed"),
            ("cancelled",  "Cancelled"),
        ],
        label="Schedule status"
    )
    scheduled_by = django_filters.UUIDFilter(
        field_name="scheduled_by__id",
        label="Scheduled by user UUID"
    )
    scheduled_after = django_filters.DateTimeFilter(
        field_name="scheduled_at",
        lookup_expr="gte",
        label="Scheduled on or after"
    )
    scheduled_before = django_filters.DateTimeFilter(
        field_name="scheduled_at",
        lookup_expr="lte",
        label="Scheduled on or before"
    )
    is_upcoming = django_filters.BooleanFilter(
        method="filter_is_upcoming",
        label="Show only upcoming (future pending) schedules"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("scheduled_at", "scheduled_at"),
            ("created_at",   "created_at"),
            ("status",       "status"),
        ),
        label="Order by"
    )

    class Meta:
        model = PublishSchedule
        fields = [
            "content_type", "status", "scheduled_by",
            "scheduled_after", "scheduled_before", "is_upcoming",
        ]

    def filter_is_upcoming(self, queryset, name, value):
        """
        True  → pending schedules with scheduled_at in the future.
        False → past or non-pending schedules.
        """
        from django.utils import timezone
        now = timezone.now()
        if value is True:
            return queryset.filter(status="pending", scheduled_at__gte=now)
        if value is False:
            return queryset.filter(scheduled_at__lt=now)
        return queryset


# ─────────────────────────────────────────────────────────────────────────────
# FAQFilter
# ─────────────────────────────────────────────────────────────────────────────

class FAQFilter(df_filters.FilterSet):
    """
    FilterSet for the FAQ model.

    Supports:
        question        — partial icontains
        category_slug   — M2M filter by category slug
        tag_slug        — M2M filter by tag slug
        is_published    — boolean
        is_featured     — boolean
        ordering        — display_order, created_at, question
    """

    question = django_filters.CharFilter(
        field_name="question",
        lookup_expr="icontains",
        label="Question contains"
    )
    category_slug = django_filters.CharFilter(
        method="filter_by_category_slug",
        label="Category slug"
    )
    tag_slug = django_filters.CharFilter(
        method="filter_by_tag_slug",
        label="Tag slug"
    )
    is_published = django_filters.BooleanFilter(
        field_name="is_published",
        label="Is published"
    )
    is_featured = django_filters.BooleanFilter(
        field_name="is_featured",
        label="Is featured"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("display_order", "display_order"),
            ("created_at",    "created_at"),
            ("question",      "question"),
        ),
        label="Order by"
    )

    class Meta:
        model = FAQ
        fields = ["question", "category_slug", "tag_slug", "is_published", "is_featured"]

    def filter_by_category_slug(self, queryset, name, value):
        """Filter FAQs that belong to a category with the given slug (M2M)."""
        if not value:
            return queryset
        return queryset.filter(categories__slug=value).distinct()

    def filter_by_tag_slug(self, queryset, name, value):
        """Filter FAQs that have a tag with the given slug (M2M)."""
        if not value:
            return queryset
        return queryset.filter(tags__slug=value).distinct()


# ─────────────────────────────────────────────────────────────────────────────
# SearchIndexFilter
# ─────────────────────────────────────────────────────────────────────────────

class SearchIndexFilter(df_filters.FilterSet):
    """
    FilterSet for the CMSSearchIndex table.

    Supports:
        content_type    — exact choice
        published_after — published_at gte
        published_before — published_at lte
        is_published    — boolean
        ordering        — published_at, title
    """

    content_type = django_filters.ChoiceFilter(
        field_name="content_type",
        choices=[
            ("article", "Article"),
            ("blog",    "Blog"),
            ("page",    "Page"),
            ("faq",     "FAQ"),
            ("tutorial","Tutorial"),
        ],
        label="Content type"
    )
    is_published = django_filters.BooleanFilter(
        field_name="is_published",
        label="Is published"
    )
    published_after = django_filters.DateTimeFilter(
        field_name="published_at",
        lookup_expr="gte",
        label="Published on or after"
    )
    published_before = django_filters.DateTimeFilter(
        field_name="published_at",
        lookup_expr="lte",
        label="Published on or before"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("published_at", "published_at"),
            ("title",        "title"),
        ),
        label="Order by"
    )

    class Meta:
        model = CMSSearchIndex
        fields = ["content_type", "is_published", "published_after", "published_before"]


# ─────────────────────────────────────────────────────────────────────────────
# AuditTrailFilter
# ─────────────────────────────────────────────────────────────────────────────

class AuditTrailFilter(df_filters.FilterSet):
    """
    FilterSet for the CMSAuditTrail model (admin-only endpoint).

    Supports:
        action          — exact or multi-choice
        content_type    — exact
        actor           — exact UUID
        after           — created_at gte
        before          — created_at lte
        ordering        — created_at
    """

    action = django_filters.CharFilter(
        field_name="action",
        lookup_expr="exact",
        label="Action (e.g. publish, delete, approve)"
    )
    content_type = django_filters.CharFilter(
        field_name="content_type",
        lookup_expr="exact",
        label="Content type"
    )
    actor = django_filters.UUIDFilter(
        field_name="actor__id",
        label="Actor user UUID"
    )
    after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
        label="After datetime"
    )
    before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
        label="Before datetime"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("action",     "action"),
        ),
        label="Order by"
    )

    class Meta:
        model = CMSAuditTrail
        fields = ["action", "content_type", "actor", "after", "before"]


# ─────────────────────────────────────────────────────────────────────────────
# RedirectFilter
# ─────────────────────────────────────────────────────────────────────────────

class RedirectFilter(df_filters.FilterSet):
    """
    FilterSet for the CMSRedirect model.

    Supports:
        from_path       — partial icontains
        to_path         — partial icontains
        redirect_type   — exact (301, 302, 307, 308)
        is_active       — boolean
        ordering        — from_path, hit_count, created_at
    """

    from_path = django_filters.CharFilter(
        field_name="from_path",
        lookup_expr="icontains",
        label="From path contains"
    )
    to_path = django_filters.CharFilter(
        field_name="to_path",
        lookup_expr="icontains",
        label="To path contains"
    )
    redirect_type = django_filters.ChoiceFilter(
        field_name="redirect_type",
        choices=[
            (301, "301 Permanent"),
            (302, "302 Temporary"),
            (307, "307 Temporary (preserve method)"),
            (308, "308 Permanent (preserve method)"),
        ],
        label="Redirect type"
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
        label="Is active"
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("from_path",  "from_path"),
            ("hit_count",  "hit_count"),
            ("created_at", "created_at"),
        ),
        label="Order by"
    )

    class Meta:
        model = CMSRedirect
        fields = ["from_path", "to_path", "redirect_type", "is_active"]


class FolderFilter(df_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    parent = django_filters.UUIDFilter(field_name="parent")

    class Meta:
        model = Folder
        fields = ["name", "parent"]


class MediaFileFilter(df_filters.FilterSet):
    folder = django_filters.UUIDFilter(field_name="folder")
    file_type = django_filters.CharFilter(field_name="file_type")
    is_public = django_filters.BooleanFilter(field_name="is_public")

    class Meta:
        model = MediaFile
        fields = ["folder", "file_type", "is_public"]
