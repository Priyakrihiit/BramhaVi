from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnalyticsEventViewSet, UserSessionViewSet, PageViewViewSet, CourseAnalyticsViewSet,
    ArticleAnalyticsViewSet, SearchAnalyticsViewSet, NotificationAnalyticsViewSet,
    WalletAnalyticsViewSet, RevenueAnalyticsViewSet, ReportViewSet, DashboardViewSet,
    DashboardWidgetViewSet, KPIViewSet, MetricViewSet, DailySummaryViewSet,
    RealtimeCounterViewSet, ExportJobViewSet, ReportScheduleViewSet,
    AuditAnalyticsViewSet, SystemMetricsViewSet
)

app_name = "analytics"

router = DefaultRouter()
router.register("events", AnalyticsEventViewSet, basename="events")
router.register("sessions", UserSessionViewSet, basename="sessions")
router.register("pageviews", PageViewViewSet, basename="pageviews")
router.register("courses", CourseAnalyticsViewSet, basename="courses")
router.register("articles", ArticleAnalyticsViewSet, basename="articles")
router.register("searches", SearchAnalyticsViewSet, basename="searches")
router.register("notifications", NotificationAnalyticsViewSet, basename="notifications")
router.register("wallets", WalletAnalyticsViewSet, basename="wallets")
router.register("revenues", RevenueAnalyticsViewSet, basename="revenues")
router.register("reports", ReportViewSet, basename="reports")
router.register("dashboards", DashboardViewSet, basename="dashboards")
router.register("widgets", DashboardWidgetViewSet, basename="widgets")
router.register("kpis", KPIViewSet, basename="kpis")
router.register("metrics", MetricViewSet, basename="metrics")
router.register("summaries", DailySummaryViewSet, basename="summaries")
router.register("counters", RealtimeCounterViewSet, basename="counters")
router.register("exports", ExportJobViewSet, basename="exports")
router.register("schedules", ReportScheduleViewSet, basename="schedules")
router.register("audits", AuditAnalyticsViewSet, basename="audits")
router.register("system-metrics", SystemMetricsViewSet, basename="system-metrics")

urlpatterns = [
    path("", include(router.urls)),
]
