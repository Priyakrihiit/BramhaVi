from rest_framework import serializers
import uuid

class SEOSerializer(serializers.Serializer):
    """
    Metadata schemas detailing search-engine discovery options, open-graph cards,
    canonical routes, and XML sitemaps declarations.
    """
    meta_title = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    meta_description = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")
    keywords = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")
    opengraph_image = serializers.URLField(required=False, allow_null=True, default=None)
    twitter_card = serializers.CharField(max_length=100, required=False, allow_blank=True, default="summary_large_image")
    canonical_url = serializers.URLField(required=False, allow_null=True, default=None)
    robots = serializers.CharField(max_length=255, required=False, allow_blank=True, default="index, follow")
    sitemap_support = serializers.BooleanField(default=True)


class FooterLinkSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=100)
    url = serializers.CharField(max_length=255)


class FooterColumnSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    links = FooterLinkSerializer(many=True, default=[])


class FooterBuilderSerializer(serializers.Serializer):
    """
    Enterprise footer layout builder supporting custom columns, links, copyright annotations,
    and responsive SVG vector social channels.
    """
    footer_columns = FooterColumnSerializer(many=True, default=[])
    copyright_text = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    social_icons = serializers.ListField(child=serializers.CharField(max_length=50), default=[])


class WebsiteSerializer(serializers.Serializer):
    """
    Top-level Portfolio container managing free subdomain registration,
    custom top-level domains, and publication workflows.
    """
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    user_id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)
    subdomain = serializers.CharField(max_length=100)
    custom_domain = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    status = serializers.ChoiceField(choices=[("draft", "draft"), ("published", "published"), ("archived", "archived")], default="draft")
    footer_builder = FooterBuilderSerializer(required=False, default=dict)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)

    def validate_subdomain(self, value):
        import re
        if not re.match(r"^[a-zA-Z0-9\-]+$", value):
            raise serializers.ValidationError("Subdomain can only contain alphanumeric characters and hyphens.")
        return value.lower().strip()


class PageSerializer(serializers.Serializer):
    """
    Layout templates defining visual and semantic boundaries for individual pages.
    """
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    website_id = serializers.UUIDField()
    slug = serializers.CharField(max_length=255)
    title = serializers.CharField(max_length=255)
    page_type = serializers.ChoiceField(choices=[
        ("home", "home"), ("about", "about"), ("services", "services"),
        ("projects", "projects"), ("portfolio", "portfolio"), ("skills", "skills"),
        ("experience", "experience"), ("education", "education"), ("team", "team"),
        ("pricing", "pricing"), ("testimonials", "testimonials"), ("gallery", "gallery"),
        ("contact", "contact"), ("blog", "blog"), ("faq", "faq"),
        ("privacy_policy", "privacy_policy"), ("terms", "terms"), ("custom", "custom")
    ], default="custom")
    is_published = serializers.BooleanField(default=False)
    display_order = serializers.IntegerField(default=0)
    seo = SEOSerializer(required=False, default=dict)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)

    def validate_slug(self, value):
        import re
        if value != "/" and not re.match(r"^[a-zA-Z0-9\-_\/]+$", value):
            raise serializers.ValidationError("Slug can only contain letters, numbers, hyphens, underscores, and forward slashes.")
        return value.lower().strip()


class NavigationMenuSerializer(serializers.Serializer):
    """
    Dynamic visual links supporting nested hierarchies and order management.
    """
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    website_id = serializers.UUIDField()
    parent_id = serializers.CharField(required=False, allow_null=True, default=None)
    label = serializers.CharField(max_length=100)
    url = serializers.CharField(max_length=255)
    icon = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    display_order = serializers.IntegerField(default=0)
    is_visible = serializers.BooleanField(default=True)
    is_external = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)


class ThemeSerializer(serializers.Serializer):
    """
    Styling properties including palettes, typography and visual layout settings.
    """
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    website_id = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    theme_type = serializers.ChoiceField(choices=[("light", "light"), ("dark", "dark"), ("custom", "custom")], default="light")
    primary_color = serializers.CharField(max_length=50, default="#1A1A1A")
    secondary_color = serializers.CharField(max_length=50, default="#4A4A4A")
    background_color = serializers.CharField(max_length=50, default="#FAFAFA")
    text_color = serializers.CharField(max_length=50, default="#212121")
    font_family_sans = serializers.CharField(max_length=100, default="Inter")
    font_family_heading = serializers.CharField(max_length=100, default="Outfit")
    layout_style = serializers.CharField(max_length=50, default="clean-grid")
    animation_settings = serializers.JSONField(required=False, default=dict)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)


class MediaItemSerializer(serializers.Serializer):
    """
    Assets index representing custom logo images, resume PDFs, hero cover-photos, or vectors.
    """
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    website_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    file_type = serializers.ChoiceField(choices=[
        ("image", "image"), ("video", "video"), ("pdf", "pdf"), ("icon", "icon"), ("logo", "logo")
    ], default="image")
    file_size = serializers.IntegerField()
    url = serializers.URLField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)


class SectionSerializer(serializers.Serializer):
    """
    Flexible content containers rendering specific grid modules on specific pages.
    """
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    page_id = serializers.UUIDField()
    section_type = serializers.ChoiceField(choices=[
        ("hero", "hero"), ("about", "about"), ("services", "services"),
        ("projects", "projects"), ("skills", "skills"), ("experience", "experience"),
        ("education", "education"), ("team", "team"), ("gallery", "gallery"),
        ("testimonials", "testimonials"), ("pricing", "pricing"),
        ("contact_form", "contact_form"), ("blog_posts", "blog_posts")
    ])
    title = serializers.CharField(max_length=255)
    subtitle = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")
    content = serializers.JSONField(required=False, default=dict)
    display_order = serializers.IntegerField(default=0)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)


class ResumeSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    template_name = serializers.CharField(max_length=100, default="modern")
    data = serializers.JSONField(required=False, default=dict)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class JobListingSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    title = serializers.CharField(max_length=255)
    company_name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=10000)
    location = serializers.CharField(max_length=255, default="Remote")
    job_type = serializers.CharField(max_length=100, default="FULL_TIME")
    salary_range = serializers.CharField(max_length=255, default="Competitive")
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CareerRoadmapSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4, read_only=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=2000)
    milestones = serializers.JSONField(required=False, default=list)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
