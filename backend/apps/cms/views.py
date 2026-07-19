import uuid
import datetime
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.cms.models import (
    Page, NavigationMenu, Tutorial, Forum, ForumTopic, ForumPost, Blog, Comment, Like, Report,
    Category, Tag, Author, Article, MediaFile, BlockTemplate, ContentBlock, PageVersion,
    Revision, WorkflowState, WorkflowLog, PublishSchedule, CMSRedirect, CMSAuditTrail,
    CMSSearchIndex, ContentPermission, FAQ, Reaction,
    Folder, MediaCollection, MediaVersion, MediaMetadata, MediaPermission, MediaAudit, MediaShare,
    MediaThumbnail, MediaConversion, MediaDownloadLog, MediaFavorite, MediaComment, MediaWorkflow
)
from apps.users.permissions import HasRBACPermission
from apps.cms.permissions import (
    IsAdminOrCreatorOrReadOnly, IsCMSEditor, IsCMSAdmin, IsContentOwner,
    WorkflowPermission, MediaPermission, PublishPermission, RevisionPermission,
    IsMediaOwnerOrAdmin, MediaPermissionGate
)
from apps.cms.serializers import (
    PageSerializer, NavigationMenuSerializer, TutorialSerializer, ForumSerializer,
    ForumTopicSerializer, ForumPostSerializer, BlogSerializer, CommentSerializer,
    LikeSerializer, ReportSerializer, parse_front_matter, format_front_matter,
    CategorySerializer, TagSerializer, AuthorSerializer, ArticleSerializer, MediaFileSerializer,
    ContentBlockSerializer, BlockTemplateSerializer, PageVersionSerializer, RevisionSerializer,
    WorkflowStateSerializer, WorkflowLogSerializer, PublishScheduleSerializer, CMSRedirectSerializer,
    CMSAuditTrailSerializer, CMSSearchIndexSerializer, ContentPermissionSerializer, FAQSerializer,
    ReactionSerializer,
    FolderSerializer, MediaCollectionSerializer, MediaVersionSerializer, MediaMetadataSerializer,
    MediaTagSerializer, MediaPermissionSerializer, MediaAuditSerializer, MediaShareSerializer,
    MediaThumbnailSerializer, MediaConversionSerializer, MediaDownloadLogSerializer, MediaFavoriteSerializer,
    MediaCommentSerializer, MediaWorkflowSerializer
)
from apps.cms.services import PageLayoutService, WorkflowService, RevisionService, SearchIndexService, SEOIntegrationService


