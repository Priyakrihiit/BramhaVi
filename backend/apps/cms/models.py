import uuid
import os
from django.db import models
from django.conf import settings

# GIN index is PostgreSQL-specific; guard import for SQLite dev environments
try:
    from django.contrib.postgres.indexes import GinIndex
    _HAS_GIN = True
except ImportError:
    GinIndex = None
    _HAS_GIN = False

from apps.base_models import BaseModel, SoftDeleteModel


class Page(SoftDeleteModel):
    """
    Dynamic web layouts crafted via Page Builders.
    """
    slug = models.CharField(max_length=255, help_text="Unique URL path identifier.")
    title = models.CharField(max_length=255, help_text="Page visual title.")
    layout_data = models.JSONField(
        default=dict,
        help_text="Nested layout structure (blocks, grids, banners)."
    )
    is_published = models.BooleanField(default=False, help_text="Indicates if the page is active and visible.")
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pages",
        help_text="User who authored the page layout."
    )

    class Meta:
        db_table = "pages"
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_pages_slug"
            )
        ]
        indexes = (
            [GinIndex(fields=["layout_data"], name="idx_pages_layout_data_gin")] if _HAS_GIN else []
        ) + [
            models.Index(
                fields=["slug"],
                condition=models.Q(is_published=True, deleted_at__isnull=True),
                name="idx_pages_active_slug"
            )
        ]

    def __str__(self):
        return self.title


class NavigationMenu(BaseModel):
    """
    Dynamic header/sidebar navigation nodes supporting hierarchical linkages and RBAC visibility.
    """
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent menu node for nested navigation."
    )
    permission = models.ForeignKey(
        "users.Permission",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="navigation_menus",
        help_text="Visibility gate permission constraint."
    )
    label = models.CharField(max_length=100, help_text="Visual label displayed in navigation menu.")
    url = models.CharField(max_length=255, help_text="Target routing path.")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Lucide icon identifier name.")
    display_order = models.IntegerField(default=0, help_text="Display order sequence.")

    class Meta:
        db_table = "navigation_menus"
        verbose_name = "Navigation Menu"
        verbose_name_plural = "Navigation Menus"
        ordering = ["display_order"]

    def __str__(self):
        return self.label


class Tutorial(SoftDeleteModel):
    """
    Quick interactive markdown guide structures.
    """
    title = models.CharField(max_length=255, help_text="Tutorial visual title.")
    slug = models.CharField(max_length=255, help_text="Unique tutorial URL identifier.")
    content = models.TextField(help_text="Tutorial body content in Markdown format.")
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tutorials",
        help_text="Author user of tutorial."
    )
    is_published = models.BooleanField(default=False, help_text="Is tutorial visible to public?")
    published_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp of publication.")

    class Meta:
        db_table = "tutorials"
        verbose_name = "Tutorial"
        verbose_name_plural = "Tutorials"
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_tutorials_slug"
            )
        ]
        indexes = [
            models.Index(
                fields=["slug"],
                condition=models.Q(is_published=True, deleted_at__isnull=True),
                name="idx_tutorials_active_slug"
            )
        ]

    def __str__(self):
        return self.title


