"""
CMS Selectors Layer - BrahmaVidya Galaxy
Sprint 15 — Enterprise CMS Extension

Purpose:
    Centralised, optimised read-only query layer for the CMS app.
    ALL data access by ViewSets must go through selectors, never raw ORM in views.

Patterns used:
    • select_related()   — eliminates FK N+1 with a single JOIN
    • prefetch_related() — eliminates M2M / reverse-FK N+1 with separate IN queries
    • Prefetch()         — custom filtered prefetch queryset with ordering
    • annotate()         — adds computed aggregate columns without extra round-trips
    • Exists() / Subquery() — correlated sub-queries replacing Python-side filtering
    • distinct()         — prevents duplicate rows from M2M JOINs
    • only() / defer()   — defers heavy TextField columns on list views
    • values() / values_list() — column projection for analytics/dashboard queries
    • F() expressions    — database-side arithmetic / comparisons
    • Q()                — complex boolean filter composition

Design rules:
    1. Selectors are pure functions — no side effects, no DB writes.
    2. Selectors return QuerySets (lazy) so callers can paginate without extra queries.
    3. Only selectors that must return concrete results (e.g. dashboard counters)
       evaluate to lists / dicts via .values() or aggregate().
    4. Selectors never import services.py (no circular dependency).
"""

from __future__ import annotations

from typing import Optional, List

