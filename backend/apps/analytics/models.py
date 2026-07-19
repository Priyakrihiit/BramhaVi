import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.base_models import BaseModel, SoftDeleteModel

User = get_user_model()


class AnalyticsEvent(BaseModel):
    """
    High-velocity performance reporting telemetry logs.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analytics_event_records"
    )
    metric_name = models.CharField(max_length=100, db_index=True, help_text="Telemetry identifier (e.g., video_playback_sec).")
    metric_value = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        blank=True,
        null=True,
        help_text="Numeric telemetry quantity."
    )
    context_data = models.JSONField(default=dict, blank=True, help_text="Dynamic telemetry details payload.")

    class Meta:
        db_table = "analytics_event_logs"
        verbose_name = "Analytics Event"
        verbose_name_plural = "Analytics Events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["metric_name", "-created_at"]),
        ]


class UserSession(SoftDeleteModel):
    """
    Tracks aggregate user sessions statistics.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="analytics_sessions"
    )
    session_key = models.CharField(max_length=255, unique=True, db_index=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    browser_type = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "analytics_user_sessions"
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        ordering = ["-login_at"]


class PageView(BaseModel):
    """
    Records page layout visits and dwell metrics.
    """
    session = models.ForeignKey(
        UserSession,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="page_views"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="analytics_page_views"
    )
    url_path = models.CharField(max_length=500, db_index=True)
    referrer = models.CharField(max_length=500, blank=True, null=True)
    dwell_time_seconds = models.IntegerField(default=0)

    class Meta:
        db_table = "analytics_page_views"
        verbose_name = "Page View"
        verbose_name_plural = "Page Views"
        ordering = ["-created_at"]


class CourseAnalytics(BaseModel):
    """
    Aggregates learning progress across courses.
    """
    course_id = models.UUIDField(db_index=True, unique=True)
    total_enrollments = models.IntegerField(default=0)
    active_students = models.IntegerField(default=0)
    completion_count = models.IntegerField(default=0)
    average_progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        db_table = "analytics_course_metrics"
        verbose_name = "Course Analytics"
        verbose_name_plural = "Course Analytics Summaries"


class ArticleAnalytics(BaseModel):
    """
    CMS articles views and likes aggregator.
    """
    article_id = models.UUIDField(db_index=True, unique=True)
    views_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)

    class Meta:
        db_table = "analytics_article_metrics"
        verbose_name = "Article Analytics"
        verbose_name_plural = "Article Analytics Summaries"


class SearchAnalytics(BaseModel):
    """
    Search queries performance analytics.
    """
    query_string = models.CharField(max_length=255, unique=True, db_index=True)
    total_queries = models.IntegerField(default=0)
    total_results = models.IntegerField(default=0)
    click_through_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)

    class Meta:
        db_table = "analytics_search_metrics"
        verbose_name = "Search Analytics"
        verbose_name_plural = "Search Analytics Summaries"


class NotificationAnalytics(BaseModel):
    """
    Global alert delivery and click metrics.
    """
    notification_id = models.UUIDField(db_index=True, unique=True)
    total_delivered = models.IntegerField(default=0)
    total_opened = models.IntegerField(default=0)
    total_clicked = models.IntegerField(default=0)

    class Meta:
        db_table = "analytics_notification_metrics"
        verbose_name = "Notification Analytics"
        verbose_name_plural = "Notification Analytics Summaries"


class WalletAnalytics(BaseModel):
    """
    Wallet net balances and transaction aggregates.
    """
    wallet_id = models.UUIDField(db_index=True, unique=True)
    total_credits = models.DecimalField(max_digits=15, decimal_places=4, default=0.0000)
    total_debits = models.DecimalField(max_digits=15, decimal_places=4, default=0.0000)
    net_balance = models.DecimalField(max_digits=15, decimal_places=4, default=0.0000)
    transaction_count = models.IntegerField(default=0)

    class Meta:
        db_table = "analytics_wallet_metrics"
        verbose_name = "Wallet Analytics"
        verbose_name_plural = "Wallet Analytics Summaries"


class RevenueAnalytics(BaseModel):
    """
    Daily aggregated sales summaries.
    """
    date = models.DateField(unique=True, db_index=True)
    total_sales = models.IntegerField(default=0)
    gross_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    refund_count = models.IntegerField(default=0)
    refund_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    net_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    class Meta:
        db_table = "analytics_revenue_metrics"
        verbose_name = "Revenue Analytics"
        verbose_name_plural = "Revenue Analytics Summaries"
        ordering = ["-date"]


