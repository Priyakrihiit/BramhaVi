# Performance Review: Enterprise Analytics Platform

This document details the performance optimization strategies, caching layers, and task scheduling designs for the analytics platform.

---

## 1. Caching & Query Tuning

To prevent database locks on SQLite from high-volume queries:
* **Aggregation Summary Tables:** Raw events (`analytics_event_logs` table) are aggregated daily into a summary table (`analytics_daily_summaries`). Dashboard widgets query this pre-computed summary table rather than scanning millions of raw event rows, reducing query latency to under 10ms.
* **Cached Counter Values:** Active sessions are tracked using a live counter cache (`analytics_realtime_counters`). It increments/decrements in real-time, preventing expensive database count scans on session updates.

---

## 2. Background Queue Offloading

* **Asynchronous Telemetry Ingestion:** Requests sent to `/api/v1/analytics/events/collect/` are offloaded to Celery background task workers immediately, avoiding thread blocks on client requests.
* **Asynchronous File Exports:** Large CSV, Excel, or PDF data exports are processed in the background. The client polls the job state in the background and is presented with a download link when compilation completes.
