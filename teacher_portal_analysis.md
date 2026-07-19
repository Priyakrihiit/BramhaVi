# Teacher Portal Audit & Architectural Analysis Report
**BrahmaVidya Galaxy LMS Platform — Sprint 21 Phase 0**

---

## Executive Summary

As the BrahmaVidya Galaxy platform expands, transitioning from a student-centric learning experience to a dual-portal educational ecosystem requires a robust, scalable, and secure **Teacher Portal**. This report presents a comprehensive repository audit of Sprint 20, assessing existing components across backend modules, database structures, frontend layouts, and middleware.

This analysis evaluates the core architectural decision: **Should a new `apps/teacher` Django app be created, or should existing LMS models be extended?** Based on our audit, we recommend a hybrid architecture: **creating a dedicated `apps/teacher` Django app to encapsulate specialized business logic, API views, and serializers, while utilizing and extending the existing relational database models within `apps/lms`**.

---

## 1. Current Architecture Audit

A complete audit of the backend (`/backend/apps`), database, frontend (`/src`), and gateway configurations has mapped the following structural landscape:

### 1.1. Existing Teacher-Related Functionality
*   **Teacher Applications:** `TeacherApplication` (in `/backend/apps/lms/models.py`) handles employment recruitment and approval processes for candidate instructors.
*   **Teacher Classes:** `TeacherClass` maps approved teachers directly to courses (`CourseStructure` where `node_type="COURSE"`). It also embeds a `schedule_info` JSON block for recurrence configurations.
*   **Live Lectures:** `LiveClass` schedules interactive stream lectures linked to courses. It includes titles, launch times, durations, and RTMP/WebRTC URL endpoints (`stream_url`).

### 1.2. Existing Course & Curriculum Management
*   **Adjacency List Curriculum Tree:** `CourseStructure` utilizes a self-referential parent-child hierarchy to organize content uniformly:
    $$\text{Program} \rightarrow \text{Subject} \rightarrow \text{Course} \rightarrow \text{Chapter} \rightarrow \text{Topic} \rightarrow \text{Subtopic} \rightarrow \text{Lesson}$$
*   **Assignments & Submissions:** `Assignment` and `AssignmentSubmission` track assignments, submissions, grades (`grade` as decimal), feedback texts (`feedback`), and grading instructors (`graded_by`).
*   **Evaluation Instruments:** `Exam`, `QuestionBank`, `ExamQuestion`, and `ExamAttempt` handle examinations, choices configurations (`options` JSON), correctness answers (`correct_answers` JSON), and attempts history.
*   **Capstone Projects:** `Project` and `ProjectSubmission` manage project requirements and text/attachment submissions.

### 1.3. Role & Permissions Infrastructure (RBAC & CBAC)
*   **Role-Based Access Control (RBAC):** Traditional roles such as `STUDENT`, `TEACHER`, `SUPERADMIN`, and `ADMIN` are defined in the `roles` table.
*   **Capability-Based Access Control (CBAC):** Deployed via active capabilities mapped to users. `User` contains helper properties:
    *   `is_teacher_cbac`: Checks if a user has the `"TEACHING"` capability or belongs to `["SUPERADMIN", "ADMIN", "TEACHER"]` roles.
    *   `is_admin_cbac`: Checks for `"ADMIN"` capability or administrative roles.
    *   `is_student_cbac`: Checks for `"LEARNING"` capability or student/admin roles.
*   **View Permission Enforcement:** Drf Viewsets subclass `BaseAiViewSet` or leverage `HasRBACPermission` with `required_permissions` dict mapping codenames (e.g., `"vidya_ai:conversation:view"`).

### 1.4. Dashboards & Analytics Pipeline
*   **Analytics Event Telemetry:** `AnalyticsEvent` in `apps/analytics/models.py` captures fine-grained events with metric names, values, and dynamic contexts.
*   **Course Performance aggregates:** `CourseAnalytics` logs statistics per course (total enrollments, active students, completion counts, average progress, and average quiz scores).
*   **Dynamic Layout Framework:** `Dashboard` and `DashboardWidget` schemas are fully functional, enabling layout configurations dynamically mapped to user roles (e.g., `role-super-admin`).

