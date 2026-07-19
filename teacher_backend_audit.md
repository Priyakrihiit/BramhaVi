# Sprint 21 — Phase 0A: Backend Teacher Audit

## Executive Summary
This document presents a comprehensive backend audit of the repository's modules for the **Teacher Portal (Sprint 21)**. In compliance with Phase 0A directives, this audit is strictly focused on the following directories:
- `backend/apps/lms`
- `backend/apps/users`
- `backend/apps/analytics`
- `backend/apps/notifications`

Our audit reveals that the backend already possesses a robust base architecture featuring structured curriculum hierarchies, dynamic role-based (RBAC) and capability-based (CBAC) permission layers, comprehensive metrics tracking, and a full-featured notification engine. No code changes have been introduced; this document serves as a complete, non-invasive assessment of the existing patterns, detailing which components are **Existing**, **Missing**, or **Needs Extension** to fully support the upcoming Teacher Portal.

---

## Complete Audit Checklist & Status

| No. | Module / Feature Target | Status | Core File References |
| :--- | :--- | :---: | :--- |
| 1 | Existing Teacher-Related Models | **Needs Extension** | `lms/models.py`, `users/models.py` |
| 2 | Course Models | **Needs Extension** | `lms/models.py` |
| 3 | Lesson Models | **Needs Extension** | `lms/models.py` |
| 4 | Assignment Models | **Needs Extension** | `lms/models.py` |
| 5 | Quiz Models | **Needs Extension** | `lms/models.py` |
| 6 | Exam Models | **Needs Extension** | `lms/models.py` |
| 7 | Certificate Models | **Needs Extension** | `lms/models.py` |
| 8 | Existing RBAC Permissions | **Needs Extension** | `users/models.py`, `users/permissions.py` |
| 9 | Existing CBAC Permissions | **Needs Extension** | `users/models.py`, `users/cbac_permissions.py` |
| 10 | Existing Analytics Integrations | **Needs Extension** | `analytics/models.py`, `analytics/services.py` |
| 11 | Existing Notification Integrations | **Needs Extension** | `notifications/models.py`, `notifications/services.py` |

---

## Detailed Audit Findings

### 1. Existing Teacher-Related Models
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `TeacherClass` (`lms/models.py`): Links an instructor (`users.User`) to a `CourseStructure` node (of type `COURSE`) and maps `schedule_info` as a flexible JSONField for recurrence, calendar, and timing.
    *   `TeacherApplication` (`lms/models.py`): Facilitates employment workflows (candidates submit resume URLs, requested subjects, and experience summaries; admins review and update status).
    *   `LiveClass` (`lms/models.py`): Represents stream-based scheduled lectures connected to a Course and instructed by a teacher, capturing the live stream RTMP/WebRTC URL and duration.
    *   `UserCapability` (`users/models.py`): Maps a `User` to a "TEACHING" `Capability` (allowing access to teacher capabilities upon admin approval).
*   **What is Missing:**
    *   **TeacherPerformance**: A model to aggregate teacher performance indexes (such as rating stars, response turnarounds on assignments, and student feedback logs).
    *   **TeacherAvailability / Booking Slots**: Missing structured models for 1-on-1 tutoring or office hours scheduling beyond the live classroom stream boundaries.
*   **What Needs Extension:**
    *   `UserProfile` should be extended (or a specific `TeacherProfile` added) to contain specialized teacher credentials (such as verified academic titles, portfolio links, and educational institution affiliations).
    *   `TeacherClass` needs additional attributes to record enrollment caps, enrollment fees, or teaching assistants (TAs) assigned to assist the primary teacher.

---

### 2. Course Models
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `CourseStructure` (`lms/models.py`): An adjacency list model representing hierarchical syllabus trees, where `node_type = CourseNodeType.COURSE` acts as the Course node.
    *   `StudentEnrollment` (`lms/models.py`): Tracks registered students per Course node.
*   **What is Missing:**
    *   **CourseDraft / Moderation Workflows**: Models and fields for tracking whether a course is a draft, under admin review, approved, or published. Currently, no moderation workflow model exists if a teacher builds a course and submits it for school authorization.
    *   **CoursePricing**: No specific course fee or pricing models exist on `CourseStructure` (wallets and transaction tables exist elsewhere, but are not mapped here).
*   **What Needs Extension:**
    *   `CourseStructure` should be extended to explicitly associate a Course with its "Creator" or "Author" (currently courses are linked to teachers only through a `TeacherClass` schedule schedule).
    *   Add fields for prerequisite requirements (e.g., must complete course $X$ before enrolling).

---

### 3. Lesson Models
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `CourseStructure` (`lms/models.py`): Nodes with `node_type = CourseNodeType.LESSON` represent Lesson models.
    *   `LearningProgress` (`lms/models.py`): Tracks precise completion percentage ratio and completion milestones for students across the syllabus nodes.
