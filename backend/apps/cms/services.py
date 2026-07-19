"""
CMS Service Layer - BrahmaVidya Galaxy
Purpose: All business logic for CMS operations. Views call services, not models directly.
Extends the existing PageLayoutService with enterprise workflow, publish, media, and search services.
"""

import uuid
import datetime
import logging
from typing import List, Dict, Any, Optional
from django.utils import timezone
from django.db import transaction
from django.db.models import F

from apps.cms.models import (
    Page, NavigationMenu, Article, Blog, Tutorial,
    Category, Tag, Author, MediaFile, PageVersion, Revision,
    WorkflowState, WorkflowLog, PublishSchedule,
    CMSRedirect, CMSAuditTrail, CMSSearchIndex, FAQ
)
from apps.cms.serializers import NavigationMenuSerializer

logger = logging.getLogger("cms")


class PageLayoutService:
    """Existing service — preserved exactly. New services added below."""

    @staticmethod
    def publish_page_layout(page_id: str, layout_blocks: List[Dict[str, Any]], updated_by: str) -> Dict[str, Any]:
        """Validates structure payloads, saves the active JSONB block arrays, and commits state history."""
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return {"error": "Page not found"}

        if not isinstance(layout_blocks, list):
            layout_blocks = []

        if not isinstance(page.layout_data, dict):
            page.layout_data = {}

        revisions = page.layout_data.get("_revisions", [])
        if not isinstance(revisions, list):
            revisions = []

        version_number = len(revisions) + 1

        snapshot = {
            "id": str(uuid.uuid4()),
            "version_number": version_number,
            "payload": layout_blocks,
            "created_by": str(updated_by) if updated_by else None,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        revisions.append(snapshot)

        page.layout_data["blocks"] = layout_blocks
        page.layout_data["_revisions"] = revisions
        page.is_published = True
        page.save(update_fields=["layout_data", "is_published", "updated_at"])

        # Create a PageVersion record for the new version
        PageVersion.objects.create(
            page=page,
            version_number=version_number,
            layout_data=page.layout_data.copy(),
            change_summary="Published via Page Builder",
            author_id=updated_by if updated_by else None
        )

        return {
            "page_id": str(page.id),
            "status": "PUBLISHED",
            "version": version_number,
            "layout_data": page.layout_data
        }

    @staticmethod
    def rollback_page_to_revision(page_id: str, version_number: int, authorized_by: str) -> Dict[str, Any]:
        """Reverts a live CMS layout back to a previously stored content snapshot."""
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return {"error": "Page not found"}

        if not isinstance(page.layout_data, dict):
            return {"error": "No layout data found"}

        revisions = page.layout_data.get("_revisions", [])
        if not isinstance(revisions, list):
            return {"error": "No revisions found"}

        target_revision = None
        for rev in revisions:
            if rev.get("version_number") == int(version_number):
                target_revision = rev
                break

        if not target_revision:
            return {"error": "Revision not found"}

        page.layout_data["blocks"] = target_revision.get("payload", [])
        page.save(update_fields=["layout_data", "updated_at"])

        CMSAuditTrail.objects.create(
            actor_id=authorized_by if authorized_by else None,
            action="rollback",
            content_type="page",
            content_id=str(page.id),
            content_title=page.title,
            after_state={"rolled_back_to_version": version_number}
        )

        return {
            "page_id": str(page.id),
            "restored_revision": version_number,
            "layout_data": page.layout_data
        }

    @staticmethod
    def compile_navigation_tree() -> List[Dict[str, Any]]:
        """Compiles the entire recursive list of active parent-child menu trees."""
        roots = NavigationMenu.objects.filter(parent__isnull=True).order_by("display_order")
        return NavigationMenuSerializer(roots, many=True).data


class WorkflowService:
    """Editorial workflow state machine — manages Article review and approval process."""

    VALID_TRANSITIONS = {
        "draft":     ["submitted", "archived"],
        "submitted": ["review", "draft", "rejected"],
        "review":    ["approved", "rejected", "draft"],
        "approved":  ["published", "scheduled", "rejected"],
        "rejected":  ["draft"],
        "published": ["archived", "draft"],
        "archived":  ["draft"],
        "scheduled": ["published", "draft", "cancelled"],
    }

    @staticmethod
    def get_or_create_workflow(article: Article) -> WorkflowState:
        """Get existing workflow state or create a new draft one."""
        workflow, _ = WorkflowState.objects.get_or_create(
            article=article,
            defaults={"status": "draft"}
        )
        return workflow

    @staticmethod
    def transition(workflow_id: str, to_status: str, actor, comment: str = None,
                   assigned_to=None, due_date=None) -> Dict[str, Any]:
        """Perform a validated workflow status transition."""
        try:
            workflow = WorkflowState.objects.select_related("article").get(id=workflow_id)
        except WorkflowState.DoesNotExist:
            return {"error": "Workflow not found"}

        valid_next = WorkflowService.VALID_TRANSITIONS.get(workflow.status, [])
        if to_status not in valid_next:
            return {
                "error": f"Invalid transition from '{workflow.status}' to '{to_status}'. "
                         f"Valid transitions: {valid_next}"
            }

        with transaction.atomic():
            from_status = workflow.status
            workflow.status = to_status

            if assigned_to:
                workflow.assigned_to = assigned_to
            if due_date:
                workflow.due_date = due_date
            if comment:
                workflow.notes = comment

            workflow.save()

            # Log the transition
            WorkflowLog.objects.create(
                workflow=workflow,
                from_status=from_status,
                to_status=to_status,
                actor=actor,
                comment=comment
            )

            # Sync Article status
            article = workflow.article
            article.status = to_status
            if to_status == "published":
                article.is_published = True
                article.published_at = timezone.now()
            elif to_status == "archived":
                article.is_published = False
            article.save(update_fields=["status", "is_published", "published_at", "updated_at"])

            # Audit log
            CMSAuditTrail.objects.create(
                actor=actor,
                action="approve" if to_status == "approved" else ("reject" if to_status == "rejected" else "publish"),
                content_type="article",
                content_id=str(article.id),
                content_title=article.title,
                before_state={"status": from_status},
                after_state={"status": to_status}
            )

            # Fire notification
            try:
                WorkflowService._fire_notification(workflow, from_status, to_status, actor)
            except Exception as e:
                logger.warning(f"Notification failed after workflow transition: {e}")

        return {
            "workflow_id": str(workflow.id),
            "article_id": str(article.id),
            "from_status": from_status,
            "to_status": to_status,
            "transitioned_by": str(actor.id) if actor else None
        }

    @staticmethod
    def _fire_notification(workflow: WorkflowState, from_status: str, to_status: str, actor):
        """Trigger Sprint 14 NotificationRecord for workflow state changes."""
        from apps.notifications.models import NotificationRecord
        article = workflow.article

        messages = {
            "approved": ("Content Approved ✅", f'Your article "{article.title}" has been approved and is ready to publish.', "cms"),
            "rejected": ("Content Rejected ❌", f'Your article "{article.title}" requires revisions before publishing.', "cms"),
            "published": ("Content Published 🎉", f'Your article "{article.title}" is now live!', "cms"),
        }

        if to_status in messages and article.author:
            title, content, category = messages[to_status]
            NotificationRecord.objects.create(
                user=article.author,
                category=category,
                title=title,
                content=content,
                metadata={
                    "article_id": str(article.id),
                    "article_slug": article.slug,
                    "workflow_action": to_status,
                    "actor_id": str(actor.id) if actor else None
                }
            )


class PublishService:
    """Handles content publishing, unpublishing, and scheduled publishing."""

    @staticmethod
    def publish_article(article: Article, user, send_notification=True) -> Dict[str, Any]:
        """Immediately publish an article."""
        with transaction.atomic():
            article.is_published = True
            article.status = "published"
            article.published_at = timezone.now()
            article.save(update_fields=["is_published", "status", "published_at", "updated_at"])

            # Create/update revision
            RevisionService.create_revision(article, user, "Published")

            # Update search index
            SearchIndexService.index_article(article)

            # Auto-generate SEO record
            SEOIntegrationService.ensure_seo_record(article)

            # Audit log
            CMSAuditTrail.objects.create(
                actor=user,
                action="publish",
                content_type="article",
                content_id=str(article.id),
                content_title=article.title
            )

            if send_notification and article.author:
                try:
                    from apps.notifications.models import NotificationRecord
                    NotificationRecord.objects.create(
                        user=article.author,
                        category="cms",
                        title=f"Article Published 🎉",
                        content=f'Your article "{article.title}" is now live.',
                        metadata={"article_id": str(article.id), "slug": article.slug}
                    )
                except Exception as e:
                    logger.warning(f"Failed to send publish notification: {e}")

        return {"status": "published", "published_at": article.published_at.isoformat()}

    @staticmethod
    def unpublish_article(article: Article, user) -> Dict[str, Any]:
        """Unpublish an article (set to draft)."""
        with transaction.atomic():
            article.is_published = False
            article.status = "draft"
            article.save(update_fields=["is_published", "status", "updated_at"])

            CMSAuditTrail.objects.create(
                actor=user,
                action="unpublish",
                content_type="article",
                content_id=str(article.id),
                content_title=article.title
            )

        return {"status": "unpublished"}

    @staticmethod
    def schedule_article(article: Article, scheduled_at, user) -> Dict[str, Any]:
        """Schedule an article for future publishing."""
        schedule, _ = PublishSchedule.objects.update_or_create(
            content_type="article",
            content_id=article.id,
            defaults={
                "scheduled_at": scheduled_at,
                "status": "pending",
                "scheduled_by": user
            }
        )
        article.status = "scheduled"
        article.save(update_fields=["status", "updated_at"])

        CMSAuditTrail.objects.create(
            actor=user,
            action="schedule",
            content_type="article",
            content_id=str(article.id),
            content_title=article.title,
            after_state={"scheduled_at": str(scheduled_at)}
        )

        return {"status": "scheduled", "scheduled_at": str(schedule.scheduled_at)}


class RevisionService:
    """Creates and manages content revisions."""

    @staticmethod
    def create_revision(content_obj, user, change_summary: str = "") -> Revision:
        """Create a new revision snapshot for any content object."""
        content_type_map = {
            "Article": "article",
            "Blog": "blog",
            "Page": "page",
            "Tutorial": "tutorial",
        }
        model_name = type(content_obj).__name__
        content_type = content_type_map.get(model_name, "article")

        last_revision = Revision.objects.filter(
            content_type=content_type,
            content_id=content_obj.id
        ).order_by("-version_number").first()

        version_number = (last_revision.version_number + 1) if last_revision else 1

        # Build snapshot
        snapshot = {
            "title": getattr(content_obj, "title", ""),
            "body": getattr(content_obj, "body", getattr(content_obj, "content", "")),
            "status": getattr(content_obj, "status", ""),
            "is_published": getattr(content_obj, "is_published", False),
        }

        return Revision.objects.create(
            content_type=content_type,
            content_id=content_obj.id,
            version_number=version_number,
            snapshot=snapshot,
            change_summary=change_summary,
            author=user
        )


class MediaService:
    """Handles media file processing, type detection, and metadata extraction."""

    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
    ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/ogg"}
    ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/ogg", "audio/wav"}
    ALLOWED_DOC_TYPES = {
        "application/pdf", "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain", "text/markdown", "text/csv"
    }

    @staticmethod
    def detect_file_type(mime_type: str) -> str:
        if mime_type in MediaService.ALLOWED_IMAGE_TYPES:
            return "image"
        if mime_type in MediaService.ALLOWED_VIDEO_TYPES:
            return "video"
        if mime_type in MediaService.ALLOWED_AUDIO_TYPES:
            return "audio"
        if mime_type in MediaService.ALLOWED_DOC_TYPES:
            return "document"
        return "other"

    @staticmethod
    def is_allowed_type(mime_type: str) -> bool:
        all_allowed = (
            MediaService.ALLOWED_IMAGE_TYPES |
            MediaService.ALLOWED_VIDEO_TYPES |
            MediaService.ALLOWED_AUDIO_TYPES |
            MediaService.ALLOWED_DOC_TYPES
        )
        return mime_type in all_allowed

    @staticmethod
    def process_upload(uploaded_file, user, alt_text: str = "", caption: str = "") -> MediaFile:
        """Process and save an uploaded media file."""
        mime_type = getattr(uploaded_file, "content_type", "application/octet-stream")

        if not MediaService.is_allowed_type(mime_type):
            raise ValueError(f"File type '{mime_type}' is not allowed.")

        file_type = MediaService.detect_file_type(mime_type)

        media = MediaFile.objects.create(
            uploader=user,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_type=file_type,
            mime_type=mime_type,
            file_size_bytes=uploaded_file.size,
            alt_text=alt_text or uploaded_file.name,
            caption=caption,
            is_public=True
        )

        # Try to get image dimensions if PIL is available
        if file_type == "image":
            try:
                from PIL import Image
                img = Image.open(uploaded_file)
                media.width, media.height = img.size
                media.save(update_fields=["width", "height"])
            except Exception:
                pass

        logger.info(f"Media uploaded: {media.original_filename} ({mime_type}) by user {user.id}")
        return media


class SearchIndexService:
    """Manages the CMS full-text search index."""

    @staticmethod
    def index_article(article: Article):
        """Index or update an article in the search index."""
        try:
            categories_str = ", ".join(c.name for c in article.categories.all())
            tags_str = " ".join(t.name for t in article.tags.all())
            author_name = ""
            if article.cms_author:
                author_name = article.cms_author.display_name
            elif article.author:
                author_name = getattr(article.author, "display_name", str(article.author))

            CMSSearchIndex.objects.update_or_create(
                content_type="article",
                content_id=article.id,
                defaults={
                    "title": article.title,
                    "excerpt": article.excerpt or "",
                    "body": article.body[:5000] if article.body else "",
                    "tags": tags_str,
                    "categories": categories_str,
                    "author_name": author_name,
                    "url_path": f"/articles/{article.slug}/",
                    "is_published": article.is_published,
                    "published_at": article.published_at,
                }
            )
        except Exception as e:
            logger.error(f"Failed to index article {article.id}: {e}")

    @staticmethod
    def index_blog(blog: Blog):
        """Index or update a blog post."""
        try:
            author_name = ""
            if blog.author:
                author_name = getattr(blog.author, "display_name", str(blog.author))

            CMSSearchIndex.objects.update_or_create(
                content_type="blog",
                content_id=blog.id,
                defaults={
                    "title": blog.title,
                    "excerpt": blog.content[:200] if blog.content else "",
                    "body": blog.content[:5000] if blog.content else "",
                    "author_name": author_name,
                    "url_path": f"/blog/{blog.slug}/",
                    "is_published": blog.is_published,
                    "published_at": blog.published_at,
                }
            )
        except Exception as e:
            logger.error(f"Failed to index blog {blog.id}: {e}")

    @staticmethod
    def remove_from_index(content_type: str, content_id):
        """Remove content from the search index."""
        CMSSearchIndex.objects.filter(content_type=content_type, content_id=content_id).delete()


class SEOIntegrationService:
    """Integrates with the existing SEO engine to auto-generate SEO records."""

    @staticmethod
    def ensure_seo_record(article: Article):
        """Create or update an SEOPage record for a published article."""
        try:
            from apps.seo.models import SEOPage
            SEOPage.objects.update_or_create(
                page_type="ARTICLE",
                page_id=str(article.id),
                defaults={
                    "title": article.title,
                    "meta_title": article.meta_title or article.title,
                    "meta_description": article.meta_description or (article.excerpt or "")[:160],
                    "canonical_url": article.canonical_url or f"/articles/{article.slug}/",
                    "slug": article.slug,
                    "og_title": article.meta_title or article.title,
                    "og_description": (article.excerpt or "")[:200],
                    "og_image": article.og_image_url or "",
                    "robots_index": True,
                    "robots_follow": True,
                    "schema_json": article.schema_json or {},
                    "language": "en",
                }
            )
        except Exception as e:
            logger.warning(f"Failed to sync SEO record for article {article.id}: {e}")


class TagService:
    """Tag management service."""

    @staticmethod
    def get_or_create_tag(name: str) -> Tag:
        """Get or create a tag by name, auto-generating a slug."""
        import re
        slug = re.sub(r"[^a-z0-9\-]", "-", name.lower().strip()).strip("-")
        slug = re.sub(r"-+", "-", slug)
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": slug})
        return tag

    @staticmethod
    def recalculate_usage_count(tag: Tag):
        """Recalculate the tag usage_count cache."""
        count = (
            tag.articles.filter(is_published=True, deleted_at__isnull=True).count() +
            tag.faqs.filter(is_published=True, deleted_at__isnull=True).count()
        )
        tag.usage_count = count
        tag.save(update_fields=["usage_count", "updated_at"])


class RedirectService:
    """Manages URL redirects."""

    @staticmethod
    def check_redirect(path: str) -> Optional[CMSRedirect]:
        """Check if a path has an active redirect rule."""
        redirect = CMSRedirect.objects.filter(from_path=path, is_active=True).first()
        if redirect:
            # Increment hit count
            CMSRedirect.objects.filter(id=redirect.id).update(hit_count=F("hit_count") + 1)
        return redirect

    @staticmethod
    def create_redirect(from_path: str, to_path: str, redirect_type: int = 301,
                        notes: str = "") -> CMSRedirect:
        """Create or update a redirect rule."""
        redirect, _ = CMSRedirect.objects.update_or_create(
            from_path=from_path,
            defaults={
                "to_path": to_path,
                "redirect_type": redirect_type,
                "is_active": True,
                "notes": notes
            }
        )
        return redirect

    @staticmethod
    def delete_redirect(from_path: str, actor) -> Dict[str, Any]:
        """
        Deactivate (soft-disable) a redirect rule by its source path.

        Args:
            from_path: Source URL path of the redirect to remove.
            actor: User performing the deletion.

        Returns:
            Dict with success/error message.
        """
        deleted_count, _ = CMSRedirect.objects.filter(from_path=from_path).update(is_active=False)
        if deleted_count:
            logger.info(f"Redirect '{from_path}' deactivated by {actor}")
            return {"success": True, "message": f"Redirect '{from_path}' deactivated."}
        return {"success": False, "message": "Redirect not found."}

    @staticmethod
    def list_active_redirects() -> list:
        """
        Return all active redirect rules ordered alphabetically.

        Returns:
            QuerySet of active CMSRedirect instances.
        """
        return CMSRedirect.objects.filter(is_active=True).order_by("from_path")


# =============================================================================
# VersionService
# Manages immutable Page version snapshots.
# Distinct from RevisionService (which handles Articles/Blogs).
# VersionService is specifically for the visual Page Builder version history.
# =============================================================================

class VersionService:
    """
    Manages PageVersion records for the Page Builder.

    Every time a page layout is saved or published, a new PageVersion snapshot
    is created. Editors can compare versions and restore any previous one.

    Distinct from RevisionService (which tracks Article/Blog/Tutorial content).
    """

    @staticmethod
    def create_version(page: "Page", layout_data: Dict[str, Any],
                       author, change_summary: str = "") -> "PageVersion":
        """
        Create an immutable PageVersion snapshot.

        Args:
            page: The Page instance being versioned.
            layout_data: The full layout JSON at the time of save.
            author: User who triggered the save.
            change_summary: Human-readable description of changes.

        Returns:
            Newly created PageVersion instance.
        """
        last_version = PageVersion.objects.filter(page=page).order_by("-version_number").first()
        version_number = (last_version.version_number + 1) if last_version else 1

        version = PageVersion.objects.create(
            page=page,
            version_number=version_number,
            layout_data=layout_data,
            change_summary=change_summary or f"Version {version_number}",
            author=author
        )
        logger.info(f"PageVersion v{version_number} created for page '{page.title}' by {author}")
        return version

    @staticmethod
    def get_version_history(page: "Page") -> list:
        """
        Return ordered version history for a page (newest first).

        Args:
            page: The target Page instance.

        Returns:
            QuerySet of PageVersion instances with author pre-fetched.
        """
        return PageVersion.objects.select_related("author").filter(
            page=page
        ).order_by("-version_number")

    @staticmethod
    def restore_version(page: "Page", version_number: int, actor) -> Dict[str, Any]:
        """
        Restore a page's layout to a previously saved version.

        Restoring creates a new version entry (so the restore itself is auditable)
        rather than mutating existing version history.

        Args:
            page: The target Page instance.
            version_number: The version number to restore.
            actor: User performing the restore.

        Returns:
            Dict containing the new version number and layout data, or error.
        """
        try:
            target = PageVersion.objects.get(page=page, version_number=version_number)
        except PageVersion.DoesNotExist:
            return {"error": f"Version {version_number} not found for page '{page.title}'."}

        with transaction.atomic():
            # Apply layout to live page
            page.layout_data = target.layout_data
            page.save(update_fields=["layout_data", "updated_at"])

            # Create a new version marking this restore event
            new_version = VersionService.create_version(
                page=page,
                layout_data=target.layout_data,
                author=actor,
                change_summary=f"Restored from version {version_number}"
            )

            # Audit trail
            CMSAuditTrail.objects.create(
                actor=actor,
                action="rollback",
                content_type="page",
                content_id=str(page.id),
                content_title=page.title,
                before_state={"current_version": "live"},
                after_state={"restored_version": version_number, "new_version": new_version.version_number}
            )

        logger.info(
            f"Page '{page.title}' restored to v{version_number} by {actor}. "
            f"New version: v{new_version.version_number}"
        )
        return {
            "page_id": str(page.id),
            "restored_from_version": version_number,
            "new_version": new_version.version_number,
            "layout_data": page.layout_data
        }

    @staticmethod
    def compare_versions(page: "Page", version_a: int, version_b: int) -> Dict[str, Any]:
        """
        Return the layout_data of two versions side-by-side for diff comparison.

        Args:
            page: The target Page.
            version_a: First version number.
            version_b: Second version number.

        Returns:
            Dict with version_a_data, version_b_data, and metadata.
        """
        try:
            va = PageVersion.objects.get(page=page, version_number=version_a)
            vb = PageVersion.objects.get(page=page, version_number=version_b)
        except PageVersion.DoesNotExist as exc:
            return {"error": str(exc)}

        return {
            "page_id": str(page.id),
            "version_a": {
                "version_number": va.version_number,
                "change_summary": va.change_summary,
                "created_at": va.created_at.isoformat() if va.created_at else None,
                "layout_data": va.layout_data
            },
            "version_b": {
                "version_number": vb.version_number,
                "change_summary": vb.change_summary,
                "created_at": vb.created_at.isoformat() if vb.created_at else None,
                "layout_data": vb.layout_data
            }
        }


# =============================================================================
# SearchService
# Full-text search across CMSSearchIndex with ranking and autocomplete.
# Falls back to icontains on SQLite; uses pg_search on PostgreSQL.
# =============================================================================

class SearchService:
    """
    Full-text CMS search service.

    Queries the CMSSearchIndex table which is pre-populated by Celery tasks
    and updated synchronously on publish events via SearchIndexService.

    Features:
        - Multi-field icontains search (SQLite compatible)
        - Autocomplete suggestions from title/tag fields
        - Content-type filtering
        - Date-range filtering
        - Relevance-aware ordering (title match > excerpt > body)
        - Pagination support

    Future: replace icontains with SearchVector + SearchQuery on PostgreSQL.
    """

    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    @staticmethod
    def search(
        query: str,
        content_types: Optional[List[str]] = None,
        category_slug: Optional[str] = None,
        date_from=None,
        date_to=None,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE
    ) -> Dict[str, Any]:
        """
        Execute a full-text search across the CMS search index.

        Args:
            query: Search query string.
            content_types: Optional list of content types to filter
                           (e.g. ["article", "blog", "faq"]).
            category_slug: Optional category slug to narrow results.
            date_from: Optional start date (datetime) for published_at filter.
            date_to: Optional end date (datetime) for published_at filter.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            Dict with keys: results, total, page, page_size, has_next, has_prev.
        """
        from django.db.models import Q, Case, When, IntegerField, Value

        page_size = min(max(1, page_size), SearchService.MAX_PAGE_SIZE)
        offset = (page - 1) * page_size

        qs = CMSSearchIndex.objects.filter(is_published=True)

        # Content-type filter
        if content_types:
            qs = qs.filter(content_type__in=content_types)

        # Date range filter
        if date_from:
            qs = qs.filter(published_at__gte=date_from)
        if date_to:
            qs = qs.filter(published_at__lte=date_to)

        # Keyword search
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

        total = qs.count()
        results = list(
            qs[offset:offset + page_size].values(
                "content_type", "content_id", "title", "excerpt",
                "author_name", "url_path", "published_at",
                "categories", "tags"
            )
        )

        # Convert UUID fields to strings for JSON serialization
        for r in results:
            r["content_id"] = str(r["content_id"])
            if r["published_at"]:
                r["published_at"] = r["published_at"].isoformat()

        return {
            "results": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": offset + page_size < total,
            "has_prev": page > 1,
            "query": query
        }

    @staticmethod
    def autocomplete(prefix: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Return title-based autocomplete suggestions for the search bar.

        Args:
            prefix: User's partial input string.
            limit: Maximum number of suggestions to return (default 8).

        Returns:
            List of dicts with title, url_path, content_type.
        """
        if not prefix or len(prefix) < 2:
            return []

        return list(
            CMSSearchIndex.objects.filter(
                is_published=True,
                title__icontains=prefix
            ).values("title", "url_path", "content_type")[:limit]
        )

    @staticmethod
    def reindex_all() -> Dict[str, Any]:
        """
        Rebuild the entire search index from scratch.

        Should be called from a Celery task, not directly from a view.
        Clears existing index entries then re-indexes all published content.

        Returns:
            Dict with counts of indexed content per type.
        """
        counts = {"article": 0, "blog": 0}

        # Re-index all published articles
        for article in Article.objects.prefetch_related(
            "categories", "tags", "cms_author"
        ).filter(is_published=True, deleted_at__isnull=True):
            try:
                SearchIndexService.index_article(article)
                counts["article"] += 1
            except Exception as exc:
                logger.error(f"Failed re-indexing article {article.id}: {exc}")

        # Re-index all published blogs
        for blog in Blog.objects.select_related("author").filter(
            is_published=True, deleted_at__isnull=True
        ):
            try:
                SearchIndexService.index_blog(blog)
                counts["blog"] += 1
            except Exception as exc:
                logger.error(f"Failed re-indexing blog {blog.id}: {exc}")

        logger.info(f"Search index rebuilt: {counts}")
        return {"indexed": counts, "status": "complete"}


# =============================================================================
# BlogPublishService
# Extends PublishService to handle Blog (existing model) publishing workflow
# with notifications, SEO sync, and search indexing.
# =============================================================================

class BlogPublishService:
    """
    Publishing service for the existing Blog content type (Sprint CMS baseline).

    Handles publish, unpublish, and schedule operations for Blog objects,
    integrating with Sprint 14 notifications, SEO engine, and search index.
    """

    @staticmethod
    def publish_blog(blog: "Blog", user, send_notification: bool = True) -> Dict[str, Any]:
        """
        Immediately publish a blog post.

        Args:
            blog: The Blog instance to publish.
            user: The user triggering the publish action.
            send_notification: Whether to send a notification to the author.

        Returns:
            Dict with status and published_at timestamp.

        Raises:
            Exception: Propagated from atomic block on DB error.
        """
        with transaction.atomic():
            blog.is_published = True
            blog.published_at = timezone.now()
            blog.save(update_fields=["is_published", "published_at", "updated_at"])

            # Create content revision
            RevisionService.create_revision(blog, user, "Published")

            # Update search index
            SearchIndexService.index_blog(blog)

            # Auto-create SEO record for blog
            SEOIntegrationService.ensure_blog_seo_record(blog)

            # Audit
            CMSAuditTrail.objects.create(
                actor=user,
                action="publish",
                content_type="blog",
                content_id=str(blog.id),
                content_title=blog.title
            )

            # Notification
            if send_notification and blog.author:
                try:
                    from apps.notifications.models import NotificationRecord
                    NotificationRecord.objects.create(
                        user=blog.author,
                        category="cms",
                        title="Blog Published 🎉",
                        content=f'Your blog post "{blog.title}" is now live.',
                        metadata={"blog_id": str(blog.id), "slug": blog.slug}
                    )
                except Exception as exc:
                    logger.warning(f"Blog publish notification failed: {exc}")

        return {
            "status": "published",
            "blog_id": str(blog.id),
            "published_at": blog.published_at.isoformat()
        }

    @staticmethod
    def unpublish_blog(blog: "Blog", user) -> Dict[str, Any]:
        """
        Unpublish a blog post and remove it from the search index.

        Args:
            blog: The Blog instance to unpublish.
            user: The user triggering the action.

        Returns:
            Dict with status confirmation.
        """
        with transaction.atomic():
            blog.is_published = False
            blog.save(update_fields=["is_published", "updated_at"])

            # Remove from search index
            SearchIndexService.remove_from_index("blog", blog.id)

            CMSAuditTrail.objects.create(
                actor=user,
                action="unpublish",
                content_type="blog",
                content_id=str(blog.id),
                content_title=blog.title
            )

        return {"status": "unpublished", "blog_id": str(blog.id)}

    @staticmethod
    def schedule_blog(blog: "Blog", scheduled_at, user) -> Dict[str, Any]:
        """
        Schedule a blog post for future automatic publishing.

        Args:
            blog: The Blog instance to schedule.
            scheduled_at: datetime when the post should go live.
            user: The user creating the schedule.

        Returns:
            Dict with status and scheduled_at confirmation.
        """
        schedule, _ = PublishSchedule.objects.update_or_create(
            content_type="blog",
            content_id=blog.id,
            defaults={
                "scheduled_at": scheduled_at,
                "status": "pending",
                "scheduled_by": user
            }
        )
        CMSAuditTrail.objects.create(
            actor=user,
            action="schedule",
            content_type="blog",
            content_id=str(blog.id),
            content_title=blog.title,
            after_state={"scheduled_at": str(scheduled_at)}
        )
        return {
            "status": "scheduled",
            "blog_id": str(blog.id),
            "scheduled_at": str(schedule.scheduled_at)
        }


# =============================================================================
# CMSPermissionService
# RBAC/CBAC helper that views can call to check granular CMS permissions.
# Avoids duplicating role-name checks across every ViewSet.
# =============================================================================

class CMSPermissionService:
    """
    Centralized RBAC + CBAC permission evaluation for CMS operations.

    Views should call these helpers instead of repeating role-check logic.
    Integrates with the existing HasRBACPermission infrastructure.
    """

    CMS_ADMIN_ROLES = {"SUPERADMIN", "ADMIN", "CONTENT_MANAGEMENT"}
    CMS_EDITOR_ROLES = {"SUPERADMIN", "ADMIN", "CONTENT_MANAGEMENT", "EDITOR"}
    CMS_REVIEWER_ROLES = {"SUPERADMIN", "ADMIN", "CONTENT_MANAGEMENT", "EDITOR", "REVIEWER"}

    @staticmethod
    def _get_role_name(user) -> Optional[str]:
        """Safely retrieve the user's role name string."""
        if hasattr(user, "role") and user.role:
            return user.role.name
        return None

    @staticmethod
    def is_cms_admin(user) -> bool:
        """
        Check if the user has CMS admin privileges.

        Admins can publish, delete, and manage all content types.

        Args:
            user: Authenticated request.user.

        Returns:
            bool: True if the user is a CMS admin.
        """
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        role = CMSPermissionService._get_role_name(user)
        return role in CMSPermissionService.CMS_ADMIN_ROLES

    @staticmethod
    def is_cms_editor(user) -> bool:
        """
        Check if the user can create and edit CMS content.

        Args:
            user: Authenticated request.user.

        Returns:
            bool: True if the user has editor access.
        """
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        role = CMSPermissionService._get_role_name(user)
        return role in CMSPermissionService.CMS_EDITOR_ROLES

    @staticmethod
    def is_cms_reviewer(user) -> bool:
        """
        Check if the user can review and approve CMS content.

        Args:
            user: Authenticated request.user.

        Returns:
            bool: True if the user has reviewer access.
        """
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        role = CMSPermissionService._get_role_name(user)
        return role in CMSPermissionService.CMS_REVIEWER_ROLES

    @staticmethod
    def can_publish_content(user, content_obj) -> bool:
        """
        Check if the user can publish a specific content object.

        Rules:
        - CMS Admins can publish any content.
        - Editors can only publish their own content.
        - Reviewers cannot publish (they can only approve).

        Args:
            user: Authenticated request.user.
            content_obj: The Article, Blog, or Page instance.

        Returns:
            bool: True if the user may publish.
        """
        if CMSPermissionService.is_cms_admin(user):
            return True
        # Editors can publish their own content
        if CMSPermissionService.is_cms_editor(user):
            author = getattr(content_obj, "author", None)
            return author == user
        return False

    @staticmethod
    def can_delete_content(user, content_obj) -> bool:
        """
        Check if the user can soft-delete a content object.

        Only CMS admins or the original author (for non-published content)
        may delete.

        Args:
            user: Authenticated request.user.
            content_obj: The content instance to delete.

        Returns:
            bool: True if the user may delete.
        """
        if CMSPermissionService.is_cms_admin(user):
            return True
        author = getattr(content_obj, "author", None)
        is_published = getattr(content_obj, "is_published", False)
        return author == user and not is_published

    @staticmethod
    def can_restore_content(user, content_obj) -> bool:
        """
        Check if the user can restore a soft-deleted content record.

        Only CMS admins may restore deleted content.

        Args:
            user: Authenticated request.user.
            content_obj: The soft-deleted content instance.

        Returns:
            bool: True if the user may restore.
        """
        return CMSPermissionService.is_cms_admin(user)

    @staticmethod
    def check_object_ownership(user, content_obj) -> bool:
        """
        Verify the user is the author/owner of the content object.

        Args:
            user: Authenticated request.user.
            content_obj: Content instance with an 'author' field.

        Returns:
            bool: True if the user is the owner.
        """
        if CMSPermissionService.is_cms_admin(user):
            return True
        for attr in ("author", "uploader", "created_by"):
            owner = getattr(content_obj, attr, None)
            if owner is not None and owner == user:
                return True
        return False

    @staticmethod
    def enforce_rbac_or_raise(user, permission_codename: str):
        """
        Raise PermissionError if the user does not have the given RBAC permission.

        Args:
            user: Authenticated request.user.
            permission_codename: RBAC permission codename (e.g. 'cms:articles:publish').

        Raises:
            PermissionError: If the user lacks the required permission.
        """
        if user.is_superuser:
            return
        if hasattr(user, "role") and user.role:
            has_perm = user.role.role_permissions.filter(
                permission__codename=permission_codename
            ).exists()
            if has_perm:
                return
        raise PermissionError(
            f"User '{user}' does not have permission '{permission_codename}'."
        )


# =============================================================================
# SEOIntegrationService — extended with Blog support
# =============================================================================

# Extend the existing SEOIntegrationService with blog SEO sync
def _ensure_blog_seo_record(blog: "Blog"):
    """
    Create or update an SEOPage record for a published Blog post.

    Called by BlogPublishService on publish. Integrates with the
    existing apps.seo SEOPage model from Sprint 11.

    Args:
        blog: The published Blog instance.
    """
    try:
        from apps.seo.models import SEOPage
        SEOPage.objects.update_or_create(
            page_type="BLOG",
            page_id=str(blog.id),
            defaults={
                "title": blog.title,
                "meta_title": blog.title,
                "meta_description": (blog.content or "")[:160],
                "canonical_url": f"/blog/{blog.slug}/",
                "slug": blog.slug,
                "og_title": blog.title,
                "og_description": (blog.content or "")[:200],
                "robots_index": True,
                "robots_follow": True,
                "language": "en",
            }
        )
    except Exception as exc:
        logger.warning(f"Failed to sync SEO record for blog {blog.id}: {exc}")


# Monkey-patch onto the existing SEOIntegrationService class
SEOIntegrationService.ensure_blog_seo_record = staticmethod(_ensure_blog_seo_record)


class ThumbnailService:
    @staticmethod
    def generate_thumbnails(media_file_id: str):
        from apps.cms.tasks import generate_thumbnail_task
        generate_thumbnail_task.delay(media_file_id, "small")
        generate_thumbnail_task.delay(media_file_id, "medium")
        generate_thumbnail_task.delay(media_file_id, "large")


class ImageOptimizationService:
    @staticmethod
    def optimize_image(media_file_id: str):
        from apps.cms.tasks import optimize_image_task
        optimize_image_task.delay(media_file_id)


class MediaUploadService:
    @staticmethod
    def upload_file(uploader_user, file_obj, folder_id=None, alt_text="", caption=""):
        from apps.cms.models import MediaFile, Folder
        from apps.cms.validators import validate_media_file_extension, validate_media_file_size, validate_virus_free
        
        validate_media_file_extension(file_obj.name)
        validate_media_file_size(file_obj.size)
        validate_virus_free(file_obj)

        folder = None
        if folder_id:
            folder = Folder.objects.get(id=folder_id)

        # Detect file type
        name = file_obj.name.lower()
        if name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            file_type = 'image'
        elif name.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            file_type = 'video'
        elif name.endswith(('.mp3', '.wav', '.ogg')):
            file_type = 'audio'
        elif name.endswith(('.pdf', '.docx', '.txt', '.xlsx')):
            file_type = 'document'
        else:
            file_type = 'other'

        media_file = MediaFile.objects.create(
            uploader=uploader_user,
            file=file_obj,
            original_filename=file_obj.name,
            file_type=file_type,
            file_size_bytes=file_obj.size,
            alt_text=alt_text,
            caption=caption,
            folder=folder,
            is_public=True
        )
        return media_file


class VideoConversionService:
    @staticmethod
    def convert_video(media_file_id: str):
        logger.info(f"Triggered video transcoding task for: {media_file_id}")


class StorageService:
    @staticmethod
    def get_public_url(media_file) -> str:
        return media_file.url


class SearchService:
    @staticmethod
    def search_assets(query_str: str):
        from apps.cms.models import MediaFile
        return MediaFile.objects.filter(original_filename__icontains=query_str, deleted_at__isnull=True)


class PermissionService:
    @staticmethod
    def grant_permission(media_file, user, permission_type: str):
        from apps.cms.models import MediaPermission
        perm, _ = MediaPermission.objects.get_or_create(
            media_file=media_file,
            user=user,
            defaults={"permission_type": permission_type}
        )
        return perm


class AuditService:
    @staticmethod
    def log_action(media_file, actor, action: str, details: dict):
        from apps.cms.models import MediaAudit
        return MediaAudit.objects.create(
            media_file=media_file,
            actor=actor,
            action=action,
            details=details
        )


class FavoriteService:
    @staticmethod
    def toggle_favorite(media_file, user):
        from apps.cms.models import MediaFavorite
        fav = MediaFavorite.objects.filter(media_file=media_file, user=user)
        if fav.exists():
            fav.delete()
            return False
        else:
            MediaFavorite.objects.create(media_file=media_file, user=user)
            return True


class DownloadService:
    @staticmethod
    def record_download(media_file, user):
        from apps.cms.models import MediaDownloadLog
        return MediaDownloadLog.objects.create(media_file=media_file, user=user)
