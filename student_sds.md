# Software Design Specification (SDS): BrahmaVidya Student Portal

**Document Version**: 1.0.0  
**Date**: July 13, 2026  
**Status**: APPROVED  
**Systems Impacted**: `student` app, `users` app, `control_center` (Vidya AI), `notifications`, `search`  

---

## 1. System Architecture Diagram Context
The BrahmaVidya Student Portal operates within a clean high-performance Django architecture integrated with a Vite/React SPA frontend.
Key structural boundaries:
```
           +----------------------------------------+
           |             Vite/React Client          |
           +----------------------------------------+
                               |
                               | (HTTP/JSON API)
                               v
           +----------------------------------------+
           |         Django Rest Framework          |
           +----------------------------------------+
             |         |                  |        |
             v         v                  v        v
         [Models]  [Selectors]       [Signals]  [Views]
             |         |                  |        |
             |         | (Read Caching)   |        | (Write Mutate)
             |         v                  v        v
             |     +--------+         +-------------------------------+
             |     | Redis  |         |   Central Telemetry Hub       |
             |     +--------+         | - CentralAnalyticsTracker     |
             v                        | - CentralNotificationEngine   |
         +--------+                   +-------------------------------+
         | SQLite/|                                |
         | Postgres|                               v
         +--------+                   +-------------------------------+
                                      |     Vidya AI Conversation     |
                                      +-------------------------------+
                                                   |
                                                   v
                                      +-------------------------------+
                                      |     Celery Task Workers       |
                                      +-------------------------------+
```

---

## 2. Core Modules & Component Specifications

### 2.1 Caching Layer (`apps.student.selectors`)
*   **Selector**: `DashboardSelector`
*   **Method**: `get_student_dashboard_context(user)`
*   **Caching Strategy**: Read-Through Caching.
    *   Cache Key: `dashboard_context_{user_id}`
    *   Timeout: 300 seconds
    *   Fallback: Pulls data from SQL db via standard query models, populates the cache, and returns context.

### 2.2 Proactive Invalidation (`apps.student.signals`)
Database changes to core student records must invalidate the cache immediately:
*   `on_bookmark_saved` / `on_bookmark_deleted`: Deletes `dashboard_context_{user_id}`.
*   `on_note_saved`: Deletes `dashboard_context_{user_id}`.
*   `on_goal_saved`: Deletes `dashboard_context_{user_id}`.
*   `on_achievement_saved`: Deletes `dashboard_context_{user_id}`.

### 2.3 Search Index Integration (`apps.search.tasks`)
To keep personal learning notes searchable:
*   `on_note_saved` triggers celery task `index_document_task.delay("StudentNote", note.id)`.
*   The worker extracts note title, content excerpts, node reference, and formats the URL endpoint.

### 2.4 Grounded AI Tutor Sync
*   **Utility Method**: `update_ai_conversation_context(user, description)`
*   **Process**:
    1. Looks up active, non-deleted `AIConversation` for the user.
    2. Appends a system trace entry as an `AIMessage` to ground the LLM tutor on the student's recent progression or activities (such as creating a bookmark, completing a goal, or unlocking a badge).

### 2.5 Centralized Notification Dispatcher
*   **Utility Method**: `CentralNotificationEngine.send_notification`
*   **Channels**: In-App Message and Email notifications are dispatched simultaneously for reminders, badges, and study goals.
