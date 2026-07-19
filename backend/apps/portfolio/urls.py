"""
Portfolio Builder Endpoints Router - BrahmaVidya Galaxy
Purpose: Maps routing paths to Websites, Pages, Navigation menus, Themes, Media, and Sections.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.portfolio.views import (
    WebsiteViewSet, PageViewSet, NavigationMenuViewSet,
    ThemeViewSet, MediaItemViewSet, SectionViewSet,
    ResumeViewSet, JobListingViewSet, CareerRoadmapViewSet, AICareerAssistantViewSet
)

router = DefaultRouter()
router.register("websites", WebsiteViewSet, basename="website")
router.register("pages", PageViewSet, basename="page")
router.register("navigation-menus", NavigationMenuViewSet, basename="navigation-menu")
router.register("themes", ThemeViewSet, basename="theme")
router.register("media-library", MediaItemViewSet, basename="media-item")
router.register("sections", SectionViewSet, basename="section")
router.register("resumes", ResumeViewSet, basename="resume")
router.register("jobs", JobListingViewSet, basename="job")
router.register("roadmaps", CareerRoadmapViewSet, basename="roadmap")
router.register("ai-assistant", AICareerAssistantViewSet, basename="ai-career-assistant")

app_name = "portfolio"

urlpatterns = [
    path("", include(router.urls)),
]
