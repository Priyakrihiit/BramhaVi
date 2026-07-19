"""
Master URL Router - BrahmaVidya Galaxy
Purpose: Establishes RESTful versioned endpoints mapping routing namespace architectures.
"""

from django.contrib import admin
from django.urls import path, include
from apps.seo.views import SitemapXMLView, RobotsTXTView

urlpatterns = [
    # Admin Interface Access
    path("admin/", admin.site.urls),
    path("seo/sitemap.xml", SitemapXMLView.as_view(), name="root-sitemap-xml"),
    path("robots.txt", RobotsTXTView.as_view(), name="root-robots-txt"),
    
    # API Version 1 Endpoints (Namespaced API Versioning)
    path("api/v1/", include(([
        path("users/", include("apps.users.urls", namespace="users")),
        path("cms/", include("apps.cms.urls", namespace="cms")),
        path("lms/", include("apps.lms.urls", namespace="lms")),
        path("wallets/", include("apps.wallets.urls", namespace="wallets")),
        path("control-center/", include("apps.control_center.urls", namespace="control_center")),
        path("ai/", include("apps.ai.urls", namespace="ai")),
        path("portfolio/", include("apps.portfolio.urls", namespace="portfolio")),
        path("publishing/", include("apps.publishing.urls", namespace="publishing")),
        path("services/", include("apps.services.urls", namespace="services")),
        path("seo/", include("apps.seo.urls", namespace="seo")),
        path("notifications/", include("apps.notifications.urls", namespace="notifications")),
        path("search/", include("apps.search.urls", namespace="search")),
        path("analytics/", include("apps.analytics.urls", namespace="analytics")),
        # Sprint 20 — Student Portal
        path("student/", include("apps.student.urls", namespace="student")),
        # Sprint 21 — Teacher Portal
        path("teacher/", include("apps.teacher.urls", namespace="teacher")),
    ], "v1"), namespace="api_v1")),
]