from django.db.models import (
    Q, Count, Prefetch, Exists, OuterRef, Subquery,
    F, IntegerField, BooleanField, Value, Case, When,
    Max, Min, Avg, Sum, CharField,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.cms.models import (
    Page, NavigationMenu,
    Blog, Tutorial, Comment, Like,
    Forum, ForumTopic, ForumPost,
    Article, FAQ,
    Category, Tag, Author, MediaFile, Folder, MediaCollection, MediaFavorite, MediaVersion,
    ContentBlock, BlockTemplate, PageVersion, Revision,
    WorkflowState, WorkflowLog, PublishSchedule,
    CMSRedirect, CMSAuditTrail, CMSSearchIndex,
    ContentPermission, Reaction,
)


# ─────────────────────────────────────────────────────────────────────────────
# PageSelector
# ─────────────────────────────────────────────────────────────────────────────

class PageSelector:
    """
    Optimised queries for the Page model (visual page builder).

    Avoids N+1 by pre-fetching ContentBlocks nested under each Page.
    Uses Exists() to cheaply annotate whether a page has a published version.
    """

    @staticmethod
    def get_published_list(search_q: Optional[str] = None):
        """
        Return all published pages for public rendering.

        Defers `layout_data` (heavy JSONField) on list views — it is only
        fetched when the detail endpoint calls `get_by_slug`.

        Args:
            search_q: Optional case-insensitive title/slug filter.

        Returns:
            QuerySet[Page] — lazy, can be sliced by caller for pagination.
        """
        qs = (
            Page.objects
            .defer("layout_data")           # Skip JSONField on listings
            .select_related("author")
            .filter(is_published=True, deleted_at__isnull=True)
        )
        if search_q:
            qs = qs.filter(
                Q(title__icontains=search_q) |
                Q(slug__icontains=search_q)
            )
        return qs.order_by("title")

    @staticmethod
    def get_by_slug(slug: str) -> Optional[Page]:
        """
        Return a single published page with all content blocks pre-fetched.

        Uses nested Prefetch to load ContentBlock children in correct display_order
        without triggering an extra query per block.

        Args:
            slug: The URL slug to look up.

        Returns:
            Page instance or None.
        """
        children_qs = ContentBlock.objects.filter(
            deleted_at__isnull=True
        ).order_by("display_order")

        blocks_qs = ContentBlock.objects.filter(
            parent__isnull=True,
            deleted_at__isnull=True
        ).prefetch_related(
            Prefetch("children", queryset=children_qs)
        ).select_related("template").order_by("display_order")

        return (
            Page.objects
            .prefetch_related(
                Prefetch("content_blocks", queryset=blocks_qs),
            )
            .select_related("author")
            .filter(slug=slug, is_published=True, deleted_at__isnull=True)
            .first()
        )

    @staticmethod
    def get_for_admin(search_q: Optional[str] = None):
        """
        Return ALL pages (published + draft) for the admin panel with
        version count annotation and latest version number.

        Uses Subquery to avoid COUNT(*) GROUP BY issues with prefetch.

        Args:
            search_q: Optional title/slug filter.

        Returns:
            QuerySet[Page] annotated with `version_count` and `latest_version`.
        """
        version_count_sq = (
            PageVersion.objects
            .filter(page=OuterRef("pk"))
            .order_by()
            .values("page")
            .annotate(c=Count("pk"))
            .values("c")
        )
        latest_version_sq = (
            PageVersion.objects
            .filter(page=OuterRef("pk"))
            .order_by("-version_number")
            .values("version_number")[:1]
        )

        qs = (
            Page.objects
            .defer("layout_data")
            .select_related("author")
            .filter(deleted_at__isnull=True)
            .annotate(
                version_count=Coalesce(Subquery(version_count_sq, output_field=IntegerField()), Value(0)),
                latest_version=Coalesce(Subquery(latest_version_sq, output_field=IntegerField()), Value(0)),
            )
        )
        if search_q:
            qs = qs.filter(
                Q(title__icontains=search_q) |
                Q(slug__icontains=search_q)
            )
        return qs.order_by("-updated_at")

    @staticmethod
    def get_all_with_block_count():
        """
        Return pages annotated with the count of active content blocks.
        Used by the page management dashboard.

        Returns:
            QuerySet[Page] annotated with `block_count`.
        """
        return (
            Page.objects
            .defer("layout_data")
            .filter(deleted_at__isnull=True)
            .annotate(
                block_count=Count(
                    "content_blocks",
                    filter=Q(content_blocks__deleted_at__isnull=True)
                )
            )
            .order_by("-updated_at")
        )


# ─────────────────────────────────────────────────────────────────────────────
# ArticleSelector
# ─────────────────────────────────────────────────────────────────────────────

class ArticleSelector:
    """
    Optimised queries for the Article model (Sprint 15 enterprise content type).

    Key optimisations:
        - M2M categories/tags use prefetch_related to avoid N+1
        - Reactions are counted via annotate() rather than loaded
        - Exists() used for has_user_reacted annotation
        - only() used on list views to skip body (large TextField)
    """

    @staticmethod
    def get_published_list(
        content_type: Optional[str] = None,
        category_slug: Optional[str] = None,
        tag_slug: Optional[str] = None,
        author_id: Optional[str] = None,
        is_featured: Optional[bool] = None,
        search_q: Optional[str] = None,
        requesting_user=None,
    ):
        """
        Return published articles for public listing pages.

        Optimisations:
            - `only()` excludes `body`, `custom_css`, `custom_js`, `schema_json`
              on listings (these fields are only needed on the detail view)
            - `annotate(reaction_count)` avoids loading all Reaction rows
            - `Exists(user_reacted_sq)` adds per-user reaction flag in one query

        Args:
            content_type: e.g. "article", "news", "legal"
            category_slug: Filter by category URL slug.
            tag_slug: Filter by tag URL slug.
            author_id: Filter by author UUID.
            is_featured: Boolean featured flag filter.
            search_q: Title / excerpt keyword filter.
            requesting_user: If provided, annotates `has_reacted` for the user.

        Returns:
            QuerySet[Article] — lazy.
        """
        qs = (
            Article.objects
            .only(
                "id", "title", "slug", "content_type", "status", "is_published",
                "is_featured", "is_pinned", "published_at", "reading_time_minutes",
                "excerpt", "views_count", "likes_count", "comments_count",
                "allow_comments", "meta_title", "meta_description", "og_image_url",
                "created_at", "updated_at",
                # FK ids — needed for select_related join
                "author_id", "cms_author_id", "featured_image_id",
            )
            .select_related("author", "cms_author", "featured_image")
            .prefetch_related(
                Prefetch(
                    "categories",
                    queryset=Category.objects.only("id", "name", "slug", "color", "icon")
                                             .filter(deleted_at__isnull=True)
                ),
                Prefetch(
                    "tags",
                    queryset=Tag.objects.only("id", "name", "slug")
                ),
            )
            .filter(is_published=True, deleted_at__isnull=True)
            .annotate(
                reaction_count=Count("reactions", distinct=True),
            )
        )

        # Annotate whether the requesting user has already reacted
        if requesting_user and requesting_user.is_authenticated:
            user_reacted_sq = Reaction.objects.filter(
                article=OuterRef("pk"),
                user=requesting_user
            )
            qs = qs.annotate(has_reacted=Exists(user_reacted_sq))

        if content_type:
            qs = qs.filter(content_type=content_type)
        if category_slug:
            qs = qs.filter(categories__slug=category_slug).distinct()
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug).distinct()
        if author_id:
            qs = qs.filter(author_id=author_id)
        if is_featured is not None:
            qs = qs.filter(is_featured=is_featured)
        if search_q:
            qs = qs.filter(
                Q(title__icontains=search_q) |
                Q(excerpt__icontains=search_q)
            )

        return qs.order_by("-is_pinned", "-published_at")

    @staticmethod
    def get_by_slug(slug: str, requesting_user=None) -> Optional[Article]:
        """
        Return a single article with full body and all relations loaded.

        This selector does NOT use only() — it loads all fields for the detail view.
        It fetches reactions grouped by type using a prefetch + annotation.

        Args:
            slug: Article URL slug.
            requesting_user: For has_reacted annotation.

        Returns:
            Article instance or None.
        """
        reaction_types_sq = (
            Reaction.objects
            .filter(article=OuterRef("pk"))
            .order_by()
            .values("article")
            .annotate(c=Count("pk"))
            .values("c")
        )

        qs = (
            Article.objects
            .select_related("author", "cms_author", "featured_image")
            .prefetch_related(
                Prefetch("categories", queryset=Category.objects.filter(deleted_at__isnull=True)),
                Prefetch("tags", queryset=Tag.objects.all()),
                Prefetch(
                    "reactions",
                    queryset=Reaction.objects.select_related("user").only(
                        "id", "reaction_type", "user_id", "article_id"
                    )
                ),
                Prefetch(
                    "workflow_states",
                    queryset=WorkflowState.objects.select_related("assigned_to")
                                                  .order_by("-created_at")[:1]
                ),
            )
            .annotate(
                reaction_count=Count("reactions", distinct=True),
                total_reactions=Coalesce(
                    Subquery(reaction_types_sq, output_field=IntegerField()), Value(0)
                ),
            )
            .filter(slug=slug, deleted_at__isnull=True)
        )

        if requesting_user and requesting_user.is_authenticated:
            qs = qs.annotate(
                has_reacted=Exists(
                    Reaction.objects.filter(article=OuterRef("pk"), user=requesting_user)
                )
            )

        return qs.first()

    @staticmethod
    def get_for_editor(user, status: Optional[str] = None, include_deleted: bool = False):
        """
        Return articles visible to an editor — admins see all, editors see own.

        Uses Exists() to annotate whether each article has a pending workflow item
        (avoids loading all WorkflowState rows).

        Args:
            user: The requesting editor/admin.
            status: Optional status filter (e.g. "draft", "review").
            include_deleted: Admins only — include soft-deleted articles.

        Returns:
            QuerySet[Article] annotated with `has_pending_review`.
        """
        _ADMIN_ROLES = {"SUPERADMIN", "ADMIN", "CONTENT_MANAGEMENT"}
        is_admin = user.is_superuser or (
            hasattr(user, "role") and user.role and user.role.name in _ADMIN_ROLES
        )

        mgr = Article.all_objects if (include_deleted and is_admin) else Article.objects
        qs = (
            mgr
            .only(
                "id", "title", "slug", "content_type", "status", "is_published",
                "is_featured", "published_at", "views_count", "created_at", "updated_at",
                "author_id", "cms_author_id",
            )
            .select_related("author", "cms_author")
            .prefetch_related(
                Prefetch("categories", queryset=Category.objects.only("id", "name", "slug")),
                Prefetch("tags", queryset=Tag.objects.only("id", "name", "slug")),
            )
            .annotate(
                has_pending_review=Exists(
                    WorkflowState.objects.filter(
                        article=OuterRef("pk"),
                        status__in=["submitted", "review"]
                    )
                )
            )
        )

        if not is_admin:
            qs = qs.filter(Q(is_published=True) | Q(author=user))
        if status:
            qs = qs.filter(status=status)

        return qs.order_by("-updated_at")

    @staticmethod
    def get_revisions(article_id) -> "QuerySet[Revision]":
        """
        Return all revision snapshots for an article, newest first.

        Args:
            article_id: UUID of the article.

        Returns:
            QuerySet[Revision]
        """
        return (
            Revision.objects
            .select_related("author")
            .only(
                "id", "version_number", "change_summary", "snapshot",
                "created_at", "author_id",
            )
            .filter(content_type="article", content_id=article_id)
            .order_by("-version_number")
        )

    @staticmethod
    def get_related(article: Article, limit: int = 4):
        """
        Return related articles sharing at least one category.

        Uses a Subquery + Exists to avoid a costly CROSS JOIN over categories.

        Args:
            article: The reference article.
            limit: Maximum results.

        Returns:
            QuerySet[Article] — limited list.
        """
        shared_category_sq = Category.objects.filter(
            articles=OuterRef("pk"),
            id__in=article.categories.values("id")
        )
        return (
            Article.objects
            .only("id", "title", "slug", "excerpt", "published_at", "featured_image_id", "reading_time_minutes")
            .select_related("featured_image")
            .filter(
                is_published=True,
                deleted_at__isnull=True,
            )
            .exclude(pk=article.pk)
            .annotate(is_related=Exists(shared_category_sq))
            .filter(is_related=True)
            .order_by("-published_at")[:limit]
        )


