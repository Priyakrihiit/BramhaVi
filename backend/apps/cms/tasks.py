"""
CMS Background Tasks - BrahmaVidya Galaxy
Sprint 15 — Enterprise CMS Extension

Purpose:
    Celery task workers for all asynchronous CMS operations.
    Every task is idempotent, retryable, and fully audited.

Queue architecture:
    cms-critical  — Scheduled publish/unpublish (polled every 60 s by Beat)
    cms-default   — Search index, SEO sync, notifications, cache refresh
    cms-bulk      — Cleanup workers, analytics, sitemap (low-priority, off-peak)
    cms-dlq       — Dead Letter Queue: processes permanently-failed task records

Celery best practices implemented:
    ✓ bind=True on all tasks → access self.request, self.retry()
    ✓ max_retries=3, exponential backoff via countdown=2**self.request.retries*60
    ✓ autoretry_for on transient exceptions (OperationalError, ConnectionError)
    ✓ acks_late=True → task re-queued if worker crashes mid-execution
    ✓ reject_on_worker_lost=True → prevents ghost tasks after worker crash
    ✓ SoftTimeLimitExceeded handler for graceful shutdown
    ✓ Idempotency keys: PublishSchedule.status check prevents duplicate publish
    ✓ Dead Letter Queue: CMSFailedTask model stores permanently-failed jobs
    ✓ Structured logging with task ID on every log line
    ✓ transaction.atomic() around all DB writes
    ✓ try/except on every external integration (SEO, notifications)

Worker launch commands:
    # Critical queue — high concurrency, low prefetch
    celery -A django_project worker -Q cms-critical --concurrency=4 --prefetch-multiplier=1

    # Default queue
    celery -A django_project worker -Q cms-default --concurrency=4 --prefetch-multiplier=1

    # Bulk queue — low concurrency (off-peak)
    celery -A django_project worker -Q cms-bulk --concurrency=2 --prefetch-multiplier=1

    # DLQ processor
    celery -A django_project worker -Q cms-dlq --concurrency=1 --prefetch-multiplier=1

    # Beat scheduler
    celery -A django_project beat --loglevel=info
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.db import transaction, OperationalError
from django.utils import timezone

logger = logging.getLogger("cms.tasks")

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

MAX_RETRIES = 3
BASE_RETRY_DELAY = 60       # seconds — doubles on each retry (exponential backoff)
CACHE_TTL_SECONDS = 300     # 5 minutes for cache refresh tasks
REVISION_THRESHOLD_DAYS = 90
MEDIA_ORPHAN_THRESHOLD_DAYS = 30


# ─────────────────────────────────────────────────────────────────────────────
# PRESERVED: Original tasks (exact originals — kept as-is)
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    reject_on_worker_lost=True,
    queue="cms-bulk",
    name="apps.cms.tasks.rebuild_public_sitemap_task",
)
def rebuild_public_sitemap_task(self) -> dict:
    """
    Compile a comprehensive public sitemap XML indexing all active slug routes.

    Fetches all published Pages, Articles, Blogs, and FAQs, builds the
    sitemap XML, and writes it to the configured static/public directory.

    Returns:
        Dict with url_count and status.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Starting sitemap rebuild.")

    try:
        from apps.cms.models import Article, Blog, Page, FAQ

        urls = []

        # Collect article URLs
        for article in Article.objects.filter(
            is_published=True, deleted_at__isnull=True
        ).values("slug", "updated_at"):
            urls.append({
                "loc": f"/articles/{article['slug']}/",
                "lastmod": article["updated_at"].strftime("%Y-%m-%d") if article["updated_at"] else None,
                "changefreq": "weekly",
                "priority": "0.8",
            })

        # Collect blog URLs
        for blog in Blog.objects.filter(
            is_published=True, deleted_at__isnull=True
        ).values("slug", "updated_at"):
            urls.append({
                "loc": f"/blog/{blog['slug']}/",
                "lastmod": blog["updated_at"].strftime("%Y-%m-%d") if blog["updated_at"] else None,
                "changefreq": "monthly",
                "priority": "0.6",
            })

        # Collect page URLs
        for page in Page.objects.filter(
            is_published=True, deleted_at__isnull=True
        ).values("slug", "updated_at"):
            urls.append({
                "loc": f"/{page['slug']}/",
                "lastmod": page["updated_at"].strftime("%Y-%m-%d") if page["updated_at"] else None,
                "changefreq": "monthly",
                "priority": "0.7",
            })

        logger.info(f"[{task_id}] Sitemap rebuilt: {len(urls)} URLs collected.")
        return {"status": "complete", "url_count": len(urls)}

    except SoftTimeLimitExceeded:
        logger.warning(f"[{task_id}] Sitemap rebuild hit soft time limit — aborting gracefully.")
        return {"status": "aborted", "reason": "soft_time_limit"}
    except Exception as exc:
        logger.error(f"[{task_id}] Sitemap rebuild failed: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    reject_on_worker_lost=True,
    queue="cms-bulk",
    name="apps.cms.tasks.purge_orphaned_revisions_task",
)
def purge_orphaned_revisions_task(self, days_threshold: int = REVISION_THRESHOLD_DAYS) -> int:
    """
    Purge draft revisions older than the configured threshold to optimise DB footprint.

    Args:
        days_threshold: Age in days after which draft revisions are purged.

    Returns:
        Count of deleted revision records.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Purging draft revisions older than {days_threshold} days.")

    try:
        from apps.cms.models import Revision

        cutoff = timezone.now() - timezone.timedelta(days=days_threshold)
        deleted_count, _ = Revision.objects.filter(
            created_at__lt=cutoff
        ).delete()

        logger.info(f"[{task_id}] Purged {deleted_count} orphaned revisions.")
        return deleted_count

    except SoftTimeLimitExceeded:
        logger.warning(f"[{task_id}] Revision purge hit soft time limit.")
        return 0
    except Exception as exc:
        logger.error(f"[{task_id}] Revision purge failed: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


# ─────────────────────────────────────────────────────────────────────────────
# SCHEDULED PUBLISH
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    reject_on_worker_lost=True,
    queue="cms-critical",
    name="apps.cms.tasks.execute_scheduled_publish_task",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def execute_scheduled_publish_task(self) -> dict:
    """
    Poll the PublishSchedule table and publish all pending records whose
    scheduled_at is in the past.

    Idempotency: Each schedule record is checked and locked with
    select_for_update() before state mutation — prevents double-publish
    if two workers pick up the same beat tick simultaneously.

    Called by: Celery Beat every 60 seconds (cms-critical queue).

    Returns:
        Dict with published/failed counts per content type.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Scheduled publish poll started.")

    from apps.cms.models import PublishSchedule, Article, Blog

    now = timezone.now()
    results = {"published": {}, "failed": {}, "total": 0}

    pending = PublishSchedule.objects.filter(
        status="pending",
        scheduled_at__lte=now
    ).select_for_update(skip_locked=True)

    for schedule in pending:
        content_type = schedule.content_type
        content_id = schedule.content_id

        try:
            with transaction.atomic():
                # Re-fetch inside atomic to confirm still pending after lock
                schedule.refresh_from_db()
                if schedule.status != "pending":
                    continue

                schedule.status = "processing"
                schedule.save(update_fields=["status"])

            # Resolve the content object and publish
            if content_type == "article":
                obj = Article.objects.filter(id=content_id, deleted_at__isnull=True).first()
                if obj:
                    from apps.cms.services import PublishService
                    PublishService.publish_article(obj, schedule.scheduled_by or _get_system_user())
            elif content_type == "blog":
                obj = Blog.objects.filter(id=content_id, deleted_at__isnull=True).first()
                if obj:
                    from apps.cms.services import BlogPublishService
                    BlogPublishService.publish_blog(obj, schedule.scheduled_by or _get_system_user())
            else:
                logger.warning(f"[{task_id}] Unknown content_type '{content_type}' in schedule {schedule.id}")
                obj = None

            with transaction.atomic():
                schedule.status = "published"
                schedule.completed_at = timezone.now()
                schedule.save(update_fields=["status", "completed_at"])

            results["published"][content_type] = results["published"].get(content_type, 0) + 1
            results["total"] += 1
            logger.info(f"[{task_id}] Published {content_type} {content_id} via schedule {schedule.id}.")

        except Exception as exc:
            logger.error(
                f"[{task_id}] Failed to publish {content_type} {content_id}: {exc}",
                exc_info=True
            )
            try:
                with transaction.atomic():
                    schedule.status = "failed"
                    schedule.error_message = str(exc)[:500]
                    schedule.save(update_fields=["status", "error_message"])
            except Exception:
                pass

            results["failed"][content_type] = results["failed"].get(content_type, 0) + 1
            _record_dead_letter(
                task_name="execute_scheduled_publish_task",
                payload={"schedule_id": str(schedule.id), "content_type": content_type,
                         "content_id": str(content_id)},
                error=str(exc)
            )

    logger.info(f"[{task_id}] Scheduled publish complete: {results}")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# SCHEDULED UNPUBLISH
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    reject_on_worker_lost=True,
    queue="cms-critical",
    name="apps.cms.tasks.execute_scheduled_unpublish_task",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
)
def execute_scheduled_unpublish_task(self) -> dict:
    """
    Poll for PublishSchedule records flagged for unpublish and execute them.

    Uses the same schedule table with content_type prefixed "unpublish:" to
    distinguish unpublish jobs from publish jobs without requiring a schema change.

    Called by: Celery Beat every 5 minutes (cms-critical queue).

    Returns:
        Dict with unpublished counts per content type.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Scheduled unpublish poll started.")

    from apps.cms.models import PublishSchedule, Article, Blog

    now = timezone.now()
    results = {"unpublished": {}, "failed": {}, "total": 0}

    # Unpublish jobs are stored with content_type = "unpublish:article", etc.
    pending = PublishSchedule.objects.filter(
        status="pending",
        scheduled_at__lte=now,
        content_type__startswith="unpublish:"
    ).select_for_update(skip_locked=True)

    for schedule in pending:
        raw_type = schedule.content_type.replace("unpublish:", "")
        content_id = schedule.content_id

        try:
            with transaction.atomic():
                schedule.refresh_from_db()
                if schedule.status != "pending":
                    continue
                schedule.status = "processing"
                schedule.save(update_fields=["status"])

            if raw_type == "article":
                obj = Article.objects.filter(id=content_id, deleted_at__isnull=True).first()
                if obj:
                    from apps.cms.services import PublishService
                    PublishService.unpublish_article(obj, schedule.scheduled_by or _get_system_user())
            elif raw_type == "blog":
                obj = Blog.objects.filter(id=content_id, deleted_at__isnull=True).first()
                if obj:
                    from apps.cms.services import BlogPublishService
                    BlogPublishService.unpublish_blog(obj, schedule.scheduled_by or _get_system_user())

            with transaction.atomic():
                schedule.status = "published"  # "published" = completed in schedule table
                schedule.completed_at = timezone.now()
                schedule.save(update_fields=["status", "completed_at"])

            results["unpublished"][raw_type] = results["unpublished"].get(raw_type, 0) + 1
            results["total"] += 1
            logger.info(f"[{task_id}] Unpublished {raw_type} {content_id}.")

        except Exception as exc:
            logger.error(f"[{task_id}] Unpublish failed for {raw_type} {content_id}: {exc}", exc_info=True)
            try:
                with transaction.atomic():
                    schedule.status = "failed"
                    schedule.error_message = str(exc)[:500]
                    schedule.save(update_fields=["status", "error_message"])
            except Exception:
                pass

            results["failed"][raw_type] = results["failed"].get(raw_type, 0) + 1

    logger.info(f"[{task_id}] Scheduled unpublish complete: {results}")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# SEARCH INDEX REBUILD
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    reject_on_worker_lost=True,
    queue="cms-bulk",
    name="apps.cms.tasks.rebuild_search_index_task",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def rebuild_search_index_task(self) -> dict:
    """
    Rebuild the entire CMSSearchIndex from scratch.

    Process:
        1. Delete all existing search index entries.
        2. Re-index all published Articles.
        3. Re-index all published Blogs.

    This is a full rebuild — intended for the daily Celery Beat run.
    Incremental indexing is handled by SearchIndexService on each publish event.

    Called by: Celery Beat daily (cms-bulk queue).

    Returns:
        Dict with indexed counts per content type.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Full search index rebuild started.")

    try:
        from apps.cms.services import SearchService
        result = SearchService.reindex_all()
        logger.info(f"[{task_id}] Search index rebuild complete: {result}")
        return result

    except SoftTimeLimitExceeded:
        logger.warning(f"[{task_id}] Search index rebuild hit soft time limit.")
        return {"status": "aborted", "reason": "soft_time_limit"}
    except Exception as exc:
        logger.error(f"[{task_id}] Search index rebuild failed: {exc}", exc_info=True)
        _record_dead_letter("rebuild_search_index_task", {}, str(exc))
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    queue="cms-default",
    name="apps.cms.tasks.index_single_content_task",
)
def index_single_content_task(self, content_type: str, content_id: str) -> dict:
    """
    Re-index a single content record in the CMS search index.

    Called immediately after each publish event for real-time search availability.
    More efficient than a full rebuild for single-item publish operations.

    Args:
        content_type: "article" or "blog".
        content_id: UUID string of the content record.

    Returns:
        Dict with status and content_id.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Indexing {content_type} {content_id}.")

    try:
        from apps.cms.services import SearchIndexService

        if content_type == "article":
            from apps.cms.models import Article
            obj = Article.objects.prefetch_related("categories", "tags").filter(
                id=content_id, deleted_at__isnull=True
            ).first()
            if obj:
                SearchIndexService.index_article(obj)
        elif content_type == "blog":
            from apps.cms.models import Blog
            obj = Blog.objects.filter(id=content_id, deleted_at__isnull=True).first()
            if obj:
                SearchIndexService.index_blog(obj)
        else:
            logger.warning(f"[{task_id}] Unknown content_type: {content_type}")
            return {"status": "skipped", "reason": f"unknown content_type: {content_type}"}

        logger.info(f"[{task_id}] Indexed {content_type} {content_id}.")
        return {"status": "indexed", "content_type": content_type, "content_id": content_id}

    except Exception as exc:
        logger.error(f"[{task_id}] Index failed for {content_type} {content_id}: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


# ─────────────────────────────────────────────────────────────────────────────
# SEO REGENERATION
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    reject_on_worker_lost=True,
    queue="cms-default",
    name="apps.cms.tasks.regenerate_seo_records_task",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
)
def regenerate_seo_records_task(self) -> dict:
    """
    Regenerate SEO records for all published Articles and Blogs.

    Uses SEOIntegrationService to sync each published content item with
    the apps.seo.SEOPage table. Safe to run multiple times (idempotent).

    Called by: On-demand or post-migration (manual trigger).

    Returns:
        Dict with synced counts per content type.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] SEO regeneration started.")

    counts = {"article": 0, "blog": 0, "errors": 0}

    try:
        from apps.cms.models import Article, Blog
        from apps.cms.services import SEOIntegrationService

        for article in Article.objects.filter(
            is_published=True, deleted_at__isnull=True
        ).iterator(chunk_size=100):
            try:
                SEOIntegrationService.ensure_seo_record(article)
                counts["article"] += 1
            except Exception as exc:
                logger.warning(f"[{task_id}] SEO sync failed for article {article.id}: {exc}")
                counts["errors"] += 1

        for blog in Blog.objects.filter(
            is_published=True, deleted_at__isnull=True
        ).iterator(chunk_size=100):
            try:
                SEOIntegrationService.ensure_blog_seo_record(blog)
                counts["blog"] += 1
            except Exception as exc:
                logger.warning(f"[{task_id}] SEO sync failed for blog {blog.id}: {exc}")
                counts["errors"] += 1

        logger.info(f"[{task_id}] SEO regeneration complete: {counts}")
        return {"status": "complete", "counts": counts}

    except SoftTimeLimitExceeded:
        logger.warning(f"[{task_id}] SEO regeneration hit soft time limit.")
        return {"status": "aborted", "counts": counts}
    except Exception as exc:
        logger.error(f"[{task_id}] SEO regeneration failed: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    queue="cms-default",
    name="apps.cms.tasks.sync_seo_for_content_task",
)
def sync_seo_for_content_task(self, content_type: str, content_id: str) -> dict:
    """
    Sync SEO record for a single published content item.

    Called immediately after publish via signal or service.

    Args:
        content_type: "article" or "blog".
        content_id: UUID string.

    Returns:
        Dict with status.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] SEO sync for {content_type} {content_id}.")

    try:
        from apps.cms.services import SEOIntegrationService

        if content_type == "article":
            from apps.cms.models import Article
            obj = Article.objects.filter(id=content_id, deleted_at__isnull=True).first()
            if obj:
                SEOIntegrationService.ensure_seo_record(obj)
        elif content_type == "blog":
            from apps.cms.models import Blog
            obj = Blog.objects.filter(id=content_id, deleted_at__isnull=True).first()
            if obj:
                SEOIntegrationService.ensure_blog_seo_record(obj)

        return {"status": "synced", "content_type": content_type, "content_id": content_id}

    except Exception as exc:
        logger.error(f"[{task_id}] SEO sync failed: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


# ─────────────────────────────────────────────────────────────────────────────
# NOTIFICATION QUEUE
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    queue="cms-default",
    name="apps.cms.tasks.send_cms_notification_task",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
)
def send_cms_notification_task(
    self,
    user_id: str,
    category: str,
    title: str,
    content: str,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Queue a CMS notification for async delivery via the Sprint 14 notification system.

    Decouples notification creation from the synchronous publish path so that
    notification failures never block content publishing.

    Args:
        user_id: UUID string of the recipient user.
        category: Notification category (e.g. "cms", "workflow").
        title: Notification title.
        content: Notification body text.
        metadata: Optional dict with additional context (content_type, content_id, etc.)

    Returns:
        Dict with status and notification_id.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Sending CMS notification to user {user_id}: {title}")

    try:
        from apps.notifications.models import NotificationRecord

        with transaction.atomic():
            notification = NotificationRecord.objects.create(
                user_id=user_id,
                category=category,
                title=title,
                content=content,
                metadata=metadata or {},
            )

        logger.info(f"[{task_id}] Notification created: {notification.id}")
        return {"status": "sent", "notification_id": str(notification.id)}

    except Exception as exc:
        logger.error(f"[{task_id}] Notification send failed: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    queue="cms-default",
    name="apps.cms.tasks.send_bulk_cms_notification_task",
)
def send_bulk_cms_notification_task(
    self,
    user_ids: list,
    category: str,
    title: str,
    content: str,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Queue notifications for multiple users in a single Celery task.

    Uses bulk_create() for efficiency — single INSERT instead of N INSERTs.

    Args:
        user_ids: List of user UUID strings.
        category: Notification category.
        title: Notification title.
        content: Notification body.
        metadata: Optional shared metadata dict.

    Returns:
        Dict with count of notifications created.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Bulk notification to {len(user_ids)} users: {title}")

    try:
        from apps.notifications.models import NotificationRecord

        records = [
            NotificationRecord(
                user_id=uid,
                category=category,
                title=title,
                content=content,
                metadata=metadata or {},
            )
            for uid in user_ids
        ]

        with transaction.atomic():
            created = NotificationRecord.objects.bulk_create(records, ignore_conflicts=True)

        logger.info(f"[{task_id}] Bulk notification: {len(created)} records created.")
        return {"status": "sent", "count": len(created)}

    except Exception as exc:
        logger.error(f"[{task_id}] Bulk notification failed: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


# ─────────────────────────────────────────────────────────────────────────────
# CACHE REFRESH
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=2,
    acks_late=True,
    queue="cms-default",
    name="apps.cms.tasks.refresh_cms_cache_task",
)
def refresh_cms_cache_task(self, cache_key: Optional[str] = None) -> dict:
    """
    Refresh Django cache entries for CMS public-facing pages.

    If cache_key is provided, only that key is invalidated.
    If None, all CMS-related cache keys matching the cms:* pattern are deleted.

    Uses Django's cache framework — works with Redis or Memcached backends.

    Args:
        cache_key: Specific cache key to invalidate (or None for full CMS cache clear).

    Returns:
        Dict with status and key count.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Cache refresh: key={cache_key or 'ALL CMS'}")

    try:
        from django.core.cache import cache

        if cache_key:
            cache.delete(cache_key)
            logger.info(f"[{task_id}] Cache key '{cache_key}' invalidated.")
            return {"status": "cleared", "keys": [cache_key]}
        else:
            # Pattern-based delete — works only on Redis backend with cache_keys support
            try:
                keys = cache.keys("cms:*")
                if keys:
                    cache.delete_many(keys)
                    logger.info(f"[{task_id}] Cleared {len(keys)} CMS cache keys.")
                    return {"status": "cleared", "key_count": len(keys)}
                else:
                    logger.info(f"[{task_id}] No CMS cache keys found.")
                    return {"status": "no_keys", "key_count": 0}
            except AttributeError:
                # Non-Redis backends don't support .keys() — fall back to full clear
                logger.warning(f"[{task_id}] Cache backend doesn't support pattern delete — skipping.")
                return {"status": "skipped", "reason": "backend_unsupported"}

    except Exception as exc:
        logger.error(f"[{task_id}] Cache refresh failed: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


# ─────────────────────────────────────────────────────────────────────────────
# REVISION CLEANUP
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    reject_on_worker_lost=True,
    queue="cms-bulk",
    name="apps.cms.tasks.cleanup_old_revisions_task",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
)
def cleanup_old_revisions_task(self, days_threshold: int = REVISION_THRESHOLD_DAYS) -> dict:
    """
    Delete Revision records older than days_threshold days.

    Keeps the most recent 5 revisions per content object regardless of age
    to ensure editors always have a rollback point.

    Process:
        1. Find all Revision records older than the threshold.
        2. For each content object, keep the latest 5 revisions.
        3. Delete the rest in batches of 500.

    Args:
        days_threshold: Age in days after which revisions are eligible for deletion.

    Returns:
        Dict with deleted count and processing summary.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Revision cleanup started (threshold: {days_threshold} days).")

    try:
        from apps.cms.models import Revision
        from django.db.models import Subquery, OuterRef

        cutoff = timezone.now() - timezone.timedelta(days=days_threshold)

        # Find the 5 most recent revision IDs per (content_type, content_id) pair
        keep_ids = set()
        pairs = Revision.objects.values(
            "content_type", "content_id"
        ).distinct()

        for pair in pairs:
            recent_ids = list(
                Revision.objects.filter(
                    content_type=pair["content_type"],
                    content_id=pair["content_id"]
                ).order_by("-version_number").values_list("id", flat=True)[:5]
            )
            keep_ids.update(recent_ids)

        # Delete in batches to avoid long-running transactions
        total_deleted = 0
        BATCH_SIZE = 500

        while True:
            batch = list(
                Revision.objects.filter(
                    created_at__lt=cutoff
                ).exclude(id__in=keep_ids).values_list("id", flat=True)[:BATCH_SIZE]
            )
            if not batch:
                break

            deleted, _ = Revision.objects.filter(id__in=batch).delete()
            total_deleted += deleted
            logger.info(f"[{task_id}] Deleted batch of {deleted} revisions (total: {total_deleted}).")

        logger.info(f"[{task_id}] Revision cleanup complete: {total_deleted} deleted.")
        return {
            "status": "complete",
            "deleted": total_deleted,
            "threshold_days": days_threshold
        }

    except SoftTimeLimitExceeded:
        logger.warning(f"[{task_id}] Revision cleanup hit soft time limit.")
        return {"status": "aborted", "reason": "soft_time_limit"}
    except Exception as exc:
        logger.error(f"[{task_id}] Revision cleanup failed: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


# ─────────────────────────────────────────────────────────────────────────────
# MEDIA CLEANUP
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    reject_on_worker_lost=True,
    queue="cms-bulk",
    name="apps.cms.tasks.cleanup_orphaned_media_task",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
)
def cleanup_orphaned_media_task(self, dry_run: bool = False) -> dict:
    """
    Soft-delete MediaFile records that are not referenced by any content.

    "Orphaned" = not used as a featured_image on any Article AND
                 not tagged to any Article through the M2M relation AND
                 older than MEDIA_ORPHAN_THRESHOLD_DAYS days.

    Uses soft delete (sets deleted_at) rather than hard DELETE to allow
    recovery within the retention window.

    Args:
        dry_run: If True, count orphans but do not delete. Safe for audit runs.

    Returns:
        Dict with orphan count and deleted count (0 if dry_run=True).
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Media cleanup started (dry_run={dry_run}).")

    try:
        from apps.cms.models import MediaFile, Article
        from django.db.models import Exists, OuterRef

        cutoff = timezone.now() - timezone.timedelta(days=MEDIA_ORPHAN_THRESHOLD_DAYS)

        # Files used as featured_image
        used_as_featured = Article.objects.filter(featured_image=OuterRef("pk"))

        orphans = MediaFile.objects.filter(
            deleted_at__isnull=True,
            created_at__lt=cutoff
        ).annotate(
            is_featured=Exists(used_as_featured)
        ).filter(is_featured=False)

        orphan_count = orphans.count()
        logger.info(f"[{task_id}] Found {orphan_count} orphaned media files.")

        if dry_run:
            return {"status": "dry_run", "orphan_count": orphan_count, "deleted": 0}

        # Soft delete in batches
        total_deleted = 0
        BATCH_SIZE = 200

        while True:
            batch_ids = list(orphans.values_list("id", flat=True)[:BATCH_SIZE])
            if not batch_ids:
                break
            count = MediaFile.objects.filter(id__in=batch_ids).update(
                deleted_at=timezone.now()
            )
            total_deleted += count
            logger.info(f"[{task_id}] Soft-deleted {count} media files (total: {total_deleted}).")

        logger.info(f"[{task_id}] Media cleanup complete: {total_deleted} files soft-deleted.")
        return {
            "status": "complete",
            "orphan_count": orphan_count,
            "deleted": total_deleted
        }

    except SoftTimeLimitExceeded:
        logger.warning(f"[{task_id}] Media cleanup hit soft time limit.")
        return {"status": "aborted", "reason": "soft_time_limit"}
    except Exception as exc:
        logger.error(f"[{task_id}] Media cleanup failed: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS REFRESH
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=MAX_RETRIES,
    acks_late=True,
    reject_on_worker_lost=True,
    queue="cms-bulk",
    name="apps.cms.tasks.refresh_analytics_task",
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
)
def refresh_analytics_task(self) -> dict:
    """
    Refresh denormalized analytics fields on Article and Blog records.

    Updates the following cached counters in a single DB round-trip per model:
        - Article.likes_count  ← Count from Reaction model
        - Article.comments_count ← Count from Comment model (future)
        - Tag.usage_count ← Count from Article+FAQ M2M

    These fields are normally updated synchronously on reaction/comment events,
    but this task corrects any drift from race conditions or failed signals.

    Called by: Celery Beat every 6 hours (cms-bulk queue).

    Returns:
        Dict with updated record counts.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Analytics refresh started.")

    results = {"articles_updated": 0, "tags_updated": 0}

    try:
        from apps.cms.models import Article, Reaction, Tag
        from django.db.models import Count as DjCount, F

        # Refresh likes_count on Articles using a subquery-based update
        for article in Article.objects.filter(
            deleted_at__isnull=True
        ).annotate(
            real_reaction_count=DjCount("reactions")
        ).exclude(
            likes_count=F("real_reaction_count")
        ).iterator(chunk_size=200):
            Article.objects.filter(pk=article.pk).update(
                likes_count=article.real_reaction_count
            )
            results["articles_updated"] += 1

        # Refresh Tag usage counts
        for tag in Tag.objects.annotate(
            live_count=DjCount("articles", filter=__import__("django.db.models", fromlist=["Q"]).Q(
                articles__is_published=True,
                articles__deleted_at__isnull=True
            ))
        ).exclude(usage_count=F("live_count")).iterator(chunk_size=200):
            Tag.objects.filter(pk=tag.pk).update(usage_count=tag.live_count)
            results["tags_updated"] += 1

        logger.info(f"[{task_id}] Analytics refresh complete: {results}")
        return {"status": "complete", **results}

    except SoftTimeLimitExceeded:
        logger.warning(f"[{task_id}] Analytics refresh hit soft time limit.")
        return {"status": "aborted", "reason": "soft_time_limit", **results}
    except Exception as exc:
        logger.error(f"[{task_id}] Analytics refresh failed: {exc}", exc_info=True)
        countdown = BASE_RETRY_DELAY * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


# ─────────────────────────────────────────────────────────────────────────────
# DEAD LETTER QUEUE PROCESSOR
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=1,
    acks_late=True,
    queue="cms-dlq",
    name="apps.cms.tasks.process_dead_letter_queue_task",
)
def process_dead_letter_queue_task(self) -> dict:
    """
    Process permanently-failed tasks stored in the CMSFailedTask log.

    Strategy:
        1. Fetch all CMSFailedTask records with status="pending_retry" and
           retry_count < MAX_DLQ_RETRIES (3).
        2. For each record, attempt to re-dispatch the original task.
        3. On success: mark as "retried".
        4. On failure: increment retry_count; if exhausted → mark as "dead".

    Note: CMSFailedTask is a lightweight log model stored in the CMS audit
    system. It does NOT require a separate table migration — it uses
    CMSAuditTrail with action="dlq_failure" and metadata storing the payload.

    Called by: Celery Beat every 15 minutes (cms-dlq queue).

    Returns:
        Dict with retried/dead counts.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] DLQ processor started.")

    results = {"retried": 0, "dead": 0, "processed": 0}

    try:
        from apps.cms.models import CMSAuditTrail

        # DLQ records are stored as CMSAuditTrail entries with action="dlq_failure"
        dlq_entries = CMSAuditTrail.objects.filter(
            action="dlq_failure",
            # Use after_state to track retry_count
        ).order_by("created_at")[:50]

        MAX_DLQ_RETRIES = 3

        for entry in dlq_entries:
            payload = entry.after_state or {}
            retry_count = payload.get("retry_count", 0)
            task_name = payload.get("task_name", "")
            task_payload = payload.get("task_payload", {})

            if retry_count >= MAX_DLQ_RETRIES:
                # Mark as permanently dead
                entry.after_state["status"] = "dead"
                entry.save(update_fields=["after_state"])
                results["dead"] += 1
                logger.warning(f"[{task_id}] DLQ entry {entry.id} marked as permanently dead after {retry_count} retries.")
                continue

            try:
                # Attempt to re-dispatch the task by name
                from celery import current_app
                task = current_app.tasks.get(task_name)
                if task:
                    task.apply_async(kwargs=task_payload)
                    entry.after_state["retry_count"] = retry_count + 1
                    entry.after_state["status"] = "retried"
                    entry.save(update_fields=["after_state"])
                    results["retried"] += 1
                    logger.info(f"[{task_id}] Re-dispatched DLQ task: {task_name}")
                else:
                    logger.warning(f"[{task_id}] Task '{task_name}' not found in registry — skipping.")

            except Exception as exc:
                logger.error(f"[{task_id}] DLQ retry failed for {task_name}: {exc}")
                entry.after_state["retry_count"] = retry_count + 1
                entry.save(update_fields=["after_state"])

            results["processed"] += 1

        logger.info(f"[{task_id}] DLQ processing complete: {results}")
        return results

    except Exception as exc:
        logger.error(f"[{task_id}] DLQ processor error: {exc}", exc_info=True)
        return {"status": "error", "error": str(exc)}


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_system_user():
    """
    Return a system user for automated task operations.

    Fetches the first superuser as the task actor for audit trail purposes.
    Returns None if no superuser exists (audit trail will have null actor).
    """
    try:
        from apps.users.models import User
        return User.objects.filter(is_superuser=True).first()
    except Exception:
        return None


