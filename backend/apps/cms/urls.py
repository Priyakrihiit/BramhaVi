"""
CMS Endpoints Router - BrahmaVidya Galaxy
Purpose: Maps routing paths to CMS views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.cms.views import (
    PageViewSet, NavigationMenuViewSet, TutorialViewSet, ForumViewSet,
    ForumTopicViewSet, ForumPostViewSet, BlogViewSet, CommentViewSet, LikeViewSet, ReportViewSet,
    CategoryViewSet, TagViewSet, AuthorViewSet, ArticleViewSet, MediaFileViewSet,
    ContentBlockViewSet, BlockTemplateViewSet, PageVersionViewSet, RevisionViewSet,
    WorkflowViewSet, WorkflowLogViewSet, PublishScheduleViewSet, CMSRedirectViewSet,
    CMSAuditTrailViewSet, CMSSearchViewSet, FAQViewSet, ReactionViewSet,
    FolderViewSet, CollectionViewSet, MediaVersionViewSet, MediaShareViewSet,
    MediaAuditViewSet, MediaFavoriteViewSet, MediaCommentViewSet, MediaSearchViewSet,
    MediaWorkflowViewSet
)

router = DefaultRouter()
router.register("pages", PageViewSet, basename="page")
router.register("menus", NavigationMenuViewSet, basename="menu")
router.register("tutorials", TutorialViewSet, basename="tutorial")
router.register("forums", ForumViewSet, basename="forum")
router.register("topics", ForumTopicViewSet, basename="topic")
router.register("posts", ForumPostViewSet, basename="post")
router.register("blogs", BlogViewSet, basename="blog")
router.register("comments", CommentViewSet, basename="comment")
router.register("likes", LikeViewSet, basename="like")
router.register("reports", ReportViewSet, basename="report")

# Appended Phase 4.2 ViewSets
router.register("articles", ArticleViewSet, basename="article")
router.register("categories", CategoryViewSet, basename="category")
router.register("tags", TagViewSet, basename="tag")
router.register("authors", AuthorViewSet, basename="author")
router.register("media", MediaFileViewSet, basename="mediafile")
router.register("blocks", ContentBlockViewSet, basename="contentblock")
router.register("templates", BlockTemplateViewSet, basename="blocktemplate")
router.register("versions", PageVersionViewSet, basename="pageversion")
router.register("revisions", RevisionViewSet, basename="revision")
router.register("workflow", WorkflowViewSet, basename="workflow")
router.register("workflow-logs", WorkflowLogViewSet, basename="workflowlog")
router.register("publish", PublishScheduleViewSet, basename="publishschedule")
router.register("redirects", CMSRedirectViewSet, basename="cmsredirect")
router.register("audit", CMSAuditTrailViewSet, basename="cmsaudittrail")
router.register("search", CMSSearchViewSet, basename="cmssearch")
router.register("faq", FAQViewSet, basename="faq")
router.register("reactions", ReactionViewSet, basename="reaction")

# DAM Subsystem Endpoints
router.register("folders", FolderViewSet, basename="folder")
router.register("collections", CollectionViewSet, basename="mediacollection")
router.register("media-versions", MediaVersionViewSet, basename="mediaversion")
router.register("media-shares", MediaShareViewSet, basename="mediashare")
router.register("media-audits", MediaAuditViewSet, basename="mediaaudit")
router.register("media-favorites", MediaFavoriteViewSet, basename="mediafavorite")
router.register("media-comments", MediaCommentViewSet, basename="mediacomment")
router.register("media-search", MediaSearchViewSet, basename="mediasearch")
router.register("media-workflows", MediaWorkflowViewSet, basename="mediaworkflow")

app_name = "cms"

urlpatterns = [
    path("", include(router.urls)),
]
