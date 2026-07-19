from rest_framework import serializers
from apps.seo.models import SEOPage, SEOAudit

class SEOPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOPage
        fields = [
            "id", "page_type", "page_id", "title", "meta_title", "meta_description",
            "canonical_url", "slug", "robots_index", "robots_follow", "keywords",
            "og_title", "og_description", "og_image", "twitter_title",
            "twitter_description", "twitter_image", "schema_json", "language",
            "created_at", "updated_at"
        ]


class SEOAuditSerializer(serializers.ModelSerializer):
    page_title = serializers.ReadOnlyField(source="page.title")

    class Meta:
        model = SEOAudit
        fields = [
            "id", "page", "page_title", "seo_score", "readability_score",
            "broken_links", "duplicate_title", "duplicate_description",
            "missing_alt_images", "missing_h1", "missing_schema",
            "recommendations", "created_at"
        ]
