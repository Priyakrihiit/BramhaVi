from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.notifications.views import (
    NotificationRecordViewSet, NotificationPreferenceViewSet, AnnouncementViewSet, NotificationTemplateViewSet, NotificationAnalyticsViewSet
)

router = DefaultRouter()
router.register("records", NotificationRecordViewSet, basename="notification-record")
router.register("preferences", NotificationPreferenceViewSet, basename="notification-preference")
router.register("announcements", AnnouncementViewSet, basename="announcement")
router.register("templates", NotificationTemplateViewSet, basename="notification-template")
router.register("analytics", NotificationAnalyticsViewSet, basename="notification-analytics")

app_name = "notifications"

urlpatterns = [
    path("", include(router.urls)),
]