class Forum(BaseModel):
    """
    Main sub-community discussion board categories.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Forum category header name.")
    description = models.TextField(blank=True, null=True, help_text="Forum purpose summary.")

    class Meta:
        db_table = "forums"
        verbose_name = "Forum"
        verbose_name_plural = "Forums"

    def __str__(self):
        return self.name


class ForumTopic(SoftDeleteModel):
    """
    Discussion thread containers inside community boards.
    """
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name="topics", help_text="Parent forum category.")
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forum_topics",
        help_text="Thread creator user."
    )
    title = models.CharField(max_length=255, help_text="Thread title.")
    is_pinned = models.BooleanField(default=False, help_text="Pinned threads stay at the top of forums.")
    is_locked = models.BooleanField(default=False, help_text="Locked threads reject new replies.")

    class Meta:
        db_table = "forum_topics"
        verbose_name = "Forum Topic"
        verbose_name_plural = "Forum Topics"

    def __str__(self):
        return self.title


class ForumPost(SoftDeleteModel):
    """
    Replies inside forum topic threads.
    """
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name="posts", help_text="Parent thread.")
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forum_posts",
        help_text="Post author user."
    )
    content = models.TextField(help_text="Post rich markdown text content.")

    class Meta:
        db_table = "forum_posts"
        verbose_name = "Forum Post"
        verbose_name_plural = "Forum Posts"

    def __str__(self):
        return f"Post by {self.author.email if self.author else 'Anonymous'} on topic {self.topic.title}"


class Blog(SoftDeleteModel):
    """
    Public educational and announcements articles.
    """
    title = models.CharField(max_length=255, help_text="Blog visual title.")
    slug = models.CharField(max_length=255, help_text="Unique URL identifier.")
    content = models.TextField(help_text="Rich body text.")
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blogs",
        help_text="Blog post author user."
    )
    is_published = models.BooleanField(default=False, help_text="Is blog visible to public portal?")
    published_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp of publication.")

    class Meta:
        db_table = "blogs"
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_blogs_slug"
            )
        ]

    def __str__(self):
        return self.title


class Comment(SoftDeleteModel):
    """
    Comment threads attached to blogs/articles.
    """
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, blank=True, null=True, related_name="comments", help_text="Parent blog.")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies",
        help_text="Nested comment reference."
    )
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comments",
        help_text="Comment author user."
    )
    content = models.TextField(help_text="Comment text content.")

    class Meta:
        db_table = "comments"
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment {self.id} by {self.author.email if self.author else 'Anonymous'}"


class Like(BaseModel):
    """
    Community reaction/like tracking mappings.
    """
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="likes", help_text="User who liked.")
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, blank=True, null=True, related_name="likes", help_text="Linked forum post.")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, blank=True, null=True, related_name="likes", help_text="Linked blog.")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True, related_name="likes", help_text="Linked comment.")

    class Meta:
        db_table = "likes"
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                condition=models.Q(post__isnull=False),
                name="uq_likes_user_post"
            ),
            models.UniqueConstraint(
                fields=["user", "blog"],
                condition=models.Q(blog__isnull=False),
                name="uq_likes_user_blog"
            ),
            models.UniqueConstraint(
                fields=["user", "comment"],
                condition=models.Q(comment__isnull=False),
                name="uq_likes_user_comment"
            )
        ]

    def __str__(self):
        return f"Like by {self.user.email}"


class Report(BaseModel):
    """
    Community moderation complaints.
    """
    reporter = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_reports",
        help_text="User submitting complaint."
    )
    target_post = models.ForeignKey(
        ForumPost,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="moderation_reports",
        help_text="Violating forum post."
    )
    target_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="moderation_reports",
        help_text="Violating comment."
    )
    reason = models.TextField(help_text="Detailed reason for complaint.")
    status = models.CharField(
        max_length=50,
        default="PENDING",
        choices=[
            ("PENDING", "Pending Review"),
            ("RESOLVED", "Resolved"),
            ("DISMISSED", "Dismissed")
        ],
        help_text="Moderation ticket workflow status."
    )

    class Meta:
        db_table = "reports"
        verbose_name = "Report"
        verbose_name_plural = "Reports"

    def __str__(self):
        return f"Report {self.id} (Status: {self.status})"


# ============================================================
# SPRINT 15 — ENTERPRISE CMS EXTENSION MODELS
# All models below are new additions. Existing models above
# are preserved exactly as-is for backward compatibility.
# ============================================================


class Category(SoftDeleteModel):
    """
    Hierarchical content category system supporting nested parent-child taxonomy.
    Used for Articles, Blogs, Tutorials, FAQs, and Pages.
    """
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent category for nested taxonomy."
    )
    name = models.CharField(max_length=150, help_text="Category display name.")
    slug = models.CharField(max_length=150, help_text="URL-safe category identifier.")
    description = models.TextField(blank=True, null=True, help_text="Category purpose summary.")
    icon = models.CharField(max_length=100, blank=True, null=True, help_text="Icon class or emoji.")
    color = models.CharField(max_length=20, blank=True, null=True, help_text="HEX color for display.")
    is_active = models.BooleanField(default=True, help_text="Active category flag.")
    display_order = models.IntegerField(default=0, help_text="Sort order.")

    class Meta:
        db_table = "cms_categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["display_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_cms_category_slug"
            )
        ]

    def __str__(self):
        return self.name


class Tag(BaseModel):
    """
    Flat content tagging system for cross-content discovery and SEO.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Tag display name.")
    slug = models.CharField(max_length=100, unique=True, help_text="URL-safe tag identifier.")
    description = models.TextField(blank=True, null=True, help_text="Tag description.")
    usage_count = models.IntegerField(default=0, help_text="How many content items use this tag.")

    class Meta:
        db_table = "cms_tags"
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Author(BaseModel):
    """
    Extended author profile linked to User for CMS bylines and contributor pages.
    """
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="cms_author_profile",
        help_text="Linked platform user account."
    )
    display_name = models.CharField(max_length=150, help_text="Public author display name.")
    bio = models.TextField(blank=True, null=True, help_text="Short author biography.")
    avatar_url = models.CharField(max_length=512, blank=True, null=True, help_text="Author avatar image URL.")
    website_url = models.CharField(max_length=512, blank=True, null=True, help_text="Author personal website.")
    twitter_handle = models.CharField(max_length=100, blank=True, null=True, help_text="Twitter/X handle.")
    linkedin_url = models.CharField(max_length=512, blank=True, null=True, help_text="LinkedIn profile URL.")
    is_active = models.BooleanField(default=True, help_text="Show on public contributor page.")
    total_articles = models.IntegerField(default=0, help_text="Cached count of published articles.")

    class Meta:
        db_table = "cms_authors"
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return self.display_name


