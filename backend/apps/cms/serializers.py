import re
import datetime
from rest_framework import serializers
from apps.cms.models import (
    Page, NavigationMenu, Tutorial, Forum, ForumTopic, ForumPost, Blog, Comment, Like, Report,
    Category, Tag, Author, Article, MediaFile, BlockTemplate, ContentBlock, PageVersion,
    Revision, WorkflowState, WorkflowLog, PublishSchedule, CMSRedirect, CMSAuditTrail,
    CMSSearchIndex, ContentPermission, FAQ, Reaction,
    Folder, MediaCollection, MediaVersion, MediaMetadata, MediaPermission, MediaAudit, MediaShare,
    MediaThumbnail, MediaConversion, MediaDownloadLog, MediaFavorite, MediaComment, MediaWorkflow, MediaTag
)

def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text:
        return {}, ""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if match:
        meta_str = match.group(1)
        body = match.group(2)
        meta = {}
        for line in meta_str.split("\n"):
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        return meta, body
    return {}, text

def format_front_matter(meta: dict, body: str) -> str:
    if not meta:
        return body or ""
    lines = ["---"]
    for k, v in meta.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n" + (body or "")


class PageSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source="author.email")
    revisions = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            "id", "slug", "title", "layout_data", "is_published", 
            "author", "author_email", "revisions", "created_at", "updated_at"
        ]

    def get_revisions(self, obj):
        if isinstance(obj.layout_data, dict):
            return obj.layout_data.get("_revisions", [])
        return []


class NavigationMenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = NavigationMenu
        fields = [
            "id", "parent", "permission", "label", "url", "icon", 
            "display_order", "children", "created_at", "updated_at"
        ]

    def get_children(self, obj):
        # Prevent deep serialization loops by checking context or limiting depth
        depth = self.context.get("depth", 0)
        if depth > 5:
            return []
        children = obj.children.all().order_by("display_order")
        # Reuse this serializer with incremented depth in context
        context = dict(self.context)
        context["depth"] = depth + 1
        return NavigationMenuSerializer(children, many=True, context=context).data


class TutorialSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source="author.email")
    category = serializers.CharField(required=False, allow_blank=True)
    difficulty = serializers.CharField(required=False, allow_blank=True)
    estimated_duration = serializers.CharField(required=False, allow_blank=True)
    thumbnail = serializers.CharField(required=False, allow_blank=True)
    seo_slug = serializers.CharField(required=False, allow_blank=True)
    body_content = serializers.CharField(source="content", required=False)

    class Meta:
        model = Tutorial
        fields = [
            "id", "title", "slug", "content", "body_content", "author", "author_email", 
            "is_published", "published_at", "category", "difficulty", 
            "estimated_duration", "thumbnail", "seo_slug", "created_at", "updated_at"
        ]
        read_only_fields = ["published_at"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        meta, body = parse_front_matter(instance.content)
        ret["category"] = meta.get("category", "")
        ret["difficulty"] = meta.get("difficulty", "")
        ret["estimated_duration"] = meta.get("estimated_duration", "")
        ret["thumbnail"] = meta.get("thumbnail", "")
        ret["seo_slug"] = meta.get("seo_slug", instance.slug)
        ret["body_content"] = body
        return ret

    def to_internal_value(self, data):
        # We need to construct content from body_content & frontmatter keys
        internal_value = super().to_internal_value(data)
        
        # Extract metadata from incoming data
        category = data.get("category", "")
        difficulty = data.get("difficulty", "")
        estimated_duration = data.get("estimated_duration", "")
        thumbnail = data.get("thumbnail", "")
        seo_slug = data.get("seo_slug", data.get("slug", ""))
        body_content = data.get("body_content", data.get("content", ""))

        meta = {}
        if category: meta["category"] = category
        if difficulty: meta["difficulty"] = difficulty
        if estimated_duration: meta["estimated_duration"] = estimated_duration
        if thumbnail: meta["thumbnail"] = thumbnail
        if seo_slug: meta["seo_slug"] = seo_slug

        # Set the merged content
        internal_value["content"] = format_front_matter(meta, body_content)
        return internal_value


class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source="author.email")
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "blog", "parent", "author", "author_email", "content", "replies", "likes_count", "created_at", "updated_at"]

    def get_replies(self, obj):
        # Limit recursion depth to avoid infinite loops
        depth = self.context.get("comment_depth", 0)
        if depth > 5:
            return []
        replies_qs = obj.replies.filter(deleted_at__isnull=True).order_by("created_at")
        context = dict(self.context)
        context["comment_depth"] = depth + 1
        return CommentSerializer(replies_qs, many=True, context=context).data

    def get_likes_count(self, obj):
        return obj.likes.count()


class BlogSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source="author.email")
    comments = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    
    # Metadata fields persisted in content front-matter
    featured_image = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.CharField(required=False, allow_blank=True)
    categories = serializers.CharField(required=False, allow_blank=True)
    scheduled_at = serializers.CharField(required=False, allow_blank=True)
    body_content = serializers.CharField(source="content", required=False)

    class Meta:
        model = Blog
        fields = [
            "id", "title", "slug", "content", "body_content", "author", "author_email", 
            "is_published", "published_at", "comments", "comments_count", "likes_count", "views_count",
            "featured_image", "tags", "categories", "scheduled_at", "created_at", "updated_at"
        ]
        read_only_fields = ["published_at"]

    def get_comments(self, obj):
        # Only return root level comments (parent is null) inside blog detail
        root_comments = obj.comments.filter(parent__isnull=True, deleted_at__isnull=True).order_by("created_at")
        return CommentSerializer(root_comments, many=True, context=self.context).data

    def get_comments_count(self, obj):
        return obj.comments.filter(deleted_at__isnull=True).count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_views_count(self, obj):
        meta, _ = parse_front_matter(obj.content)
        try:
            return int(meta.get("_views_count", 0))
        except ValueError:
            return 0

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        meta, body = parse_front_matter(instance.content)
        ret["featured_image"] = meta.get("featured_image", "")
        ret["tags"] = meta.get("tags", "")
        ret["categories"] = meta.get("categories", "")
        ret["scheduled_at"] = meta.get("scheduled_at", "")
        ret["body_content"] = body
        return ret

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        
        featured_image = data.get("featured_image", "")
        tags = data.get("tags", "")
        categories = data.get("categories", "")
        scheduled_at = data.get("scheduled_at", "")
        body_content = data.get("body_content", data.get("content", ""))

        # Preserve existing _views_count if editing
        views_count = 0
        if self.instance:
            meta_old, _ = parse_front_matter(self.instance.content)
            views_count = meta_old.get("_views_count", "0")

        meta = {}
        if featured_image: meta["featured_image"] = featured_image
        if tags: meta["tags"] = tags
        if categories: meta["categories"] = categories
        if scheduled_at: meta["scheduled_at"] = scheduled_at
        meta["_views_count"] = str(views_count)

        internal_value["content"] = format_front_matter(meta, body_content)
        return internal_value


class ForumPostSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source="author.email")
    likes_count = serializers.SerializerMethodField()
    parent_post_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    body_content = serializers.CharField(source="content", required=False)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = [
            "id", "topic", "author", "author_email", "content", "body_content", 
            "parent_post_id", "likes_count", "replies", "created_at", "updated_at"
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_replies(self, obj):
        # Nested replies inside ForumPostViewSet can represent children
        depth = self.context.get("post_depth", 0)
        if depth > 5:
            return []
        
        # Since we don't have a direct database relation, we scan sibling posts in the same topic
        # and match whose parent_post_id in frontmatter is this post's id.
        # To avoid performance degradation, we cache or select appropriately.
        siblings = self.context.get("topic_posts_map")
        if siblings is None:
            # Fallback query
            sibling_posts = ForumPost.objects.filter(topic=obj.topic, deleted_at__isnull=True).order_by("created_at")
            siblings = []
            for sp in sibling_posts:
                meta, _ = parse_front_matter(sp.content)
                siblings.append({
                    "obj": sp,
                    "parent_post_id": meta.get("parent_post_id")
                })
        
        matching = [s["obj"] for s in siblings if s["parent_post_id"] == str(obj.id)]
        context = dict(self.context)
        context["post_depth"] = depth + 1
        return ForumPostSerializer(matching, many=True, context=context).data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        meta, body = parse_front_matter(instance.content)
        ret["parent_post_id"] = meta.get("parent_post_id", None)
        ret["body_content"] = body
        return ret

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        parent_post_id = data.get("parent_post_id", None)
        body_content = data.get("body_content", data.get("content", ""))

        meta = {}
        if parent_post_id:
            meta["parent_post_id"] = str(parent_post_id)

        internal_value["content"] = format_front_matter(meta, body_content)
        return internal_value


class ForumTopicSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source="author.email")
    forum_name = serializers.ReadOnlyField(source="forum.name")
    posts_count = serializers.SerializerMethodField()
    is_solved = serializers.SerializerMethodField()

    class Meta:
        model = ForumTopic
        fields = [
            "id", "forum", "forum_name", "author", "author_email", "title", 
            "is_pinned", "is_locked", "is_solved", "posts_count", "created_at", "updated_at"
        ]

    def get_posts_count(self, obj):
        return obj.posts.filter(deleted_at__isnull=True).count()

    def get_is_solved(self, obj):
        # Evaluated from the prefix "[SOLVED]" in the title
        return obj.title.startswith("[SOLVED]")


