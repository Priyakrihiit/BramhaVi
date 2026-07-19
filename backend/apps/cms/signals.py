"""
CMS Event Signals - BrahmaVidya Galaxy
Purpose: Automates multi-platform synchronization across CMS models.
"""

import logging
from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from middleware.request_id import get_current_request_id

logger = logging.getLogger("cms.signals")

# Dummy model representation for signal demonstration
class PagePlaceholder:
    pass

# Helper to serialize instance fields for auditing
def serialize_instance(instance):
    try:
        return {
            field.name: str(getattr(instance, field.name))
            for field in instance._meta.fields
            if not field.many_to_many
        }
    except Exception as e:
        logger.warning(f"Failed to serialize instance: {e}")
        return {}

@receiver(pre_save)
def cms_pre_save_handler(sender, instance, **kwargs):
    """
    Captures before-state before saving for audit log tracking.
    """
    model_name = sender.__name__
    if model_name not in ["Page", "Article", "Blog", "Comment", "MediaFile", "WorkflowState", "PublishSchedule"]:
        return

    # Check if object is being updated
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._before_state = serialize_instance(old_instance)
        except Exception:
            instance._before_state = {}
    else:
        instance._before_state = {}

@receiver(post_save)
def cms_post_save_handler(sender, instance, created, **kwargs):
    """
    Executes automated post-save routines for CMS models.
    Triggers: Notification, SEO, Search Index, Audit Trail, Revision, Workflow, Version History, Cache, Analytics.
    """
    model_name = sender.__name__
    if model_name not in ["Page", "Article", "Blog", "Comment", "MediaFile", "WorkflowState", "PublishSchedule"]:
        return

    # Local imports to prevent circular dependency
    from apps.cms.models import CMSAuditTrail
    from apps.cms.services import RevisionService, VersionService, WorkflowService
    from apps.cms.tasks import (
        index_single_content_task,
        sync_seo_for_content_task,
        send_cms_notification_task,
        refresh_cms_cache_task,
        refresh_analytics_task,
    )

    action = "create" if created else "update"
    request_id = get_current_request_id()

    # Determine actor
    actor = None
    if hasattr(instance, "author") and instance.author:
        actor = instance.author
    elif hasattr(instance, "uploader") and instance.uploader:
        actor = instance.uploader
    elif hasattr(instance, "user") and instance.user:
        actor = instance.user

    before_state = getattr(instance, "_before_state", {})
    after_state = serialize_instance(instance)

    # 1. Audit Trail
    try:
        CMSAuditTrail.objects.create(
            actor=actor,
            action=action,
            content_type=model_name.lower(),
            content_id=str(instance.id),
            content_title=str(instance),
            before_state=before_state,
            after_state=after_state,
            request_id=request_id
        )
    except Exception as e:
        logger.error(f"Audit log failed in signal for {model_name}: {e}")

    # 2. Workflow & Revision & Version History & Cache & SEO & Search Index
    if model_name == "Article":
        # Workflow initialization
        try:
            WorkflowService.get_or_create_workflow(instance)
        except Exception as e:
            logger.error(f"Workflow auto-provisioning failed for article {instance.id}: {e}")

        # Revision Snapshot
        try:
            RevisionService.create_revision(instance, actor, change_summary=f"Automated save snapshot ({action})")
        except Exception as e:
            logger.error(f"Revision creation failed for article {instance.id}: {e}")

        # SEO Integration (Async task queue)
        try:
            sync_seo_for_content_task.delay("article", str(instance.id))
        except Exception as e:
            logger.error(f"SEO sync trigger failed for article {instance.id}: {e}")

        # Search Index Integration (Async task queue)
        try:
            index_single_content_task.delay("article", str(instance.id))
        except Exception as e:
            logger.error(f"Search indexing trigger failed for article {instance.id}: {e}")

        # Cache Invalidation
        try:
            cache.delete("global_navigation_menu_tree")
            refresh_cms_cache_task.delay(cache_key=f"article_{instance.id}")
        except Exception as e:
            logger.error(f"Cache refresh trigger failed for article {instance.id}: {e}")

        # Article Published Notification
        was_published = before_state.get("is_published") == "True"
        is_published = instance.is_published
        if is_published and not was_published:
            try:
                send_cms_notification_task.delay(
                    user_id=str(instance.author.id) if instance.author else "",
                    category="cms",
                    title="Article Published 🎉",
                    content=f'Your article "{instance.title}" is now live!',
                    metadata={"article_id": str(instance.id), "article_slug": instance.slug}
                )
            except Exception as e:
                logger.error(f"Failed to queue article published notification: {e}")

    elif model_name == "Blog":
        # Revision Snapshot
        try:
            RevisionService.create_revision(instance, actor, change_summary=f"Automated save snapshot ({action})")
        except Exception as e:
            logger.error(f"Revision creation failed for blog {instance.id}: {e}")

        # SEO Integration
        try:
            sync_seo_for_content_task.delay("blog", str(instance.id))
        except Exception as e:
            logger.error(f"SEO sync trigger failed for blog {instance.id}: {e}")

        # Search Index Integration
        try:
            index_single_content_task.delay("blog", str(instance.id))
        except Exception as e:
            logger.error(f"Search indexing trigger failed for blog {instance.id}: {e}")

        # Cache Invalidation
        try:
            refresh_cms_cache_task.delay(cache_key=f"blog_{instance.id}")
        except Exception as e:
            logger.error(f"Cache refresh trigger failed for blog {instance.id}: {e}")

    elif model_name == "Page":
        # Version History snapshot
        try:
            VersionService.create_version(instance, instance.layout_data, author=actor, change_summary=f"Automated layout update ({action})")
        except Exception as e:
            logger.error(f"Version snapshot failed for page {instance.id}: {e}")

        # SEO Integration
        try:
            from apps.seo.signals import sync_seo_record
            sync_seo_record("WEBSITE", instance.id, instance.title, "")
        except Exception as e:
            logger.error(f"SEO sync failed for page {instance.id}: {e}")

        # Cache Invalidation
        try:
            cache.delete("global_navigation_menu_tree")
            refresh_cms_cache_task.delay(cache_key="global_navigation_menu_tree")
        except Exception as e:
            logger.error(f"Cache refresh trigger failed for page {instance.id}: {e}")

        # Page Published Notification
        was_published = before_state.get("is_published") == "True"
        is_published = instance.is_published
        if is_published and not was_published:
            try:
                send_cms_notification_task.delay(
                    user_id=str(instance.author.id) if instance.author else "",
                    category="cms",
                    title="Page Published 🌐",
                    content=f'Your page "{instance.title}" has been published.',
                    metadata={"page_id": str(instance.id), "page_slug": instance.slug}
                )
            except Exception as e:
                logger.error(f"Failed to queue page published notification: {e}")

    elif model_name == "MediaFile":
        from apps.cms.tasks import (
            scan_file_for_virus_task,
            extract_metadata_task,
            generate_thumbnail_task,
            optimize_image_task
        )
        
        is_new = not before_state
        if is_new:
            try:
                scan_file_for_virus_task.delay(str(instance.id))
                extract_metadata_task.delay(str(instance.id))
                if instance.file_type == "image":
                    generate_thumbnail_task.delay(str(instance.id), "small")
                    generate_thumbnail_task.delay(str(instance.id), "medium")
                    generate_thumbnail_task.delay(str(instance.id), "large")
                    optimize_image_task.delay(str(instance.id))

                # Notifications Integration
                from apps.cms.tasks import send_cms_notification_task
                send_cms_notification_task.delay(
                    user_id=str(instance.uploader.id) if instance.uploader else "",
                    category="cms",
                    title="Media Uploaded 📂",
                    content=f'Your asset "{instance.original_filename}" has been successfully uploaded and scanned.',
                    metadata={"media_file_id": str(instance.id)}
                )
            except Exception as e:
                logger.error(f"Failed to trigger async media tasks: {e}")

        # Search Index Integration
        try:
            from apps.cms.tasks import index_single_content_task
            index_single_content_task.delay("media_file", str(instance.id))
        except Exception as e:
            logger.error(f"Search indexing failed for media file {instance.id}: {e}")

        # SEO Integration
        if instance.is_public:
            try:
                from apps.seo.signals import sync_seo_record
                sync_seo_record("WEBSITE", instance.id, instance.original_filename, instance.caption or "")
            except Exception as e:
                logger.error(f"SEO sync failed for media file {instance.id}: {e}")

        # Audit
        try:
            CMSAuditTrail.objects.create(
                actor=instance.uploader,
                action="create" if is_new else "update",
                content_type="media_file",
                content_id=str(instance.id),
                content_title=instance.original_filename,
                before_state=before_state,
                after_state={"size": instance.file_size_bytes, "mime_type": instance.mime_type},
                request_id=get_current_request_id()
            )
        except Exception as e:
            logger.error(f"Audit log failed for media file: {e}")

        # Cache Invalidation
        try:
            cache.delete(f"media_file_{instance.id}")
        except Exception as e:
            logger.error(f"Cache delete failed for media file {instance.id}: {e}")

    elif model_name == "WorkflowState":
        # Trigger notifications on transitions
        # We check if the status changed and if the transition warrants notification.
        from_status = before_state.get("status")
        to_status = instance.status
        if from_status and from_status != to_status:
            # Audit the transition
            try:
                CMSAuditTrail.objects.create(
                    actor=actor or instance.assigned_to,
                    action="approve" if to_status == "approved" else ("reject" if to_status == "rejected" else "update"),
                    content_type="workflowstate",
                    content_id=str(instance.id),
                    content_title=str(instance),
                    before_state={"status": from_status},
                    after_state={"status": to_status},
                    request_id=request_id
                )
            except Exception as e:
                logger.error(f"Workflow transition audit log failed: {e}")

            # Notify author
            article = instance.article
            if article and article.author:
                messages = {
                    "approved": ("Content Approved ✅", f'Your article "{article.title}" has been approved and is ready to publish.', "cms"),
                    "rejected": ("Content Rejected ❌", f'Your article "{article.title}" requires revisions before publishing.', "cms"),
                    "published": ("Content Published 🎉", f'Your article "{article.title}" is now live!', "cms"),
                }
                if to_status in messages:
                    title, content, category = messages[to_status]
                    try:
                        send_cms_notification_task.delay(
                            user_id=str(article.author.id),
                            category=category,
                            title=title,
                            content=content,
                            metadata={
                                "article_id": str(article.id),
                                "article_slug": article.slug,
                                "workflow_action": to_status
                            }
                        )
                    except Exception as e:
                        logger.error(f"Failed to queue notification task: {e}")

    elif model_name == "PublishSchedule":
        # Notify on scheduled publish completed
        from_status = before_state.get("status")
        to_status = instance.status
        if to_status == "completed" and from_status != "completed":
            try:
                send_cms_notification_task.delay(
                    user_id=str(instance.scheduled_by.id) if instance.scheduled_by else "",
                    category="cms",
                    title="Scheduled Publish Complete ⏰",
                    content=f'Your scheduled content "{instance.content_type}" ({instance.content_id}) has been published successfully.',
                    metadata={"content_id": str(instance.content_id), "content_type": instance.content_type}
                )
            except Exception as e:
                logger.error(f"Failed to queue scheduled publish notification: {e}")

    # 3. Analytics Trigger
    try:
        refresh_analytics_task.delay()
    except Exception as e:
        logger.error(f"Analytics refresh trigger failed: {e}")


