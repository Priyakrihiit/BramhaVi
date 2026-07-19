# Software Design Specification (SDS): Enterprise Analytics Platform

## 1. System Design
The analytics platform backend is implemented using a service-oriented structure within the Django application (`apps.analytics`), routed via the Express API gateway, and rendered in the React dashboard.

### Subsystems Map
* **Event Ingestion:** Client events are sent to the `collect/` endpoint, where the view delegates database writes to Celery workers using Redis.
* **Daily Aggregator:** A Celery Beat scheduler triggers the daily summary task `aggregate_daily_metrics_task` at midnight to aggregate raw events into structured stats.
* **Export Worker:** On-demand exports (PDF, Excel, CSV) are processed asynchronously in the background.

## 2. Dynamic Performance Scoring
Aggregations process counts and sums dynamically:
$$\text{KPI Value} = \sum (\text{Metric Events}) \text{ or } \text{Count}(\text{Unique Entities})$$
* Dashboard widgets query target database tables dynamically using reflection methods to fetch counts.
* Caching layers keep aggregated stats available in under 10ms.