class ForumSerializer(serializers.ModelSerializer):
    topics_count = serializers.SerializerMethodField()

    class Meta:
        model = Forum
        fields = ["id", "name", "description", "topics_count", "created_at", "updated_at"]

    def get_topics_count(self, obj):
        return obj.topics.filter(deleted_at__isnull=True).count()


class LikeSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Like
        fields = ["id", "user", "user_email", "post", "blog", "comment", "created_at", "updated_at"]


class ReportSerializer(serializers.ModelSerializer):
    reporter_email = serializers.ReadOnlyField(source="reporter.email")

    class Meta:
        model = Report
        fields = ["id", "reporter", "reporter_email", "target_post", "target_comment", "reason", "status", "created_at", "updated_at"]


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model supporting parent-child hierarchy.
    """
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "description", "parent", "display_order",
            "children", "created_at", "updated_at", "deleted_at"
        ]
        read_only_fields = ["created_at", "updated_at", "deleted_at"]

    def get_children(self, obj):
        depth = self.context.get("category_depth", 0)
        if depth > 3:
            return []
        context = dict(self.context)
        context["category_depth"] = depth + 1
        return CategorySerializer(obj.children.filter(deleted_at__isnull=True), many=True, context=context).data

    def validate_slug(self, value):
        if not re.match(r'^[a-z0-9-]+$', value):
            raise serializers.ValidationError("Slug must contain only lowercase alphanumeric characters and hyphens.")
        return value

    def validate_title(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Category name must be at least 2 characters long.")
        return value

    def validate_name(self, value):
        return self.validate_title(value)


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for the Tag model.
    """
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "description", "usage_count", "created_at", "updated_at"]
        read_only_fields = ["usage_count", "created_at", "updated_at"]

    def validate_slug(self, value):
        if not re.match(r'^[a-z0-9-]+$', value):
            raise serializers.ValidationError("Slug must contain only lowercase alphanumeric characters and hyphens.")
        return value


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for Author profile details.
    """
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Author
        fields = [
            "id", "user", "user_email", "display_name", "bio", "avatar_url",
            "website_url", "twitter_handle", "linkedin_url", "is_active",
            "total_articles", "created_at", "updated_at"
        ]
        read_only_fields = ["total_articles", "created_at", "updated_at"]


class MediaFileSerializer(serializers.ModelSerializer):
    """
    Serializer for Media Library uploads.
    """
    uploader_email = serializers.ReadOnlyField(source="uploader.email")
    url = serializers.ReadOnlyField()

    class Meta:
        model = MediaFile
        fields = [
            "id", "uploader", "uploader_email", "file", "url", "original_filename",
            "file_type", "mime_type", "file_size_bytes", "width", "height",
            "alt_text", "caption", "tags", "folder", "is_public", "created_at", "updated_at", "deleted_at"
        ]
        read_only_fields = ["url", "file_size_bytes", "mime_type", "width", "height", "created_at", "updated_at", "deleted_at"]

    def validate_media(self, value):
        if value and value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 50MB.")
        return value

    def validate_file(self, value):
        return self.validate_media(value)


class BlockTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for reusable Page builder templates.
    """
    created_by_email = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = BlockTemplate
        fields = [
            "id", "name", "block_type", "schema", "preview_image_url",
            "is_active", "created_by", "created_by_email", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]


class ContentBlockSerializer(serializers.ModelSerializer):
    """
    Serializer for Content Block layout instances.
    """
    children = serializers.SerializerMethodField()

    class Meta:
        model = ContentBlock
        fields = [
            "id", "page", "template", "parent", "block_type", "data",
            "display_order", "is_visible", "css_classes", "custom_styles",
            "children", "created_at", "updated_at", "deleted_at"
        ]
        read_only_fields = ["created_at", "updated_at", "deleted_at"]

    def get_children(self, obj):
        depth = self.context.get("block_depth", 0)
        if depth > 4:
            return []
        context = dict(self.context)
        context["block_depth"] = depth + 1
        return ContentBlockSerializer(obj.children.filter(deleted_at__isnull=True), many=True, context=context).data