@receiver(post_delete)
def cms_post_delete_handler(sender, instance, **kwargs):
    """
    Executes post-deletion cleanups.
    Triggers: Audit Trail, Search Index, Cache, Media Cleanup, Analytics.
    """
    model_name = sender.__name__
    if model_name not in ["Page", "Article", "Blog", "Comment", "MediaFile"]:
        return

    from apps.cms.models import CMSAuditTrail
    from apps.cms.services import SearchIndexService
    from apps.cms.tasks import refresh_cms_cache_task, refresh_analytics_task

    request_id = get_current_request_id()

    # Determine actor
    actor = None
    if hasattr(instance, "author") and instance.author:
        actor = instance.author
    elif hasattr(instance, "uploader") and instance.uploader:
        actor = instance.uploader
    elif hasattr(instance, "user") and instance.user:
        actor = instance.user

    before_state = serialize_instance(instance)

    # 1. Audit Trail
    try:
        CMSAuditTrail.objects.create(
            actor=actor,
            action="delete",
            content_type=model_name.lower(),
            content_id=str(instance.id),
            content_title=str(instance),
            before_state=before_state,
            after_state={},
            request_id=request_id
        )
    except Exception as e:
        logger.error(f"Audit log failed on deletion of {model_name}: {e}")

    # 2. Search Index Cleanup
    if model_name in ["Article", "Blog"]:
        try:
            SearchIndexService.remove_from_index(model_name.lower(), instance.id)
        except Exception as e:
            logger.error(f"Failed to remove {model_name} from index: {e}")

    # 3. Media Cleanup (physical file removal)
    if model_name == "MediaFile":
        if instance.file:
            try:
                instance.file.delete(save=False)
                logger.info(f"Physical file deleted for MediaFile {instance.id}")
            except Exception as e:
                logger.error(f"Physical file deletion failed for MediaFile {instance.id}: {e}")

    # 4. Cache Invalidation
    try:
        if model_name in ["Page", "Article"]:
            cache.delete("global_navigation_menu_tree")
        refresh_cms_cache_task.delay()
    except Exception as e:
        logger.error(f"Cache refresh trigger failed on deletion: {e}")

    # 5. Analytics Update
    try:
        refresh_analytics_task.delay()
    except Exception as e:
        logger.error(f"Analytics refresh trigger failed on deletion: {e}")


@receiver(m2m_changed)
def cms_m2m_changed_handler(sender, instance, action, **kwargs):
    """
    Handles M2M updates such as Article categories/tags adjustments.
    Triggers: Search Index, Audit Trail.
    """
    # Verify if the sender is the categories or tags through model for Article
    if action in ["post_add", "post_remove", "post_clear"]:
        instance_model_name = type(instance).__name__
        if instance_model_name == "Article":
            from apps.cms.models import CMSAuditTrail
            from apps.cms.tasks import index_single_content_task

            # Re-index search
            try:
                index_single_content_task.delay("article", str(instance.id))
            except Exception as e:
                logger.error(f"Search indexing failed on M2M change: {e}")

            # Audit log entry
            try:
                actor = getattr(instance, "author", None)
                CMSAuditTrail.objects.create(
                    actor=actor,
                    action="update",
                    content_type="article",
                    content_id=str(instance.id),
                    content_title=instance.title,
                    before_state={"info": f"M2M relation updated: {action}"},
                    after_state={"info": "M2M relation update completed"},
                    request_id=get_current_request_id()
                )
            except Exception as e:
                logger.error(f"Audit log failed on M2M change: {e}")
