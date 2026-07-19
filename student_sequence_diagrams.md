# Sequence Diagrams: BrahmaVidya Student Portal Flows

**UML Flow Specifications**

---

## 1. Flow: Bookmark Creation & Caching Invalidation

```
[Vite FrontEnd]             [Bookmark View]            [Bookmark Model]          [Django Signals]            [Redis Cache]            [Vidya AI Companion]
       |                            |                          |                         |                          |                       |
       |--- POST /api/bookmarks --->|                          |                         |                          |                       |
       |                            |--- .create() ----------->|                         |                          |                       |
       |                            |                          |--- (DB Commit Success)->|                          |                       |
       |                            |                          |                         |--- on_bookmark_saved --->|                       |
       |                            |                          |                         |                          |--- cache.delete() --->|                       |
       |                            |                          |                         |                          |                       |                       |
       |                            |                          |                         |------------------------------------------------->| update_context()
       |                            |                          |                         |                          |                       |--- AIMessage.create()
       |<-- 201 Created ------------|                          |                         |                          |                       |
```

---

## 2. Flow: Dynamic Reading of Dashboard (Selector Execution)

```
[Vite FrontEnd]             [Dashboard View]             [DashboardSelector]                  [Redis Cache]                   [SQL Database]
       |                            |                             |                                 |                                |
       |--- GET /api/dashboard ---->|                             |                                 |                                |
       |                            |--- get_dashboard_context ->|                                 |                                |
       |                            |                             |--- cache.get(dashboard_key) --->|                                |
       |                            |                             |<-- Cache Miss (None) -----------|                                |
       |                            |                             |                                 |                                |
       |                            |                             |--- Run SQL aggregations queries -------------------------------->|
       |                            |                             |<-- Return counts, lists, history, streaks -----------------------|
       |                            |                             |                                 |                                |
       |                            |                             |--- cache.set(dashboard_key) --->|                                |
       |                            |<-- Returns Dashboard JSON --|                                 |                                |
       |<-- 200 OK (50ms) ----------|                             |                                 |                                |
```

---

## 3. Flow: Automated Learning Reminders Execution

```
[Celery Beat Scheduler]       [Celery Task Worker]            [SQL Database]          [CentralNotificationEngine]         [User Portal]
         |                             |                            |                              |                             |
         |--- Triggers Cron Cronjob -->|                            |                              |                             |
         |                             |--- Query pending Reminders ->|                            |                             |
         |                             |<-- List reminder records --|                            |                             |
         |                             |                            |                              |                             |
         |                             |--- Loop Reminders ->       |                              |                             |
         |                             |    (Status to "sent") ---->|                              |                             |
         |                             |                            |                              |                             |
         |                             |--- send_notification ------------------------------------>|                             |
         |                             |                            |                              |--- Dispatch email --------->|
         |                             |                            |                              |--- Dispatch push socket --->|
```
