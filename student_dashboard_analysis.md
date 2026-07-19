# Student Dashboard Analysis — Sprint 20 Phase 0
## BrahmaVidya Galaxy — Repository Deep Dive

**Date:** 2026-07-12  
**Sprint:** 20 — Student Portal & Learning Dashboard  
**Analyst:** Antigravity AI  
**Status:** ✅ Phase 0 Complete — Awaiting Approval

---

## 1. Repository Structure Overview

```
bramhavi/
├── backend/                   ← Django REST Framework backend
│   ├── apps/
│   │   ├── ai/                ← Gemini AI integration
│   │   ├── analytics/         ← Platform-wide analytics engine
│   │   ├── cms/               ← Content Management System (largest app: 48KB models)
│   │   ├── control_center/    ← Admin dashboard & platform settings
│   │   ├── lms/               ← Learning Management System
│   │   ├── notifications/     ← Multi-channel notification engine
│   │   ├── portfolio/         ← Career & resume management
│   │   ├── publishing/        ← Book/ebook publishing platform
│   │   ├── search/            ← Unified search platform
│   │   ├── seo/               ← SEO & sitemap management
│   │   ├── services/          ← Freelance services marketplace
│   │   ├── users/             ← Authentication, RBAC, CBAC
│   │   └── wallets/           ← Wallet, transactions, payments
│   ├── django_project/        ← Settings, URLs, Celery, ASGI/WSGI
│   ├── middleware/            ← Request ID, custom middleware
│   └── manage.py
├── src/                       ← React/TypeScript frontend
│   ├── components/            ← Shared and feature components
│   ├── layouts/               ← PortalLayout, AdminLayout
│   ├── pages/                 ← Public & Admin page shells
│   ├── services/              ← API client services
│   ├── stores/                ← Zustand-style React Context stores
│   └── types.ts               ← Shared TypeScript type definitions
├── server.ts                  ← Express.js API Gateway (2018 lines)
├── vite.config.ts             ← Vite build config
├── package.json
└── docs/                      ← Organized documentation
```

---

## 2. LMS Module — Complete Model Inventory

**File:** `backend/apps/lms/models.py` (603 lines, 21,618 bytes)

| Model | Table | Purpose |
|---|---|---|
| `CourseNodeType` | — | Enum: PROGRAM, SUBJECT, COURSE, CHAPTER, TOPIC, SUBTOPIC, LESSON |
| `CourseStructure` | `course_structures` | Unified adjacency-list curriculum tree (self-referential) |
| `LearningProgress` | `learning_progress` | Per-student, per-node completion tracking (progress_percentage, is_completed) |
| `Assignment` | `assignments` | Lesson-linked assignment criteria |
| `AssignmentSubmission` | `assignment_submissions` | Student submissions with grading & feedback |
| `PracticeSession` | `practice_sessions` | Quick quiz session history |
| `Project` | `projects` | Capstone project definitions |
| `ProjectSubmission` | `project_submissions` | Student project uploads |
| `Exam` | `exams` | Milestone examinations |
| `QuestionBank` | `question_banks` | Master question repository |
| `ExamQuestion` | `exam_questions` | Bridge: Exam ↔ QuestionBank |
| `ExamAttempt` | `exam_attempts` | Student exam attempts with scores (STARTED/SUBMITTED/TIMED_OUT) |
| `Certificate` | `certificates` | SHA-256 signed course completion certificates |
| `Badge` | `badges` | Gamification achievement badges |
| `UserBadge` | `user_badges` | Student ↔ Badge mapping |
| `TeacherApplication` | `teacher_applications` | Instructor recruitment applications |
| `TeacherClass` | `teacher_classes` | Teacher ↔ Course assignment |
| `StudentEnrollment` | `student_enrollments` | Student ↔ Course registration (ACTIVE/COMPLETED/CANCELLED) |
| `LiveClass` | `live_classes` | Scheduled streaming lectures |