*   **What is Missing:**
    *   **Interactive Lesson Discussions**: No direct model for a lesson-specific comment block, discussion forum, or student QA panel moderated by teachers.
*   **What Needs Extension:**
    *   `CourseStructure.metadata` stores video URLs and attachments as raw JSON. This is functional but needs structured models or explicit validation fields (e.g., `LessonAttachment` with secure download URLs) to help teachers manage student-facing assets cleanly in the Teacher Portal interface.

---

### 4. Assignment Models
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `Assignment` (`lms/models.py`): Stores lesson assignment definitions (instructions, lesson link, and `max_points`).
    *   `AssignmentSubmission` (`lms/models.py`): Student submissions with grading records (stores essay text/attachments in `submission_payload`, grades, instructor feedback, `graded_by`, and timestamps).
*   **What is Missing:**
    *   **Late Submission Policies**: Models/fields defining late penalties, grace periods, or hard cut-off dates.
    *   **AssignmentRubrics**: Missing structured rubrics or criteria breakdowns to aid teachers in objective grading.
*   **What Needs Extension:**
    *   `Assignment` lacks a formal `due_date` field. This is critical for teacher assignment list views (e.g., "Grading Queue", "Overdue Submissions").
    *   `AssignmentSubmission` needs file asset fields instead of a generic JSON `submission_payload` to allow standard file storage audits.

---

### 5. Quiz Models
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `PracticeSession` (`lms/models.py`): Tracks student mock quiz performance, storing selected responses and correct answers in a JSON payload.
*   **What is Missing:**
    *   **Curated Quizzes**: There is no dedicated `Quiz` or `QuizQuestion` model. Quizzes are currently managed either globally via standard `Exams` or dynamically as a student-initiated `PracticeSession`.
*   **What Needs Extension:**
    *   Need a formal `Quiz` model (bridged to lesson nodes) so teachers can assemble curated short quizzes for active tracking instead of relying entirely on high-stakes `Exams` or random automated mock testing.

---

### 6. Exam Models
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `Exam` (`lms/models.py`): Stores milestone evaluations linked to Courses, capturing passing score thresholds and durations.
    *   `QuestionBank` (`lms/models.py`): System question repository (contains question prompts, options list, correct answers indexes, and question type).
    *   `ExamQuestion` (`lms/models.py`): Bridges `Exam` to `QuestionBank`.
    *   `ExamAttempt` (`lms/models.py`): Records student attempt transcripts, scores, and status.
*   **What is Missing:**
    *   **Teacher Evaluation Queue**: Missing manual grading capabilities for open-ended or subjective exam responses. Currently, `QuestionBank` and `ExamAttempt` are designed around auto-graded (multiple choice) questions, lacking fields like `graded_by` or `feedback` on attempts.
    *   **Exam Windows**: Scheduled windows (starts_at, ends_at) where exams are accessible to students.
*   **What Needs Extension:**
    *   `QuestionBank` should be extended to allow tags, difficulties, and "Creator" markers so teachers can identify questions they authored versus platform-default items.

---

### 7. Certificate Models
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `Certificate` (`lms/models.py`): Records verified completion transcripts with storage paths (`certificate_url`) and cryptographic hashes (`signature_hash`).
*   **What is Missing:**
    *   **Custom Certificate Templates**: Missing models that define customizable layout schemes, signature images, and school badges for teachers or organizations to style graduation certificates.
*   **What Needs Extension:**
    *   Add an explicit field linking the issuing instructor or authorized reviewer who verified the graduation criteria.

---

### 8. Existing RBAC Permissions
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `Role` and `Permission` Tables (`users/models.py`): Full database tables establishing roles (e.g., "TEACHER", "STUDENT", "SUPERADMIN", "ADMIN") and individual action tokens.
    *   `HasRBACPermission` (`users/permissions.py`): REST API security guard enforcing DB-level permission queries.
*   **What is Missing:**
    *   No customized view-level class mapping for teacher action endpoints.
*   **What Needs Extension:**
    *   We need to seed the `permissions` table with specific teacher capabilities (e.g., `lms:course:edit`, `lms:submission:grade`, `lms:liveclass:stream`) and bind them to the `"TEACHER"` role in the DB setup routine.

---

### 9. Existing CBAC Permissions
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `Capability` and `UserCapability` (`users/models.py`): Advanced framework mapping user accounts to capabilities with states (`ACTIVE`, `PENDING`, `SUSPENDED`).
    *   `HasCapabilityPermission` (`users/cbac_permissions.py`): Main security gateway enforcing CBAC checks.
    *   `User` helper properties (`users/models.py`): `is_teacher_cbac`, checking if the user holds an active `TEACHING` capability.
*   **What is Missing:**
    *   No explicit capability boundaries or definitions for teacher delegation roles (e.g., Teaching Assistant, Course Co-author).
