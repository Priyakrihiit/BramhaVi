# Architecture Overview: BrahmaVidya Student Portal

**System Version**: 1.0.0  
**Domain**: Student Experience, Learning Progression, & AI Tutoring  

---

## 1. Architectural Philosophy
The BrahmaVidya architecture adheres strictly to a clean, decoupled design emphasizing high-read performance, transactional consistency for writes, asynchronous task execution, and real-time AI context grounding.

The Student Portal is structured around four primary architectural tiers:
1.  **Frontend Single-Page Application (SPA)**: React 18, Vite, Tailwind CSS, and Recharts. Built for lightning-fast responsive renderings and crisp layouts.
2.  **API Routing & Control Layer**: Django Rest Framework (DRF) views, serializers, and permission classes.
3.  **Core Domain Layer**: Clean separation of `selectors.py` (reads and aggregations) and `services.py` (writes and mutations).
4.  **Asynchronous Integration & Cache Infrastructure**: Redis, Celery, and the Centralized Telemetry and Notification Engines.

---

## 2. Dynamic Integration Infrastructure

### 2.1 The Read-Optimized Path (Cached Selectors)
Due to the high frequency of Student Dashboard visits, queries are aggressively cached at the selector level:
*   **No Cache Overheads in Business Logic**: Controllers read from selectors that abstract caching entirely.
*   **In-Memory Local Memory Cache Support**: The environment dynamically switches to standard local memory caches in testing environments to prevent socket errors.

### 2.2 The Asynchronous Path (Celery Tasks)
Heavy tasks are offloaded to background Celery workers:
*   **Search Engine Ingestion**: Note document updates trigger `apps.search.tasks.index_document_task`.
*   **Automated Reminder Dispatch**: Scheduled reminders are evaluated and dispatched sequentially via background crons.

### 2.3 The Feedback Loop (Django Signals)
BrahmaVidya utilizes low-coupling event triggers (Signals) to sync independent apps. When a student takes action:
1.  **Database Write**: The database transaction is completed.
2.  **Signal Fires**: `post_save` / `post_delete` signal handlers intercept the event.
3.  **Telemetry Dispatched**: Analytics tracking events are logged.
4.  **Cache Invalidated**: Cached metrics and dashboard context values are immediately cleared.
5.  **Notifications Dispatched**: Milestone success emails or alerts are queued.
6.  **AI Grounding Context Injected**: System traces are fed into active chatbot conversations to maintain educational context.