### LMS APIs Currently Registered (`/api/v1/lms/`)
```
GET/POST   programs/
GET/POST   subjects/
GET/POST   courses/               ← Primary course listing
GET/POST   chapters/
GET/POST   topics/
GET/POST   subtopics/
GET/POST   lessons/
GET/POST   learning-progress/     ← Progress tracking
GET/POST   assignments/
GET/POST   assignment-submissions/
GET/POST   practice/
GET/POST   practice-attempts/
GET/POST   projects/
GET/POST   project-submissions/
GET/POST   exams/
GET/POST   exam-attempts/
GET/POST   question-banks/
GET/POST   exam-questions/
GET/POST   certificates/
GET/POST   badges/
GET/POST   user-badges/
GET/POST   teacher-applications/
GET/POST   teacher-classes/
GET/POST   student-enrollments/
GET/POST   live-classes/
GET        students/me/enrollments/    ← Student self-service
GET        students/me/progress/
GET        students/me/certificates/
GET        students/me/badges/
```

### ⚠️ Missing LMS Models (to be created in Phase 2)
The following do NOT exist yet:
- `StudentDashboard` — dashboard state/preferences persistence
- `LearningHistory` — auditable lesson visit log
- `ContinueLearning` — last-accessed lesson bookmark per course
- `Bookmark` — explicit student bookmarks for any content
- `StudentNote` — in-lesson notes
- `StudyGoal` — personal study targets
- `StudySession` — timed study sessions
- `StudyCalendar` — calendar event entries
- `DailyProgress` / `WeeklyProgress` / `MonthlyProgress` — aggregated snapshots
- `LearningStreak` — consecutive day tracking
- `Achievement` — extended achievement system (beyond badge)
- `StudentPreference` — dashboard layout, notification preferences
- `RecentlyViewedLesson` — last N viewed lessons
- `LearningReminder` — scheduled study reminders

---

## 3. Users / Authentication Module

**File:** `backend/apps/users/models.py` (483 lines, 20,684 bytes)

| Model | Table | Purpose |
|---|---|---|
| `Role` | `roles` | RBAC roles: SUPERADMIN, ADMIN, TEACHER, STUDENT |
| `Permission` | `permissions` | Granular permission codenames (e.g., `lms:course:publish`) |
| `RolePermission` | `role_permissions` | Role ↔ Permission bridge |
| `User` | `users` | Email-based auth with soft delete, RBAC + CBAC |
| `Session` | `sessions` | JWT session tracking |
| `Device` | `devices` | Push notification device registry |
| `UserProfile` | `user_profiles` | Rich bio: avatar, bio, skills, education, experience, projects, achievements (JSON) |
| `Notification` | `notifications` | In-app notification records |
| `Organization` | `organizations` | Multi-tenant workspace |
| `OrganizationMember` | `organization_members` | User ↔ Organization mapping |
| `LoginHistory` | `login_history` | Login attempt log |
| `Capability` | `capabilities` | CBAC capability definitions (TEACHING, LEARNING, AUTHORING, ADMIN, etc.) |
| `UserCapability` | `user_capabilities` | User ↔ Capability with status |
| `CapabilityPermission` | `capability_permissions` | Capability ↔ Permission bridge |
| `CapabilityApplication` | `capability_applications` | APPROVAL_REQUIRED capability applications |

### Key Auth Capabilities for Student Dashboard
```python
user.is_student_cbac  # has LEARNING capability OR role=STUDENT
user.has_capability("LEARNING")
user.get_all_permissions_set()  # Flat permission codename set
```

### UserProfile — Existing JSON Fields
```
settings        → {"theme": ..., "notifications": ...}
skills          → [{"name": "Python", "level": "Advanced"}]
education       → [{"degree": ..., "school": ..., "year": ...}]
experience      → [{"role": ..., "company": ..., "duration": ...}]
projects        → [...]
achievements    → [...]
privacy_settings→ {...}
```

---

## 4. CMS Module

**File:** `backend/apps/cms/models.py` (1303 lines, 48,262 bytes)

Key models relevant to Student Dashboard:
- `Tutorial` / `TutorialLesson` — learning content
- `Blog` / `Article` — editorial content
- `Tag`, `Category` — content taxonomy
- `MediaFile` — managed media assets
- `Page` — dynamic CMS pages
- `NavigationMenu` — sidebar/header navigation
- `FAQ` — learning-related Q&A

---

## 5. Analytics Module

**File:** `backend/apps/analytics/models.py` (450 lines, 15,488 bytes)

| Model | Purpose |
|---|---|
| `AnalyticsEvent` | High-velocity telemetry: metric_name, metric_value, context_data |
| `UserSession` | Aggregate session stats: device_type, country, login_at |
| `PageView` | Page visit dwell metrics |
| (+ more) | Course completion rates, engagement metrics |