def cms_media_upload_path(instance, filename):
    """Compute upload path: cms/media/<year>/<month>/<filename>"""
    from django.utils import timezone
    now = timezone.now()
    return os.path.join("cms", "media", str(now.year), str(now.month).zfill(2), filename)


class MediaFile(SoftDeleteModel):
    """
    CMS Media Library — stores uploaded images, videos, and documents.
    """
    FILE_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("document", "Document"),
        ("other", "Other"),
    ]
    uploader = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cms_media_files",
        help_text="User who uploaded the file."
    )
    folder = models.ForeignKey(
        "Folder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="files",
        help_text="Target folder inside the hierarchy."
    )
    file = models.FileField(upload_to=cms_media_upload_path, help_text="Uploaded file path.")
    original_filename = models.CharField(max_length=255, help_text="Original file name before upload.")
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default="other", help_text="File category.")
    mime_type = models.CharField(max_length=100, blank=True, null=True, help_text="MIME type of the file.")
    file_size_bytes = models.BigIntegerField(default=0, help_text="File size in bytes.")
    width = models.IntegerField(null=True, blank=True, help_text="Image width in pixels.")
    height = models.IntegerField(null=True, blank=True, help_text="Image height in pixels.")
    alt_text = models.CharField(max_length=255, blank=True, null=True, help_text="Accessibility alt text.")
    caption = models.CharField(max_length=500, blank=True, null=True, help_text="Display caption.")
    tags = models.ManyToManyField(Tag, blank=True, related_name="media_files", help_text="Media tags.")
    is_public = models.BooleanField(default=True, help_text="Publicly accessible via URL.")

    class Meta:
        db_table = "cms_media_files"
        verbose_name = "Media File"
        verbose_name_plural = "Media Files"
        ordering = ["-created_at"]

    def __str__(self):
        return self.original_filename

    @property
    def url(self):
        """Return the public URL for the media file."""
        if self.file:
            try:
                return self.file.url
            except Exception:
                return ""
        return ""


