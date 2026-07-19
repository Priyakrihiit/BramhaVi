import uuid
from django.db import models
from apps.base_models import BaseModel

class SEOPage(BaseModel):
    """
    Search engine optimization metadata mappings indexing corporate entities, 
    LMS courses, CMS articles, portfolios, and organization directories.
    """
    page_type = models.CharField(
        max_length=50, 
        help_text="Classification namespace (e.g., COURSE, BLOG, BOOK, PRODUCT, PORTFOLIO, RESUME, WEBSITE, ORGANIZATION, PROFILE)"
    )
    page_id = models.CharField(
        max_length=255, 
        db_index=True, 
        help_text="Linked target page primary identifier."
    )
    title = models.CharField(max_length=255, help_text="Visual visual title label.")
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    canonical_url = models.CharField(max_length=512, blank=True, null=True)
    slug = models.CharField(max_length=255, blank=True, null=True)
    robots_index = models.BooleanField(default=True)
    robots_follow = models.BooleanField(default=True)
    keywords = models.CharField(max_length=500, blank=True, null=True)
    og_title = models.CharField(max_length=255, blank=True, null=True)
    og_description = models.TextField(blank=True, null=True)
    og_image = models.CharField(max_length=512, blank=True, null=True)
    twitter_title = models.CharField(max_length=255, blank=True, null=True)
    twitter_description = models.TextField(blank=True, null=True)
    twitter_image = models.CharField(max_length=512, blank=True, null=True)
    schema_json = models.JSONField(default=dict, blank=True)
    language = models.CharField(max_length=10, default="en")

    class Meta:
        db_table = "seo_pages"
        verbose_name = "SEO Page"
        verbose_name_plural = "SEO Pages"
        constraints = [
            models.UniqueConstraint(
                fields=["page_type", "page_id"],
                name="uq_seo_page_type_id"
            )
        ]

    def __str__(self):
        return f"[{self.page_type}] {self.title}"


class SEOAudit(models.Model):
    """
    Search-engine readability scores, headers indexing status, and missing markup diagnostics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(SEOPage, on_delete=models.CASCADE, related_name="audits")
    seo_score = models.IntegerField(default=0)
    readability_score = models.IntegerField(default=0)
    broken_links = models.JSONField(default=list, blank=True)
    duplicate_title = models.BooleanField(default=False)
    duplicate_description = models.BooleanField(default=False)
    missing_alt_images = models.IntegerField(default=0)
    missing_h1 = models.BooleanField(default=False)
    missing_schema = models.BooleanField(default=False)
    recommendations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "seo_audits"
        verbose_name = "SEO Audit"
        verbose_name_plural = "SEO Audits"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Audit for {self.page.title} ({self.seo_score}/100)"
