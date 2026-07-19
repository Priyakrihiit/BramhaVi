from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.lms.models import CourseStructure
from apps.cms.models import Blog, Page
from apps.publishing.models import Book
from apps.services.models import ProfessionalService
from apps.users.models import UserProfile
from apps.seo.models import SEOPage
from apps.seo.services import AISEOService

def sync_seo_record(page_type, page_id, title, description=""):
    slug = AISEOService.generate_slug(title)
    meta_title = AISEOService.generate_meta_title(page_type, title, description)
    meta_description = AISEOService.generate_meta_description(page_type, title, description)
    keywords = AISEOService.suggest_keywords(page_type, title, description)
    schema_json = AISEOService.generate_schema_org("Website" if page_type == "WEBSITE" else "Article", title, description)

    defaults = {
        "title": title,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "slug": slug,
        "keywords": keywords,
        "schema_json": schema_json,
        "canonical_url": f"https://brahmavidya.edu/{page_type.lower()}/{slug}",
        "robots_index": True,
        "robots_follow": True
    }

    SEOPage.objects.update_or_create(
        page_type=page_type.upper(),
        page_id=str(page_id),
        defaults=defaults
    )

@receiver(post_save, sender=CourseStructure)
def on_course_save(sender, instance, **kwargs):
    if instance.node_type == "COURSE":
        sync_seo_record("COURSE", instance.id, instance.title, instance.description)

@receiver(post_save, sender=Blog)
def on_blog_save(sender, instance, **kwargs):
    sync_seo_record("BLOG", instance.id, instance.title, instance.content)

@receiver(post_save, sender=Book)
def on_book_save(sender, instance, **kwargs):
    sync_seo_record("BOOK", instance.id, instance.title, instance.description)

@receiver(post_save, sender=ProfessionalService)
def on_service_save(sender, instance, **kwargs):
    sync_seo_record("PRODUCT", instance.id, instance.name, instance.description)

@receiver(post_save, sender=Page)
def on_page_save(sender, instance, **kwargs):
    sync_seo_record("WEBSITE", instance.id, instance.title, "")

@receiver(post_save, sender=UserProfile)
def on_profile_save(sender, instance, **kwargs):
    name = f"{instance.first_name or ''} {instance.last_name or ''}".strip() or instance.user.email
    sync_seo_record("PROFILE", instance.id, name, instance.bio)