class BlockTemplate(BaseModel):
    """
    Reusable page block templates for the visual page builder.
    """
    BLOCK_TYPE_CHOICES = [
        ("hero", "Hero Section"),
        ("text", "Rich Text"),
        ("image", "Image Block"),
        ("gallery", "Image Gallery"),
        ("cta", "Call To Action"),
        ("testimonial", "Testimonial"),
        ("pricing", "Pricing Table"),
        ("faq", "FAQ Block"),
        ("team", "Team Members"),
        ("stats", "Statistics"),
        ("video", "Video Embed"),
        ("form", "Contact Form"),
        ("columns", "Multi-Column"),
        ("spacer", "Spacer"),
        ("html", "Raw HTML"),
        ("custom", "Custom Block"),
    ]
    name = models.CharField(max_length=150, help_text="Template display name.")
    block_type = models.CharField(max_length=50, choices=BLOCK_TYPE_CHOICES, help_text="Block category.")
    schema = models.JSONField(default=dict, help_text="JSON Schema defining block fields and defaults.")
    preview_image_url = models.CharField(max_length=512, blank=True, null=True, help_text="Template preview thumbnail.")
    is_active = models.BooleanField(default=True, help_text="Available in page builder.")
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="block_templates",
        help_text="Template creator."
    )

    class Meta:
        db_table = "cms_block_templates"
        verbose_name = "Block Template"
        verbose_name_plural = "Block Templates"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.block_type})"


class ContentBlock(SoftDeleteModel):
    """
    Individual page builder block instance attached to a Page.
    Supports nested parent-child block hierarchy.
    """
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="content_blocks",
        help_text="Parent page."
    )
    template = models.ForeignKey(
        BlockTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="instances",
        help_text="Block template used."
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent block for nested layouts."
    )
    block_type = models.CharField(max_length=50, help_text="Block type identifier.")
    data = models.JSONField(default=dict, help_text="Block content data payload.")
    display_order = models.IntegerField(default=0, help_text="Position in page.")
    is_visible = models.BooleanField(default=True, help_text="Block visibility toggle.")
    css_classes = models.CharField(max_length=500, blank=True, null=True, help_text="Custom CSS class names.")
    custom_styles = models.TextField(blank=True, null=True, help_text="Inline style overrides.")

    class Meta:
        db_table = "cms_content_blocks"
        verbose_name = "Content Block"
        verbose_name_plural = "Content Blocks"
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.block_type} block on {self.page.title} (order={self.display_order})"


class PageVersion(BaseModel):
    """
    Immutable snapshot of a Page at a specific point in time.
    Enables full version history and one-click rollback.
    """
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="versions",
        help_text="Parent page."
    )
    version_number = models.IntegerField(help_text="Sequential version number.")
    layout_data = models.JSONField(default=dict, help_text="Full layout data snapshot at this version.")
    change_summary = models.CharField(max_length=500, blank=True, null=True, help_text="Short description of changes.")
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="page_versions",
        help_text="User who created this version."
    )

    class Meta:
        db_table = "cms_page_versions"
        verbose_name = "Page Version"
        verbose_name_plural = "Page Versions"
        ordering = ["-version_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["page", "version_number"],
                name="uq_page_version_number"
            )
        ]

    def __str__(self):
        return f"{self.page.title} v{self.version_number}"


