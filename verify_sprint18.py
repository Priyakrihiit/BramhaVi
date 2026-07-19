import os
import sys
import django

# Setup django environment
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.db import connection
from apps.analytics.models import AnalyticsEvent, UserSession, KPI, Metric, DailySummary
from apps.analytics.services import EventCollectorService, AggregationService
from apps.analytics.selectors import get_timeseries_metrics


def hard_delete_metric(key: str):
    """Hard-delete a metric and its FK-dependent daily summaries using SQLite PRAGMA."""
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute(f"DELETE FROM analytics_daily_summaries WHERE metric_id IN (SELECT id FROM analytics_metric_definitions WHERE key='{key}')")
    cursor.execute(f"DELETE FROM analytics_metric_definitions WHERE key='{key}'")
    cursor.execute("PRAGMA foreign_keys = ON")


def run_checks():
    print("==================================================")
    print("BrahmaVidya Analytics Platform Verification Script")
    print("==================================================")

    # 1. Check schema row counts
    print(f"[*] Raw Analytics Events count: {AnalyticsEvent.objects.count()}")
    print(f"[*] User Sessions count: {UserSession.objects.count()}")

    # 2. Test event collector tracking
    print("[*] Tracking mock pageview event...")
    event = EventCollectorService.track_event(
        user=None,
        metric_name="Page Navigation",
        metric_value=1.0,
        context_data={"url_path": "/test/verify-analytics"}
    )
    print(f"    - Event logged successfully (ID: {event.id})")

    # 3. Seed metric definition - purge stale first with FK disabled
    print("[*] Registering mock metric configuration...")
    hard_delete_metric("mock_test_runs")
    metric = Metric.objects.create(
        key="mock_test_runs",
        name="Page Navigation",
        category="testing",
        unit="count",
        description="Mock check metrics"
    )
    print(f"    - Metric Key: {metric.key}")

    # 4. Test daily aggregations
    print("[*] Compiling daily summary aggregate...")
    summary = AggregationService.aggregate_metric_daily("mock_test_runs", event.created_at.date())
    print(f"    - Generated DailySummary ID: {summary.id} (Value: {summary.value})")

    # 5. Verify timeseries selector
    print("[*] Querying timeseries charts format...")
    chart_series = get_timeseries_metrics("mock_test_runs", days_limit=7)
    print(f"    - Charts Data Array size: {len(chart_series)}")
    for data in chart_series:
        print(f"      * {data['label']}: {data['value']}")

    # 6. Verify Django URL routing
    print("[*] Running analytics URL resolver verification...")
    from django.urls import resolve
    match = resolve('/api/v1/analytics/events/collect/')
    print(f"    - Route resolved: {match.url_name} -> {match.namespaces}")

    # 7. Verify signal receivers are loaded
    print("[*] Verifying signal receivers are registered...")
    from django.db.models.signals import post_save
    receivers = post_save.receivers
    print(f"    - Total post_save signal receivers: {len(receivers)}")

    # 8. Clean up all mock items
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute(f"DELETE FROM analytics_event_logs WHERE id='{event.id}'")
    hard_delete_metric("mock_test_runs")
    cursor.execute("PRAGMA foreign_keys = ON")
    print("    - Verification entries cleaned up successfully.")

    print("\n[+] Verification checks completed successfully!")
    print("==================================================")


if __name__ == '__main__':
    run_checks()
