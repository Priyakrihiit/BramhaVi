from django.contrib import admin
from apps.seo.models import SEOPage, SEOAudit

@admin.register(SEOPage)
class SEOPageAdmin(admin.ModelAdmin):
    list_display = ["id", "page_type", "page_id", "title", "slug", "robots_index", "robots_follow", "created_at"]
    list_filter = ["page_type", "robots_index", "robots_follow"]
    search_fields = ["title", "slug", "keywords"]


@admin.register(SEOAudit)
class SEOAuditAdmin(admin.ModelAdmin):
    list_display = ["id", "page", "seo_score", "readability_score", "created_at"]
    list_filter = ["seo_score", "readability_score"]
    search_fields = ["page__title"]