### 1.5. APIs & Gateway Configuration
*   **JSON-Based API Routers:** Django REST Framework viewsets power current portals with enterprise features (pagination, custom filtering, and search indices).
*   **Control Center Integration:** `/backend/apps/control_center/integration_hub.py` serves as a centralized gateway for cross-module orchestration:
    *   `CentralNotificationEngine`: Sends alerts over multiple channels (In-app, Email, SMS, Push).
    *   `CentralAnalyticsTracker`: Dispatches tracking events to DB and background processes.
    *   `CentralAuditLogger`: Commits administrative audit trails and physical file logs redundantly.
    *   `BackgroundJobQueue`: Executes non-blocking workloads (PDF generation, emails) via `ThreadPoolExecutor`.

### 1.6. Notification Infrastructure
*   **Flexible Delivery Channels:** `NotificationTemplate`, `NotificationPreference`, `NotificationRecord`, and `NotificationDelivery` configure in-app notification logs and pub-sub pushes.
*   **Redis Pub-Sub Gateway:** Creating a `NotificationRecord` publishes live notifications to Redis on `notifications_pubsub` channel for real-time WebSocket delivery.

### 1.7. AI Integration & Vidya Assistant
*   **Vidya AI Engine:** Encapsulated inside `/backend/apps/ai`. Supports robust conversation structures (`AIConversation`, `AIMessage`), prompt libraries (`PromptTemplate`), and usage accounting (`AIUsageTracking`).
*   **Intelligent Features:** Leverages models like `gemini-1.5-pro` for dynamic mentorship.

### 1.8. Financial & Wallet Structures
*   **Points Ledger System:** `Wallet` and `Transaction` track user points balances, credits, debits, and descriptive ledger trails.
*   **Payment Tracking:** `Payment` logs Stripe transaction references, currencies, amounts, and completion hooks.

---

## 2. Reusable Modules Analysis

To maximize development velocity and maintain system consistency, the following modules can be reused directly:

| Module / Component | Category | Reusability Potential & Application |
| :--- | :--- | :--- |
| **`apps/users`** (RBAC / CBAC) | Backend | Reuse role checks (`is_teacher_cbac`) and permission guards (`HasRBACPermission`) for API access. |
| **`apps/analytics`** (Dashboard Grid) | Backend | Reuse `Dashboard`, `DashboardWidget`, and `CourseAnalytics` to build the Teacher Portal dynamically. |
| **`apps/control_center`** (Integration) | Backend | Use `CentralAuditLogger` to record grading, `CentralAnalyticsTracker` for teacher actions, and `BackgroundJobQueue` for asynchronous tasks. |
| **`apps/notifications`** (Alerts) | Backend | Trigger real-time notifications to instructors upon assignment submissions, and to students upon grading. |
| **`apps/ai`** (AI Engine) | Backend | Reuse the core prompt template, feedback auditing, and conversational backend to support an AI Teacher Copilot. |
| **`apps/wallets`** (Points Ledger) | Backend | Leverage wallet transactional points credit to incentivize teachers based on student performance or grading tasks. |
| **`PortalLayout.tsx`** | Frontend | Highly modular UI layout containing sidebars, user headers, and notifications integration. Can easily be styled for Teachers. |
| **`EnterpriseAnalyticsView.tsx`** | Frontend | Reusable charting structures utilizing `recharts` for rendering course engagement, scores distribution, and telemetry rates. |
| **`CurriculumView.tsx`** | Frontend | Adjacency tree visualizer. Can be enhanced with curation controls (Edit, Delete, Add Node) for teacher access. |

---

## 3. Missing Modules & Structural Gaps

While the foundations are present, several critical features are missing to support a full-scale Teacher Portal:

