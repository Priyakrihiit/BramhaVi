import logging
from django.utils import timezone
from django.core.cache import caches
from datetime import timedelta
from django.db.models import Sum, Avg, Count, F
from .models import UserSession, AnalyticsEvent, PageView, DailySummary, RealtimeCounter, Metric

logger = logging.getLogger("brahmavidya.analytics")

# Use the dedicated analytics cache tier (1h TTL) or fall back to default
def _get_cache():
    try:
        return caches["analytics"]
    except Exception:
        try:
            return caches["default"]
        except Exception:
            from django.core.cache import cache
            return cache


def get_user_sessions(user=None, is_active=None, limit=100):
    """
    Retrieves filtered list of user session logs.
    Uses select_related and only() to minimize DB query payload.
    """
    qs = UserSession.objects.select_related("user").only(
        "id", "session_key", "ip_address", "device_type", "browser_type",
        "country", "login_at", "logout_at", "is_active",
        "user__id", "user__email", "user__first_name",
    )
    if user:
        qs = qs.filter(user=user)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs.order_by("-login_at")[:limit]


def get_analytics_events(metric_name=None, days_limit=30, limit=100):
    """
    Retrieves filtered metrics log events.
    Cached for 60 seconds per metric/days combination.
    """
    cache = _get_cache()
    cache_key = f"events:{metric_name}:{days_limit}:{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    qs = AnalyticsEvent.objects.select_related("user").only(
        "id", "metric_name", "metric_value", "context_data", "created_at",
        "user__id", "user__email",
    )
    if metric_name:
        qs = qs.filter(metric_name=metric_name)
    if days_limit:
        cutoff = timezone.now() - timedelta(days=days_limit)
        qs = qs.filter(created_at__gte=cutoff)

    result = list(qs.order_by("-created_at")[:limit])
    cache.set(cache_key, result, timeout=60)
    return result


def get_timeseries_metrics(metric_key, interval="daily", days_limit=30):
    """
    Returns data formatted for charts from the daily summaries table.
    Cached in the analytics cache tier for 1 hour (summaries are pre-aggregated).
    """
    cache = _get_cache()
    cache_key = f"timeseries:{metric_key}:{interval}:{days_limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.debug(f"Cache HIT timeseries for {metric_key}")
        return cached

    cutoff = timezone.now().date() - timedelta(days=days_limit)
    summaries = DailySummary.objects.filter(
        metric__key=metric_key,
        summary_date__gte=cutoff,
    ).select_related("metric").only(
        "id", "summary_date", "value", "change_percentage",
        "metric__key", "metric__name",
    ).order_by("summary_date")

    fmt = "%Y-%m-%d" if interval == "daily" else "%b %d"
    timeseries = [
        {
            "label": s.summary_date.strftime(fmt),
            "value": float(s.value),
            "change": float(s.change_percentage),
        }
        for s in summaries
    ]

    cache.set(cache_key, timeseries, timeout=3600)
    logger.debug(f"Cache SET timeseries for {metric_key}: {len(timeseries)} points")
    return timeseries


def get_active_realtime_count(counter_key):
    """
    Retrieves current count from live realtime counters.
    Short-lived cache (10 seconds) to reduce hammering on dashboard refresh.
    """
    cache = _get_cache()
    cache_key = f"realtime:{counter_key}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        counter = RealtimeCounter.objects.only("current_count").get(counter_key=counter_key)
        value = counter.current_count
    except RealtimeCounter.DoesNotExist:
        value = 0

    cache.set(cache_key, value, timeout=10)
    return value


def get_dashboard_kpi_summary():
    """
    Returns aggregated KPI health summary across all defined metrics.
    Cached for 5 minutes — expensive multi-table aggregation.
    """
    cache = _get_cache()
    cache_key = "dashboard:kpi_summary"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    from .models import KPI
    kpis = list(KPI.objects.only(
        "id", "name", "metric_key", "current_value", "target_value", "status"
    ).order_by("name"))

    result = [
        {
            "id": str(k.id),
            "name": k.name,
            "metric_key": k.metric_key,
            "current_value": float(k.current_value),
            "target_value": float(k.target_value),
            "status": k.status,
            "progress_pct": round(min((k.current_value / k.target_value) * 100, 100), 1) if k.target_value else 0,
        }
        for k in kpis
    ]

    cache.set(cache_key, result, timeout=300)
    return result
