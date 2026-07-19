from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.seo.views import (
    SEOPageViewSet, GenerateMetaAPIView, GenerateSchemaAPIView,
    CheckSEOAPIView, SitemapXMLView, RobotsTXTView
)

router = DefaultRouter()
router.register("pages", SEOPageViewSet, basename="seopage")

app_name = "seo"

urlpatterns = [
    path("", include(router.urls)),
    path("generate-meta/", GenerateMetaAPIView.as_view(), name="generate-meta"),
    path("generate-schema/", GenerateSchemaAPIView.as_view(), name="generate-schema"),
    path("check-seo/", CheckSEOAPIView.as_view(), name="check-seo"),
    path("sitemap.xml", SitemapXMLView.as_view(), name="sitemap-xml"),
    path("robots.txt", RobotsTXTView.as_view(), name="robots-txt"),
]