# ─────────────────────────────────────────────────────────────────────────────
# BlogSelector
# ─────────────────────────────────────────────────────────────────────────────

class BlogSelector:
    """
    Optimised queries for the Blog model (Sprint CMS baseline model).

    Blog has no categories/tags M2M but does have comments, likes, and reactions.
    Reactions are reverse FK from the new Reaction model.
    """

    @staticmethod
    def get_published_list(search_q: Optional[str] = None, author_id: Optional[str] = None):
        """
        Return all published blog posts for the public blog listing.

        Defers `content` (large TextField) on list views.
        Annotates comment_count and like_count using aggregate subqueries.

        Args:
            search_q: Title keyword filter.
            author_id: Filter by author UUID.

        Returns:
            QuerySet[Blog] — lazy.
        """
        comment_count_sq = (
            Comment.objects
            .filter(blog=OuterRef("pk"), deleted_at__isnull=True)
            .order_by()
            .values("blog")
            .annotate(c=Count("pk"))
            .values("c")
        )
        like_count_sq = (
            Like.objects
            .filter(blog=OuterRef("pk"))
            .order_by()
            .values("blog")
            .annotate(c=Count("pk"))
            .values("c")
        )

        qs = (
            Blog.objects
            .defer("content")
            .select_related("author")
            .filter(is_published=True, deleted_at__isnull=True)
            .annotate(
                comment_count=Coalesce(
                    Subquery(comment_count_sq, output_field=IntegerField()), Value(0)
                ),
                like_count=Coalesce(
                    Subquery(like_count_sq, output_field=IntegerField()), Value(0)
                ),
            )
        )

        if search_q:
            qs = qs.filter(Q(title__icontains=search_q))
        if author_id:
            qs = qs.filter(author_id=author_id)

        return qs.order_by("-published_at")

    @staticmethod
    def get_by_slug(slug: str, requesting_user=None) -> Optional[Blog]:
        """
        Return a single blog post with comments tree pre-fetched.

        Uses nested Prefetch to load top-level comments with their replies
        in a single extra IN query — avoids N+1 per comment row.

        Args:
            slug: Blog URL slug.
            requesting_user: If provided, annotates `user_has_liked`.

        Returns:
            Blog instance or None.
        """
        replies_qs = (
            Comment.objects
            .select_related("author")
            .filter(deleted_at__isnull=True)
            .order_by("created_at")
        )
        top_comments_qs = (
            Comment.objects
            .select_related("author")
            .prefetch_related(Prefetch("replies", queryset=replies_qs))
            .filter(parent__isnull=True, deleted_at__isnull=True)
            .order_by("-created_at")
        )

        qs = (
            Blog.objects
            .select_related("author")
            .prefetch_related(
                Prefetch("comments", queryset=top_comments_qs),
                Prefetch(
                    "reactions",
                    queryset=Reaction.objects.only("id", "reaction_type", "user_id")
                ),
            )
            .filter(slug=slug, deleted_at__isnull=True)
        )

        if requesting_user and requesting_user.is_authenticated:
            qs = qs.annotate(
                user_has_liked=Exists(
                    Like.objects.filter(blog=OuterRef("pk"), user=requesting_user)
                ),
                user_has_reacted=Exists(
                    Reaction.objects.filter(blog=OuterRef("pk"), user=requesting_user)
                ),
            )

        return qs.first()

    @staticmethod
    def get_for_admin(search_q: Optional[str] = None, is_published: Optional[bool] = None):
        """
        Return all blog posts for the admin management table.

        Annotates comment and reaction counts. Includes soft-deleted items
        only if explicitly requested (callers filter after calling).

        Args:
            search_q: Title/author name keyword filter.
            is_published: Optional published flag filter.

        Returns:
            QuerySet[Blog] — annotated with `comment_count`, `reaction_count`.
        """
        qs = (
            Blog.objects
            .defer("content")
            .select_related("author")
            .filter(deleted_at__isnull=True)
            .annotate(
                comment_count=Count(
                    "comments",
                    filter=Q(comments__deleted_at__isnull=True),
                    distinct=True
                ),
                reaction_count=Count("reactions", distinct=True),
            )
        )

        if search_q:
            qs = qs.filter(
                Q(title__icontains=search_q) |
                Q(author__email__icontains=search_q)
            )
        if is_published is not None:
            qs = qs.filter(is_published=is_published)

        return qs.order_by("-published_at", "-created_at")

    @staticmethod
    def get_revisions(blog_id) -> "QuerySet[Revision]":
        """
        Return all revision snapshots for a blog post, newest first.

        Args:
            blog_id: UUID of the blog.

        Returns:
            QuerySet[Revision]
        """
        return (
            Revision.objects
            .select_related("author")
            .only("id", "version_number", "change_summary", "created_at", "author_id")
            .filter(content_type="blog", content_id=blog_id)
            .order_by("-version_number")
        )


