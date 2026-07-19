import csv
import io
import decimal
from django.utils import timezone
from datetime import datetime, date
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Avg, F
from .models import (
    AnalyticsEvent, UserSession, PageView, DailySummary, RealtimeCounter,
    Metric, KPI, Dashboard, DashboardWidget, ExportJob, Report
)

User = get_user_model()


class EventCollectorService:
    @staticmethod
    def track_event(user, metric_name, metric_value=1.0, context_data=None):
        """
        Saves a raw event metrics log.
        """
        return AnalyticsEvent.objects.create(
            user=user if user and user.is_authenticated else None,
            metric_name=metric_name,
            metric_value=decimal.Decimal(str(metric_value)),
            context_data=context_data or {}
        )

    @staticmethod
    @transaction.atomic
    def start_session(user, session_key, ip_address=None, user_agent=None, device_type=None, browser_type=None, country=None):
        """
        Creates or updates a session log and increments the active users counter.
        """
        session, created = UserSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                "user": user,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "device_type": device_type or "Desktop",
                "browser_type": browser_type or "Chrome",
                "country": country or "India",
                "is_active": True,
                "login_at": timezone.now()
            }
        )

        # Increment active users counter
        counter, _ = RealtimeCounter.objects.get_or_create(
            counter_key="live_active_users",
            defaults={"current_count": 0}
        )
        counter.current_count = F("current_count") + 1
        counter.save()
        return session

    @staticmethod
    @transaction.atomic
    def end_session(session_key):
        """
        Ends a session log and decrements the active users counter.
        """
        try:
            session = UserSession.objects.get(session_key=session_key, is_active=True)
            session.is_active = False
            session.logout_at = timezone.now()
            session.save()

            # Decrement active users counter
            counter = RealtimeCounter.objects.filter(counter_key="live_active_users").first()
            if counter and counter.current_count > 0:
                counter.current_count = F("current_count") - 1
                counter.save()
            return session
        except UserSession.DoesNotExist:
            return None

    @staticmethod
    def log_page_view(session_key, user, url_path, referrer=None, dwell_time=0):
        """
        Logs a user page view.
        """
        session = UserSession.objects.filter(session_key=session_key).first()
        return PageView.objects.create(
            session=session,
            user=user if user and user.is_authenticated else None,
            url_path=url_path,
            referrer=referrer,
            dwell_time_seconds=dwell_time
        )


class AggregationService:
    @staticmethod
    @transaction.atomic
    def aggregate_metric_daily(metric_key, target_date):
        """
        Computes summary values for a metric key on a specific date.
        """
        metric = Metric.objects.filter(key=metric_key).first()
        if not metric:
            return None

        # Resolve total sum value or fallback values
        events = AnalyticsEvent.objects.filter(
            metric_name=metric.name,
            created_at__date=target_date
        )
        total_val = events.aggregate(total=Sum("metric_value"))["total"] or decimal.Decimal("0.0000")

        # Get previous value to compute change percentage
        prev_summary = DailySummary.objects.filter(
            metric=metric,
            summary_date=target_date - timezone.timedelta(days=1)
        ).first()

        change_pct = decimal.Decimal("0.0000")
        if prev_summary and prev_summary.value > 0:
            change_pct = ((total_val - prev_summary.value) / prev_summary.value) * 100

        summary, _ = DailySummary.objects.update_or_create(
            summary_date=target_date,
            metric=metric,
            defaults={
                "value": total_val,
                "change_percentage": change_pct
            }
        )
        return summary

    @staticmethod
    def run_global_daily_aggregation(target_date=None):
        """
        Runs aggregation calculations for all active metric definitions.
        """
        if not target_date:
            target_date = timezone.now().date()

        metrics = Metric.objects.filter(deleted_at__isnull=True)
        results = []
        for metric in metrics:
            summary = AggregationService.aggregate_metric_daily(metric.key, target_date)
            if summary:
                results.append(summary)
        return results


class DashboardService:
    @staticmethod
    def get_kpi_metrics():
        """
        Retrieves current target stats for all registered key performance indicators.
        """
        return KPI.objects.filter(deleted_at__isnull=True).order_by("name")

    @staticmethod
    def get_live_widgets(user_role):
        """
        Compiles dynamic widget counts matching authorization role limits.
        """
        dashboards = Dashboard.objects.filter(role_required=user_role, deleted_at__isnull=True)
        if not dashboards.exists():
            return []

        widgets = DashboardWidget.objects.filter(
            dashboard__in=dashboards,
            is_active=True,
            deleted_at__isnull=True
        ).order_by("display_order")

        payloads = []
        for w in widgets:
            val = "0"
            try:
                # Count queries matching target
                if w.metric_type == "DB_COUNT" and w.query_target:
                    from django.apps import apps
                    app_label, model_name = w.query_target.split(".")[:2]
                    model_class = apps.get_model(app_label=app_label, model_name=model_name)
                    val = str(model_class.objects.count())
                elif w.metric_type == "STATIC_VALUE":
                    val = w.query_target
            except Exception:
                val = "N/A"

            payloads.append({
                "id": str(w.id),
                "title": w.title,
                "value": val,
                "color": w.color_scheme,
                "icon": w.icon_name
            })
        return payloads


class ExportService:
    @staticmethod
    def export_events_csv(job_id):
        """
        Writes pageviews or events logs to a CSV string buffer.
        """
        job = ExportJob.objects.filter(id=job_id).first()
        if not job:
            return ""

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(["Event ID", "Metric Name", "Metric Value", "Timestamp"])
        
        # Query matching events
        events = AnalyticsEvent.objects.all().order_by("-created_at")[:1000]
        for e in events:
            writer.writerow([str(e.id), e.metric_name, str(e.metric_value), e.created_at.isoformat()])
            
        return output.getvalue()

    @staticmethod
    def export_events_excel(job_id):
        """
        Writes pageviews or events logs to a tab-separated Excel mock sheet.
        """
        job = ExportJob.objects.filter(id=job_id).first()
        if not job:
            return ""

        output = io.StringIO()
        # Excel Tab-Separated representation
        output.write("Event ID\tMetric Name\tMetric Value\tTimestamp\n")
        
        events = AnalyticsEvent.objects.all().order_by("-created_at")[:1000]
        for e in events:
            output.write(f"{e.id}\t{e.metric_name}\t{e.metric_value}\t{e.created_at.isoformat()}\n")
            
        return output.getvalue()

    @staticmethod
    def export_events_pdf(job_id):
        """
        Creates a text representation simulating formatted PDF layouts.
        """
        job = ExportJob.objects.filter(id=job_id).first()
        if not job:
            return ""

        output = io.StringIO()
        output.write("==================================================\n")
        output.write("   BrahmaVidya Platform Analytics Export Report   \n")
        output.write(f"   Generated on: {timezone.now().isoformat()}   \n")
        output.write("==================================================\n\n")
        
        events = AnalyticsEvent.objects.all().order_by("-created_at")[:100]
        for e in events:
            output.write(f"[{e.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {e.metric_name}: {e.metric_value}\n")
            
        return output.getvalue()