class Article(SoftDeleteModel):
    """
    Full editorial content type for long-form articles, news, documentation,
    policies, legal pages, and marketing content.
    """
    CONTENT_TYPE_CHOICES = [
        ("article", "Article"),
        ("news", "News"),
        ("documentation", "Documentation"),
        ("policy", "Policy"),
        ("legal", "Legal Page"),
        ("marketing", "Marketing Page"),
        ("landing", "Landing Page"),
        ("about", "About Page"),
        ("careers", "Careers Page"),
        ("announcement", "Announcement"),
        ("press", "Press Release"),
        ("case_study", "Case Study"),
        ("white_paper", "White Paper"),
        ("guide", "Guide"),
        ("changelog", "Changelog"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("review", "In Review"),
        ("approved", "Approved"),
        ("published", "Published"),
        ("archived", "Archived"),
        ("rejected", "Rejected"),
        ("scheduled", "Scheduled"),
    ]
    title = models.CharField(max_length=255, help_text="Article title.")
    slug = models.CharField(max_length=255, help_text="Unique URL slug.")
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default="article", help_text="Content classification.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True, help_text="Editorial workflow status.")
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        help_text="Primary author."
    )
    cms_author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        help_text="CMS author profile for byline."
    )
    categories = models.ManyToManyField(Category, blank=True, related_name="articles", help_text="Content categories.")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles", help_text="Content tags.")
    featured_image = models.ForeignKey(
        MediaFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="featured_in_articles",
        help_text="Hero/featured image."
    )
    excerpt = models.TextField(blank=True, null=True, help_text="Short summary for listings and SEO.")
    body = models.TextField(help_text="Full article body (supports Markdown and HTML).")
    reading_time_minutes = models.IntegerField(default=0, help_text="Estimated reading time.")
    is_featured = models.BooleanField(default=False, db_index=True, help_text="Featured on homepage.")
    is_pinned = models.BooleanField(default=False, help_text="Pinned to top of listing.")
    views_count = models.IntegerField(default=0, db_index=True, help_text="Total view counter.")
    likes_count = models.IntegerField(default=0, help_text="Cached like counter.")
    comments_count = models.IntegerField(default=0, help_text="Cached comment counter.")
    allow_comments = models.BooleanField(default=True, help_text="Enable comments on this article.")
    is_published = models.BooleanField(default=False, db_index=True, help_text="Public visibility flag.")
    published_at = models.DateTimeField(null=True, blank=True, db_index=True, help_text="Timestamp of publication.")
    custom_css = models.TextField(blank=True, null=True, help_text="Per-article custom CSS overrides.")
    custom_js = models.TextField(blank=True, null=True, help_text="Per-article custom JS overrides.")
    meta_title = models.CharField(max_length=255, blank=True, null=True, help_text="SEO meta title override.")
    meta_description = models.TextField(blank=True, null=True, help_text="SEO meta description override.")
    og_image_url = models.CharField(max_length=512, blank=True, null=True, help_text="OpenGraph image URL.")
    schema_json = models.JSONField(default=dict, blank=True, help_text="JSON-LD structured data.")
    canonical_url = models.CharField(max_length=512, blank=True, null=True, help_text="Canonical URL override.")

    class Meta:
        db_table = "cms_articles"
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-published_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_cms_article_slug"
            )
        ]
        indexes = [
            models.Index(fields=["status", "is_published"], name="idx_article_status_published"),
            models.Index(fields=["content_type"], name="idx_article_content_type"),
            models.Index(fields=["published_at"], name="idx_article_published_at"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-calculate reading time: ~200 words per minute
        if self.body:
            word_count = len(self.body.split())
            self.reading_time_minutes = max(1, round(word_count / 200))
        super().save(*args, **kwargs)


class FAQ(SoftDeleteModel):
    """
    Frequently Asked Questions — supports categories, ordering, and rich answers.
    """
    question = models.CharField(max_length=500, help_text="The FAQ question text.")
    answer = models.TextField(help_text="Full answer (supports Markdown).")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faqs",
        help_text="FAQ category grouping."
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="faqs", help_text="FAQ tags.")
    display_order = models.IntegerField(default=0, help_text="Sort order within category.")
    is_published = models.BooleanField(default=False, help_text="Publicly visible.")
    views_count = models.IntegerField(default=0, help_text="View counter.")
    is_featured = models.BooleanField(default=False, help_text="Featured FAQ flag.")

    class Meta:
        db_table = "cms_faqs"
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ["display_order", "question"]

    def __str__(self):
        return self.question[:80]


class Reaction(BaseModel):
    """
    Emoji-based reactions on Articles and Blogs (love, fire, clap, etc.).
    """
    REACTION_CHOICES = [
        ("like", "👍 Like"),
        ("love", "❤️ Love"),
        ("clap", "👏 Clap"),
        ("fire", "🔥 Fire"),
        ("mind_blown", "🤯 Mind Blown"),
        ("sad", "😢 Sad"),
        ("angry", "😡 Angry"),
    ]
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="cms_reactions",
        help_text="Reacting user."
    )
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES, help_text="Reaction emoji type.")
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reactions",
        help_text="Linked article."
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reactions",
        help_text="Linked blog."
    )

    class Meta:
        db_table = "cms_reactions"
        verbose_name = "Reaction"
        verbose_name_plural = "Reactions"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "article"],
                condition=models.Q(article__isnull=False),
                name="uq_reaction_user_article"
            ),
            models.UniqueConstraint(
                fields=["user", "blog"],
                condition=models.Q(blog__isnull=False),
                name="uq_reaction_user_blog"
            ),
        ]

    def __str__(self):
        return f"{self.user} reacted {self.reaction_type}"


