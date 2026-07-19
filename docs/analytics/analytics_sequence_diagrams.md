# BrahmaVidya Analytics: Sequence Diagrams

This document maps execution sequences for key analytics processes.

---

## 1. Event Telemetry Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Client as React Client
    participant GW as Express Gateway (server.ts)
    participant View as Django View (views.py)
    participant Queue as Celery Queue (Redis)
    participant DB as SQLite (AnalyticsEvent)

    Client->>GW: POST /api/v1/analytics/events/collect/
    Note over GW: Track request trace context headers
    GW->>View: Forward payload
    View->>Queue: Dispatch track_event_task.delay()
    View-->>GW: Return HTTP 201 Created (immediate)
    GW-->>Client: Acknowledge successful ingestion
    Note over Queue: Celery worker processes task
    Queue->>DB: Save AnalyticsEvent record
```

---

## 2. Daily Metrics Aggregation

```mermaid
sequenceDiagram
    autonumber
    participant Beat as Celery Beat Scheduler
    participant Task as aggregate_daily_metrics_task
    participant Selector as Selectors Query layer
    participant DB as SQLite (DailySummary)

    Beat->>Task: Trigger daily metrics calculation at midnight
    Task->>Selector: Query sum and counts over raw events
    Selector-->>Task: Return compiled daily values
    Task->>DB: Update or create DailySummary record
    DB-->>Task: Acknowledge write
```

---

## 3. On-Demand File Exporter

```mermaid
sequenceDiagram
    autonumber
    actor Mgr as Portal Manager
    participant Client as React Client
    participant GW as Express Gateway
    participant View as Django View (exports/)
    participant Task as run_export_job_task
    participant File as Files Directory (exports/)

    Mgr->>Client: Click "Create PDF Export"
    Client->>GW: POST /api/v1/analytics/exports/ (payload: PDF)
    GW->>View: Forward request
    View->>View: Create ExportJob in PENDING state
    View->>Task: Dispatch run_export_job_task.delay(id)
    View-->>GW: Return HTTP 201 Created (job details)
    GW-->>Client: Update UI to show job is PENDING
    Note over Task: Worker compiles events to text PDF stream
    Task->>File: Write file to static directory
    Task->>View: Update ExportJob to COMPLETED
    Client->>View: Poll job status
    View-->>Client: Return COMPLETED (with file_url)
    Client->>Mgr: Display "Download File" link
```
