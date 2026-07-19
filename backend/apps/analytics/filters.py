import django_filters
from .models import AnalyticsEvent, UserSession, PageView, DailySummary


class AnalyticsEventFilter(django_filters.FilterSet):
    metric_name = django_filters.CharFilter(lookup_expr="icontains")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = AnalyticsEvent
        fields = ["metric_name", "user"]


class UserSessionFilter(django_filters.FilterSet):
    device_type = django_filters.CharFilter(lookup_expr="iexact")
    country = django_filters.CharFilter(lookup_expr="iexact")
    is_active = django_filters.BooleanFilter()
    login_after = django_filters.DateTimeFilter(field_name="login_at", lookup_expr="gte")
    login_before = django_filters.DateTimeFilter(field_name="login_at", lookup_expr="lte")

    class Meta:
        model = UserSession
        fields = ["user", "device_type", "country", "is_active"]


class PageViewFilter(django_filters.FilterSet):
    url_path = django_filters.CharFilter(lookup_expr="icontains")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = PageView
        fields = ["user", "session", "url_path"]


class DailySummaryFilter(django_filters.FilterSet):
    metric_key = django_filters.CharFilter(field_name="metric__key", lookup_expr="iexact")
    metric_category = django_filters.CharFilter(field_name="metric__category", lookup_expr="iexact")
    summary_after = django_filters.DateFilter(field_name="summary_date", lookup_expr="gte")
    summary_before = django_filters.DateFilter(field_name="summary_date", lookup_expr="lte")

    class Meta:
        model = DailySummary
        fields = ["metric", "summary_date"]