class Revision(BaseModel):
    """
    Generic content revision / diff record for Articles and Blogs.
    Stores the full content snapshot at each save for rollback capability.
    """
    CONTENT_TYPE_CHOICES = [
        ("article", "Article"),
        ("blog", "Blog"),
        ("page", "Page"),
        ("tutorial", "Tutorial"),
    ]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, help_text="Type of content revised.")
    content_id = models.UUIDField(db_index=True, help_text="UUID of the content record.")
    version_number = models.IntegerField(help_text="Sequential revision number.")
    snapshot = models.JSONField(default=dict, help_text="Full content snapshot at this revision.")
    change_summary = models.CharField(max_length=500, blank=True, null=True, help_text="Summary of changes.")
    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_revisions",
        help_text="User who created the revision."
    )

    class Meta:
        db_table = "cms_revisions"
        verbose_name = "Revision"
        verbose_name_plural = "Revisions"
        ordering = ["-version_number"]
        indexes = [
            models.Index(fields=["content_type", "content_id"], name="idx_revision_content"),
        ]

    def __str__(self):
        return f"{self.content_type} [{self.content_id}] v{self.version_number}"


class WorkflowState(BaseModel):
    """
    Editorial workflow state machine for Article publishing approval process.
    """
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted for Review"),
        ("review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("published", "Published"),
        ("archived", "Archived"),
        ("scheduled", "Scheduled"),
    ]
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="workflow_states",
        help_text="Article under workflow."
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True, help_text="Current workflow status.")
    assigned_to = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_workflows",
        help_text="Reviewer or editor assigned."
    )
    due_date = models.DateTimeField(null=True, blank=True, help_text="Review deadline.")
    notes = models.TextField(blank=True, null=True, help_text="Reviewer notes.")

    class Meta:
        db_table = "cms_workflow_states"
        verbose_name = "Workflow State"
        verbose_name_plural = "Workflow States"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.article.title} — {self.status}"


class WorkflowLog(BaseModel):
    """
    Immutable audit log of every editorial workflow state transition.
    """
    workflow = models.ForeignKey(
        WorkflowState,
        on_delete=models.CASCADE,
        related_name="logs",
        help_text="Parent workflow state."
    )
    from_status = models.CharField(max_length=20, help_text="Previous status.")
    to_status = models.CharField(max_length=20, help_text="New status after transition.")
    actor = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_actions",
        help_text="User who triggered the transition."
    )
    comment = models.TextField(blank=True, null=True, help_text="Reason or comment for transition.")

    class Meta:
        db_table = "cms_workflow_logs"
        verbose_name = "Workflow Log"
        verbose_name_plural = "Workflow Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_status} → {self.to_status} by {self.actor}"


