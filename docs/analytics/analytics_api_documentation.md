# REST API Endpoints & Permissions Manual: Enterprise Analytics Platform

This document describes version 1 (`/api/v1/analytics/`) REST endpoints, request payloads, response states, and dynamic capability permissions mapping.

---

## 1. REST Endpoints Registry

The platform exposes the following versioned endpoints:

| Endpoint Path | HTTP Method | Action | Expected Payload / Response | Required Permission |
|---|---|---|---|---|
| `/api/v1/analytics/events/` | GET | List events | Returns list of raw events log. | `analytics:view` |
| `/api/v1/analytics/events/collect/` | POST | Log client event | Body: `{"metric_name": "Video Progress", "metric_value": 30.5, "context_data": {"user_id": "std-101", "course_id": "course-99"}}` | Public / `AllowAny` |
| `/api/v1/analytics/sessions/` | GET | List sessions | Returns active session records. | `analytics:view` |
| `/api/v1/analytics/sessions/start/` | POST | Open session | Body: `{"session_key": "sess-xxxx", "device_type": "Mobile", "browser_type": "Safari", "country": "Singapore"}` | Public / `AllowAny` |
| `/api/v1/analytics/sessions/end/` | POST | Close session | Body: `{"session_key": "sess-xxxx"}` | Public / `AllowAny` |
| `/api/v1/analytics/dashboards/` | GET | List dashboards | Returns dashboards and widgets configs list. | `analytics:view` |
| `/api/v1/analytics/dashboards/statistics/` | GET | Live dashboard KPIs | Returns dynamically resolved metrics counts (LMS, CMS, Wallet balances). | `analytics:view` |
| `/api/v1/analytics/summaries/` | GET | List summaries | Returns daily summaries totals. | `analytics:view` |
| `/api/v1/analytics/summaries/timeseries/` | GET | Chart timeseries data | Query params: `?metric=active_students&days=30` | `analytics:view` |
| `/api/v1/analytics/exports/` | POST | Trigger export | Body: `{"job_type": "CSV"}`. Automatically launches Celery task. | `analytics:manage` |
| `/api/v1/analytics/schedules/` | POST | Schedule reports | Body: `{"report_title": "Weekly Payouts Summary", "frequency": "WEEKLY", "recipients": ["admin@brahmavidya.edu"], "next_run_at": "2026-07-20T09:00:00Z"}` | `analytics:manage` |
| `/api/v1/analytics/widgets/` | POST/PUT | Edit widgets | Full CRUD operations over dashboard widget metrics layouts. | `analytics:admin` |
| `/api/v1/analytics/kpis/` | POST/PUT | Edit KPIs | Adjust targets thresholds and monitoring states. | `analytics:admin` |

---

## 2. Telemetry Event Formats

### Client Page Navigation payload
Client tracking logs dispatch:
```json
{
  "metric_name": "Page Navigation",
  "metric_value": 1.0,
  "session_key": "sess_9123847acba",
  "context_data": {
    "url_path": "/lms/courses/sanskrit-intro",
    "referrer": "/lms/explore",
    "dwell_time": 45
  }
}
```

### Response on successful ingestion (HTTP 201 Created)
```json
{
  "id": "e91a2384-2a25-4a3b-8401-69095d9f9f17",
  "metric_name": "Page Navigation",
  "metric_value": "1.0000",
  "context_data": {
    "url_path": "/lms/courses/sanskrit-intro",
    "referrer": "/lms/explore",
    "dwell_time": 45
  },
  "created_at": "2026-07-12T06:06:00Z"
}
```