*   **What Needs Extension:**
    *   Extend `Capability` records in standard fixtures to map specific granular sub-permissions so that CBAC and RBAC fallbacks are tightly synchronized across the entire Teacher Portal API.

---

### 10. Existing Analytics Integrations
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `CourseAnalytics` (`analytics/models.py`): Generates aggregated course summaries (active students, completion count, average score, average progress).
    *   `Dashboard` and `DashboardWidget` (`analytics/models.py`): Dynamic container allowing widgets with `metric_type` (e.g., `DB_COUNT`) to evaluate query targets directly.
    *   `DashboardService` (`analytics/services.py`): Gathers stats according to active user roles (e.g., resolving `lms.CourseStructure.count`).
*   **What is Missing:**
    *   **Teacher Analytics Panels**: No built-in metrics specific to teacher workflows. There is no code designed to fetch teacher-scoped metrics (e.g., "aggregated grades distribution for classes under Teacher $X$").
*   **What Needs Extension:**
    *   Extend `DashboardService` to support teacher-scoped queries. Currently, `get_live_widgets` is designed primarily for global superadmins or generic system-level scopes. It must be extended to dynamically resolve context-filtered counts (e.g., counting only students enrolled in courses taught by the requesting teacher).

---

### 11. Existing Notification Integrations
*   **Status:** **Needs Extension**
*   **What is Existing:**
    *   `NotificationRecord` and `NotificationTemplate` (`notifications/models.py`): Robust message models supporting Redis PubSub distribution.
    *   `EmailService`, `SMSService`, `PushNotificationService` (`notifications/services.py`): Fully functional dispatchers with E.164 phone validation, templates formatting, and multi-channel routing.
*   **What is Missing:**
    *   **Class Broadcast Models**: No direct model allowing an authorized teacher to issue a broadcast alert targeting all students within their specific classes.
*   **What Needs Extension:**
    *   We need to create notification template definitions specifically for teacher events (such as `assignment_graded`, `live_class_scheduled`, and `new_course_content_published`) and hook them up to the service layer triggers.

---

## Technical Architecture Overview

The backend integrates these four applications seamlessly. Below is a structural illustration of how these components coordinate data and authorization:

```
                  +----------------------------------------------+
                  |                 users app                    |
                  |  - Role / Capability (TEACHING)             |
                  |  - HasCapabilityPermission Guard (CBAC)      |
                  +----------------------+-----------------------+
                                         |
                                         v
                  +----------------------+-----------------------+
                  |                  lms app                     |
                  |  - CourseStructure (Adjacency Tree)          |
                  |  - TeacherClass / LiveClass (Schedules)      |
                  |  - Assignment / Exam / Certificate (Content) |
                  +-----------+----------------------+-----------+
                              |                      |
                              v                      v
+-----------------------------+-------+  +-----------+-----------------------+
|             analytics app           |  |           notifications app       |
|  - CourseAnalytics Summaries        |  |  - Email / SMS / Push Services    |
|  - DashboardWidget Metrics Query    |  |  - Redis PubSub Broker            |
+-------------------------------------+  +-----------------------------------+
```

1.  **Authorization Flow**: Every inbound request hitting the LMS endpoints passes through the `HasRBACPermission` and `HasCapabilityPermission` gateways, evaluating the user's role ("TEACHER") and capability ("TEACHING") status dynamically.
2.  **LMS Management**: Course curriculum nodes are managed by the teacher, scheduling live lectures in `LiveClass` and checking enrollments inside `StudentEnrollment`.
3.  **Audits & Metrics**: When events happen (e.g., progress tracking), telemetry triggers flow into `analytics.AnalyticsEvent` and are captured by `analytics.CourseAnalytics`.
4.  **Real-Time Alerts**: Changes or alerts trigger `notifications.services` pipelines to deliver multi-channel alerts back to students.

---

## Conclusion & Recommended Roadmap

We recommend **extending the existing LMS models** (e.g., `CourseStructure`, `Assignment`, `ExamAttempt`) rather than creating a separate `apps/teacher` Django app. This preserves database normalization and prevents duplicated entities since Course, Lesson, and student enrollment models already reside in the LMS app and are tightly linked to active teachers.

### Recommended Steps for Phase 1 (Next Phase):
1.  **Enhance Core Schemas**: Add `due_date` to `Assignment` and introduce draft/publish state markers to `CourseStructure`.
2.  **Configure Permissive Roles**: Write DB migration fixtures seeding the `Permission` and `RolePermission` tables for specialized teacher actions.
3.  **Develop Teacher API Controllers**: Build a suite of REST API endpoints filtering submissions, assignments, and curriculum lists to the requesting teacher's workspace scope.
4.  **Initialize Teacher Metrics**: Create specific widgets in the `analytics` module targeting teacher KPIs (Active Student Count, Grading Queue Size, Overall Course Progress Average).