### 3.1. Backend Missing Modules
1.  **Teacher Dashboard API Service:** A consolidated viewset aggregating real-time instructor metrics, pending submissions, active live schedules, and revenue share totals.
2.  **Curriculum Curation Views & Serializers:** Write-enabled API routes for instructors to add, edit, rearrange, or delete nodes (Chapters, Lessons) in the hierarchical `CourseStructure` tree.
3.  **Assignment Evaluation & Grading Service:** A dedicated endpoint supporting grading submissions, posting text commentaries, and verifying grade ranges.
4.  **Live Lecture Streaming Gateway Manager:** API integrations to generate stream credentials, track live attendance logs, and process session completions.
5.  **Teacher Financial Payout System:** Specialized payout tracking models or wallet payout ledgers to process revenue splits from premium courses.

### 3.2. Frontend Missing Pages & Views
1.  **Teacher Dashboard Home:** Overview of metrics (Total Students, Pass Rate, Active Courses) using `EnterpriseAnalyticsView`.
2.  **Curriculum Editor Workspace:** A drag-and-drop workspace to organize the `CourseStructure` hierarchy.
3.  **Grading Hub:** A split-pane viewer for instructors to read assignment submissions, write feedback, and assign grades.
4.  **Live Stream Management Center:** Scheduling and monitoring panel for `LiveClass` streaming.
5.  **AI Assistant Workspace:** Chat panel with pre-built prompts to help instructors design questions, write lesson summaries, or grade assignments.

---

## 4. Key Architectural Risks

Implementing the Teacher Portal introduces several architectural and operational risks that must be addressed:

```
                  +----------------------------------------------+
                  |               CRITICAL RISKS                 |
                  +----------------------------------------------+
                                  /       |       \
                                 /        |        \
                                /         |         \
         +--------------------+   +---------------+   +--------------------+
         |   Security Leak    |   | Cascade Chaos |   |  Write Contention  |
         +--------------------+   +---------------+   +--------------------+
         | Privileges bypass  |   | Deleting parent|  | DB lockups during  |
         | on grading / ledgers|  | deletes child |  | bulk assignments   |
         +--------------------+   +---------------+   +--------------------+
```

### 4.1. Privilege Escalation & Security Leaks
*   *Risk:* Incomplete RBAC/CBAC checks could allow students to call curation endpoints or self-grade submissions.
*   *Mitigation:* Apply strict capability checks (`is_teacher_cbac` and `HasRBACPermission` on custom permission codenames like `teacher:assignment:grade`) across all viewsets.

### 4.2. Cascade Deletion (Adjacency Tree Vulnerabilities)
*   *Risk:* Since `CourseStructure` uses a self-referential `parent` foreign key, deleting a parent node (e.g., a Course or Chapter) could trigger a cascading delete of all child lessons, progress logs, and completions.
*   *Mitigation:* Override the soft-delete controller to block operations if active children exist, or require multi-factor administrative confirmations.

### 4.3. Database Write Contention & Latency
*   *Risk:* Heavy write contention on `learning_progress` and `assignment_submissions` during peak periods (e.g., final exams) can degrade database performance.
*   *Mitigation:* Offload read analytics to Redis cache, and defer heavy notifications and analytical updates to the `BackgroundJobQueue` thread pool.

### 4.4. Financial Ledger Vulnerabilities
*   *Risk:* Revenue distribution from purchased premium courses is vulnerable to double-spending or unauthorized payout modifications.
*   *Mitigation:* Use atomic transactional blocks (`@transaction.atomic`) for ledger modifications, and log actions redundantly via `CentralAuditLogger`.

---

## 5. Recommended Architecture

We recommend creating a **dedicated `apps/teacher` Django app** rather than expanding `apps/lms`.

### 5.1. Rationale for Dedicated `apps/teacher`
1.  **Separation of Concerns:** Core `apps/lms` acts as the curriculum engine. Business logic for instructors (grading, application reviews, analytics, and payouts) should remain isolated.
2.  **Security Controls:** Segmenting views into `apps/teacher` simplifies access control, ensuring clear, manageable authorization checks.
3.  **Modular Scalability:** Enables the teacher dashboard to scale its API surface independently without bloating or destabilizing core LMS models.

