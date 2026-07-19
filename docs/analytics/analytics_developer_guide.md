# Developer Guide: Enterprise Analytics Platform

**BrahmaVidya Galaxy — Analytics Module**
**Version:** 1.0 | **Audience:** Backend Engineers, Frontend Developers

---

## 1. Module Structure

```
backend/apps/analytics/
├── __init__.py
├── apps.py               # AppConfig, signals auto-discovery
├── models.py             # 22 database models (BaseModel + SoftDeleteModel)
├── serializers.py        # DRF serializers for all models
├── permissions.py        # AnalyticsViewer, AnalyticsManager, AnalyticsAdmin
├── views.py              # 20 ModelViewSets with custom actions
├── urls.py               # DefaultRouter with app_name = "analytics"
├── services.py           # EventCollectorService, AggregationService, ExportService
├── selectors.py          # get_timeseries_metrics, get_kpi_status
├── validators.py         # Input validation helpers
├── filters.py            # DjangoFilterBackend filter classes
├── signals.py            # 15+ post_save signal receivers
└── tasks.py              # Celery async tasks (track, aggregate, export)
```

---

## 2. Adding a New Tracked Event

To add a new analytics signal for a new model:

**Step 1 — Add the signal receiver to `signals.py`:**
```python
@receiver(post_save, sender="myapp.MyModel")
def handle_my_model_event(sender, instance, created, **kwargs):
    if created:
        EventCollectorService.track_event(
            user=instance.user,
            metric_name="My Event Name",
            metric_value=1.0,
            context_data={"id": str(instance.id)}
        )
```

**Step 2 — Ensure the app is registered** in `django_project/settings.py` under `INSTALLED_APPS`.

**Step 3 — Verify signal loads** in shell:
```bash
python backend/manage.py shell -c "from apps.analytics import signals; print('Loaded')"
```

---

## 3. Adding a New Dashboard Widget

Widgets are database-backed configurations queried by `DashboardService.get_widgets()`:

1. Open Django Admin at `/admin/analytics/dashboardwidget/add/`.
2. Fill in:
   - `title`: Display label (e.g., `"New Metric"`)
   - `metric_type`: One of `count`, `sum`, `avg`
   - `query_target`: The target Django model path (e.g., `"lms.Certificate"`)
   - `color_scheme`: CSS Tailwind color class prefix
   - `icon_name`: Lucide icon name (e.g., `"Award"`)
   - `display_order`: Integer sort order
3. Save. The widget appears on the Control Dashboard automatically.

---

## 4. Extending the API

All viewsets are registered via `DefaultRouter` in `urls.py`. To add a new custom action:

```python
# In views.py
@action(detail=False, methods=["get"], url_path="my-custom-action")
def my_custom_action(self, request):
    data = selectors.get_my_custom_data()
    return Response(data)
```

Then add the corresponding client method in `src/services/analyticsApi.ts`:
```typescript
myCustomAction: () => request<MyType>(`${BASE_URL}/events/my-custom-action/`),
```

---

## 5. Celery Task Queue

All heavy operations run via Celery. The task definitions are in `tasks.py`:

| Task | Trigger | Description |
|---|---|---|
| `track_event_task` | On `collect/` request | Async event write to database |
| `aggregate_daily_metrics_task` | Celery Beat midnight | Computes daily summaries |
| `run_export_job_task` | On export POST | Builds CSV/Excel/PDF file |
| `send_scheduled_report_task` | Celery Beat by frequency | Emails report to recipients |

To manually trigger an aggregate:
```bash
python backend/manage.py shell -c "from apps.analytics.tasks import aggregate_daily_metrics_task; aggregate_daily_metrics_task.delay()"
```

---

## 6. Frontend Architecture

```
src/
├── services/analyticsApi.ts          # Typed API client
└── components/analytics/
    └── EnterpriseAnalyticsView.tsx   # Main dashboard view (tabs, charts, exports)
```

The component is mounted at `/admin/analytics` via `App.tsx` routing and linked in the `DynamicSidebar.tsx` config.

Charts are rendered using native inline SVG — no external chart library dependency required.