**Key analytics services:** `selectors.py` (56,852 bytes!), `services.py` (51,616 bytes), `tasks.py` (50,207 bytes)

---

## 6. Notifications Module

**File:** `backend/apps/notifications/models.py` (119 lines)

| Model | Table | Purpose |
|---|---|---|
| `NotificationTemplate` | `notification_templates` | Email/push templates by `code` |
| `NotificationPreference` | `notification_preferences` | Per-user per-category opt-in (email/sms/push) |
| `NotificationRecord` | `notification_records` | Delivered notification inbox records |
| `NotificationDelivery` | `notification_deliveries` | Channel delivery tracking (email/sms/push/in_app) |
| `Announcement` | `announcements` | Platform-wide pinned announcements |
| `NotificationAnalytics` | `notification_analytics` | Per-category sent/delivered/opened counts |

**Redis Pub/Sub:** `NotificationRecord.save()` publishes to `notifications_pubsub` channel for real-time delivery.

---

## 7. Search Module

**File:** `backend/apps/search/models.py` (254 lines)

| Model | Table | Purpose |
|---|---|---|
| `SearchIndex` | `search_indexes` | Named search indexes (courses, articles, books) |
| `SearchDocument` | `search_documents` | Unified indexed entity: entity_type + entity_id + full-text |
| `SearchTerm` | `search_terms` | Query trend tracking |
| `SearchAnalytics` | `search_analytics` | CTR, dwell time per query |

---

## 8. Wallet Module

**File:** `backend/apps/wallets/models.py` (128 lines)

| Model | Table | Purpose |
|---|---|---|
| `Wallet` | `wallets` | OneToOne per user, VIDYA currency balance |
| `Transaction` | `transactions` | Append-only CREDIT/DEBIT ledger |
| `Payment` | `payments` | External payment records (Stripe gateway) |

---

## 9. AI Module

**File:** `backend/apps/ai/` (no models.py — uses `ai_store.json` 38KB)
- Gemini AI integration via `GoogleGenAI`
- AI conversations, messages, prompts, feedback
- `ai_store.py` — JSON-driven store/configuration

---

## 10. Control Center

**File:** `backend/apps/control_center/models.py` (322 lines)

| Model | Purpose |
|---|---|
| `Theme` | Frontend visual theme configurations |
| `PlatformSetting` | Key-value platform configuration |
| `DashboardWidget` | Admin dashboard widget configurations (DB_COUNT, DB_SUM, TELEMETRY_RATE) |
| `AdministrativeTask` | Pending supervisor actions |
| `MediaFile` | Managed media upload tracking |

---

## 11. Existing React Frontend

### Layouts
| File | Purpose |
|---|---|
| `PortalLayout.tsx` (24,743 bytes) | Main shell: navbar, notifications, search, theme toggle, mobile menu |
| `AdminLayout.tsx` (5,733 bytes) | Admin panel shell with sidebar |

### Routing (`App.tsx`)
```
/                     → HomeShell
/auth                 → AuthPage
/about, /pricing...   → SimplePages
/tutorials            → TutorialsPage
/courses              → CoursesShell
/bookstore            → BookstoreView
/marketplace          → MarketplaceView
/services             → ServicesPage
/portfolio, /resumes  → TemplatesPage
/blogs                → BlogsPage
/community            → CommunityPage
/become-*             → BecomePartnerPage
/dashboard            → EnhancedDashboardView   ← EXISTING (needs extension)
/saas                 → SaaSSuiteView
/search               → GlobalSearchView
/admin/*              → AdminLayout + DashboardShell/etc.
```

### Key Existing Components
| Component | Size | Purpose |
|---|---|---|
| `StudentPortal.tsx` | 36,253 bytes | Tab-based student portal: courses, exams, badges, AI chat (Vidya) |
| `EnhancedDashboardView.tsx` | 32,623 bytes | Multi-tab dashboard: overview, content, career, capabilities, profile |
| `ControlCenter.tsx` | 53,889 bytes | Admin control center |
| `NotificationCenter.tsx` | 12,758 bytes | In-app notifications overlay |
| `ExamArena.tsx` | 14,699 bytes | Exam taking interface |
| `QuizPractice.tsx` | 9,962 bytes | Quiz practice interface |
| `CurriculumView.tsx` | 14,098 bytes | Curriculum tree navigation |
| `DesignSystem.tsx` | 26,366 bytes | Shared UI components: Button, Input, Dialog, StatsCard, ChartsWrapper, etc. |