# ─────────────────────────────────────────────────────────────────────────────
# CategorySelector
# ─────────────────────────────────────────────────────────────────────────────

class CategorySelector:
    """
    Optimised queries for the Category hierarchical taxonomy model.
    """

    @staticmethod
    def get_tree():
        """
        Return full nested category tree (root nodes only, children pre-fetched).

        Uses nested Prefetch to load grandchildren in the same batch query,
        preventing N+1 when rendering a 3-level category nav.

        Returns:
            QuerySet[Category] — root nodes with `.children` pre-loaded.
        """
        grandchildren_qs = Category.objects.filter(
            deleted_at__isnull=True, is_active=True
        ).order_by("display_order", "name")

        children_qs = Category.objects.filter(
            deleted_at__isnull=True, is_active=True
        ).prefetch_related(
            Prefetch("children", queryset=grandchildren_qs)
        ).order_by("display_order", "name")

        return (
            Category.objects
            .prefetch_related(Prefetch("children", queryset=children_qs))
            .filter(parent__isnull=True, is_active=True, deleted_at__isnull=True)
            .order_by("display_order", "name")
        )

    @staticmethod
    def get_flat_with_counts():
        """
        Return all active categories annotated with published article and FAQ counts.

        Uses filtered Count() to exclude unpublished/deleted records from counts
        without loading any child rows into Python.

        Returns:
            QuerySet[Category] — annotated with `article_count`, `faq_count`.
        """
        return (
            Category.objects
            .filter(deleted_at__isnull=True, is_active=True)
            .annotate(
                article_count=Count(
                    "articles",
                    filter=Q(
                        articles__is_published=True,
                        articles__deleted_at__isnull=True
                    ),
                    distinct=True
                ),
                faq_count=Count(
                    "faqs",
                    filter=Q(
                        faqs__is_published=True,
                        faqs__deleted_at__isnull=True
                    ),
                    distinct=True
                ),
            )
            .select_related("parent")
            .order_by("display_order", "name")
        )

    @staticmethod
    def get_by_slug(slug: str) -> Optional[Category]:
        """
        Return a single category by slug.

        Args:
            slug: Category URL slug.

        Returns:
            Category instance or None.
        """
        return (
            Category.objects
            .select_related("parent")
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=Category.objects.filter(
                        deleted_at__isnull=True, is_active=True
                    ).order_by("display_order")
                )
            )
            .filter(slug=slug, deleted_at__isnull=True, is_active=True)
            .first()
        )

    @staticmethod
    def get_categories_for_content_type(content_type: str):
        """
        Return categories that have at least one published content item of the given type.

        Uses Exists() correlated subquery — zero extra Python filtering.

        Args:
            content_type: "article" (only type supported via M2M to Category for now).

        Returns:
            QuerySet[Category]
        """
        has_article_sq = Article.objects.filter(
            categories=OuterRef("pk"),
            is_published=True,
            deleted_at__isnull=True
        )
        return (
            Category.objects
            .filter(deleted_at__isnull=True, is_active=True)
            .annotate(has_content=Exists(has_article_sq))
            .filter(has_content=True)
            .order_by("display_order", "name")
        )


