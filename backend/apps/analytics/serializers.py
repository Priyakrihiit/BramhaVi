from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AnalyticsEvent, UserSession, PageView, CourseAnalytics, ArticleAnalytics,
    SearchAnalytics, NotificationAnalytics, WalletAnalytics, RevenueAnalytics,
    Report, Dashboard, DashboardWidget, KPI, Metric, DailySummary,
    MonthlySummary, YearlySummary, RealtimeCounter, ExportJob,
    ReportSchedule, AuditAnalytics, SystemMetrics
)

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username"]


class AnalyticsEventSerializer(serializers.ModelSerializer):
    user_details = UserMinimalSerializer(source="user", read_only=True)

    class Meta:
        model = AnalyticsEvent
        fields = ["id", "user", "user_details", "metric_name", "metric_value", "context_data", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSessionSerializer(serializers.ModelSerializer):
    user_details = UserMinimalSerializer(source="user", read_only=True)

    class Meta:
        model = UserSession
        fields = [
            "id", "user", "user_details", "session_key", "ip_address", "user_agent",
            "device_type", "browser_type", "country", "login_at", "logout_at",
            "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "login_at", "created_at", "updated_at"]


class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = ["id", "session", "user", "url_path", "referrer", "dwell_time_seconds", "created_at"]
        read_only_fields = ["id", "created_at"]


class CourseAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAnalytics
        fields = [
            "id", "course_id", "total_enrollments", "active_students",
            "completion_count", "average_progress", "average_score", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ArticleAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleAnalytics
        fields = ["id", "article_id", "views_count", "shares_count", "likes_count", "comments_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SearchAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchAnalytics
        fields = ["id", "query_string", "total_queries", "total_results", "click_through_rate", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class NotificationAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationAnalytics
        fields = ["id", "notification_id", "total_delivered", "total_opened", "total_clicked", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class WalletAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletAnalytics
        fields = ["id", "wallet_id", "total_credits", "total_debits", "net_balance", "transaction_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class RevenueAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueAnalytics
        fields = ["id", "date", "total_sales", "gross_revenue", "refund_count", "refund_amount", "net_revenue", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReportSerializer(serializers.ModelSerializer):
    generated_by_details = UserMinimalSerializer(source="generated_by", read_only=True)

    class Meta:
        model = Report
        fields = ["id", "title", "description", "file_path", "format", "status", "query_params", "generated_by", "generated_by_details", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = ["id", "dashboard", "title", "metric_type", "query_target", "color_scheme", "icon_name", "display_order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DashboardSerializer(serializers.ModelSerializer):
    widgets = DashboardWidgetSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = ["id", "title", "description", "role_required", "is_system", "widgets", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = ["id", "name", "metric_key", "current_value", "target_value", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = ["id", "key", "name", "category", "unit", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DailySummarySerializer(serializers.ModelSerializer):
    metric_details = MetricSerializer(source="metric", read_only=True)

    class Meta:
        model = DailySummary
        fields = ["id", "summary_date", "metric", "metric_details", "value", "change_percentage", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MonthlySummarySerializer(serializers.ModelSerializer):
    metric_details = MetricSerializer(source="metric", read_only=True)

    class Meta:
        model = MonthlySummary
        fields = ["id", "summary_month", "metric", "metric_details", "value", "change_percentage", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class YearlySummarySerializer(serializers.ModelSerializer):
    metric_details = MetricSerializer(source="metric", read_only=True)

    class Meta:
        model = YearlySummary
        fields = ["id", "summary_year", "metric", "metric_details", "value", "change_percentage", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class RealtimeCounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealtimeCounter
        fields = ["id", "counter_key", "current_count", "last_updated_at", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ExportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportJob
        fields = ["id", "job_type", "status", "file_url", "error_message", "request_payload", "created_at", "updated_at"]
        read_only_fields = ["id", "file_url", "error_message", "created_at", "updated_at"]


class ReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = ["id", "report_title", "frequency", "recipients", "next_run_at", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AuditAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditAnalytics
        fields = ["id", "audit_date", "total_mutations", "error_mutations", "unauthorized_attempts", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SystemMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetrics
        fields = ["id", "cpu_usage_pct", "memory_usage_pct", "disk_usage_pct", "active_connections", "api_response_time_avg", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
