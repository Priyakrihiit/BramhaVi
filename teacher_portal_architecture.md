# Teacher Portal Complete Architectural Design Document
**BrahmaVidya Galaxy LMS Platform — Sprint 21 Phase 1 Design Specification**

---

## 1. High-Level System Architecture

The BrahmaVidya Teacher Portal provides certified instructors, course directors, and academic administrators with a high-performance web workspace. It leverages our existing robust core platform services (analytics engines, notification distribution channels, wallets, and AI assistance) to deliver course design, live virtual streaming, student assessment grading, and transaction payouts.

```
+--------------------------------------------------------------------------------------------------+
|                                    TEACHER PORTAL MULTI-TIER SYSTEM                              |
+--------------------------------------------------------------------------------------------------+

  [ RESPONSIVE CLIENTS ] (Vite + React 18, Tailwind CSS, Recharts, Custom SVG Frameworks)
         |
         | (Secure HTTPS / JWT Token Authenticated)
         v
  [ API GATEWAY PROXY ] (Express Gateway server.ts @ Port 3000)
         |
         |---> Rate Limiting (Redis Sorted Sets + Memory Fallback)
         |---> JWT Extraction & Bearer Verification
         |---> Header/Cookie Injection (`csrftoken`, `sessionid`)
         v
  [ CORE BACKEND ENGINES ] (Django REST Framework @ Port 8000)
         |
         +---> apps/teacher (NEW: Views, Serializers, Routing Controller)
         +---> apps/users   (RBAC/CBAC Context, Profile, Identity Management)
         +---> apps/lms     (Adjacency Tree Curriculum, Exams, Assignments)
         +---> apps/ai      (Vidya AI Copilot context & Gemini proxy)
         |
         v (Database & Cache Access)
  [ DATA & EVENT LAYER ]
         |---> Redis Cache Cluster (Instructor View Caching, 300s TTL)
         |---> PostgreSQL Relational Store (Transactional Ledger, Course Trees, Users)
         |---> Celery & Redis Queue (Shared background workers for PDF generation & digests)
```

---

## 2. Core Functional Modules Design

### 2.1. Teacher Dashboard
*   **Purpose:** Serving as the central operational hub, giving instructors a comprehensive overview of active tasks, earnings, student submissions, and lecture alerts.
*   **Key Widgets:**
    *   *Metric Strips:* Total Enrolled Students, Pass Rate (%), Total Active Courses, and Month-to-Date Net Revenue.
    *   *Direct Cues Panel:* Highlights "Awaiting Evaluation" assignment submissions and "Next Live Lecture" scheduling times.
    *   *Recent Activity Stream:* Real-time user logs detailing course enrollments, student comments, and goal progress.

### 2.2. Course Builder
*   **Purpose:** Managing and structuring curriculum containers using an intuitive visual hierarchy.
*   **Technical Design:**
    *   Interfaces with the self-referential `CourseStructure` table where `node_type = 'COURSE'`.
    *   Includes fields for course descriptions, syllabus cards, difficulty tiers (`BEGINNER`, `INTERMEDIATE`, `ADVANCED`), price ledgers, and banner artwork.
    *   Supports draft status (`is_draft = True`), publishing workflows, and dynamic co-teacher assignments (`TeacherClass`).

### 2.3. Lesson Builder
*   **Purpose:** Customizing individual lecture pages and subtopics within the hierarchical curriculum tree.
*   **Technical Design:**
    *   Creates child nodes where `node_type = 'LESSON'` linked to parent chapters or topics.
    *   Supports rich multimedia types (Markdown texts, HTML embeds, uploaded video streams, PDF reference documents).
    *   Supports incremental drip release dates (`drip_delay_days` integer) and lock status constraints.

### 2.4. Assignment Builder
*   **Purpose:** Creating student assessment portals with custom grading configurations.
*   **Technical Design:**
    *   Enables creation of assignments mapped to courses or lessons.
    *   Stores custom constraints: max grade scores, due dates, attachment rules, and late-submission policy options.
    *   Grading panel supports side-by-side reading of student submissions, text feedback commentaries, and digital rubric assessments.

