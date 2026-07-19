# Sprint 22 — Live Classes Platform Repository Analysis

This document presents a comprehensive, independent repository audit and analysis for the upcoming **Live Classes Platform** implementation (Sprint 22).

---

## 1. Audit & System Analysis

### 1.1. Existing Live Class Functionality
*   **Database Model**:
    -   `LiveClass` model is defined in [backend/apps/lms/models.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L573-L603).
    -   Includes fields: `id`, `course` (ForeignKey to `CourseStructure`), `teacher` (ForeignKey to `users.User`), `title`, `scheduled_at`, `duration_minutes`, `stream_url`.
*   **Backend API ViewSets**:
    -   `LiveClassViewSet` is registered in [backend/apps/lms/urls.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/urls.py#L45) under the endpoint `/api/v1/lms/live-classes/`.
    -   Includes simple custom creation logic (`perform_create`) to assign `teacher = self.request.user` on save.
*   **Frontend UI Views**:
    -   React components `LiveClasses.tsx` under `src/components/teacher/` and `LiveClassView.tsx` under `src/components/education/` exist as template shells.

---

### 1.2. Audit of Related Modules

| Domain Component | Existing Components | Gaps / Needs Extension |
| :--- | :--- | :--- |
| **Meeting Models** | `LiveClass` (LMS node structure-linked), `TeachingSession` (Teacher model) | Needs extension to support external meeting platform metadata (e.g. Google Meet, Zoom, Jitsi, or internal RTMP token keys). |
| **Attendance Models** | `Attendance` in [backend/apps/teacher/models.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/teacher/models.py#L123-L150). | Needs extension to automatically register joining logs (`joined_at`, `left_at`) via frontend event triggers. |
| **Calendar Functionality**| `TeachingCalendar` and `TeacherSchedule` in `apps/teacher/models.py`. | Needs extension to sync upcoming Live Classes directly into the student and teacher calendar tables on creation. |
| **Notifications** | Celery task `alert_upcoming_live_classes` in `apps/teacher/tasks.py`. | Needs extension to support real-time SSE notifications or mailer cues for active streams. |
| **Analytics Engine** | Event tracking models in `apps/analytics`. | Needs extension to capture engagement rates (average stream watch times per student). |
| **Search Engine** | Search hooks inside `apps/search`. | Needs extension to index upcoming live streams. |
| **AI Integration** | Gemini SDK interface inside `apps/ai`. | Needs extension to auto-summarize stream transcripts. |
| **Permissions** | Gated RBAC and CBAC rules (e.g. `IsTeacherOrAdmin`, `IsTeacherOwner`). | Needs extension to ensure student access to live streams is gated based on course enrollment. |
| **API Endpoints** | `/api/v1/lms/live-classes/` CRUD router. | Needs extension to offer actions like `start-stream`, `end-stream`, and `join-stream`. |

---

## 2. Classification Mapping

*   **Existing**:
    -   `LiveClass` database model (`apps/lms/models.py`)
    -   `LiveClassViewSet` API wrapper (`apps/lms/views.py`)
    -   `Attendance` database model (`apps/teacher/models.py`)
    -   Celery background cron alert task (`apps/teacher/tasks.py`)
*   **Missing**:
    -   Student/Teacher Live Stream Room WebSocket/SSE message board integrations.
    -   Dynamic streaming credentials verification systems.
*   **Needs Extension**:
    -   `LiveClass` model: Support third-party API metadata (e.g. Jitsi Room Names or RTMP broadcast targets).
    -   `LiveClassViewSet` permissions: Implement dynamic validation checks ensuring that only enrolled students can view or fetch stream tokens.
*   **Needs Replacement**:
    -   **NONE** (All existing systems are structurally sound and do not require code deletion).

---

## 3. Architecture Recommendation

### Recommendation: Extend `apps/lms`
Rather than creating a standalone `apps/live_classes` Django app, it is highly recommended to **extend `apps/lms`**.

**Rationale**:
1.  **Avoids Duplicate/Stale Migrations**: The `LiveClass` database table is already fully defined and integrated into `apps/lms` (with applied database tables and references in `apps/teacher` and `apps/student`). Introducing a new app would require migrating this model, introducing foreign-key complexity and potential circular dependencies.
2.  **Preserves Domain Cohesion**: Live classes are inherently curriculum items associated with particular course modules. Keeping them inside `apps/lms` guarantees unified curriculum management.
3.  **Low Development Friction**: Reusing the existing viewset structure keeps codebase complexity low and complies with the clean architecture rules.