class Report(SoftDeleteModel):
    """
    Stores compiled metrics pdf/csv report metadata.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    format = models.CharField(max_length=10, default="PDF", help_text="PDF, CSV, JSON")
    status = models.CharField(max_length=20, default="PENDING", help_text="PENDING, GENERATING, COMPLETED, FAILED")
    query_params = models.JSONField(default=dict, blank=True)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="generated_analytics_reports"
    )

    class Meta:
        db_table = "analytics_reports"
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ["-created_at"]


class Dashboard(SoftDeleteModel):
    """
    Dynamic container mapping role widgets panels.
    """
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    role_required = models.CharField(max_length=100, default="role-super-admin", db_index=True)
    is_system = models.BooleanField(default=False)

    class Meta:
        db_table = "analytics_dashboards"
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"


class DashboardWidget(SoftDeleteModel):
    """
    Configures widgets grids panels shown on dashboards.
    """
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name="widgets"
    )
    title = models.CharField(max_length=100)
    metric_type = models.CharField(
        max_length=30,
        choices=[
            ("DB_COUNT", "Database Count Query"),
            ("DB_SUM", "Database Sum/Aggregate Query"),
            ("TELEMETRY_RATE", "Telemetry Event Rate"),
            ("STATIC_VALUE", "Fixed Parameter"),
        ],
        default="DB_COUNT"
    )
    query_target = models.CharField(max_length=255, help_text="E.g. lms.CourseStructure.count")
    color_scheme = models.CharField(max_length=50, default="indigo")
    icon_name = models.CharField(max_length=50, default="Activity")
    display_order = models.IntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "analytics_dashboard_widgets"
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"
        ordering = ["display_order"]


class KPI(SoftDeleteModel):
    """
    Tracks performance indicators against target figures.
    """
    name = models.CharField(max_length=100, unique=True)
    metric_key = models.CharField(max_length=100, db_index=True)
    current_value = models.DecimalField(max_digits=15, decimal_places=4, default=0.0000)
    target_value = models.DecimalField(max_digits=15, decimal_places=4, default=0.0000)
    status = models.CharField(max_length=20, default="STABLE", help_text="CRITICAL, STABLE, ACHIEVED")

    class Meta:
        db_table = "analytics_kpis"
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"


class Metric(SoftDeleteModel):
    """
    Definitions catalog registry for trackable system metrics.
    """
    key = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, db_index=True)
    unit = models.CharField(max_length=20, default="count")
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "analytics_metric_definitions"
        verbose_name = "Metric Definition"
        verbose_name_plural = "Metric Definitions"


class DailySummary(BaseModel):
    """
    Aggregated stats summary by day.
    """
    summary_date = models.DateField(db_index=True)
    metric = models.ForeignKey(
        Metric,
        on_delete=models.CASCADE,
        related_name="daily_summaries"
    )
    value = models.DecimalField(max_digits=15, decimal_places=4, default=0.0000)
    change_percentage = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000)

    class Meta:
        db_table = "analytics_daily_summaries"
        verbose_name = "Daily Summary"
        verbose_name_plural = "Daily Summaries"
        ordering = ["-summary_date"]
        unique_together = ("summary_date", "metric")


class MonthlySummary(BaseModel):
    """
    Aggregated stats summary by month.
    """
    summary_month = models.DateField(db_index=True, help_text="First day of the month.")
    metric = models.ForeignKey(
        Metric,
        on_delete=models.CASCADE,
        related_name="monthly_summaries"
    )
    value = models.DecimalField(max_digits=15, decimal_places=4, default=0.0000)
    change_percentage = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000)

    class Meta:
        db_table = "analytics_monthly_summaries"
        verbose_name = "Monthly Summary"
        verbose_name_plural = "Monthly Summaries"
        ordering = ["-summary_month"]
        unique_together = ("summary_month", "metric")


class YearlySummary(BaseModel):
    """
    Aggregated stats summary by year.
    """
    summary_year = models.IntegerField(db_index=True)
    metric = models.ForeignKey(
        Metric,
        on_delete=models.CASCADE,
        related_name="yearly_summaries"
    )
    value = models.DecimalField(max_digits=15, decimal_places=4, default=0.0000)
    change_percentage = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000)

    class Meta:
        db_table = "analytics_yearly_summaries"
        verbose_name = "Yearly Summary"
        verbose_name_plural = "Yearly Summaries"
        ordering = ["-summary_year"]
        unique_together = ("summary_year", "metric")


class RealtimeCounter(BaseModel):
    """
    Cached real-time counter values.
    """
    counter_key = models.CharField(max_length=150, unique=True, db_index=True)
    current_count = models.IntegerField(default=0)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "analytics_realtime_counters"
        verbose_name = "Realtime Counter"
        verbose_name_plural = "Realtime Counters"


class ExportJob(SoftDeleteModel):
    """
    Tracks requests for bulk file data exports.
    """
    job_type = models.CharField(max_length=50, db_index=True)
    status = models.CharField(max_length=20, default="PENDING", db_index=True)
    file_url = models.CharField(max_length=500, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    request_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "analytics_export_jobs"
        verbose_name = "Export Job"
        verbose_name_plural = "Export Jobs"
        ordering = ["-created_at"]


class ReportSchedule(SoftDeleteModel):
    """
    Configures automated report emails.
    """
    report_title = models.CharField(max_length=200)
    frequency = models.CharField(
        max_length=20,
        choices=[
            ("DAILY", "Daily"),
            ("WEEKLY", "Weekly"),
            ("MONTHLY", "Monthly"),
        ],
        default="WEEKLY"
    )
    recipients = models.JSONField(default=list)
    next_run_at = models.DateTimeField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "analytics_report_schedules"
        verbose_name = "Report Schedule"
        verbose_name_plural = "Report Schedules"
        ordering = ["next_run_at"]


class AuditAnalytics(BaseModel):
    """
    Monitors operations security mutations.
    """
    audit_date = models.DateField(unique=True, db_index=True)
    total_mutations = models.IntegerField(default=0)
    error_mutations = models.IntegerField(default=0)
    unauthorized_attempts = models.IntegerField(default=0)

    class Meta:
        db_table = "analytics_audit_summaries"
        verbose_name = "Audit Analytics"
        verbose_name_plural = "Audit Analytics Summaries"
        ordering = ["-audit_date"]


class SystemMetrics(BaseModel):
    """
    Records raw OS infrastructure performance stats.
    """
    cpu_usage_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    memory_usage_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    disk_usage_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    active_connections = models.IntegerField(default=0)
    api_response_time_avg = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)

    class Meta:
        db_table = "analytics_system_metrics"
        verbose_name = "System Metric"
        verbose_name_plural = "System Metrics"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]
