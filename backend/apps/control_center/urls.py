"""
Control Center Endpoints Router - BrahmaVidya Galaxy
Purpose: Maps routing paths to Control Center views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.control_center.views import (
    ThemeViewSet, PlatformSettingViewSet, DashboardWidgetViewSet, AdministrativeTaskViewSet,
    SystemAuditLogViewSet, ActivityLogViewSet, AnalyticsEventViewSet, ConversationViewSet,
    AIMessageViewSet, AIFeedbackViewSet, MediaFileViewSet, PublicStatsView,
    HealthCheckView, LivenessCheckView, ReadinessCheckView
)
from apps.control_center.dashboard_views import EnterpriseDashboardViewSet, AdminAnalyticsViewSet
from apps.control_center.user_views import AdminUserViewSet, AdminRBACViewSet
from apps.control_center.lms_cms_views import AdminLMSViewSet, AdminCMSViewSet
from apps.control_center.portfolio_wallet_views import AdminPortfolioViewSet, AdminWalletViewSet
from apps.control_center.ai_community_views import AdminVidyaAIViewSet, AdminCommunityViewSet, AdminNotificationViewSet
from apps.control_center.system_admin_views import (
    AdminAuditLogViewSet, AdminSystemSettingsViewSet, AdminSearchEngineViewSet,
    AdminExportCenterViewSet, AdminBackupViewSet, AdminMonitoringViewSet
)

router = DefaultRouter()
router.register("themes", ThemeViewSet, basename="theme")
router.register("settings", PlatformSettingViewSet, basename="platformsetting")
router.register("widgets", DashboardWidgetViewSet, basename="dashboardwidget")
router.register("tasks", AdministrativeTaskViewSet, basename="administrativetask")
router.register("audits", SystemAuditLogViewSet, basename="systemauditlog")
router.register("activities", ActivityLogViewSet, basename="activitylog")
router.register("analytics", AnalyticsEventViewSet, basename="analyticsevent")
router.register("conversations", ConversationViewSet, basename="conversation")
router.register("messages", AIMessageViewSet, basename="aimessage")
router.register("feedbacks", AIFeedbackViewSet, basename="aifeedback")
router.register("media", MediaFileViewSet, basename="mediafile")

# Modular Administration Routers
router.register("admin/dashboard", EnterpriseDashboardViewSet, basename="admin-dashboard")
router.register("admin/users", AdminUserViewSet, basename="admin-users")
router.register("admin/rbac", AdminRBACViewSet, basename="admin-rbac")
router.register("admin/lms", AdminLMSViewSet, basename="admin-lms")
router.register("admin/cms", AdminCMSViewSet, basename="admin-cms")
router.register("admin/portfolio", AdminPortfolioViewSet, basename="admin-portfolio")
router.register("admin/wallets", AdminWalletViewSet, basename="admin-wallets")
router.register("admin/ai", AdminVidyaAIViewSet, basename="admin-ai")
router.register("admin/community", AdminCommunityViewSet, basename="admin-community")
router.register("admin/notifications", AdminNotificationViewSet, basename="admin-notifications")
router.register("admin/audit-logs", AdminAuditLogViewSet, basename="admin-audit-logs")
router.register("admin/system-settings", AdminSystemSettingsViewSet, basename="admin-system-settings")
router.register("admin/analytics-reports", AdminAnalyticsViewSet, basename="admin-analytics")
router.register("admin/search", AdminSearchEngineViewSet, basename="admin-search")
router.register("admin/export", AdminExportCenterViewSet, basename="admin-export")
router.register("admin/backup", AdminBackupViewSet, basename="admin-backup")
router.register("admin/monitoring", AdminMonitoringViewSet, basename="admin-monitoring")

app_name = "control_center"

urlpatterns = [
    path("stats/", PublicStatsView.as_view(), name="public-stats"),
    path("health/", HealthCheckView.as_view(), name="health"),
    path("live/", LivenessCheckView.as_view(), name="live"),
    path("ready/", ReadinessCheckView.as_view(), name="ready"),
    path("", include(router.urls)),
]