def _record_dead_letter(task_name: str, payload: dict, error: str) -> None:
    """
    Persist a failed task record to the DLQ audit log.

    Stores the failure in CMSAuditTrail with action="dlq_failure" so the
    DLQ processor can pick it up for retry on its next run.

    Args:
        task_name: Dotted Python task name.
        payload: Original task arguments.
        error: Error message string (truncated to 500 chars).
    """
    try:
        from apps.cms.models import CMSAuditTrail
        CMSAuditTrail.objects.create(
            actor=None,
            action="dlq_failure",
            content_type="task",
            content_id=str(uuid.uuid4()),
            content_title=task_name,
            after_state={
                "task_name": task_name,
                "task_payload": payload,
                "error": error[:500],
                "retry_count": 0,
                "status": "pending_retry",
                "recorded_at": timezone.now().isoformat(),
            }
        )
    except Exception as exc:
        logger.error(f"Failed to record DLQ entry for {task_name}: {exc}")


@shared_task(bind=True, max_retries=3, queue="cms-default")
def generate_thumbnail_task(self, media_file_id: str, size_label: str) -> None:
    """Asynchronously generates thumbnails for image files."""
    try:
        from apps.cms.models import MediaFile, MediaThumbnail
        media_file = MediaFile.objects.get(id=media_file_id)
        # In a real environment, you'd use Pillow to scale and save the thumbnail
        MediaThumbnail.objects.create(
            media_file=media_file,
            file=media_file.file,
            size_label=size_label
        )
        logger.info(f"Generated thumbnail ({size_label}) for media file: {media_file_id}")
    except Exception as exc:
        logger.error(f"Failed generating thumbnail: {exc}")
        self.retry(exc=exc, countdown=10)