### State Management (Context Stores)
| Store | Purpose |
|---|---|
| `authStore.tsx` | JWT auth, current user, login/logout/refreshProfile |
| `layoutStore.tsx` | currentPath, currentView, navigateTo |
| `themeStore.tsx` | dark/light theme toggle |
| `menuStore.tsx` | Dynamic navigation menus |
| `globalSystemStore.tsx` | Locale, translations, global dialog |

### API Services
| Service | Purpose |
|---|---|
| `api.ts` (17,511 bytes) | Master API client with auth header injection |
| `cmsApi.ts` (11,253 bytes) | CMS-specific API calls |
| `searchApi.ts` (4,899 bytes) | Search API integration |
| `analyticsApi.ts` (5,268 bytes) | Analytics event tracking |
| `mediaApi.ts` (3,235 bytes) | Media upload/management |

---

## 12. API Gateway (`server.ts`)

**Size:** 2,018 lines, 73,364 bytes  
**Stack:** Express.js + Vite dev server + Redis rate limiting

### Architecture
- `PATH_MAP` dictionary routes client paths → Django REST paths
- `proxyToDjango()` — HTTP proxy with JWT forwarding, tracing headers
- Redis-backed distributed rate limiting
- Gemini AI integration for `/api/ai/*` routes

### Currently Registered Proxy Paths (relevant to student)
```
/api/courses                  → /api/v1/lms/courses/
/api/certificates             → /api/v1/lms/certificates/
/api/exams                    → /api/v1/lms/exams/
/api/exam-attempts            → /api/v1/lms/exam-attempts/
/api/live-classes             → /api/v1/lms/live-classes/
/api/notifications/records    → /api/v1/notifications/records/
/api/notifications/preferences→ /api/v1/notifications/preferences/
/api/notifications/announcements → /api/v1/notifications/announcements/
/api/v1/search                → /api/v1/search/
/api/v1/analytics             → /api/v1/analytics/
/api/wallets                  → /api/v1/wallets/wallets/
```

### ⚠️ Missing Gateway Paths (to be added in Phase 6)
```
/api/v1/student/*  →  /api/v1/student/*   ← ENTIRE student namespace not registered
```

---

## 13. Database (SQLite dev / PostgreSQL prod)

**Current DB:** `backend/db.sqlite3` (23MB — seeded data)

### Applied Migrations
```
admin:         0001–0003  ✅
analytics:     0001       ✅
auth:          0001–0012  ✅
cms:           0001–0005  ✅
control_center:0001–0003  ✅
lms:           0001–0005  ✅
notifications: 0001–0002  ✅
portfolio:     (none)
publishing:    0001       ✅
search:        0001       ✅
seo:           0001       ✅
services:      0001       ✅
sessions:      0001       ✅
token_blacklist:0001–0012 ✅
users:         0001–0003  ✅
wallets:       0001       ✅
```

---

## 14. Backend Architecture Patterns

### Base Models
```python
BaseModel     → UUID PK + created_at + updated_at + created_by + updated_by
SoftDeleteModel → BaseModel + deleted_at + SoftDeleteManager
```

### Permissions Architecture (Dual: RBAC + CBAC)
```python
# Role-based
role = "STUDENT" | "TEACHER" | "ADMIN" | "SUPERADMIN"

# Capability-based  
user.is_student_cbac       # has LEARNING capability
user.is_teacher_cbac       # has TEACHING capability
user.has_capability("LEARNING")
user.has_capability_permission("lms:lesson:view")
```

### Settings
- Database: SQLite dev, PostgreSQL prod (GinIndex guards: `try/except ImportError`)
- Celery: Async task queue
- Redis: Rate limiting + Pub/Sub notifications
- JWT: `rest_framework_simplejwt` with token blacklisting
- Throttle classes: ANON/USER/STRICT rates
- CORS configured

---

## 15. What ALREADY EXISTS vs. What to Build