```
+----------------------------------------------------------------------------------+
|                              TEACHER PORTAL ARCHITECTURE                         |
+----------------------------------------------------------------------------------+

   [ CLIENT BROWSER ]
          | (JWT HTTPS Request)
          v
   [ GATEWAY / ROUTER ]
          |
          +---> apps/users/middleware  -----> Authenticates User & checks is_teacher_cbac
          |
          v
   [ apps/teacher ] (NEW SERVICE APP)
          |
          +---> views.py -------------> Grading, Curation, Streaming Scheduling APIs
          +---> serializers.py -------> Data validations for curation and grading
          |
          v
   [ Shared Database Stores ]
          |
          +---> apps/lms/models.py ----> Modifies CourseStructure, Grades Submissions
          +---> apps/analytics --------> Course Analytics & Telemetry Writes
          +---> apps/wallets ----------> Financial payout ledger adjustments
```

---

## 6. Implementation Blueprint

### 6.1. Database Schema Extensions (in `apps/lms/models.py`)
To maintain relational integrity, existing models in the LMS app should be preserved, with additional fields added to support advanced features:

```python
# apps/lms/models.py (Partial extensions blueprint)

class TeacherClass(BaseModel):
    # Already exists:
    # teacher = models.ForeignKey("users.User", on_delete=models.RESTRICT)
    # course = models.ForeignKey(CourseStructure, on_delete=models.RESTRICT)
    # schedule_info = models.JSONField()
    # is_active = models.BooleanField(default=True)
    
    # Recommended additions:
    share_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Instructor revenue split percentage.")
    payout_address = models.CharField(max_length=255, blank=True, null=True, help_text="Target payment gateway address/ID.")
```

### 6.2. Security Verification & Permissions Blueprint
The new `apps/teacher/views.py` will enforce capability controls across all views:

```python
# apps/teacher/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.users.permissions import HasRBACPermission
from apps.control_center.integration_hub import CentralAuditLogger, CentralNotificationEngine

class TeacherGradingViewSet(viewsets.ViewSet):
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list": "teacher:assignment:view",
        "retrieve": "teacher:assignment:view",
        "update": "teacher:assignment:grade",
    }

    def update(self, request, pk=None):
        # 1. Enforce active teaching capability
        if not request.user.is_teacher_cbac:
            return Response({"detail": "Access restricted to certified teachers."}, status=status.HTTP_403_FORBIDDEN)
            
        # 2. Complete atomic grading updates and log action
        # ...
        return Response({"status": "Grading recorded"})
```

### 6.3. Event-Driven Workflows & Triggers
We will leverage `apps.control_center.integration_hub` to automate notifications and tracking:

```python
# Trigger flow on successful grading
@receiver(post_save, sender="lms.AssignmentSubmission")
def handle_assignment_graded(sender, instance, created, **kwargs):
    if not created and instance.grade is not None:
        # 1. Send immediate real-time in-app / email notification
        CentralNotificationEngine.send_notification(
            user=instance.student,
            event_type="ASSIGNMENT_GRADED",
            title="Assignment Evaluation Released!",
            message=f"Your submission for {instance.assignment.title} has been graded. Score: {instance.grade}%.",
            channels=["IN_APP", "EMAIL"]
        )
        # 2. Track grading telemetry
        CentralAnalyticsTracker.track_event(
            user=instance.graded_by,
            metric_name="Submission Graded",
            metric_value=1.0,
            context_data={"student_id": str(instance.student.id), "score": float(instance.grade)}
        )
```

---

## 7. Next Steps Plan

To successfully kick off Sprint 21 Phase 1, we recommend the following execution plan:

1.  **Provision the `teacher` app directory structure:** Create `/backend/apps/teacher` containing standard files (`apps.py`, `urls.py`, `views.py`, `serializers.py`).
2.  **Configure URL gateways:** Route `/api/teacher/` endpoints through the central API gateway in `server.ts`.
3.  **Run migrations:** Deploy database extensions to support teacher schedules and revenue splits.
4.  **Register capabilities:** Ensure the `"TEACHING"` capability and roles are fully mapped in the database for the test environment.
5.  **Build Frontend Workspaces:** Extend `PortalLayout` to support teacher navigation and develop pages for grading, curriculum curation, and performance analytics.