class PublishSchedule(BaseModel):
    """
    Scheduled publishing queue — Celery picks up pending schedules and auto-publishes.
    """
    CONTENT_TYPE_CHOICES = [
        ("article", "Article"),
        ("blog", "Blog"),
        ("page", "Page"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("published", "Published"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
    ]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, help_text="Content type to publish.")
    content_id = models.UUIDField(db_index=True, help_text="UUID of content to publish.")
    scheduled_at = models.DateTimeField(db_index=True, help_text="When to auto-publish.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True, help_text="Schedule status.")
    scheduled_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publish_schedules",
        help_text="User who scheduled the publish."
    )
    executed_at = models.DateTimeField(null=True, blank=True, help_text="When the schedule was executed.")
    failure_reason = models.TextField(blank=True, null=True, help_text="Error message if publish failed.")

    class Meta:
        db_table = "cms_publish_schedules"
        verbose_name = "Publish Schedule"
        verbose_name_plural = "Publish Schedules"
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"Schedule {self.content_type} [{self.content_id}] at {self.scheduled_at}"


class CMSRedirect(BaseModel):
    """
    URL redirect manager — supports 301 and 302 redirects with regex matching.
    """
    REDIRECT_TYPE_CHOICES = [
        (301, "301 Permanent"),
        (302, "302 Temporary"),
    ]
    from_path = models.CharField(max_length=512, unique=True, db_index=True, help_text="Source URL path to redirect from.")
    to_path = models.CharField(max_length=512, help_text="Destination URL path.")
    redirect_type = models.IntegerField(choices=REDIRECT_TYPE_CHOICES, default=301, help_text="HTTP redirect type.")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Active redirect rule.")
    hit_count = models.IntegerField(default=0, help_text="Number of times redirect was triggered.")
    notes = models.CharField(max_length=500, blank=True, null=True, help_text="Admin notes for this redirect.")

    class Meta:
        db_table = "cms_redirects"
        verbose_name = "CMS Redirect"
        verbose_name_plural = "CMS Redirects"
        ordering = ["from_path"]

    def __str__(self):
        return f"{self.from_path} → {self.to_path} ({self.redirect_type})"


class CMSAuditTrail(BaseModel):
    """
    Granular audit log for all CMS write operations — create, update, delete, publish.
    Used for compliance, security review, and editorial accountability.
    """
    ACTION_CHOICES = [
        ("create", "Created"),
        ("update", "Updated"),
        ("delete", "Soft Deleted"),
        ("restore", "Restored"),
        ("publish", "Published"),
        ("unpublish", "Unpublished"),
        ("approve", "Approved"),
        ("reject", "Rejected"),
        ("schedule", "Scheduled"),
        ("rollback", "Rolled Back"),
    ]
    actor = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cms_audit_trail",
        help_text="User who performed the action."
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True, help_text="Type of action performed.")
    content_type = models.CharField(max_length=50, db_index=True, help_text="Content model type (article, blog, page, etc.).")
    content_id = models.CharField(max_length=100, db_index=True, help_text="ID of the affected content record.")
    content_title = models.CharField(max_length=255, blank=True, null=True, help_text="Title of the content for readability.")
    before_state = models.JSONField(default=dict, blank=True, help_text="Snapshot before the action.")
    after_state = models.JSONField(default=dict, blank=True, help_text="Snapshot after the action.")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Actor IP address.")
    user_agent = models.CharField(max_length=500, blank=True, null=True, help_text="Actor browser user agent.")
    request_id = models.CharField(max_length=100, blank=True, null=True, db_index=True, help_text="Request correlation ID.")

    class Meta:
        db_table = "cms_audit_trails"
        verbose_name = "CMS Audit Trail"
        verbose_name_plural = "CMS Audit Trails"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "content_id"], name="idx_audit_content"),
            models.Index(fields=["actor", "action"], name="idx_audit_actor_action"),
        ]

    def __str__(self):
        return f"[{self.action}] {self.content_type} by {self.actor}"


class CMSSearchIndex(BaseModel):
    """
    Full-text search index for CMS content — populated by Celery tasks.
    Enables fast PostgreSQL GIN-indexed search across all content types.
    """
    CONTENT_TYPE_CHOICES = [
        ("article", "Article"),
        ("blog", "Blog"),
        ("page", "Page"),
        ("tutorial", "Tutorial"),
        ("faq", "FAQ"),
    ]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, db_index=True, help_text="Content model type.")
    content_id = models.UUIDField(db_index=True, help_text="UUID of the indexed content.")
    title = models.CharField(max_length=255, help_text="Searchable title.")
    excerpt = models.TextField(blank=True, null=True, help_text="Searchable excerpt.")
    body = models.TextField(blank=True, null=True, help_text="Full searchable body text.")
    tags = models.CharField(max_length=1000, blank=True, null=True, help_text="Space-separated tag names for search.")
    categories = models.CharField(max_length=500, blank=True, null=True, help_text="Comma-separated category names.")
    author_name = models.CharField(max_length=150, blank=True, null=True, help_text="Author name for search.")
    url_path = models.CharField(max_length=512, help_text="Canonical public URL path.")
    is_published = models.BooleanField(default=True, db_index=True, help_text="Only index published content.")
    published_at = models.DateTimeField(null=True, blank=True, db_index=True, help_text="Publication timestamp for date-based search.")
    search_vector = models.TextField(blank=True, null=True, help_text="Pre-computed search tokens.")

    class Meta:
        db_table = "cms_search_index"
        verbose_name = "CMS Search Index"
        verbose_name_plural = "CMS Search Indexes"
        ordering = ["-published_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "content_id"],
                name="uq_search_index_content"
            )
        ]
        indexes = [
            models.Index(fields=["content_type", "is_published"], name="idx_search_type_published"),
        ]

    def __str__(self):
        return f"[{self.content_type}] {self.title}"