# ─────────────────────────────────────────────────────────────────────────────
# TagSelector
# ─────────────────────────────────────────────────────────────────────────────

class TagSelector:
    """
    Optimised queries for the Tag flat taxonomy model.
    """

    @staticmethod
    def get_popular(limit: int = 50):
        """
        Return the most-used tags ordered by cached usage_count descending.

        `usage_count` is a pre-computed integer field updated by TagService on
        content publish/unpublish — avoids a COUNT JOIN on every request.

        Args:
            limit: Maximum number of tags to return.

        Returns:
            QuerySet[Tag]
        """
        return Tag.objects.filter(usage_count__gt=0).order_by("-usage_count")[:limit]

    @staticmethod
    def get_all():
        """Return all tags alphabetically."""
        return Tag.objects.all().order_by("name")

    @staticmethod
    def get_with_live_counts(limit: int = 100):
        """
        Return tags with real-time counts computed from the database.

        Slower than `get_popular()` but always accurate. Use for admin tag management.
        Uses Count() with filtered annotation — single query.

        Args:
            limit: Maximum number of tags to return.

        Returns:
            QuerySet[Tag] annotated with `live_article_count`, `live_faq_count`.
        """
        return (
            Tag.objects
            .annotate(
                live_article_count=Count(
                    "articles",
                    filter=Q(
                        articles__is_published=True,
                        articles__deleted_at__isnull=True
                    ),
                    distinct=True
                ),
                live_faq_count=Count(
                    "faqs",
                    filter=Q(
                        faqs__is_published=True,
                        faqs__deleted_at__isnull=True
                    ),
                    distinct=True
                ),
            )
            .order_by("-live_article_count", "name")[:limit]
        )

    @staticmethod
    def get_by_slug(slug: str) -> Optional[Tag]:
        """
        Return a single tag by slug.

        Args:
            slug: Tag URL slug.

        Returns:
            Tag instance or None.
        """
        return Tag.objects.filter(slug=slug).first()

    @staticmethod
    def search_tags(prefix: str, limit: int = 10):
        """
        Autocomplete tag search — returns tags whose name starts with prefix.

        Args:
            prefix: User's partial input.
            limit: Max results.

        Returns:
            QuerySet[Tag] — values("id", "name", "slug", "usage_count")
        """
        return (
            Tag.objects
            .filter(name__istartswith=prefix)
            .values("id", "name", "slug", "usage_count")
            .order_by("-usage_count")[:limit]
        )


# ─────────────────────────────────────────────────────────────────────────────
# MediaSelector
# ─────────────────────────────────────────────────────────────────────────────

class MediaSelector:
    """
    Optimised queries for the MediaFile library model.
    """

    @staticmethod
    def get_library(
        file_type: Optional[str] = None,
        search_q: Optional[str] = None,
        uploader_id: Optional[str] = None,
        is_public: Optional[bool] = None,
    ):
        """
        Return media files for the admin media library view.

        Uses select_related("uploader") and prefetch_related("tags") to
        prevent N+1 when rendering uploader info and tags per file card.

        Args:
            file_type: "image", "video", "audio", "document", or "other".
            search_q: Filename / alt_text / caption keyword filter.
            uploader_id: Filter by uploader UUID.
            is_public: Filter by public visibility flag.

        Returns:
            QuerySet[MediaFile]
        """
        qs = (
            MediaFile.objects
            .select_related("uploader")
            .prefetch_related(Prefetch("tags", queryset=Tag.objects.only("id", "name", "slug")))
            .filter(deleted_at__isnull=True)
        )

        if file_type:
            qs = qs.filter(file_type=file_type)
        if uploader_id:
            qs = qs.filter(uploader_id=uploader_id)
        if is_public is not None:
            qs = qs.filter(is_public=is_public)
        if search_q:
            qs = qs.filter(
                Q(original_filename__icontains=search_q) |
                Q(alt_text__icontains=search_q) |
                Q(caption__icontains=search_q)
            )

        return qs.order_by("-created_at")

    @staticmethod
    def get_by_id(media_id) -> Optional[MediaFile]:
        """
        Return a single media file with uploader and tags.

        Args:
            media_id: UUID of the media file.

        Returns:
            MediaFile instance or None.
        """
        return (
            MediaFile.objects
            .select_related("uploader")
            .prefetch_related("tags")
            .filter(id=media_id, deleted_at__isnull=True)
            .first()
        )

    @staticmethod
    def get_stats() -> dict:
        """
        Return aggregate statistics for the media library dashboard widget.

        Returns a single database round-trip via aggregate().

        Returns:
            Dict with total_files, total_size_bytes, images, videos, docs counts.
        """
        from django.db.models import Sum as DjSum
        qs = MediaFile.objects.filter(deleted_at__isnull=True)
        aggregates = qs.aggregate(
            total_files=Count("id"),
            total_size_bytes=Coalesce(Sum("file_size_bytes"), Value(0)),
            image_count=Count("id", filter=Q(file_type="image")),
            video_count=Count("id", filter=Q(file_type="video")),
            audio_count=Count("id", filter=Q(file_type="audio")),
            document_count=Count("id", filter=Q(file_type="document")),
        )
        return aggregates

    @staticmethod
    def get_unused_media(limit: int = 50):
        """
        Return media files not referenced as a featured_image in any Article.

        Uses Exists() correlated subquery — avoids Python-side set difference.

        Args:
            limit: Max results to return.

        Returns:
            QuerySet[MediaFile]
        """
        used_sq = Article.objects.filter(featured_image=OuterRef("pk"))
        return (
            MediaFile.objects
            .filter(deleted_at__isnull=True)
            .annotate(is_used=Exists(used_sq))
            .filter(is_used=False)
            .order_by("-created_at")[:limit]
        )


