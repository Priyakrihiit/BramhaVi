import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.search.tasks import index_document_task, delete_document_task

logger = logging.getLogger("search.signals")

# ==========================
# LMS SIGNALS
# ==========================
@receiver(post_save, sender="lms.CourseStructure")
def course_structure_post_save(sender, instance, created, **kwargs):
    """
    Hooks LMS CourseStructure post-save updates to background search index task.
    """
    try:
        index_document_task.delay("CourseStructure", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for CourseStructure {instance.id}: {e}")

@receiver(post_delete, sender="lms.CourseStructure")
def course_structure_post_delete(sender, instance, **kwargs):
    """
    Hooks LMS CourseStructure deletion to background search index removal.
    """
    try:
        delete_document_task.delay("CourseStructure", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for CourseStructure {instance.id}: {e}")


# ==========================
# CMS SIGNALS
# ==========================
@receiver(post_save, sender="cms.Article")
def article_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("Article", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for Article {instance.id}: {e}")

@receiver(post_delete, sender="cms.Article")
def article_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("Article", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for Article {instance.id}: {e}")


@receiver(post_save, sender="cms.Blog")
def blog_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("Blog", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for Blog {instance.id}: {e}")

@receiver(post_delete, sender="cms.Blog")
def blog_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("Blog", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for Blog {instance.id}: {e}")


@receiver(post_save, sender="cms.Page")
def page_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("Page", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for Page {instance.id}: {e}")

@receiver(post_delete, sender="cms.Page")
def page_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("Page", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for Page {instance.id}: {e}")


@receiver(post_save, sender="cms.Tutorial")
def tutorial_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("Tutorial", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for Tutorial {instance.id}: {e}")

@receiver(post_delete, sender="cms.Tutorial")
def tutorial_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("Tutorial", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for Tutorial {instance.id}: {e}")


@receiver(post_save, sender="cms.FAQ")
def faq_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("FAQ", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for FAQ {instance.id}: {e}")

@receiver(post_delete, sender="cms.FAQ")
def faq_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("FAQ", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for FAQ {instance.id}: {e}")


@receiver(post_save, sender="cms.MediaFile")
def media_file_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("MediaFile", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for MediaFile {instance.id}: {e}")

@receiver(post_delete, sender="cms.MediaFile")
def media_file_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("MediaFile", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for MediaFile {instance.id}: {e}")


# ==========================
# PUBLISHING SIGNALS
# ==========================
@receiver(post_save, sender="publishing.Book")
def book_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("Book", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for Book {instance.id}: {e}")

@receiver(post_delete, sender="publishing.Book")
def book_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("Book", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for Book {instance.id}: {e}")


# ==========================
# SEO SIGNALS
# ==========================
@receiver(post_save, sender="seo.SEOPage")
def seo_page_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("SEOPage", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for SEOPage {instance.id}: {e}")

@receiver(post_delete, sender="seo.SEOPage")
def seo_page_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("SEOPage", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for SEOPage {instance.id}: {e}")


# ==========================
# NOTIFICATIONS SIGNALS
# ==========================
@receiver(post_save, sender="notifications.Announcement")
def announcement_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("Announcement", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for Announcement {instance.id}: {e}")

@receiver(post_delete, sender="notifications.Announcement")
def announcement_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("Announcement", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for Announcement {instance.id}: {e}")


@receiver(post_save, sender="notifications.NotificationRecord")
def notification_record_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("NotificationRecord", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for NotificationRecord {instance.id}: {e}")

@receiver(post_delete, sender="notifications.NotificationRecord")
def notification_record_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("NotificationRecord", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for NotificationRecord {instance.id}: {e}")


# ==========================
# USER SIGNALS
# ==========================
@receiver(post_save, sender="users.UserProfile")
def user_profile_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("UserProfile", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for UserProfile {instance.id}: {e}")

@receiver(post_delete, sender="users.UserProfile")
def user_profile_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("UserProfile", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for UserProfile {instance.id}: {e}")


@receiver(post_save, sender="users.Organization")
def organization_post_save(sender, instance, created, **kwargs):
    try:
        index_document_task.delay("Organization", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch index task for Organization {instance.id}: {e}")

@receiver(post_delete, sender="users.Organization")
def organization_post_delete(sender, instance, **kwargs):
    try:
        delete_document_task.delay("Organization", str(instance.id))
    except Exception as e:
        logger.error(f"Failed to dispatch delete task for Organization {instance.id}: {e}")
