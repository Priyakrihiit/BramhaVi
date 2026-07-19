import decimal
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .permissions import (
    HasAnalyticsViewerPermission, HasAnalyticsManagerPermission, HasAnalyticsAdminPermission
)
from .models import (
    AnalyticsEvent, UserSession, PageView, CourseAnalytics, ArticleAnalytics,
    SearchAnalytics, NotificationAnalytics, WalletAnalytics, RevenueAnalytics,
    Report, Dashboard, DashboardWidget, KPI, Metric, DailySummary,
    RealtimeCounter, ExportJob, ReportSchedule, AuditAnalytics, SystemMetrics
)
from .serializers import (
    AnalyticsEventSerializer, UserSessionSerializer, PageViewSerializer,
    CourseAnalyticsSerializer, ArticleAnalyticsSerializer, SearchAnalyticsSerializer,
    NotificationAnalyticsSerializer, WalletAnalyticsSerializer, RevenueAnalyticsSerializer,
    ReportSerializer, DashboardSerializer, DashboardWidgetSerializer,
    KPISerializer, MetricSerializer, DailySummarySerializer,
    RealtimeCounterSerializer, ExportJobSerializer, ReportScheduleSerializer,
    AuditAnalyticsSerializer, SystemMetricsSerializer
)
from .services import (
    EventCollectorService, DashboardService
)
from .selectors import (
    get_timeseries_metrics
)
from .tasks import (
    run_export_job_task
)


class AnalyticsEventViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsEvent.objects.all().order_by("-created_at")
    serializer_class = AnalyticsEventSerializer
    permission_classes = [HasAnalyticsViewerPermission]

    @action(detail=False, methods=["post"], url_path="collect")
    def collect(self, request):
        """
        Lightweight endpoint for high-velocity client telemetry collections.
        """
        metric_name = request.data.get("metric_name", "").strip()
        metric_value = request.data.get("metric_value", 1.0)
        context_data = request.data.get("context_data", {})
        session_key = request.data.get("session_key")

        if not metric_name:
            return Response({"error": "metric_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Record event
        event = EventCollectorService.track_event(
            user=request.user,
            metric_name=metric_name,
            metric_value=metric_value,
            context_data=context_data
        )

        # Log page view details if it is a Navigation event
        if metric_name == "Page Navigation" and session_key:
            url_path = context_data.get("url_path", "/")
            referrer = context_data.get("referrer")
            dwell = context_data.get("dwell_time", 0)
            EventCollectorService.log_page_view(
                session_key=session_key,
                user=request.user,
                url_path=url_path,
                referrer=referrer,
                dwell_time=dwell
            )

        return Response(AnalyticsEventSerializer(event).data, status=status.HTTP_201_CREATED)


class UserSessionViewSet(viewsets.ModelViewSet):
    queryset = UserSession.objects.all().order_by("-login_at")
    serializer_class = UserSessionSerializer
    permission_classes = [HasAnalyticsViewerPermission]

    @action(detail=False, methods=["post"], url_path="start")
    def start_session(self, request):
        session_key = request.data.get("session_key")
        if not session_key:
            return Response({"error": "session_key is required."}, status=status.HTTP_400_BAD_REQUEST)

        ip = request.META.get("REMOTE_ADDR")
        agent = request.META.get("HTTP_USER_AGENT")
        device = request.data.get("device_type", "Desktop")
        browser = request.data.get("browser_type", "Chrome")
        country = request.data.get("country", "India")

        session = EventCollectorService.start_session(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            ip_address=ip,
            user_agent=agent,
            device_type=device,
            browser_type=browser,
            country=country
        )
        return Response(UserSessionSerializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="end")
    def end_session(self, request):
        session_key = request.data.get("session_key")
        if not session_key:
            return Response({"error": "session_key is required."}, status=status.HTTP_400_BAD_REQUEST)

        session = EventCollectorService.end_session(session_key)
        if not session:
            return Response({"error": "Active session key not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserSessionSerializer(session).data, status=status.HTTP_200_OK)


class PageViewViewSet(viewsets.ModelViewSet):
    queryset = PageView.objects.all().order_by("-created_at")
    serializer_class = PageViewSerializer
    permission_classes = [HasAnalyticsViewerPermission]


class CourseAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseAnalytics.objects.all()
    serializer_class = CourseAnalyticsSerializer
    permission_classes = [HasAnalyticsViewerPermission]


class ArticleAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArticleAnalytics.objects.all()
    serializer_class = ArticleAnalyticsSerializer
    permission_classes = [HasAnalyticsViewerPermission]


class SearchAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SearchAnalytics.objects.all().order_by("-total_queries")
    serializer_class = SearchAnalyticsSerializer
    permission_classes = [HasAnalyticsViewerPermission]


class NotificationAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationAnalytics.objects.all()
    serializer_class = NotificationAnalyticsSerializer
    permission_classes = [HasAnalyticsViewerPermission]


class WalletAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WalletAnalytics.objects.all()
    serializer_class = WalletAnalyticsSerializer
    permission_classes = [HasAnalyticsViewerPermission]


class RevenueAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RevenueAnalytics.objects.all().order_by("-date")
    serializer_class = RevenueAnalyticsSerializer
    permission_classes = [HasAnalyticsViewerPermission]


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by("-created_at")
    serializer_class = ReportSerializer
    permission_classes = [HasAnalyticsManagerPermission]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)


class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [HasAnalyticsViewerPermission]

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        """
        Dynamic statistics endpoint mapping configurations lists based on roles authorizations.
        """
        role = "role-super-admin"
        if request.user.is_authenticated and hasattr(request.user, "role") and request.user.role:
            role = f"role-{request.user.role.name.lower()}"
            
        widgets_payload = DashboardService.get_live_widgets(role)
        return Response({
            "generated_at": timezone.now().isoformat(),
            "role": role,
            "widgets": widgets_payload
        }, status=status.HTTP_200_OK)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    queryset = DashboardWidget.objects.all().order_by("display_order")
    serializer_class = DashboardWidgetSerializer
    permission_classes = [HasAnalyticsAdminPermission]


class KPIViewSet(viewsets.ModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [HasAnalyticsViewerPermission]


class MetricViewSet(viewsets.ModelViewSet):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    permission_classes = [HasAnalyticsAdminPermission]


class DailySummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailySummary.objects.all().order_by("-summary_date")
    serializer_class = DailySummarySerializer
    permission_classes = [HasAnalyticsViewerPermission]

    @action(detail=False, methods=["get"], url_path="timeseries")
    def timeseries(self, request):
        metric_key = request.query_params.get("metric")
        days = int(request.query_params.get("days", 30))

        if not metric_key:
            return Response({"error": "metric parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        timeseries_data = get_timeseries_metrics(metric_key, interval="daily", days_limit=days)
        return Response({
            "metric": metric_key,
            "days_limit": days,
            "timeseries": timeseries_data
        }, status=status.HTTP_200_OK)


class RealtimeCounterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RealtimeCounter.objects.all()
    serializer_class = RealtimeCounterSerializer
    permission_classes = [HasAnalyticsViewerPermission]


class ExportJobViewSet(viewsets.ModelViewSet):
    queryset = ExportJob.objects.all().order_by("-created_at")
    serializer_class = ExportJobSerializer
    permission_classes = [HasAnalyticsManagerPermission]

    def perform_create(self, serializer):
        job = serializer.save()
        # Enqueue background Celery task
        run_export_job_task.delay(job.id)


class ReportScheduleViewSet(viewsets.ModelViewSet):
    queryset = ReportSchedule.objects.all().order_by("next_run_at")
    serializer_class = ReportScheduleSerializer
    permission_classes = [HasAnalyticsManagerPermission]


class AuditAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditAnalytics.objects.all().order_by("-audit_date")
    serializer_class = AuditAnalyticsSerializer
    permission_classes = [HasAnalyticsAdminPermission]


class SystemMetricsViewSet(viewsets.ModelViewSet):
    queryset = SystemMetrics.objects.all().order_by("-created_at")
    serializer_class = SystemMetricsSerializer
    permission_classes = [HasAnalyticsAdminPermission]
from django.utils import timezone