# ─────────────────────────────────────────────────────────────────────────────
# WorkflowSelector
# ─────────────────────────────────────────────────────────────────────────────

class WorkflowSelector:
    """
    Optimised queries for the editorial workflow state machine (WorkflowState/Log).
    """

    @staticmethod
    def get_pending_for_reviewer(user):
        """
        Return workflow items assigned to the given reviewer, ordered by due_date.

        Pre-fetches article author to avoid N+1 when rendering notification info.

        Args:
            user: The reviewer user.

        Returns:
            QuerySet[WorkflowState]
        """
        return (
            WorkflowState.objects
            .select_related(
                "article",
                "article__author",
                "article__cms_author",
                "assigned_to"
            )
            .filter(assigned_to=user, status__in=["submitted", "review"])
            .order_by(
                Case(When(due_date__isnull=True, then=Value(1)), default=Value(0)),
                "due_date",
                "-created_at"
            )
        )

    @staticmethod
    def get_all_pending():
        """
        Return all workflow items across all reviewers that need attention.

        Annotates `is_overdue` flag using Case/When + timezone comparison.

        Returns:
            QuerySet[WorkflowState] annotated with `is_overdue`.
        """
        now = timezone.now()
        return (
            WorkflowState.objects
            .select_related("article", "article__author", "assigned_to")
            .filter(status__in=["submitted", "review"])
            .annotate(
                is_overdue=Case(
                    When(due_date__lt=now, due_date__isnull=False, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
            .order_by("-is_overdue", "due_date")
        )

    @staticmethod
    def get_workflow_with_logs(workflow_id):
        """
        Return a single WorkflowState with all transition logs pre-fetched.

        Uses filtered Prefetch to order logs by created_at descending
        without loading them all and sorting in Python.

        Args:
            workflow_id: UUID of the WorkflowState.

        Returns:
            WorkflowState instance.

        Raises:
            WorkflowState.DoesNotExist
        """
        return (
            WorkflowState.objects
            .select_related("article", "article__author", "assigned_to")
            .prefetch_related(
                Prefetch(
                    "logs",
                    queryset=WorkflowLog.objects
                             .select_related("actor")
                             .only(
                                 "id", "from_status", "to_status", "comment",
                                 "created_at", "actor_id"
                             )
                             .order_by("-created_at")
                )
            )
            .get(id=workflow_id)
        )

    @staticmethod
    def get_workflow_for_article(article) -> Optional[WorkflowState]:
        """
        Return the current workflow state for an article.

        Args:
            article: Article instance.

        Returns:
            WorkflowState or None.
        """
        return (
            WorkflowState.objects
            .select_related("assigned_to")
            .filter(article=article)
            .order_by("-created_at")
            .first()
        )

    @staticmethod
    def get_stats_by_status() -> dict:
        """
        Return workflow item counts grouped by status.

        Single aggregated query — used in admin dashboard widget.

        Returns:
            Dict mapping status → count.
        """
        rows = (
            WorkflowState.objects
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        return {row["status"]: row["count"] for row in rows}


# ─────────────────────────────────────────────────────────────────────────────
# VersionSelector
# ─────────────────────────────────────────────────────────────────────────────

class VersionSelector:
    """
    Optimised queries for PageVersion (Page Builder version history).
    """

    @staticmethod
    def get_history_for_page(page, include_layout_data: bool = False):
        """
        Return version history for a page, newest first.

        `layout_data` (large JSONField) is deferred on list views and only
        loaded when include_layout_data=True (e.g. diff/compare endpoints).

        Args:
            page: The Page instance.
            include_layout_data: Whether to load the full layout_data JSON.

        Returns:
            QuerySet[PageVersion]
        """
        qs = (
            PageVersion.objects
            .select_related("author")
            .filter(page=page)
            .order_by("-version_number")
        )
        if not include_layout_data:
            qs = qs.defer("layout_data")
        return qs

    @staticmethod
    def get_version(page, version_number: int) -> Optional[PageVersion]:
        """
        Return a specific version for a page.

        Args:
            page: The Page instance.
            version_number: The sequential version number.

        Returns:
            PageVersion instance or None.
        """
        return (
            PageVersion.objects
            .select_related("author")
            .filter(page=page, version_number=version_number)
            .first()
        )

    @staticmethod
    def get_latest_version(page) -> Optional[PageVersion]:
        """
        Return the most recent PageVersion for a page.

        Args:
            page: The Page instance.

        Returns:
            PageVersion or None.
        """
        return (
            PageVersion.objects
            .select_related("author")
            .filter(page=page)
            .order_by("-version_number")
            .first()
        )

    @staticmethod
    def get_versions_for_comparison(page, version_a: int, version_b: int):
        """
        Return two PageVersion instances for diff comparison in one query.

        Args:
            page: The Page instance.
            version_a: First version number.
            version_b: Second version number.

        Returns:
            QuerySet[PageVersion] — 2 items (or fewer if not found).
        """
        return (
            PageVersion.objects
            .select_related("author")
            .filter(
                page=page,
                version_number__in=[version_a, version_b]
            )
            .order_by("version_number")
        )


# ─────────────────────────────────────────────────────────────────────────────
# DashboardSelector
# ─────────────────────────────────────────────────────────────────────────────

class DashboardSelector:
    """
    Admin CMS dashboard aggregate selectors.

    All methods issue a single database round-trip and return plain dicts
    or flat QuerySets suitable for serialization — no lazy QuerySets.

    Designed to power the /cms/dashboard/ API endpoint.
    """

    @staticmethod
    def get_content_overview() -> dict:
        """
        Return aggregate content counts across all CMS content types.

        Single database round-trip per content type using aggregate().

        Returns:
            Dict with total/published/draft counts per type.
        """
        article_agg = Article.objects.filter(deleted_at__isnull=True).aggregate(
            total=Count("id"),
            published=Count("id", filter=Q(is_published=True)),
            drafts=Count("id", filter=Q(is_published=False)),
            featured=Count("id", filter=Q(is_featured=True)),
        )
        blog_agg = Blog.objects.filter(deleted_at__isnull=True).aggregate(
            total=Count("id"),
            published=Count("id", filter=Q(is_published=True)),
            drafts=Count("id", filter=Q(is_published=False)),
        )
        page_agg = Page.objects.filter(deleted_at__isnull=True).aggregate(
            total=Count("id"),
            published=Count("id", filter=Q(is_published=True)),
            drafts=Count("id", filter=Q(is_published=False)),
        )
        faq_agg = FAQ.objects.filter(deleted_at__isnull=True).aggregate(
            total=Count("id"),
            published=Count("id", filter=Q(is_published=True)),
        )
        media_agg = MediaFile.objects.filter(deleted_at__isnull=True).aggregate(
            total=Count("id"),
            total_size=Coalesce(Sum("file_size_bytes"), Value(0)),
        )

        return {
            "articles": article_agg,
            "blogs": blog_agg,
            "pages": page_agg,
            "faqs": faq_agg,
            "media": media_agg,
        }

    @staticmethod
    def get_recent_activity(limit: int = 20) -> list:
        """
        Return the most recent CMS audit trail entries for the dashboard feed.

        Pre-fetches actor to display "who did what" in the activity timeline.

        Args:
            limit: Number of entries to return.

        Returns:
            List of dicts from .values().
        """
        return list(
            CMSAuditTrail.objects
            .select_related("actor")
            .only(
                "id", "action", "content_type", "content_id", "content_title",
                "created_at", "actor_id"
            )
            .order_by("-created_at")[:limit]
            .values(
                "id", "action", "content_type", "content_title",
                "created_at", "actor__email"
            )
        )

    @staticmethod
    def get_pending_workflow_count() -> dict:
        """
        Return counts of workflow items that need editor/admin attention.

        Returns:
            Dict with submitted, review, overdue counts.
        """
        now = timezone.now()
        agg = WorkflowState.objects.aggregate(
            submitted=Count("id", filter=Q(status="submitted")),
            in_review=Count("id", filter=Q(status="review")),
            overdue=Count(
                "id",
                filter=Q(
                    status__in=["submitted", "review"],
                    due_date__lt=now,
                    due_date__isnull=False
                )
            ),
        )
        return agg

    @staticmethod
    def get_upcoming_schedules(hours_ahead: int = 48) -> list:
        """
        Return pending publish schedules due in the next N hours.

        Args:
            hours_ahead: Look-ahead window in hours.

        Returns:
            List of PublishSchedule dicts.
        """
        cutoff = timezone.now() + timezone.timedelta(hours=hours_ahead)
        return list(
            PublishSchedule.objects
            .select_related("scheduled_by")
            .filter(status="pending", scheduled_at__lte=cutoff)
            .order_by("scheduled_at")
            .values(
                "id", "content_type", "content_id", "scheduled_at",
                "scheduled_by__email"
            )
        )

    @staticmethod
    def get_top_articles(limit: int = 10) -> list:
        """
        Return top articles by views_count for the analytics widget.

        Args:
            limit: Number of results.

        Returns:
            List of dicts with title, slug, views_count, published_at.
        """
        return list(
            Article.objects
            .filter(is_published=True, deleted_at__isnull=True)
            .values("id", "title", "slug", "views_count", "published_at", "likes_count")
            .order_by("-views_count")[:limit]
        )

    @staticmethod
    def get_content_by_status_breakdown() -> list:
        """
        Return article counts grouped by status for pipeline funnel chart.

        Returns:
            List of dicts: [{"status": "draft", "count": 12}, ...]
        """
        return list(
            Article.objects
            .filter(deleted_at__isnull=True)
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

    @staticmethod
    def get_category_content_counts() -> list:
        """
        Return article counts per category for the category breakdown widget.

        Returns:
            List of dicts: [{"name": "Technology", "slug": "...", "article_count": 5}, ...]
        """
        return list(
            Category.objects
            .filter(deleted_at__isnull=True, is_active=True)
            .annotate(
                article_count=Count(
                    "articles",
                    filter=Q(articles__is_published=True, articles__deleted_at__isnull=True),
                    distinct=True
                )
            )
            .values("id", "name", "slug", "color", "icon", "article_count")
            .order_by("-article_count")
        )


# ─────────────────────────────────────────────────────────────────────────────
# SearchSelector
# ─────────────────────────────────────────────────────────────────────────────

class SearchSelector:
    """
    Optimised queries against the CMSSearchIndex pre-built search table.

    This selector is intentionally lightweight — heavy ranking logic lives in
    SearchService. SearchSelector provides the raw filtered QuerySet that
    SearchService annotates and paginates.
    """

    @staticmethod
    def search(
        query: Optional[str],
        content_types: Optional[List[str]] = None,
        date_from=None,
        date_to=None,
        limit: int = 20,
        offset: int = 0,
    ):
        """
        Full-text search across CMS search index with icontains fallback.

        Annotates relevance score using Case/When for ranking:
            title match (10) > excerpt (5) > tags (4) > categories (3) > body (1)

        Args:
            query: Search string.
            content_types: Optional list of content types to include.
            date_from: Optional published_at start filter.
            date_to: Optional published_at end filter.
            limit: Max results per page.
            offset: Pagination offset.

        Returns:
            QuerySet[CMSSearchIndex] — with optional `relevance` annotation.
        """
        from django.db.models import IntegerField

        qs = CMSSearchIndex.objects.filter(is_published=True)

        if content_types:
            qs = qs.filter(content_type__in=content_types)
        if date_from:
            qs = qs.filter(published_at__gte=date_from)
        if date_to:
            qs = qs.filter(published_at__lte=date_to)

        if query and query.strip():
            q = query.strip()
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(excerpt__icontains=q) |
                Q(body__icontains=q) |
                Q(tags__icontains=q) |
                Q(categories__icontains=q) |
                Q(author_name__icontains=q)
            ).annotate(
                relevance=Case(
                    When(title__icontains=q, then=Value(10)),
                    When(excerpt__icontains=q, then=Value(5)),
                    When(tags__icontains=q, then=Value(4)),
                    When(categories__icontains=q, then=Value(3)),
                    When(body__icontains=q, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by("-relevance", "-published_at")
        else:
            qs = qs.order_by("-published_at")

        return qs[offset: offset + limit]

    @staticmethod
    def autocomplete(prefix: str, limit: int = 8) -> list:
        """
        Autocomplete title suggestions for the search bar.

        Uses `istartswith` for prefix matching — faster than icontains
        on indexed title columns.

        Args:
            prefix: User's partial input (min 2 chars enforced by caller).
            limit: Max suggestions.

        Returns:
            List of dicts: [{"title": "...", "url_path": "...", "content_type": "..."}, ...]
        """
        if not prefix or len(prefix) < 2:
            return []
        return list(
            CMSSearchIndex.objects
            .filter(is_published=True, title__icontains=prefix)
            .values("title", "url_path", "content_type")
            .order_by("-published_at")[:limit]
        )

    @staticmethod
    def get_indexed_count_by_type() -> dict:
        """
        Return count of indexed entries per content type.

        Used by the admin dashboard search stats widget.

        Returns:
            Dict mapping content_type → count.
        """
        rows = (
            CMSSearchIndex.objects
            .filter(is_published=True)
            .values("content_type")
            .annotate(count=Count("id"))
            .order_by("content_type")
        )
        return {row["content_type"]: row["count"] for row in rows}


# ─────────────────────────────────────────────────────────────────────────────
# AuditSelector
# ─────────────────────────────────────────────────────────────────────────────

class AuditSelector:
    """
    Optimised queries for the CMSAuditTrail model.
    """

    @staticmethod
    def get_trail(
        content_type: Optional[str] = None,
        content_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ):
        """
        Return audit trail entries with optional filtering.

        Args:
            content_type: Filter by content model type (e.g. "article").
            content_id: Filter by specific content record ID.
            actor_id: Filter by actor user UUID.
            action: Filter by action type (e.g. "publish", "delete").
            limit: Max results.

        Returns:
            QuerySet[CMSAuditTrail]
        """
        qs = (
            CMSAuditTrail.objects
            .select_related("actor")
            .only(
                "id", "action", "content_type", "content_id", "content_title",
                "ip_address", "request_id", "created_at", "actor_id"
            )
        )

        if content_type:
            qs = qs.filter(content_type=content_type)
        if content_id:
            qs = qs.filter(content_id=str(content_id))
        if actor_id:
            qs = qs.filter(actor_id=actor_id)
        if action:
            qs = qs.filter(action=action)

        return qs.order_by("-created_at")[:limit]

    @staticmethod
    def get_action_summary(days: int = 30) -> list:
        """
        Return audit actions grouped by type for the last N days.

        Used in admin analytics dashboard.

        Args:
            days: Lookback window in days.

        Returns:
            List of dicts: [{"action": "publish", "count": 42}, ...]
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return list(
            CMSAuditTrail.objects
            .filter(created_at__gte=cutoff)
            .values("action")
            .annotate(count=Count("id"))
            .order_by("-count")
        )


class FolderSelector:
    @staticmethod
    def get_all_folders():
        """Retrieve all active folders."""
        return Folder.objects.filter(deleted_at__isnull=True).select_related("parent")

    @staticmethod
    def get_children(folder_id: str):
        """Retrieve children of a specific folder."""
        return Folder.objects.filter(parent_id=folder_id, deleted_at__isnull=True)


class MediaCollectionSelector:
    @staticmethod
    def get_user_collections(user_id: str):
        """Retrieve collections belonging to a user."""
        return MediaCollection.objects.filter(user_id=user_id, deleted_at__isnull=True)


class MediaFavoriteSelector:
    @staticmethod
    def get_user_favorites(user_id: str):
        """Retrieve media files favorited by a user."""
        return MediaFile.objects.filter(favorited_by__user_id=user_id, deleted_at__isnull=True)


class MediaVersionSelector:
    @staticmethod
    def get_file_versions(media_file_id: str):
        """Retrieve all versions of a media file."""
        return MediaVersion.objects.filter(media_file_id=media_file_id, deleted_at__isnull=True).order_by("-version_number")