class ContentPermission(BaseModel):
    """
    Per-object content permission layer (CBAC) for CMS content.
    Allows fine-grained access control beyond global RBAC roles.
    """
    PERMISSION_TYPE_CHOICES = [
        ("read", "Read Only"),
        ("write", "Read & Write"),
        ("publish", "Can Publish"),
        ("admin", "Full Admin"),
    ]
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="content_permissions",
        help_text="Granted user (null = role-based)."
    )
    content_type = models.CharField(max_length=50, db_index=True, help_text="Content model type.")
    content_id = models.CharField(max_length=100, db_index=True, help_text="Target content ID (empty = all of type).")
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPE_CHOICES, help_text="Permission level granted.")
    granted_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_content_permissions",
        help_text="Admin who granted the permission."
    )
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional permission expiry.")

    class Meta:
        db_table = "cms_content_permissions"
        verbose_name = "Content Permission"
        verbose_name_plural = "Content Permissions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.permission_type} on {self.content_type} [{self.content_id}]"


class Folder(SoftDeleteModel):
    name = models.CharField(max_length=255, help_text="Folder name.")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent folder."
    )

    class Meta:
        db_table = "cms_folders"
        verbose_name = "Folder"
        verbose_name_plural = "Folders"

    def __str__(self):
        return self.name


class MediaCollection(SoftDeleteModel):
    name = models.CharField(max_length=255, help_text="Collection name.")
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="media_collections")

    class Meta:
        db_table = "cms_media_collections"

    def __str__(self):
        return self.name


class MediaVersion(SoftDeleteModel):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name="versions")
    file = models.FileField(upload_to=cms_media_upload_path)
    version_number = models.IntegerField(default=1)
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "cms_media_versions"


class MediaMetadata(SoftDeleteModel):
    media_file = models.OneToOneField(MediaFile, on_delete=models.CASCADE, related_name="metadata")
    metadata_json = models.JSONField(default=dict)

    class Meta:
        db_table = "cms_media_metadata"


class MediaTag(SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = "cms_media_tags"

    def __str__(self):
        return self.name


class MediaPermission(SoftDeleteModel):
    PERMISSION_CHOICES = [
        ("read", "Read"),
        ("write", "Write"),
        ("admin", "Admin"),
    ]
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name="permissions")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="media_permissions")
    permission_type = models.CharField(max_length=20, choices=PERMISSION_CHOICES)

    class Meta:
        db_table = "cms_media_permissions"


class MediaAudit(SoftDeleteModel):
    media_file = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    actor = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)
    details = models.JSONField(default=dict)

    class Meta:
        db_table = "cms_media_audits"


class MediaShare(SoftDeleteModel):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name="shares")
    shared_by = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="shared_media_sent")
    shared_with = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="shared_media_received", null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "cms_media_shares"


class MediaThumbnail(SoftDeleteModel):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name="thumbnails")
    file = models.FileField(upload_to=cms_media_upload_path)
    size_label = models.CharField(max_length=20)

    class Meta:
        db_table = "cms_media_thumbnails"


class MediaConversion(SoftDeleteModel):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name="conversions")
    file = models.FileField(upload_to=cms_media_upload_path)
    format = models.CharField(max_length=20)

    class Meta:
        db_table = "cms_media_conversions"


class MediaDownloadLog(SoftDeleteModel):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name="downloads")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cms_media_download_logs"


class MediaFavorite(SoftDeleteModel):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name="favorited_by")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    class Meta:
        db_table = "cms_media_favorites"
        unique_together = ("media_file", "user")


class MediaComment(SoftDeleteModel):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    comment = models.TextField()

    class Meta:
        db_table = "cms_media_comments"


class MediaWorkflow(SoftDeleteModel):
    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name="workflows")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    assigned_to = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "cms_media_workflows"