### 2.5. Quiz Builder
*   **Purpose:** Creating interactive, timed evaluation checks with instant grading feedback.
*   **Technical Design:**
    *   Builds `Exam` structures where `exam_type = 'QUIZ'`.
    *   Provides inputs for test duration (minutes), shuffle configurations, passing scores, maximum retries, and question selection rules (manual selection vs. randomized pools from Question Bank).

### 2.6. Question Bank
*   **Purpose:** Maintaining a central repository of reusable assessment items.
*   **Technical Design:**
    *   CRUD operations on `QuestionBank` and `QuestionChoice` models.
    *   Supports multiple formats: Single-Choice, Multi-Select, True/False, and Markdown/Code input.
    *   Categorized by academic taxonomy, tags, and cognitive difficulty tiers.

### 2.7. Attendance Tracker
*   **Purpose:** Monitoring student attendance in live lectures and physical milestones.
*   **Technical Design:**
    *   Introduces an `AttendanceRecord` logging student presence, joining timestamps, active durations, and attention scores.
    *   Provides bulk-marking panels for asynchronous sessions and automated exports for school administrators.

### 2.8. Live Classes Scheduler
*   **Purpose:** Setting up interactive streams and scheduling group learning events.
*   **Technical Design:**
    *   Integrates with `LiveClass` models to register stream slots.
    *   Secures stream endpoints via WebRTC key generation and RTMP ingest setups.
    *   Automates dynamic announcements and schedules calendar updates for enrolled students.

### 2.9. Student Progress Monitoring
*   **Purpose:** Tracking course completion rates and student performance metrics.
*   **Technical Design:**
    *   Aggregates data from `LearningProgress` and `AssignmentSubmission` tables.
    *   Flags inactive or struggling users (completion < 20% or average score < 60%) to help teachers offer targeted support.
    *   Features a direct message option powered by the centralized messaging channel.

### 2.10. Batch Management
*   **Purpose:** Grouping students into separate cohorts for targeted scheduling and grading.
*   **Technical Design:**
    *   Introduces a `CourseBatch` model to segment cohorts.
    *   Allows teachers to assign instructors, define batch-specific deadlines, and schedule live lectures for specific cohorts.

### 2.11. Teacher Earnings & Financial Dashboard
*   **Purpose:** Tracking course revenue share, points, and financial payout histories.
*   **Technical Design:**
    *   Pulls records from `Transaction` where wallet points are credited from course purchases.
    *   Displays payout trends and month-over-month summaries.
    *   Includes payout configurations (Stripe/PayPal accounts) and logs administrative payout audits.

### 2.12. Certificates Manager
*   **Purpose:** Creating, customizing, and awarding credentials to course graduates.
*   **Technical Design:**
    *   Manages certificate templates with custom metadata variables (Student Name, Course Title, Issue Date).
    *   Generates secure verification hashes and signs PDF files in the background using Celery.
    *   Verifies authenticity via the public `CertificateVerifier` model.

### 2.13. Teacher Analytics Engine
*   **Purpose:** Visualizing engagement telemetry, assignment pass rates, and revenue trends.
*   **Technical Design:**
    *   Pulls pre-aggregated course metrics from `CourseAnalytics` and logs raw event details via `AnalyticsEvent`.
    *   Visualizes data in the frontend using clean, high-performance SVG graphs and charts.

### 2.14. Teacher Profile Configuration
*   **Purpose:** Showcasing teacher bios, resumes, and academic backgrounds to students.
*   **Technical Design:**
    *   Updates fields in the base `User` table (bio, avatar, certifications).
    *   Integrates verification badge requests reviewed by administrators.

### 2.15. Teacher Settings Panel
*   **Purpose:** Customizing application parameters and notification preferences.
*   **Technical Design:**
    *   Configures preference controls (`NotificationPreference`) across delivery channels (Email, Push, SMS, In-App).
    *   Enables security options (Two-Factor Auth, password resets, session terminations).

---

## 3. Database Architecture

The Teacher Portal reuses our existing LMS model structures and extends them with key tables. This maintains relational integrity and avoids data duplication.

