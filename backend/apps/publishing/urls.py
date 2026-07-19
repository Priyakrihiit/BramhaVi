"""
Website Publishing & Hosting Endpoints Router - BrahmaVidya Galaxy
Purpose: Maps routing paths to Rendering, Subdomains, Versions, Analytics, and submissions.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.publishing.views import (
    PublicWebsiteViewSet, WebsitePublishingViewSet, SubdomainManagementViewSet,
    WebsiteVersioningViewSet, FormSubmissionViewSet, AnalyticsViewSet, MediaDeliveryViewSet,
    AuthorProfileViewSet, PublisherProfileViewSet, BookViewSet,
    ProductOwnershipViewSet, OrderViewSet, ReadingProgressViewSet
)

router = DefaultRouter()
router.register("public", PublicWebsiteViewSet, basename="public-website")
router.register("configs", WebsitePublishingViewSet, basename="publishing-config")
router.register("subdomains", SubdomainManagementViewSet, basename="subdomain")
router.register("versions", WebsiteVersioningViewSet, basename="website-version")
router.register("submissions", FormSubmissionViewSet, basename="form-submission")
router.register("analytics", AnalyticsViewSet, basename="analytics")
router.register("media", MediaDeliveryViewSet, basename="media-delivery")
router.register("authors", AuthorProfileViewSet, basename="authorprofile")
router.register("publishers", PublisherProfileViewSet, basename="publisherprofile")
router.register("books", BookViewSet, basename="book")
router.register("ownerships", ProductOwnershipViewSet, basename="productownership")
router.register("orders", OrderViewSet, basename="order")
router.register("reading-progress", ReadingProgressViewSet, basename="readingprogress")

app_name = "publishing"

urlpatterns = [
    path("", include(router.urls)),
]
