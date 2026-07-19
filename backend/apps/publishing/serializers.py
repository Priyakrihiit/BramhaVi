from rest_framework import serializers
import uuid
from apps.publishing.models import (
    AuthorProfile, PublisherProfile, Book, ProductOwnership, Order, OrderItem, ReadingProgress
)

# ==========================================
# 1. SECURITY & CONFIGURATION SERIALIZERS
# ==========================================

class PublishingConfigSerializer(serializers.Serializer):
    """
    Manages website access levels, maintenance windows, password-protection hashes,
    and granular request limits.
    """
    website_id = serializers.CharField()
    is_private = serializers.BooleanField(default=False)
    password_protected = serializers.BooleanField(default=False)
    password_hash = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    is_maintenance = serializers.BooleanField(default=False)
    is_suspended = serializers.BooleanField(default=False)
    rate_limit_rpm = serializers.IntegerField(default=60, min_value=1)
    suspended_reason = serializers.CharField(required=False, allow_blank=True, default="")
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class PasswordVerifySerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


# ==========================================
# 2. SUBDOMAIN MANAGEMENT SERIALIZERS
# ==========================================

class SubdomainReservationSerializer(serializers.Serializer):
    """
    Subdomain registration records containing parent ID associations,
    reservation states, and future custom domain configuration overrides.
    """
    subdomain = serializers.CharField(max_length=100)
    website_id = serializers.CharField()
    reserved_by = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)

    def validate_subdomain(self, value):
        import re
        if not re.match(r"^[a-zA-Z0-9\-]+$", value):
            raise serializers.ValidationError("Subdomain can only contain alphanumeric characters and hyphens.")
        return value.lower().strip()


class SubdomainAvailabilitySerializer(serializers.Serializer):
    subdomain = serializers.CharField(max_length=100)
    available = serializers.BooleanField(read_only=True)
    reason = serializers.CharField(read_only=True, required=False)


# ==========================================
# 3. VERSIONING SERIALIZERS
# ==========================================

class WebsiteVersionSerializer(serializers.Serializer):
    """
    Immutable snapshots capturing the website structure, schemas, layout templates, and pages
    at specific historical milestones.
    """
    id = serializers.CharField(read_only=True)
    website_id = serializers.CharField()
    version_number = serializers.IntegerField(read_only=True)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")
    snapshot = serializers.JSONField(read_only=True)
    created_by = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class CreateVersionSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")


class RollbackVersionSerializer(serializers.Serializer):
    version_number = serializers.IntegerField()


class VersionComparisonSerializer(serializers.Serializer):
    source_version = serializers.IntegerField()
    target_version = serializers.IntegerField()
    differences = serializers.JSONField(read_only=True)


# ==========================================
# 4. SEO & REDIRECT SERIALIZERS
# ==========================================

class RedirectRuleSerializer(serializers.Serializer):
    """
    301 and 302 canonical paths routing old SEO structures to modern pages.
    """
    source_path = serializers.CharField(max_length=500)
    target_url = serializers.CharField(max_length=1000)
    is_permanent = serializers.BooleanField(default=True)


class SchemaOrgSerializer(serializers.Serializer):
    """
    Structured data payloads for search engine snippets representing Professional,
    Service, Article or Academic structures.
    """
    schema_type = serializers.CharField(max_length=100, default="ProfessionalService")
    properties = serializers.JSONField()


class SEOEnhancementSerializer(serializers.Serializer):
    """
    Aggregated schemas delivering meta, twitter cards, sitemaps, schema, and robots instructions.
    """
    xml_sitemap_url = serializers.URLField()
    robots_text = serializers.CharField()
    canonical_url = serializers.URLField()
    open_graph = serializers.JSONField()
    twitter_card = serializers.JSONField()
    structured_data = SchemaOrgSerializer(many=True, default=[])
    redirect_rules = RedirectRuleSerializer(many=True, default=[])
    not_found_handling = serializers.JSONField()


# ==========================================
# 5. FORM SUBMISSION SERIALIZERS
# ==========================================

class FormSubmissionSerializer(serializers.Serializer):
    """
    Structured entries tracking customer inquiries, newsletter registrations, spam scoring,
    and lead generation metadata.
    """
    id = serializers.CharField(read_only=True)
    website_id = serializers.CharField()
    form_type = serializers.ChoiceField(choices=[("contact", "contact"), ("newsletter", "newsletter"), ("lead", "lead")])
    data = serializers.JSONField()
    is_spam = serializers.BooleanField(default=False)
    spam_score = serializers.FloatField(default=0.0)
    created_at = serializers.DateTimeField(read_only=True)


# ==========================================
# 6. ANALYTICS SERIALIZERS
# ==========================================