### ✅ Already Exists
| Feature | Location |
|---|---|
| Course browsing & enrollment | `StudentPortal.tsx` + `/api/v1/lms/` |
| Basic progress tracking | `LearningProgress` model + `students/me/progress/` |
| Certificates | `Certificate` model + `students/me/certificates/` |
| Badges / Gamification | `Badge`, `UserBadge` models |
| Exam taking | `ExamArena.tsx` + `ExamAttempt` model |
| Quiz practice | `QuizPractice.tsx` + `PracticeSession` |
| AI chat (Vidya) | `StudentPortal.tsx` + `/api/v1/ai/` |
| Notifications | `NotificationCenter.tsx` + `NotificationRecord` |
| Dashboard shell | `EnhancedDashboardView.tsx` at `/dashboard` |
| Auth + profile | `UserProfile` model + `authStore` |
| Search | `GlobalSearchView.tsx` + `SearchDocument` |
| Wallet balance | `Wallet` model |

### 🔨 To Build in Sprint 20
| Feature | Phase |
|---|---|
| New LMS models (streak, bookmark, notes, goals, calendar, history) | Phase 2 |
| Student dashboard backend services/selectors | Phase 3 |
| `/api/v1/student/` REST API namespace | Phase 4 |
| `StudentDashboard.tsx` and all sub-components | Phase 5 |
| Gateway `/api/v1/student/` registration | Phase 6 |
| Cross-platform signals and tasks | Phase 7 |
| Verification and test suite | Phase 8 |
| Documentation suite (11 docs) | Phase 9 |

---

## 16. Integration Points Summary

| Platform | How Student Dashboard Integrates |
|---|---|
| **LMS** | `StudentEnrollment`, `LearningProgress`, `Certificate`, `Badge`, `Exam` |
| **CMS** | `Tutorial`, `Blog`, `Article` for recommendations and learning history |
| **Notifications** | `NotificationRecord` for dashboard notification feed |
| **Analytics** | `AnalyticsEvent` for study session telemetry |
| **Search** | `SearchDocument` for content recommendations |
| **Wallet** | `Wallet` balance display, `Transaction` history |
| **AI** | Vidya AI chat assistant integration |
| **Media** | Course thumbnails, lesson video references |
| **SEO** | Meta tags for student profile pages |

---

## 17. Risks & Notes

> [!IMPORTANT]
> **No `/api/v1/student/` namespace exists yet.** The entire student API must be created as a new Django app (`apps.student`) or as an extension inside `apps.lms`. Given the scale, a **dedicated `apps.student` app** is recommended to keep separation of concerns clean.

> [!NOTE]
> **`StudentPortal.tsx` (36KB) already provides basic student views** but is not used in the main routing — it is imported inside `CoursesShell`. The new `StudentDashboard.tsx` will be a **separate, richer component** mounted at `/student-dashboard`.

> [!WARNING]
> **SQLite in dev does not support GinIndex** — the CMS models already handle this with a `try/except ImportError` guard. All new models must follow the same pattern.

> [!TIP]
> **`EnhancedDashboardView.tsx`** already handles: overview, teaching content builder, career, capabilities, profile. The new Student Dashboard should be a **dedicated route at `/student`** to avoid bloating `EnhancedDashboardView`.

---

## 18. Proposed New App: `apps.student`

A new Django app `apps/student/` will be created as the backend extension point. It will:
- Import and reference models from `apps.lms`, `apps.users`, `apps.notifications`, etc.
- Create only NEW models not present in any existing app
- Register at `api/v1/student/` in `django_project/urls.py`
- NOT modify any existing app's files

**New models to live in `apps/student/models.py`:**
```python
LearningHistory        # Auditable lesson visit log
ContinueLearning       # Last-accessed position per enrollment
Bookmark               # Content bookmarks (polymorphic)
StudentNote            # In-lesson notes
StudyGoal              # Personal study targets with progress
StudySession           # Timed study sessions
StudyCalendar          # Calendar events/reminders
DailyProgress          # Aggregated daily XP/time stats
WeeklyProgress         # Weekly aggregated stats
MonthlyProgress        # Monthly aggregated stats
LearningStreak         # Consecutive study days
Achievement            # Extended achievement catalog
StudentPreference      # Dashboard layout preferences
RecentlyViewedLesson   # LRU lesson view history
LearningReminder       # Scheduled study reminders
```

---

## 19. Verification Status (Pre-Sprint)

```
✅ python backend/manage.py check          → 0 issues
✅ python backend/manage.py showmigrations → All [X] applied
✅ npm run build                           → 2350 modules, 9.55s
```

---

**Phase 0 — COMPLETE.**  
**Awaiting approval to proceed to Phase 1 (Architecture Design).**
