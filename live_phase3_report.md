# BrahmaVidya Galaxy — Live Classes Phase 3 Backend Services Report

This document reports the implementation and validation of the backend business logic and query selector layers for the **Live Classes Platform** (Sprint 22).

---

## 1. Summary of Implemented Backend Services

The following core modules were created or verified in `apps.lms`:

### 1.1. Core Service Layer ([services.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/services.py))
*   **Class**: `LiveClassService`
*   **Key Operations**:
    -   `schedule_live_class()`: Checks scheduler validator triggers and registers a `LiveClass` item.
    -   `start_live_session()`: Transitions status to `LIVE` and creates a `LiveSession` model.
    -   `end_live_session()`: Closes active sessions, transitions status to `COMPLETED`, and kicks off recording and AI summarizer worker tasks.
    -   `record_attendance()`: Tracks student check-ins and check-outs, writing records to the `teacher.Attendance` logging system.
    -   `create_poll()`: Creates interactive question poll objects.
    -   `cast_vote()`: Saves poll response choices from students.

### 1.2. Selector Layer ([selectors.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/selectors.py))
*   **Class**: `LiveClassSelector`
*   **Key Operations**:
    -   `get_upcoming_live_classes()`: Filters future scheduled classes.
    -   `get_active_participants()`: Lists participants currently logged into a stream.
    -   `get_poll_results()`: Aggregates votes for active polls.
    -   `get_live_class_analytics()`: Retrieves concurrent user counts and engagement indices.

### 1.3. Validations & Filtering ([validators.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/validators.py) and [filters.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/filters.py))
*   **Validators**:
    -   `validate_live_class_timing()`: Checks that scheduled times are set in the future.
    -   `validate_poll_options()`: Requires at least 2 option items.
*   **Filters**:
    -   `LiveClassFilter`: DjangoFilterBackend structure filtering by `status`, `course_id`, and `teacher_id`.

### 1.4. Celery Tasks & Event Hooks ([tasks.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/tasks.py) and [signals.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/signals.py))
*   **Celery Tasks**:
    -   `compile_class_recording_task`: Archives completed broadcast videos and computes stream analytics.
    -   `generate_ai_class_summary`: Summarizes lecture audio/transcripts using AI prompts.
    -   `alert_upcoming_live_classes`: Regularly scans for classes starting in under 30 minutes to notify students.
*   **Signals**:
    -   `on_live_class_scheduled`: Listens to `post_save` on `LiveClass` to sync schedule dates directly into the `CalendarEvent` table.

---

## 2. Integrity Verification

*   Command: `python backend/manage.py check`
*   Status: 🟢 **SUCCESS**
*   Logs: `System check identified no issues (0 silenced)`.