```
       +-----------------------+              +------------------------+
       |       users.User      |              |   LMS.CourseStructure  |
       +-----------------------+              +------------------------+
       | pk: UUID              |              | pk: UUID               |
       | role: [TEACHER, etc]  |              | parent_id: FK -> Self  |
       | capabilities: JSON    |              | node_type: String      |
       +-----------+-----------+              +-----------+------------+
                   | (1)                                  | (1)
                   |                                      |
                   | (0..*)                               | (0..*)
       +-----------v--------------------------------------v------------+
       |                       LMS.TeacherClass                        |
       +---------------------------------------------------------------+
       | pk: UUID                                                      |
       | teacher_id: FK -> users.User                                  |
       | course_id: FK -> LMS.CourseStructure                          |
       | share_percentage: Decimal(5,2)                                |
       | schedule_info: JSON                                           |
       +---------------------------------------------------------------+
```

### 3.1. New and Extended Model Schemas

```python
# Proposed database updates (apps/teacher and apps/lms)

class CourseBatch(BaseModel):
    """Segments course registrations into cohorts with unique schedules."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey("lms.CourseStructure", on_delete=models.CASCADE, related_name="batches")
    name = models.CharField(max_length=120, help_text="Cohort tag. e.g. 'Fall 2026 Batch Alpha'")
    instructors = models.ManyToManyField("users.User", related_name="assigned_batches")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

class AttendanceRecord(BaseModel):
    """Tracks student attendance for live stream lectures."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    live_class = models.ForeignKey("lms.LiveClass", on_delete=models.CASCADE, related_name="attendance")
    student = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="attendance_records")
    join_time = models.DateTimeField(null=True, blank=True)
    leave_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=[("PRESENT", "Present"), ("ABSENT", "Absent"), ("LATE", "Late")], default="ABSENT")
```

---

## 4. API Architecture

All endpoints use REST patterns, with input validations handled by Django REST Framework serializers and outputs mapped to camelCase.

### 4.1. Endpoint Specifications

| Endpoint Pattern | Method | Purpose | Payload Input Schema | Output Success Code |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/teacher/dashboard/summary/` | `GET` | Pulls aggregated dashboard indicators. | None | `200 OK` |
| `/api/v1/teacher/courses/curate/` | `POST` | Creates or updates nodes in `CourseStructure`. | `{"parent": "UUID", "title": "...", "node_type": "LESSON"}` | `201 Created` |
| `/api/v1/teacher/assignments/submissions/` | `GET` | Lists pending assignment submissions. | Filter query parameters. | `200 OK` |
| `/api/v1/teacher/assignments/submissions/<id>/grade/` | `POST` | Grades a student's submission. | `{"grade": 88.5, "feedback": "Excellent progress!"}` | `200 OK` |
| `/api/v1/teacher/live/schedule/` | `POST` | Schedules a live streaming lecture. | `{"course_id": "UUID", "title": "...", "start_time": "..."}` | `201 Created` |
| `/api/v1/teacher/earnings/history/` | `GET` | Pulls earnings ledger and transactions. | Query page size parameters. | `200 OK` |

---

## 5. Gateway Routing & Security

The Express API Gateway (`server.ts`) handles request routing, security rules, and rate limits.

```
+-----------------------------------------------------------------------------------------+
|                                API GATEWAY ROUTING SCHEME                               |
+-----------------------------------------------------------------------------------------+

   [ React Frontend Request ] ---> /api/teacher/dashboard/summary (No trailing slash)
                                              |
                                              v (server.ts Proxy Rules)
                                   Normalize Trailing Slash
                                              |
                                              v
                                  Check Security Headers
                                              |
                                              v
                              Verify & Forward Session Cookie
                                              |
                                              v
   [ Django API Router ] --------> /api/v1/teacher/dashboard/summary/ (With trailing slash)
