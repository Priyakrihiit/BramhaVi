# Analytics Backend Specifications Manual

This documentation details the business logic, selectors, validation rules, signal listeners, and background tasks of the analytics platform backend.

---

## 1. Services Specifications

Defined inside `services.py`:
* **`EventCollectorService`:**
  - `track_event(user, name, value, context)`: Creates raw `AnalyticsEvent` records.
  - `start_session(user, key, ip, user_agent, ...)`: Tracks user logins, starts sessions, and increments the `live_active_users` counter.
  - `end_session(key)`: Ends sessions and decrements the counter.
  - `log_page_view(key, user, url, ...)`: Logs page navigations.
* **`AggregationService`:**
  - `aggregate_metric_daily(key, date)`: Resolves day-over-day metrics changes.
  - `run_global_daily_aggregation(date)`: Performs scheduled aggregations for active KPI metrics.
* **`DashboardService`:**
  - `get_live_widgets(role)`: Performs dynamic reflection queries based on user roles.
* **`ExportService`:**
  - `export_events_csv` / `export_events_excel` / `export_events_pdf`: Generates formatted CSVs, tab-separated Excel sheets, or print-ready PDF text streams.

---

## 2. Selectors Specifications

Defined inside `selectors.py`:
* `get_user_sessions(user, is_active)`: Retrieves user login sessions history.
* `get_analytics_events(metric_name, days_limit)`: Retrieves raw telemetry metrics events.
* `get_timeseries_metrics(metric_key)`: Resolves aggregated values formatted as timeseries arrays for React chart rendering.

---

## 3. Celery Tasks & Signals Pipeline

### Celery Tasks (`tasks.py`)
- `track_event_task`: Enqueues and saves raw client events.
- `aggregate_daily_metrics_task`: Re-aggregates performance records.
- `run_export_job_task`: Compiles and outputs data export files.
- `process_scheduled_reports_task`: Checks active schedules and emails compiled PDF/CSV reports.

### Signal Automation (`signals.py`)
- **Login/Logout Hooks:** Automatically creates or ends active user session records when users log in or out.
- **Learning Progression Logs:** Listens to `post_save` on `LearningProgress` to log `Lesson Started` or `Course Completed` events.
- **Conversions Logs:** Listens to `post_save` on `Payment` to track payments and financial volumes.