class AnalyticsEventSerializer(serializers.Serializer):
    """
    Granular user agent, referrer, IP resolution and session metadata records.
    """
    id = serializers.CharField(read_only=True)
    website_id = serializers.CharField()
    page_id = serializers.CharField(required=False, allow_null=True)
    path = serializers.CharField(max_length=500)
    visitor_id = serializers.CharField(max_length=100)
    ip_address = serializers.IPAddressField()
    device = serializers.CharField(max_length=50)
    browser = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    referrer = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")
    created_at = serializers.DateTimeField(read_only=True)


class StatItemSerializer(serializers.Serializer):
    key = serializers.CharField()
    count = serializers.IntegerField()


class AnalyticsAggregateSerializer(serializers.Serializer):
    """
    Consolidated operational metrics over specified periods.
    """
    total_page_views = serializers.IntegerField()
    unique_visitors = serializers.IntegerField()
    devices = StatItemSerializer(many=True)
    browsers = StatItemSerializer(many=True)
    countries = StatItemSerializer(many=True)
    referrers = StatItemSerializer(many=True)
    top_pages = StatItemSerializer(many=True)
    top_websites = StatItemSerializer(many=True)


# ==========================================
# 7. PUBLIC DELIVERY & OPTIMIZATION SERIALIZERS
# ==========================================

class ImageOptimizationSerializer(serializers.Serializer):
    """
    Instruction sets for real-time asset resizing, compression, and caching rules.
    """
    url = serializers.URLField()
    width = serializers.IntegerField(required=False, min_value=1, max_value=3840)
    height = serializers.IntegerField(required=False, min_value=1, max_value=3840)
    quality = serializers.IntegerField(default=85, min_value=1, max_value=100)
    format = serializers.ChoiceField(choices=[("webp", "webp"), ("png", "png"), ("jpg", "jpg"), ("original", "original")], default="webp")


class AssetVersionSerializer(serializers.Serializer):
    """
    Cache metadata containing file digests, caching headers, and version numbers.
    """
    asset_id = serializers.CharField()
    version = serializers.CharField()
    md5_digest = serializers.CharField()
    cache_control = serializers.CharField(default="public, max-age=31536000, immutable")
    file_size = serializers.IntegerField()


# ==========================================
# 8. RENDER SERIALIZERS (HYDRATED RENDER PAYLOADS)
# ==========================================

class PageRenderSerializer(serializers.Serializer):
    id = serializers.CharField()
    slug = serializers.CharField()
    title = serializers.CharField()
    page_type = serializers.CharField()
    seo = serializers.JSONField()
    sections = serializers.JSONField()


class WebsiteRenderSerializer(serializers.Serializer):
    """
    Fully unified hierarchy incorporating navigation layout trees, default custom themes,
    and nested pages ready for direct compilation or rendering engine consumption.
    """
    website = serializers.JSONField()
    theme = serializers.JSONField()
    navigation = serializers.JSONField()
    pages = PageRenderSerializer(many=True)
    footer = serializers.JSONField()
    security = serializers.JSONField()


class AuthorProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = AuthorProfile
        fields = ["id", "user", "user_email", "name", "bio", "avatar_url", "verified", "metadata", "created_at", "updated_at"]
        read_only_fields = ["id", "verified", "created_at", "updated_at"]


class PublisherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublisherProfile
        fields = ["id", "name", "description", "website_url", "logo_url", "verified", "created_at", "updated_at"]
        read_only_fields = ["id", "verified", "created_at", "updated_at"]


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source="author.name")
    publisher_name = serializers.ReadOnlyField(source="publisher.name")

    class Meta:
        model = Book
        fields = [
            "id", "title", "slug", "description", "isbn", "status", "book_type", 
            "price", "author", "author_name", "publisher", "publisher_name", 
            "cover_image_url", "preview_file_url", "full_file_url", "inventory_count", 
            "metadata", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductOwnershipSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source="book.title")
    course_title = serializers.ReadOnlyField(source="course.title")
    owner_email = serializers.ReadOnlyField(source="owner_user.email")

    class Meta:
        model = ProductOwnership
        fields = ["id", "book", "book_title", "course", "course_title", "owner_type", "owner_user", "owner_email", "commission_rate", "wallet_destination", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source="book.title")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = OrderItem
        fields = ["id", "order", "book", "book_title", "course", "course_title", "price"]


class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "user_email", "total_amount", "status", "items", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "total_amount", "created_at", "updated_at"]


class ReadingProgressSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    book_title = serializers.ReadOnlyField(source="book.title")

    class Meta:
        model = ReadingProgress
        fields = ["id", "user", "user_email", "book", "book_title", "progress_percentage", "current_location", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