```

### 5.1. Path Mapping Updates
Add the following routes to the `PATH_MAP` configurations in the Express gateway:
```typescript
const PATH_MAP: Record<string, string> = {
  "/api/student/dashboard/summary": "/api/v1/student/dashboard/summary/",
  "/api/teacher/dashboard/summary": "/api/v1/teacher/dashboard/summary/",
  "/api/teacher/courses/curate": "/api/v1/teacher/courses/curate/",
  "/api/teacher/assignments/grade": "/api/v1/teacher/assignments/grade/",
  "/api/teacher/live/schedule": "/api/v1/teacher/live/schedule/",
  "/api/teacher/earnings": "/api/v1/teacher/earnings/",
};
```

---

## 6. Access Control & Permissions (RBAC/CBAC)

Permissions are enforced at the gateway and backend levels using role and capability checks.

*   **Role Check:** Reuses `role` context mapping fields, validating user roles against `["SUPERADMIN", "ADMIN", "TEACHER"]`.
*   **Capability check (CBAC):** Checks for the presence of the `"TEACHING"` capability.

### 6.1. Verification Middleware Blueprint (Backend)
```python
# apps/users/permissions.py extension draft
from rest_framework import permissions

class IsCertifiedTeacher(permissions.BasePermission):
    """Restricts view access to verified instructors with the TEACHING capability."""
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_teacher_cbac
        )
```

---

## 7. Caching Strategy

The Teacher Portal uses our existing Redis cache manager to improve dashboard speed and reduce database load:

*   **Caching Strategy:** Key-Value caching for expensive read views (dashboard indicators, analytics reports, and cohort statistics).
*   **Cache Invalidation:** Event-driven invalidation via Django signals. Any change in curriculum, grades, or registrations immediately clears the respective cache keys.

```
       [ Read Operation ]                           [ Write Operation ]
  Instructor requests Dashboard.             Instructor submits a Grade.
              |                                            |
              v                                            v
     Check Redis Cache.                           Perform Database Write.
    /                 \                                    |
(Hit)                (Miss)                                v
  |                    |                     Trigger post_save Django Signal.
  v                    v                                   |
Return Data.      Query Database                           v
                  & populate Redis.                 Clear Redis Cache.
```

---

## 8. Asynchronous Processing & Task Queues

We use Celery to move heavy, non-critical tasks out of the main request-response cycle:

*   **Automated Email Reports:** Weekly student progress digests are compiled and dispatched asynchronously.
*   **Certificate Compilation:** Compiles high-resolution PDF certificates, registers hashes, and generates verification signatures in the background.
*   **Vidya AI Prompts:** Dynamic prompt context generation and system logs are generated asynchronously during grading actions.

---

## 9. Frontend React Architecture & Responsive Design

The frontend utilizes our modular React architecture and Tailwind CSS for styling. It uses custom, lightweight SVG frameworks for visual charts, ensuring fast load times and responsive layouts on all screens.

```
+--------------------------------------------------------------------------------------+
|                           FRONTEND REACT WORKSPACE STRUCTURE                         |
+--------------------------------------------------------------------------------------+

  [/src/components/student/TeacherPortal.tsx]  <-- Modular Portal Root Entry
         |
         +---> Layout Component Container (Extends and overrides PortalLayout.tsx)
         |
         +---> Sub-Navigation Tab Panel Router:
                 |
                 +---> [Dashboard/Home]  ----> Aggregated metrics & EnterpriseAnalyticsView
                 +---> [Course Curation] ----> CurriculumView tree + Create/Edit Modals
                 +---> [Grading Hub]     ----> Student submission rows + Feedback inputs
                 +---> [Live Classes]    ----> Scheduling panel + WebRTC stream views
                 +---> [Earning Vault]   ----> Points ledger listings + Payout forms
```

### 9.1. Mobile Accessibility & Touch Target Parameters
*   **Aesthetic Layouts:** Avoids fixed width coordinates; uses responsive grid rules (`grid-cols-1 md:grid-cols-2 lg:grid-cols-4`).
*   **Tactile Targets:** Interactive touch targets (buttons, inputs, tabs) are designed with a minimum height of `44px` for easy mobile navigation.
*   **State Indicators:** Dynamic loading skeletons and explicit error notifications provide clear, instant user feedback.

---

## Conclusion & Staging Roadmap

The proposed architecture for the **Teacher Portal** is secure, modular, and highly scalable. By encapsulating custom teacher logic in a dedicated `apps/teacher` app while sharing underlying `apps/lms` database models, the system remains performant, cohesive, and easy to maintain.