class PageVersionSerializer(serializers.ModelSerializer):
    """
    Serializer for Page Version snapshots.
    """
    author_email = serializers.ReadOnlyField(source="author.email")

    class Meta:
        model = PageVersion
        fields = [
            "id", "page", "version_number", "layout_data", "change_summary",
            "author", "author_email", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]


class RevisionSerializer(serializers.ModelSerializer):
    """
    Serializer for generic Article/Blog revisions.
    """
    author_email = serializers.ReadOnlyField(source="author.email")

    class Meta:
        model = Revision
        fields = [
            "id", "content_type", "content_id", "version_number", "snapshot",
            "change_summary", "author", "author_email", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]


class WorkflowStateSerializer(serializers.ModelSerializer):
    """
    Serializer for Article Workflow state.
    """
    assigned_to_email = serializers.ReadOnlyField(source="assigned_to.email")
    article_title = serializers.ReadOnlyField(source="article.title")

    class Meta:
        model = WorkflowState
        fields = [
            "id", "article", "article_title", "status", "assigned_to", "assigned_to_email",
            "due_date", "notes", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_status(self, value):
        valid_statuses = [c[0] for c in WorkflowState.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Choose from: {valid_statuses}")
        return value


class WorkflowLogSerializer(serializers.ModelSerializer):
    """
    Serializer for Workflow logs.
    """
    actor_email = serializers.ReadOnlyField(source="actor.email")

    class Meta:
        model = WorkflowLog
        fields = [
            "id", "workflow", "from_status", "to_status", "actor", "actor_email", "comment", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]


class PublishScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for scheduled publishing queue entries.
    """
    scheduled_by_email = serializers.ReadOnlyField(source="scheduled_by.email")

    class Meta:
        model = PublishSchedule
        fields = [
            "id", "content_type", "content_id", "scheduled_at", "status",
            "scheduled_by", "scheduled_by_email", "executed_at", "failure_reason", "created_at", "updated_at"
        ]
        read_only_fields = ["executed_at", "failure_reason", "created_at", "updated_at"]

    def validate_publish_date(self, value):
        if value and value < datetime.datetime.now(datetime.timezone.utc):
            raise serializers.ValidationError("Schedule date cannot be in the past.")
        return value

    def validate_scheduled_at(self, value):
        return self.validate_publish_date(value)


class CMSRedirectSerializer(serializers.ModelSerializer):
    """
    Serializer for CMSRedirect rules.
    """
    class Meta:
        model = CMSRedirect
        fields = ["id", "from_path", "to_path", "redirect_type", "is_active", "hit_count", "notes", "created_at", "updated_at"]
        read_only_fields = ["hit_count", "created_at", "updated_at"]

    def validate_slug(self, value):
        if value and not value.startswith("/"):
            raise serializers.ValidationError("Redirect path must start with a slash '/'.")
        return value

    def validate_from_path(self, value):
        return self.validate_slug(value)


class CMSAuditTrailSerializer(serializers.ModelSerializer):
    """
    Serializer for Audit logs.
    """
    actor_email = serializers.ReadOnlyField(source="actor.email")

    class Meta:
        model = CMSAuditTrail
        fields = [
            "id", "actor", "actor_email", "action", "content_type", "content_id", "content_title",
            "before_state", "after_state", "ip_address", "user_agent", "request_id", "created_at", "updated_at"
        ]
        read_only_fields = [
            "actor", "actor_email", "action", "content_type", "content_id", "content_title",
            "before_state", "after_state", "ip_address", "user_agent", "request_id", "created_at", "updated_at"
        ]


class CMSSearchIndexSerializer(serializers.ModelSerializer):
    """
    Serializer for Full-text Search Index.
    """
    class Meta:
        model = CMSSearchIndex
        fields = [
            "id", "content_type", "content_id", "title", "excerpt", "body",
            "tags", "categories", "author_name", "url_path", "is_published", "published_at", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]


class ContentPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for object-level Content Permission (CBAC).
    """
    user_email = serializers.ReadOnlyField(source="user.email")
    granted_by_email = serializers.ReadOnlyField(source="granted_by.email")

    class Meta:
        model = ContentPermission
        fields = [
            "id", "user", "user_email", "content_type", "content_id",
            "permission_type", "granted_by", "granted_by_email", "expires_at", "created_at", "updated_at"
        ]
        read_only_fields = ["granted_by", "created_at", "updated_at"]


class FAQSerializer(serializers.ModelSerializer):
    """
    Serializer for FAQ entries.
    """
    class Meta:
        model = FAQ
        fields = [
            "id", "question", "answer", "category", "tags", "display_order",
            "is_published", "views_count", "is_featured", "created_at", "updated_at", "deleted_at"
        ]
        read_only_fields = ["views_count", "created_at", "updated_at", "deleted_at"]


class ReactionSerializer(serializers.ModelSerializer):
    """
    Serializer for content Reaction records.
    """
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Reaction
        fields = ["id", "user", "user_email", "reaction_type", "article", "blog", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        article = attrs.get("article")
        blog = attrs.get("blog")
        if article and blog:
            raise serializers.ValidationError("Reaction cannot be attached to both Article and Blog.")
        if not article and not blog:
            raise serializers.ValidationError("Reaction must be attached to either Article or Blog.")
        return attrs


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for long-form Editorial Articles.
    """
    author_email = serializers.ReadOnlyField(source="author.email")
    reading_time_minutes = serializers.ReadOnlyField()

    class Meta:
        model = Article
        fields = [
            "id", "title", "slug", "content_type", "status", "author", "author_email", "cms_author",
            "categories", "tags", "featured_image", "excerpt", "body", "reading_time_minutes",
            "is_published", "is_featured", "is_pinned", "views_count", "likes_count", "comments_count",
            "allow_comments", "published_at", "custom_css", "custom_js", "meta_title", "meta_description",
            "og_image_url", "schema_json", "canonical_url", "created_at", "updated_at", "deleted_at"
        ]
        read_only_fields = ["reading_time_minutes", "views_count", "likes_count", "comments_count", "created_at", "updated_at", "deleted_at"]

    def validate_slug(self, value):
        if not re.match(r'^[a-z0-9-]+$', value):
            raise serializers.ValidationError("Slug must contain only lowercase letters, numbers, and hyphens.")
        return value

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value

    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Article.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status: {value}. Allowed choices: {valid_statuses}")
        return value

    def validate_publish_date(self, value):
        if value and value < datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=365):
            raise serializers.ValidationError("Publish date cannot be more than 1 year in the past.")
        return value

    def validate_published_at(self, value):
        return self.validate_publish_date(value)

    def validate_category(self, value):
        if not value:
            raise serializers.ValidationError("At least one category must be assigned.")
        return value

    def validate_categories(self, value):
        return self.validate_category(value)

    def validate_tags(self, value):
        return value

    def validate_media(self, value):
        if value and getattr(value, "file_type", None) != "image":
            raise serializers.ValidationError("Featured image must be of type 'image'.")
        return value

    def validate_featured_image(self, value):
        return self.validate_media(value)

    def validate(self, attrs):
        status = attrs.get("status")
        is_published = attrs.get("is_published")
        published_at = attrs.get("published_at")

        if is_published and status != "published":
            raise serializers.ValidationError("If the article is marked as published, the status must be 'published'.")
        if status == "published":
            attrs["is_published"] = True
            if not published_at:
                attrs["published_at"] = datetime.datetime.now(datetime.timezone.utc)

        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.cms_author:
            ret["cms_author_details"] = AuthorSerializer(instance.cms_author).data
        if instance.featured_image:
            ret["featured_image_details"] = MediaFileSerializer(instance.featured_image).data
        ret["categories_details"] = CategorySerializer(instance.categories.filter(deleted_at__isnull=True), many=True).data
        ret["tags_details"] = TagSerializer(instance.tags.all(), many=True).data
        return ret


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ["id", "name", "parent", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaCollection
        fields = ["id", "name", "description", "user", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaVersion
        fields = ["id", "media_file", "file", "version_number", "created_by", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaMetadata
        fields = ["id", "media_file", "metadata_json", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaTag
        fields = ["id", "name", "slug"]


class MediaPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaPermission
        fields = ["id", "media_file", "user", "permission_type", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAudit
        fields = ["id", "media_file", "actor", "action", "details", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaShare
        fields = ["id", "media_file", "shared_by", "shared_with", "expires_at", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaThumbnail
        fields = ["id", "media_file", "file", "size_label", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaConversionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaConversion
        fields = ["id", "media_file", "file", "format", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaDownloadLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaDownloadLog
        fields = ["id", "media_file", "user", "downloaded_at", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFavorite
        fields = ["id", "media_file", "user", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaComment
        fields = ["id", "media_file", "user", "comment", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class MediaWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaWorkflow
        fields = ["id", "media_file", "status", "assigned_to", "notes", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