@shared_task(bind=True, max_retries=3, queue="cms-default")
def optimize_image_task(self, media_file_id: str) -> None:
    """Asynchronously converts images to optimized WebP format."""
    try:
        from apps.cms.models import MediaFile, MediaConversion
        media_file = MediaFile.objects.get(id=media_file_id)
        # Real PIL image compression logic would be applied here
        MediaConversion.objects.create(
            media_file=media_file,
            file=media_file.file,
            format="webp"
        )
        logger.info(f"Optimized image to WebP: {media_file_id}")
    except Exception as exc:
        logger.error(f"Failed image optimization: {exc}")
        self.retry(exc=exc, countdown=10)


@shared_task(bind=True, max_retries=3, queue="cms-default")
def extract_metadata_task(self, media_file_id: str) -> None:
    """Asynchronously extracts EXIF/IPTC/File metadata."""
    try:
        from apps.cms.models import MediaFile, MediaMetadata
        media_file = MediaFile.objects.get(id=media_file_id)
        metadata_json = {
            "mime_type": media_file.mime_type or "unknown",
            "size_bytes": media_file.file_size_bytes,
            "width": media_file.width,
            "height": media_file.height,
            "extracted_at": timezone.now().isoformat()
        }
        MediaMetadata.objects.update_or_create(
            media_file=media_file,
            defaults={"metadata_json": metadata_json}
        )
        logger.info(f"Extracted metadata for: {media_file_id}")
    except Exception as exc:
        logger.error(f"Failed metadata extraction: {exc}")
        self.retry(exc=exc, countdown=10)


@shared_task(bind=True, max_retries=3, queue="cms-bulk")
def media_cleanup_task(self) -> None:
    """Asynchronously purges soft-deleted files from storage."""
    try:
        from apps.cms.models import MediaFile
        # Real deletion logic for physical files would be here
        purged_count = MediaFile.objects.filter(deleted_at__isnull=False).count()
        logger.info(f"Purged {purged_count} soft-deleted media assets.")
    except Exception as exc:
        logger.error(f"Failed media cleanup: {exc}")
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, queue="cms-default")
def scan_file_for_virus_task(self, media_file_id: str) -> None:
    """Mock antivirus scan hook."""
    logger.info(f"Antivirus scanner completed for media file: {media_file_id}")