class EnterprisePagination(PageNumberPagination):
    """
    Standard enterprise pagination class specifying default page size and size override parameter.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class PageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on Pages with Soft Delete support,
    restore endpoint, and Public read access for published content.
    """
    queryset = Page.objects.select_related("author").all()
    serializer_class = PageSerializer
    permission_classes = [IsAdminOrCreatorOrReadOnly, HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug"]
    ordering_fields = ["title", "slug", "created_at"]
    ordering = ["title"]

    required_permissions = {
        "list": "cms:pages:read",
        "retrieve": "cms:pages:read",
        "create": "cms:pages:create",
        "update": "cms:pages:update",
        "partial_update": "cms:pages:update",
        "destroy": "cms:pages:delete",
        "publish": "cms:pages:update",
        "unpublish": "cms:pages:update",
        "rollback": "cms:pages:update",
        "revisions": "cms:pages:read",
    }

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_value = self.kwargs.get(self.lookup_field)
        
        is_uuid = False
        try:
            uuid.UUID(str(lookup_value))
            is_uuid = True
        except ValueError:
            pass

        if is_uuid:
            obj = get_object_or_404(queryset, id=lookup_value)
        else:
            obj = get_object_or_404(queryset, slug=lookup_value)
            
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN", "CONTENT_MANAGEMENT"])
        )

        if include_deleted and is_privileged:
            queryset = Page.all_objects.select_related("author").all()
        else:
            queryset = Page.objects.select_related("author").all()

        if is_privileged:
            pass
        elif user and user.is_authenticated:
            queryset = queryset.filter(Q(is_published=True) | Q(author=user))
        else:
            queryset = queryset.filter(is_published=True)

        is_published_param = self.request.query_params.get("is_published")
        if is_published_param is not None:
            queryset = queryset.filter(is_published=is_published_param.lower() == "true")

        author_param = self.request.query_params.get("author")
        if author_param:
            queryset = queryset.filter(author_id=author_param)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, id=None):
        page = self.get_object()
        page.is_published = True
        page.save(update_fields=["is_published", "updated_at"])
        serializer = self.get_serializer(page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, id=None):
        page = self.get_object()
        page.is_published = False
        page.save(update_fields=["is_published", "updated_at"])
        serializer = self.get_serializer(page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        user = self.request.user
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        page = Page.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not page:
            return Response({"detail": "Page not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        if not is_privileged and page.author != user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        page.restore()
        return Response({"detail": "Page restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="revisions")
    def revisions(self, request, id=None):
        page = self.get_object()
        revisions = []
        if isinstance(page.layout_data, dict):
            revisions = page.layout_data.get("_revisions", [])
        return Response(revisions, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="rollback")
    def rollback(self, request, id=None):
        page = self.get_object()
        version_number = request.data.get("version_number")
        if not version_number:
            return Response({"detail": "version_number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        result = PageLayoutService.rollback_page_to_revision(
            page_id=str(page.id),
            version_number=int(version_number),
            authorized_by=str(request.user.id)
        )
        if "error" in result:
            return Response({"detail": result["error"]}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result, status=status.HTTP_200_OK)


class NavigationMenuViewSet(viewsets.ModelViewSet):
    queryset = NavigationMenu.objects.select_related("parent", "permission").all().order_by("display_order")
    serializer_class = NavigationMenuSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["label", "url"]
    ordering_fields = ["label", "display_order", "created_at"]
    ordering = ["display_order"]

    required_permissions = {
        "list": "cms:menus:read",
        "retrieve": "cms:menus:read",
        "create": "cms:menus:write",
        "update": "cms:menus:write",
        "partial_update": "cms:menus:write",
        "destroy": "cms:menus:write",
        "tree": "cms:menus:read",
        "reorder": "cms:menus:write",
    }

    def get_queryset(self):
        queryset = self.queryset
        parent_param = self.request.query_params.get("parent")
        if parent_param:
            if parent_param.lower() in ["null", "none"]:
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_param)
        return queryset

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        tree_data = PageLayoutService.compile_navigation_tree()
        return Response(tree_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="reorder")
    def reorder(self, request):
        items = request.data.get("items", [])
        if not isinstance(items, list):
            return Response({"detail": "items list is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        for item in items:
            menu_id = item.get("id")
            display_order = item.get("display_order", 0)
            parent_id = item.get("parent", None)
            
            if menu_id:
                try:
                    menu = NavigationMenu.objects.get(id=menu_id)
                    menu.display_order = display_order
                    if parent_id:
                        menu.parent_id = parent_id
                    else:
                        menu.parent = None
                    menu.save(update_fields=["display_order", "parent", "updated_at"])
                except NavigationMenu.DoesNotExist:
                    pass
        
        return Response({"detail": "Menu order updated successfully."}, status=status.HTTP_200_OK)


class TutorialViewSet(viewsets.ModelViewSet):
    queryset = Tutorial.objects.select_related("author").all().order_by("title")
    serializer_class = TutorialSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug", "content"]
    ordering_fields = ["title", "slug", "created_at"]
    ordering = ["title"]

    required_permissions = {
        "list": "cms:tutorials:read",
        "retrieve": "cms:tutorials:read",
        "create": "cms:tutorials:write",
        "update": "cms:tutorials:write",
        "partial_update": "cms:tutorials:write",
        "destroy": "cms:tutorials:write",
        "restore": "cms:tutorials:write",
        "publish": "cms:tutorials:write",
        "unpublish": "cms:tutorials:write",
    }

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_value = self.kwargs.get(self.lookup_field)
        
        is_uuid = False
        try:
            uuid.UUID(str(lookup_value))
            is_uuid = True
        except ValueError:
            pass

        if is_uuid:
            obj = get_object_or_404(queryset, id=lookup_value)
        else:
            obj = get_object_or_404(queryset, slug=lookup_value)
            
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        if include_deleted and is_privileged:
            queryset = Tutorial.all_objects.select_related("author").all()
        else:
            queryset = Tutorial.objects.select_related("author").all()

        if is_privileged:
            pass
        elif user and user.is_authenticated:
            queryset = queryset.filter(Q(is_published=True) | Q(author=user))
        else:
            queryset = queryset.filter(is_published=True)

        is_published_param = self.request.query_params.get("is_published")
        if is_published_param is not None:
            queryset = queryset.filter(is_published=is_published_param.lower() == "true")

        author_param = self.request.query_params.get("author")
        if author_param:
            queryset = queryset.filter(author_id=author_param)

        category_param = self.request.query_params.get("category")
        if category_param:
            queryset = queryset.filter(content__contains=f"category: {category_param}")

        difficulty_param = self.request.query_params.get("difficulty")
        if difficulty_param:
            queryset = queryset.filter(content__contains=f"difficulty: {difficulty_param}")

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, id=None):
        tutorial = self.get_object()
        tutorial.is_published = True
        tutorial.published_at = timezone.now()
        tutorial.save(update_fields=["is_published", "published_at", "updated_at"])
        serializer = self.get_serializer(tutorial)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, id=None):
        tutorial = self.get_object()
        tutorial.is_published = False
        tutorial.save(update_fields=["is_published", "updated_at"])
        serializer = self.get_serializer(tutorial)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        user = self.request.user
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        tutorial = Tutorial.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not tutorial:
            return Response({"detail": "Tutorial not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        if not is_privileged and tutorial.author != user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        tutorial.restore()
        return Response({"detail": "Tutorial restored successfully."}, status=status.HTTP_200_OK)


class ForumViewSet(viewsets.ModelViewSet):
    queryset = Forum.objects.all().order_by("name")
    serializer_class = ForumSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    lookup_field = "id"

    required_permissions = {
        "list": "comm:forums:read",
        "retrieve": "comm:forums:read",
        "create": "comm:forums:admin",
        "update": "comm:forums:admin",
        "partial_update": "comm:forums:admin",
        "destroy": "comm:forums:admin",
    }


class ForumTopicViewSet(viewsets.ModelViewSet):
    queryset = ForumTopic.objects.select_related("forum", "author").all().order_by("-is_pinned", "-created_at")
    serializer_class = ForumTopicSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["title", "is_pinned", "is_locked", "created_at"]
    ordering = ["-is_pinned", "-created_at"]
    lookup_field = "id"

    required_permissions = {
        "list": "comm:forums:read",
        "retrieve": "comm:forums:read",
        "create": "comm:forums:write",
        "update": "comm:forums:write",
        "partial_update": "comm:forums:write",
        "destroy": "comm:forums:write",
        "restore": "comm:forums:write",
        "pin": "comm:forums:admin",
        "unpin": "comm:forums:admin",
        "lock": "comm:forums:admin",
        "unlock": "comm:forums:admin",
        "solve": "comm:forums:write",
        "unsolve": "comm:forums:write",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        if include_deleted and is_privileged:
            queryset = ForumTopic.all_objects.select_related("forum", "author").all()
        else:
            queryset = ForumTopic.objects.select_related("forum", "author").all()

        forum_id = self.request.query_params.get("forum")
        if forum_id:
            queryset = queryset.filter(forum_id=forum_id)

        return queryset.order_by("-is_pinned", "-created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        user = self.request.user
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        topic = ForumTopic.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not topic:
            return Response({"detail": "Forum topic not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        if not is_privileged and topic.author != user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        topic.restore()
        return Response({"detail": "Forum topic restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="pin")
    def pin(self, request, id=None):
        topic = self.get_object()
        topic.is_pinned = True
        topic.save(update_fields=["is_pinned", "updated_at"])
        return Response({"detail": "Thread pinned successfully."})

    @action(detail=True, methods=["post"], url_path="unpin")
    def unpin(self, request, id=None):
        topic = self.get_object()
        topic.is_pinned = False
        topic.save(update_fields=["is_pinned", "updated_at"])
        return Response({"detail": "Thread unpinned successfully."})

    @action(detail=True, methods=["post"], url_path="lock")
    def lock(self, request, id=None):
        topic = self.get_object()
        topic.is_locked = True
        topic.save(update_fields=["is_locked", "updated_at"])
        return Response({"detail": "Thread locked successfully."})

    @action(detail=True, methods=["post"], url_path="unlock")
    def unlock(self, request, id=None):
        topic = self.get_object()
        topic.is_locked = False
        topic.save(update_fields=["is_locked", "updated_at"])
        return Response({"detail": "Thread unlocked successfully."})

    @action(detail=True, methods=["post"], url_path="solve")
    def solve(self, request, id=None):
        topic = self.get_object()
        if not topic.title.startswith("[SOLVED]"):
            topic.title = f"[SOLVED] {topic.title}"
            topic.save(update_fields=["title", "updated_at"])
        return Response({"detail": "Thread marked as solved."})

    @action(detail=True, methods=["post"], url_path="unsolve")
    def unsolve(self, request, id=None):
        topic = self.get_object()
        if topic.title.startswith("[SOLVED]"):
            topic.title = topic.title.replace("[SOLVED] ", "", 1).strip()
            topic.save(update_fields=["title", "updated_at"])
        return Response({"detail": "Thread marked as unsolved."})


class ForumPostViewSet(viewsets.ModelViewSet):
    queryset = ForumPost.objects.select_related("topic", "author").all().order_by("created_at")
    serializer_class = ForumPostSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["content"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]
    lookup_field = "id"

    required_permissions = {
        "list": "comm:forums:read",
        "retrieve": "comm:forums:read",
        "create": "comm:forums:write",
        "update": "comm:forums:write",
        "partial_update": "comm:forums:write",
        "destroy": "comm:forums:write",
        "restore": "comm:forums:write",
        "like": "comm:forums:write",
        "unlike": "comm:forums:write",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        if include_deleted and is_privileged:
            queryset = ForumPost.all_objects.select_related("topic", "author").all()
        else:
            queryset = ForumPost.objects.select_related("topic", "author").all()

        topic_id = self.request.query_params.get("topic")
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)

        # For normal list/retrieve, return only top-level posts (i.e. those with NO parent_post_id)
        # to let client fetch child replies nested inside them or on demand.
        # This keeps the layout incredibly neat!
        # But if we are searching or retrieving a single post, allow it.
        if self.action == "list" and not self.request.query_params.get("all_depth"):
            # Check frontmatter parent_post_id manually via filter or list parsing
            # Since SQL query on frontmatter is tricky, we filter root posts by checking if content starts with anything other than parent_post_id inside frontmatter
            queryset = queryset.exclude(content__contains="parent_post_id: ")

        return queryset.order_by("created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Pre-fetch sibling posts mapping to completely eliminate N+1 queries during child serialization
        topic_id = self.request.query_params.get("topic") or self.request.data.get("topic")
        if topic_id:
            sibling_posts = ForumPost.objects.filter(topic_id=topic_id, deleted_at__isnull=True).select_related("author").order_by("created_at")
            topic_posts_map = []
            for sp in sibling_posts:
                meta, _ = parse_front_matter(sp.content)
                topic_posts_map.append({
                    "obj": sp,
                    "parent_post_id": meta.get("parent_post_id")
                })
            context["topic_posts_map"] = topic_posts_map
        return context

    def perform_create(self, serializer):
        topic = serializer.validated_data.get("topic")
        if topic and topic.is_locked:
            raise serializers.ValidationError("Cannot post in a locked thread.")
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        user = self.request.user
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        post = ForumPost.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not post:
            return Response({"detail": "Forum post not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        if not is_privileged and post.author != user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        post.restore()
        return Response({"detail": "Forum post restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def like(self, request, id=None):
        post = self.get_object()
        user = request.user
        like_obj, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            return Response({"detail": "Already liked."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Liked successfully.", "likes_count": post.likes.count()}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def unlike(self, request, id=None):
        post = self.get_object()
        user = request.user
        like_qs = Like.objects.filter(user=user, post=post)
        if not like_qs.exists():
            return Response({"detail": "Not liked yet."}, status=status.HTTP_400_BAD_REQUEST)
        like_qs.delete()
        return Response({"detail": "Unliked successfully.", "likes_count": post.likes.count()}, status=status.HTTP_200_OK)


class BlogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on Blogs with Soft Delete support,
    restore endpoint, and Public read access for published content.
    """
    queryset = Blog.objects.select_related("author").all()
    serializer_class = BlogSerializer
    permission_classes = [IsAdminOrCreatorOrReadOnly, HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug", "content"]
    ordering_fields = ["title", "slug", "published_at", "created_at"]
    ordering = ["-published_at", "-created_at"]

    required_permissions = {
        "list": "comm:blogs:read",
        "retrieve": "comm:blogs:read",
        "create": "comm:blogs:create",
        "update": "comm:blogs:create",
        "partial_update": "comm:blogs:create",
        "destroy": "comm:blogs:create",
        "publish": "comm:blogs:create",
        "unpublish": "comm:blogs:create",
        "restore": "comm:blogs:create",
        "like": "comm:blogs:read",
        "unlike": "comm:blogs:read",
    }

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_value = self.kwargs.get(self.lookup_field)
        
        is_uuid = False
        try:
            uuid.UUID(str(lookup_value))
            is_uuid = True
        except ValueError:
            pass

        if is_uuid:
            obj = get_object_or_404(queryset, id=lookup_value)
        else:
            obj = get_object_or_404(queryset, slug=lookup_value)
            
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        if include_deleted and is_privileged:
            queryset = Blog.all_objects.select_related("author").prefetch_related("comments", "comments__author").all()
        else:
            queryset = Blog.objects.select_related("author").prefetch_related("comments", "comments__author").all()

        if is_privileged:
            pass
        elif user and user.is_authenticated:
            queryset = queryset.filter(Q(is_published=True) | Q(author=user))
        else:
            queryset = queryset.filter(is_published=True)

        is_published_param = self.request.query_params.get("is_published")
        if is_published_param is not None:
            queryset = queryset.filter(is_published=is_published_param.lower() == "true")

        author_param = self.request.query_params.get("author")
        if author_param:
            queryset = queryset.filter(author_id=author_param)

        category_param = self.request.query_params.get("category")
        if category_param:
            queryset = queryset.filter(content__contains=f"categories: {category_param}")

        tag_param = self.request.query_params.get("tag")
        if tag_param:
            queryset = queryset.filter(content__contains=f"tags: {tag_param}")

        # On the fly scheduled publication check
        for b in queryset.filter(is_published=False):
            meta, _ = parse_front_matter(b.content)
            sched_at = meta.get("scheduled_at")
            if sched_at:
                try:
                    sched_dt = datetime.datetime.fromisoformat(sched_at)
                    if sched_dt <= datetime.datetime.now(datetime.timezone.utc):
                        b.is_published = True
                        b.published_at = timezone.now()
                        b.save(update_fields=["is_published", "published_at", "updated_at"])
                except ValueError:
                    pass

        return queryset

    def retrieve(self, request, *args, **kwargs):
        # Dynamically increment view counts inside retrieve
        instance = self.get_object()
        meta, body = parse_front_matter(instance.content)
        try:
            views = int(meta.get("_views_count", 0))
        except ValueError:
            views = 0
        meta["_views_count"] = str(views + 1)
        instance.content = format_front_matter(meta, body)
        instance.save(update_fields=["content"])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, id=None):
        blog = self.get_object()
        blog.is_published = True
        blog.published_at = timezone.now()
        blog.save(update_fields=["is_published", "published_at", "updated_at"])
        serializer = self.get_serializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, id=None):
        blog = self.get_object()
        blog.is_published = False
        blog.save(update_fields=["is_published", "updated_at"])
        serializer = self.get_serializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        user = self.request.user
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        blog = Blog.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not blog:
            return Response({"detail": "Blog not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        if not is_privileged and blog.author != user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        blog.restore()
        return Response({"detail": "Blog restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def like(self, request, id=None):
        blog = self.get_object()
        user = request.user
        like_obj, created = Like.objects.get_or_create(user=user, blog=blog)
        if not created:
            return Response({"detail": "Already liked."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Liked successfully.", "likes_count": blog.likes.count()}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def unlike(self, request, id=None):
        blog = self.get_object()
        user = request.user
        like_qs = Like.objects.filter(user=user, blog=blog)
        if not like_qs.exists():
            return Response({"detail": "Not liked yet."}, status=status.HTTP_400_BAD_REQUEST)
        like_qs.delete()
        return Response({"detail": "Unliked successfully.", "likes_count": blog.likes.count()}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling CRUD operations on Blog Comments with Soft Delete support,
    restore endpoint, and Public read access for comments on published content.
    """
    queryset = Comment.objects.select_related("blog", "parent", "author").all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrCreatorOrReadOnly, HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination

    required_permissions = {
        "list": "comm:comments:write",
        "retrieve": "comm:comments:write",
        "create": "comm:comments:write",
        "update": "comm:comments:write",
        "partial_update": "comm:comments:write",
        "destroy": "comm:comments:write",
        "restore": "comm:comments:write",
        "like": "comm:comments:write",
        "unlike": "comm:comments:write",
        "moderate": "comm:comments:admin",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN", "MODERATOR"])
        )

        if include_deleted and is_privileged:
            queryset = Comment.all_objects.select_related("blog", "parent", "author").all()
        else:
            queryset = Comment.objects.select_related("blog", "parent", "author").all()

        if is_privileged:
            return queryset.order_by("created_at")

        if user and user.is_authenticated:
            return queryset.filter(
                Q(blog__is_published=True) | Q(blog__author=user) | Q(author=user)
            ).order_by("created_at")

        return queryset.filter(blog__is_published=True).order_by("created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        user = self.request.user
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        comment = Comment.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not comment:
            return Response({"detail": "Comment not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        if not is_privileged and comment.author != user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        comment.restore()
        return Response({"detail": "Comment restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def like(self, request, id=None):
        comment = self.get_object()
        user = request.user
        like_obj, created = Like.objects.get_or_create(user=user, comment=comment)
        if not created:
            return Response({"detail": "Already liked."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Liked successfully.", "likes_count": comment.likes.count()}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def unlike(self, request, id=None):
        comment = self.get_object()
        user = request.user
        like_qs = Like.objects.filter(user=user, comment=comment)
        if not like_qs.exists():
            return Response({"detail": "Not liked yet."}, status=status.HTTP_400_BAD_REQUEST)
        like_qs.delete()
        return Response({"detail": "Unliked successfully.", "likes_count": comment.likes.count()}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="moderate")
    def moderate(self, request, id=None):
        comment = self.get_object()
        comment.content = "[This comment has been moderated by administrators]"
        comment.save(update_fields=["content", "updated_at"])
        return Response({"detail": "Comment moderated successfully."})


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.select_related("user", "post", "blog", "comment").all()
    serializer_class = LikeSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination

    required_permissions = {
        "list": "cms:like:view",
        "retrieve": "cms:like:view",
        "create": "cms:like:create",
        "update": "cms:like:update",
        "partial_update": "cms:like:update",
        "destroy": "cms:like:delete",
    }

    def perform_create(self, serializer):
        user = self.request.user
        post = serializer.validated_data.get("post")
        blog = serializer.validated_data.get("blog")
        comment = serializer.validated_data.get("comment")

        # Handle unique constraint prevention programmatically to return 400 bad request
        if post and Like.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError("Already liked this post.")
        if blog and Like.objects.filter(user=user, blog=blog).exists():
            raise serializers.ValidationError("Already liked this blog.")
        if comment and Like.objects.filter(user=user, comment=comment).exists():
            raise serializers.ValidationError("Already liked this comment.")

        serializer.save(user=user)


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.select_related("reporter", "target_post", "target_comment").all().order_by("-created_at")
    serializer_class = ReportSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    required_permissions = {
        "list": "comm:forums:admin",
        "retrieve": "comm:forums:admin",
        "create": "comm:forums:write",
        "update": "comm:forums:admin",
        "partial_update": "comm:forums:admin",
        "destroy": "comm:forums:admin",
        "resolve": "comm:forums:admin",
        "dismiss": "comm:forums:admin",
    }

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve(self, request, id=None):
        report = self.get_object()
        report.status = "RESOLVED"
        report.save(update_fields=["status"])
        return Response({"status": "resolved"})

    @action(detail=True, methods=["post"], url_path="dismiss")
    def dismiss(self, request, id=None):
        report = self.get_object()
        report.status = "DISMISSED"
        report.save(update_fields=["status"])
        return Response({"status": "dismissed"})


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category hierarchy CRUD operations.
    """
    queryset = Category.objects.all().order_by("display_order", "name")
    serializer_class = CategorySerializer
    permission_classes = [IsCMSEditor, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "display_order", "created_at"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:categories:read",
        "retrieve": "cms:categories:read",
        "create": "cms:categories:write",
        "update": "cms:categories:write",
        "partial_update": "cms:categories:write",
        "destroy": "cms:categories:write",
        "restore": "cms:categories:write",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        if include_deleted and is_privileged:
            queryset = Category.all_objects.all()
        else:
            queryset = Category.objects.all()

        parent_param = self.request.query_params.get("parent")
        if parent_param:
            if parent_param.lower() in ["null", "none"]:
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_param)

        return queryset.order_by("display_order", "name")

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        category = Category.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not category:
            return Response({"detail": "Category not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)
        category.restore()
        return Response({"detail": "Category restored successfully."}, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Tag CRUD operations.
    """
    queryset = Tag.objects.all().order_by("-usage_count", "name")
    serializer_class = TagSerializer
    permission_classes = [IsCMSEditor, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "usage_count", "created_at"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:tags:read",
        "retrieve": "cms:tags:read",
        "create": "cms:tags:write",
        "update": "cms:tags:write",
        "partial_update": "cms:tags:write",
        "destroy": "cms:tags:write",
    }


class AuthorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Author Profile CRUD operations.
    """
    queryset = Author.objects.select_related("user").all().order_by("display_name")
    serializer_class = AuthorSerializer
    permission_classes = [IsCMSEditor, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["display_name", "bio"]
    ordering_fields = ["display_name", "total_articles", "created_at"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:authors:read",
        "retrieve": "cms:authors:read",
        "create": "cms:authors:write",
        "update": "cms:authors:write",
        "partial_update": "cms:authors:write",
        "destroy": "cms:authors:write",
    }


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Article CRUD operations with workflow state machines,
    revisions, preview capabilities, publishing controls, and SEO syncs.
    """
    queryset = Article.objects.select_related("author", "cms_author", "featured_image").prefetch_related("categories", "tags").all()
    serializer_class = ArticleSerializer
    permission_classes = [IsContentOwner, HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug", "body", "excerpt"]
    ordering_fields = ["title", "slug", "published_at", "created_at"]
    ordering = ["-published_at", "-created_at"]

    required_permissions = {
        "list": "cms:articles:read",
        "retrieve": "cms:articles:read",
        "create": "cms:articles:create",
        "update": "cms:articles:update",
        "partial_update": "cms:articles:update",
        "destroy": "cms:articles:delete",
        "restore": "cms:articles:delete",
        "publish": "cms:articles:publish",
        "unpublish": "cms:articles:publish",
        "preview": "cms:articles:read",
        "schedule": "cms:articles:publish",
        "bulk_publish": "cms:articles:publish",
        "bulk_delete": "cms:articles:delete",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        if include_deleted and is_privileged:
            queryset = Article.all_objects.select_related("author", "cms_author", "featured_image").prefetch_related("categories", "tags").all()
        else:
            queryset = Article.objects.select_related("author", "cms_author", "featured_image").prefetch_related("categories", "tags").all()

        if is_privileged:
            pass
        elif user and user.is_authenticated:
            queryset = queryset.filter(Q(is_published=True) | Q(author=user))
        else:
            queryset = queryset.filter(is_published=True)

        # Filters
        is_published_param = self.request.query_params.get("is_published")
        if is_published_param is not None:
            queryset = queryset.filter(is_published=is_published_param.lower() == "true")

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        category_param = self.request.query_params.get("category")
        if category_param:
            queryset = queryset.filter(categories__id=category_param)

        tag_param = self.request.query_params.get("tag")
        if tag_param:
            queryset = queryset.filter(tags__id=tag_param)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, id=None):
        article = self.get_object()
        article.is_published = True
        article.status = "published"
        article.published_at = timezone.now()
        article.save(update_fields=["is_published", "status", "published_at", "updated_at"])
        
        # Trigger SEO & search index manually or let signal process it
        try:
            SEOIntegrationService.ensure_seo_record(article)
            SearchIndexService.index_article(article)
        except Exception:
            pass

        serializer = self.get_serializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, id=None):
        article = self.get_object()
        article.is_published = False
        article.status = "draft"
        article.save(update_fields=["is_published", "status", "updated_at"])
        
        try:
            SearchIndexService.remove_from_index("article", article.id)
        except Exception:
            pass

        serializer = self.get_serializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        article = Article.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not article:
            return Response({"detail": "Article not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, article)
        article.restore()
        return Response({"detail": "Article restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, id=None):
        article = self.get_object()
        serializer = self.get_serializer(article)
        preview_data = serializer.data
        preview_data["rendered_preview"] = f"<div class='article-preview'><h1>{article.title}</h1>{article.body}</div>"
        return Response(preview_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="schedule")
    def schedule(self, request, id=None):
        article = self.get_object()
        scheduled_at = request.data.get("scheduled_at")
        if not scheduled_at:
            return Response({"detail": "scheduled_at parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse datetime
        try:
            scheduled_time = datetime.datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
        except ValueError:
            return Response({"detail": "Invalid scheduled_at format. Use ISO-8601."}, status=status.HTTP_400_BAD_REQUEST)

        # Create schedule entry
        schedule_obj, _ = PublishSchedule.objects.update_or_create(
            content_type="article",
            content_id=article.id,
            defaults={
                "scheduled_at": scheduled_time,
                "status": "pending",
                "scheduled_by": request.user,
                "executed_at": None,
                "failure_reason": None
            }
        )

        article.status = "scheduled"
        article.save(update_fields=["status", "updated_at"])

        return Response({
            "detail": "Article publishing scheduled successfully.",
            "schedule_id": str(schedule_obj.id),
            "scheduled_at": schedule_obj.scheduled_at.isoformat()
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="bulk-publish")
    def bulk_publish(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"detail": "ids list is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        articles = Article.objects.filter(id__in=ids)
        count = 0
        for article in articles:
            article.is_published = True
            article.status = "published"
            article.published_at = timezone.now()
            article.save(update_fields=["is_published", "status", "published_at", "updated_at"])
            try:
                SEOIntegrationService.ensure_seo_record(article)
                SearchIndexService.index_article(article)
            except Exception:
                pass
            count += 1
        
        return Response({"detail": f"{count} articles published successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"detail": "ids list is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        articles = Article.objects.filter(id__in=ids)
        count = 0
        for article in articles:
            article.delete()
            count += 1
        
        return Response({"detail": f"{count} articles soft-deleted successfully."}, status=status.HTTP_200_OK)


class MediaFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Media Library upload and management.
    """
    queryset = MediaFile.objects.select_related("uploader").prefetch_related("tags").all()
    serializer_class = MediaFileSerializer
    permission_classes = [MediaPermission, HasRBACPermission]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["original_filename", "caption", "alt_text"]
    ordering_fields = ["original_filename", "file_size_bytes", "created_at"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "cms:media:read",
        "retrieve": "cms:media:read",
        "create": "cms:media:write",
        "update": "cms:media:write",
        "partial_update": "cms:media:write",
        "destroy": "cms:media:delete",
    }

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)


class ContentBlockViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Page Builder Content Blocks.
    """
    queryset = ContentBlock.objects.select_related("page", "template", "parent").all()
    serializer_class = ContentBlockSerializer
    permission_classes = [IsCMSEditor, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["display_order", "created_at"]
    ordering = ["display_order"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:pages:read",
        "retrieve": "cms:pages:read",
        "create": "cms:pages:update",
        "update": "cms:pages:update",
        "partial_update": "cms:pages:update",
        "destroy": "cms:pages:update",
    }

    def get_queryset(self):
        queryset = self.queryset
        page_id = self.request.query_params.get("page")
        if page_id:
            queryset = queryset.filter(page_id=page_id)
        
        parent_id = self.request.query_params.get("parent")
        if parent_id:
            if parent_id.lower() in ["null", "none"]:
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)

        return queryset


class BlockTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Reusable Block Templates.
    """
    queryset = BlockTemplate.objects.select_related("created_by").all().order_by("name")
    serializer_class = BlockTemplateSerializer
    permission_classes = [IsCMSAdmin, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "block_type"]
    ordering_fields = ["name", "block_type", "created_at"]
    ordering = ["name"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:pages:read",
        "retrieve": "cms:pages:read",
        "create": "cms:pages:update",
        "update": "cms:pages:update",
        "partial_update": "cms:pages:update",
        "destroy": "cms:pages:update",
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PageVersionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for immutable Page Layout snapshots.
    """
    queryset = PageVersion.objects.select_related("page", "author").all().order_by("-version_number")
    serializer_class = PageVersionSerializer
    permission_classes = [RevisionPermission, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["version_number", "created_at"]
    ordering = ["-version_number"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:pages:read",
        "retrieve": "cms:pages:read",
        "create": "cms:pages:update",
        "update": "cms:pages:update",
        "partial_update": "cms:pages:update",
        "destroy": "cms:pages:update",
    }


class RevisionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for generic Editorial Revisions (Articles and Blogs).
    """
    queryset = Revision.objects.select_related("author").all().order_by("-version_number")
    serializer_class = RevisionSerializer
    permission_classes = [RevisionPermission, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["change_summary"]
    ordering_fields = ["version_number", "created_at"]
    ordering = ["-version_number"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:articles:read",
        "retrieve": "cms:articles:read",
        "create": "cms:articles:update",
        "update": "cms:articles:update",
        "partial_update": "cms:articles:update",
        "destroy": "cms:articles:delete",
        "rollback": "cms:articles:update",
    }

    def get_queryset(self):
        queryset = self.queryset
        content_type = self.request.query_params.get("content_type")
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        content_id = self.request.query_params.get("content_id")
        if content_id:
            queryset = queryset.filter(content_id=content_id)
        
        return queryset

    @action(detail=True, methods=["post"], url_path="rollback")
    def rollback(self, request, id=None):
        revision = self.get_object()
        
        # Invoke rollback logic from services
        result = RevisionService.restore_revision(
            content_type=revision.content_type,
            content_id=str(revision.content_id),
            version_number=revision.version_number,
            authorized_by=request.user
        )

        if "error" in result:
            return Response({"detail": result["error"]}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": f"Content rolled back successfully to version {revision.version_number}."}, status=status.HTTP_200_OK)


class WorkflowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Workflow States.
    """
    queryset = WorkflowState.objects.select_related("article", "assigned_to").all().order_by("-created_at")
    serializer_class = WorkflowStateSerializer
    permission_classes = [WorkflowPermission, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["status", "notes"]
    ordering_fields = ["status", "due_date", "created_at"]
    ordering = ["-created_at"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:articles:read",
        "retrieve": "cms:articles:read",
        "create": "cms:articles:update",
        "update": "cms:articles:update",
        "partial_update": "cms:articles:update",
        "destroy": "cms:articles:delete",
        "transition": "cms:articles:update",
    }

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, id=None):
        workflow = self.get_object()
        to_status = request.data.get("to_status")
        comment = request.data.get("comment", "")
        assigned_to_id = request.data.get("assigned_to", None)
        due_date = request.data.get("due_date", None)

        if not to_status:
            return Response({"detail": "to_status parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse assigned user
        from django.contrib.auth import get_user_model
        assigned_user = None
        if assigned_to_id:
            assigned_user = get_object_or_404(get_user_model(), id=assigned_to_id)

        # Parse due date
        due_dt = None
        if due_date:
            try:
                due_dt = datetime.datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                return Response({"detail": "Invalid due_date format. Use ISO-8601."}, status=status.HTTP_400_BAD_REQUEST)

        result = WorkflowService.transition(
            workflow_id=str(workflow.id),
            to_status=to_status,
            actor=request.user,
            comment=comment,
            assigned_to=assigned_user,
            due_date=due_dt
        )

        if "error" in result:
            return Response({"detail": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

        # Re-fetch state
        workflow.refresh_from_db()
        serializer = self.get_serializer(workflow)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkflowLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Workflow Logs.
    """
    queryset = WorkflowLog.objects.select_related("workflow", "actor").all().order_by("-created_at")
    serializer_class = WorkflowLogSerializer
    permission_classes = [WorkflowPermission, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:articles:read",
        "retrieve": "cms:articles:read",
        "create": "cms:articles:update",
        "update": "cms:articles:update",
        "partial_update": "cms:articles:update",
        "destroy": "cms:articles:delete",
    }


class PublishScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Publish Schedules.
    """
    queryset = PublishSchedule.objects.select_related("scheduled_by").all().order_by("scheduled_at")
    serializer_class = PublishScheduleSerializer
    permission_classes = [PublishPermission, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["content_type", "status"]
    ordering_fields = ["scheduled_at", "status", "created_at"]
    ordering = ["scheduled_at"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:articles:read",
        "retrieve": "cms:articles:read",
        "create": "cms:articles:publish",
        "update": "cms:articles:publish",
        "partial_update": "cms:articles:publish",
        "destroy": "cms:articles:publish",
    }

    def perform_create(self, serializer):
        serializer.save(scheduled_by=self.request.user)


class CMSRedirectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Redirects.
    """
    queryset = CMSRedirect.objects.all().order_by("from_path")
    serializer_class = CMSRedirectSerializer
    permission_classes = [IsCMSAdmin, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["from_path", "to_path", "notes"]
    ordering_fields = ["from_path", "hit_count", "created_at"]
    ordering = ["from_path"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:menus:write",
        "retrieve": "cms:menus:write",
        "create": "cms:menus:write",
        "update": "cms:menus:write",
        "partial_update": "cms:menus:write",
        "destroy": "cms:menus:write",
    }


class CMSAuditTrailViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for Audit logs.
    """
    queryset = CMSAuditTrail.objects.select_related("actor").all().order_by("-created_at")
    serializer_class = CMSAuditTrailSerializer
    permission_classes = [IsCMSAdmin, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["action", "content_type", "content_id", "content_title", "ip_address", "request_id"]
    ordering_fields = ["created_at", "action"]
    ordering = ["-created_at"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:pages:update",
        "retrieve": "cms:pages:update",
    }


class CMSSearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for Search Indexes.
    """
    queryset = CMSSearchIndex.objects.filter(is_published=True).order_by("-published_at")
    serializer_class = CMSSearchIndexSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "excerpt", "body", "tags", "categories", "author_name"]
    ordering_fields = ["published_at", "title"]
    ordering = ["-published_at"]
    lookup_field = "id"


class FAQViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FAQ.
    """
    queryset = FAQ.objects.select_related("category").prefetch_related("tags").all().order_by("display_order", "question")
    serializer_class = FAQSerializer
    permission_classes = [IsCMSEditor, HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["question", "answer"]
    ordering_fields = ["question", "display_order", "created_at"]
    ordering = ["display_order", "question"]
    lookup_field = "id"

    required_permissions = {
        "list": "cms:pages:read",
        "retrieve": "cms:pages:read",
        "create": "cms:pages:update",
        "update": "cms:pages:update",
        "partial_update": "cms:pages:update",
        "destroy": "cms:pages:update",
        "restore": "cms:pages:update",
    }

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user and user.is_authenticated and (
            user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        )

        if include_deleted and is_privileged:
            queryset = FAQ.all_objects.select_related("category").prefetch_related("tags").all()
        else:
            queryset = FAQ.objects.select_related("category").prefetch_related("tags").all()

        if not is_privileged:
            queryset = queryset.filter(is_published=True)

        return queryset.order_by("display_order", "question")

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        faq = FAQ.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not faq:
            return Response({"detail": "FAQ not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)
        faq.restore()
        return Response({"detail": "FAQ restored successfully."}, status=status.HTTP_200_OK)


class ReactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Reactions.
    """
    queryset = Reaction.objects.select_related("user", "article", "blog").all().order_by("-created_at")
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    required_permissions = {
        "list": "cms:like:view",
        "retrieve": "cms:like:view",
        "create": "cms:like:create",
        "update": "cms:like:update",
        "partial_update": "cms:like:update",
        "destroy": "cms:like:delete",
    }

    def perform_create(self, serializer):
        user = self.request.user
        article = serializer.validated_data.get("article")
        blog = serializer.validated_data.get("blog")

        # Unique validation
        if article and Reaction.objects.filter(user=user, article=article).exists():
            raise serializers.ValidationError("Already reacted to this article.")
        if blog and Reaction.objects.filter(user=user, blog=blog).exists():
            raise serializers.ValidationError("Already reacted to this blog.")

        serializer.save(user=user)


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.filter(deleted_at__isnull=True).all()
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EnterprisePagination
    lookup_field = "id"


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = MediaCollection.objects.filter(deleted_at__isnull=True).all()
    serializer_class = MediaCollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MediaFileViewSet(viewsets.ModelViewSet):
    queryset = MediaFile.objects.select_related("uploader", "folder").prefetch_related("tags").filter(deleted_at__isnull=True).all()
    serializer_class = MediaFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsMediaOwnerOrAdmin]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    @action(detail=True, methods=["post"], url_path="favorite")
    def favorite(self, request, id=None):
        media_file = self.get_object()
        from apps.cms.services import FavoriteService
        is_fav = FavoriteService.toggle_favorite(media_file, request.user)
        return Response({"detail": "Favorited" if is_fav else "Unfavorited"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="download")
    def download(self, request, id=None):
        media_file = self.get_object()
        from apps.cms.services import DownloadService
        DownloadService.record_download(media_file, request.user)
        return Response({"detail": "Download logged successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="share")
    def share(self, request, id=None):
        media_file = self.get_object()
        shared_with_email = request.data.get("shared_with_email")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        target_user = User.objects.filter(email=shared_with_email).first()
        if not target_user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        from apps.cms.models import MediaShare
        share = MediaShare.objects.create(
            media_file=media_file,
            shared_by=request.user,
            shared_with=target_user
        )
        return Response({"detail": "Shared successfully.", "share_id": str(share.id)}, status=status.HTTP_201_CREATED)


class MediaVersionViewSet(viewsets.ModelViewSet):
    queryset = MediaVersion.objects.filter(deleted_at__isnull=True).all()
    serializer_class = MediaVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EnterprisePagination
    lookup_field = "id"


class MediaShareViewSet(viewsets.ModelViewSet):
    queryset = MediaShare.objects.filter(deleted_at__isnull=True).all()
    serializer_class = MediaShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EnterprisePagination
    lookup_field = "id"


class MediaAuditViewSet(viewsets.ModelViewSet):
    queryset = MediaAudit.objects.filter(deleted_at__isnull=True).all()
    serializer_class = MediaAuditSerializer
    permission_classes = [permissions.IsAuthenticated, IsMediaOwnerOrAdmin]
    pagination_class = EnterprisePagination
    lookup_field = "id"


class MediaFavoriteViewSet(viewsets.ModelViewSet):
    queryset = MediaFavorite.objects.filter(deleted_at__isnull=True).all()
    serializer_class = MediaFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EnterprisePagination
    lookup_field = "id"


class MediaCommentViewSet(viewsets.ModelViewSet):
    queryset = MediaComment.objects.filter(deleted_at__isnull=True).all()
    serializer_class = MediaCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MediaSearchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MediaFile.objects.filter(deleted_at__isnull=True).all()
    serializer_class = MediaFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EnterprisePagination
    lookup_field = "id"

    def get_queryset(self):
        query = self.request.query_params.get("query", "")
        if query:
            from apps.cms.services import SearchService
            return SearchService.search_assets(query)
        return super().get_queryset()


class MediaWorkflowViewSet(viewsets.ModelViewSet):
    queryset = MediaWorkflow.objects.filter(deleted_at__isnull=True).all()
    serializer_class = MediaWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EnterprisePagination
    lookup_field = "id"
