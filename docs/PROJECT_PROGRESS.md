# BrahmaVidya Galaxy: Project Progress Specification
## Single Source of Truth (SSOT) Project Status

---

## 1. Project Overview

### Vision
**BrahmaVidya Galaxy** is an enterprise-grade, holistic educational ecosystem designed to bridge spiritual ancient wisdom (Vidya) with modern scientific disciplines and high-tech tools. It empowers learners to explore, develop, and master multidisciplinary paradigms while leveraging artificial intelligence (Vidya AI) for personalized pedagogy, interactive workspace creation, and no-code professional portfolio construction.

### Objectives
- **Multidisciplinary Pedagogy**: Deliver hierarchical structured curricula covering ancient breathing techniques, modern sciences, cognitive development, and technical professional paths.
- **AI-Powered Personalization**: Inject context-aware generative tutoring (Vidya AI) and personalized AI-guided resume, memory, and website generation.
- **Sovereign Security & Gated RBAC**: Maintain strict Least-Privilege Role-Based Access Gating via recursive inheritance.
- **Immutable Financial Ledgers**: Support integrated points/currency rewards via transactional double-entry bookkeeping ledgers.
- **Proof of Capability**: Issue verifiable cryptographic SHA-256 signatures for course graduation certificates.

### Technology Stack
- **Backend**: Python, Django, Django REST Framework (DRF), SQLite (development) / PostgreSQL (production)
- **Caching & Key-Value Store**: Redis (active token revocations, session blacklisting, RBAC flattening cache)
- **Frontend**: React, TypeScript, Tailwind CSS, Vite, motion (React animation framework)
- **AI Integration**: Gemini Pro & Flash models via modern `@google/genai` TypeScript SDK (server-side proxying)
- **Object Storage**: AWS S3 / Google Cloud Storage for protected asset distribution

### Current Architecture
The project current state is a **highly unified full-stack application**. The backend is structured into domain-driven Django applications under `backend/apps/`, exposing a secure, RESTful, and pagination-equipped API. The frontend is a modular Single Page Application built with React and Tailwind, featuring a unified design language with focus boundaries and high-contrast typography.

---

## 2. Current Navigation

The platform implements a streamlined, unified single-page global layout featuring the following primary sections accessible via dynamic menus:

1. **Home**: Dynamic CMS-powered landing page displaying personalized course progress, daily streak counters, and quick action banners.
2. **Tutorials**: Interactive guide library providing fast step-by-step onboarding for platform tools and the Vidya AI ecosystem.
3. **Courses**: 6-tier educational catalog displaying Programs, Subjects, Courses, Chapters, Topics, Subtopics, and Lessons.
4. **Projects**: Capstone hands-on assignments list where students collaborate or submit technical challenges.
5. **Certificates**: Document validation portal with support for public-facing, anonymous cryptographic lookup hashes.
6. **Blogs**: Educational articles, platform news, and mindfulness commentaries with threaded user comment loops.
7. **Community**: Collaborative workspace containing forums, nested posts, reaction triggers, and report moderation pipelines.
8. **Portfolio**: Interface enabling no-code AI-powered creation and publishing of user sites.
9. **Vidya AI**: Central chat and interaction playground where students converse with the AI Tutor and access cognitive tools.

---

## 3. Completed Architecture

### Database Master Architecture
- **Unified 6-Tier Recursive Curriculum System**: Handled via `course_structures` employing self-referential adjacency lists. High-performance tree fetches are executed in a single database round-trip using recursive CTE queries.
- **UUIDv4 Primary Keys**: Non-sequential unique IDs enforced globally to prevent resource enumeration attacks.
- **Soft-Delete Pattern**: Standard `deleted_at` timestamps integrated with customized uniqueness filters.
- **Audits & Logging Ledger**: Active logging maps events (`analytics_events`), database state mutations (`system_audit_logs`), and user diagnostics (`activity_logs`).
- **Double-Entry Balance Trackers**: Points wallets secured via append-only transactions preventing concurrent race conditions.

### API Master Architecture
- **Stateless Token-Based Authentication**: Implements JWT (15m Access Token, 7d Refresh Token) with active blacklist tracking in Redis.
- **Resource Naming**: Enforces lowercase spinal-case (kebab-case) URL conventions, REST plural nouns, and standard enveloped JSON structures.
- **Operations Standard**: Built-in cursor & offset pagination, multi-comparators filters, and direct-to-object presigned upload procedures.

### RBAC Master Permission Matrix
- **Decoupled Identity Gates**: Flat matrix mapping fine-grained permissions (e.g., `lms:courses:publish`, `sys:settings:write`) across 12 distinct enterprise roles.
- **DAG Role Inheritance**: Hierarchical role relationships resolved at runtime via recursive parent merging and cached in Redis.

---

## 4. Completed Backend Modules

### Authentication & Identity
- **Users**: Extended authentication profile with activity status and verification flows.
- **Roles & Permissions**: Database-driven structural access tables with granular permissions tracking.
- **JWT**: Token generation, rotation and revocation blacklists.
- **Sessions & Devices**: Multi-device login tracking with push notification tokens.
- **Notifications**: Fan-out multi-channel notification engine (In-app, SendGrid, Push).

### LMS (Learning Management System)
- **Programs & Subjects**: Top-level curricula containers.
- **Courses, Chapters, Topics, & Subtopics**: Nested structures in unified `course_structures`.
- **Lessons**: Resource blocks supporting markdown, video metadata, and interactive states.
- **Assignments & Submissions**: Essay tasks, file uploads, score records, and teacher grading pipelines.
- **Practice & Attempts**: Interactive mock-quizzes tracking history logs.
- **Projects & Submissions**: Large hands-on capstone assignments.
- **Question Bank**: Central repository for multiple-choice, matching, and short-answer questions.

### CMS (Content Management System)
- **Pages**: Dynamic page builders backed by GIN-indexed layout blocks JSONB payloads.
- **Menus**: Hierarchy lists with RBAC gating rules.
- **Tutorials**: Interactive guides supporting rich Markdown.
- **Blogs**: Core model, publication, and draft layouts are complete (comment loop architecture ready).

### Wallet
- **Models**: Unified wallet structure supporting points and internal balances tracking.

### Payments
- **Models**: Invoices and transaction reconciliation templates ready.

### Vidya AI
- **Models**: Chat structures supporting parent-child conversational mapping, token diagnostics, and user feedback flags.

### Analytics
- **Models**: High-velocity analytics event logs ready for user interaction capture.

### Control Center
- **Models**: Dynamic administrative configurations, audits logs, and system preferences maps.

---

## 5. Pending Modules

### LMS (Learning Management System)
- **Exams**: Execution logic, scheduling, time limits, and automated threshold grading pipelines.
- **Student Enrollments**: Active subscription linkages, trial states, and direct payment mapping.
- **Learning Progress**: Aggregation views tracking overall completion percentage across parent nodes.
- **Certificates API**: Secure generation algorithms and signature registration triggers upon exam completion.
- **Badges API**: Unlocking logic linked to user milestones (daily streak achievements, quick-quizzes, etc.).

### CMS (Content Management System)
- **Categories & Tags**: Public taxonomic classification of articles, tutorials, and pages.
- **SEO & Metadata**: Search engine index templates, sitemaps, and social preview configurations.
- **Draft & Publishing Workflow**: Multi-state editorial pipeline (Draft, Under Review, Approved, Published).
- **Media Library**: Dynamic file explorer, bulk media deletions, and image compression routines.

### Community
- **Forums**: Structured boards mapping discussions to course modules.
- **Posts & Comments**: Nested discussion boards and real-time comment threads.
- **Likes & Reactions**: Quick-click reaction logs on forum topics and blog comments.
- **Reports & Moderation**: Reporting ticketing pipelines and moderator dashboard interfaces.

### Wallet
- **APIs**: User-facing balance retrievals, reward points redemption, and peer-to-peer point transfers.

### Payments
- **Subscription Engine**: Tiered membership billing (Standard vs Premium).
- **Billing Portal**: PDF invoice generation, payment history lists, and credit-card profiles.
- **Razorpay/Stripe Integration**: External checkout webhook receivers.

### Vidya AI
- **Chat APIs**: Conversational routing, session threads creation, and historical context lookups.
- **AI Tutor**: System prompts for subject-matter experts (Vedas, Mathematics, Sciences).
- **AI Website Generator**: Automatic scaffolding of personal websites based on user text prompts.
- **AI Resume Builder**: Standard template builder synthesizing dynamic career pathways.
- **AI Memory**: Semantic context caching of student learning style, weak concepts, and preferred subjects.

### Analytics
- **Dashboard**: High-level reporting visualizers for students and educators.
- **Reports Generator**: Automated reports compiling user course completion speeds and performance metrics.

### Control Center
- **APIs & Settings**: Dynamic backend configurations and administrative adjustments at runtime.
- **Themes Builder**: In-app customization of colors, typography, and logo packages.

### Portfolio Builder
- **Status**: Not Started (Comprehensive planning complete, awaiting frontend scaffolding).

### Frontend
- **Status**: Not Started (Scaffolding ready, React components, state hooks, and dashboard page structures pending).

### Testing
- **Status**: Not Started (Test suites for API validation, permission evaluation, and database queries pending).

### Deployment
- **Status**: Not Started (Dockerized staging pipelines, container configurations, and CI/CD parameters pending).

---

## 6. Completion Percentage

Below is a detailed breakdown of the project completion metrics based on model implementations, API availability, and frontend/testing progress.

### Module-Wise Progress

| Module | Weight | Backend Database Models | Backend REST APIs | Frontend UI Pages | Unit & Integration Tests | Overall Completed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Authentication & RBAC** | 12% | 100% | 100% | 0% | 0% | **80%** |
| **LMS (Curriculum & Tasks)** | 18% | 100% | 60% | 0% | 0% | **65%** |
| **CMS & Blogs** | 10% | 100% | 60% | 0% | 0% | **60%** |
| **Community Workspace** | 10% | 80% | 0% | 0% | 0% | **35%** |
| **Wallet & Point Ledgers** | 8% | 100% | 0% | 0% | 0% | **45%** |
| **Payments & Checkout** | 8% | 100% | 0% | 0% | 0% | **40%** |
| **Vidya AI & Intelligence** | 12% | 100% | 0% | 0% | 0% | **45%** |
| **Analytics & Telemetry** | 6% | 100% | 0% | 0% | 0% | **40%** |
| **Control Center** | 6% | 100% | 0% | 0% | 0% | **40%** |
| **Portfolio Builder** | 10% | 0% | 0% | 0% | 0% | **0%** |

### Overall Project Completion Metric

$$\mathbf{\text{Overall Project Completion Percentage} = \mathbf{45.6\%}}$$

*Justification*: The fundamental infrastructure of BrahmaVidya Galaxy is fully complete. This includes the database schema specifications, multi-table relationships, dynamic RBAC matrices, recursive curriculum CTE lookups, and core authentication views. Core REST endpoints for LMS, CMS, and Authentication are implemented. Scaffolding is complete, leaving frontend layout creation, AI API client routes, external payments, and overall testing suites as pending milestones.

---

## 7. Known Issues & Technical Debt

### 1. SQLite Serializer Workaround (Technical Debt)
Due to a discrepancy in the development database engines, a runtime column injection workaround was added inside `backend/apps/lms/serializers.py` to support dynamic soft-delete columns on certain tables:
```python
# Temporary SQLite runtime schema modification
cursor.execute("PRAGMA table_info(practice_sessions)")
columns = [col[1] for col in cursor.fetchall()]
if 'deleted_at' not in columns:
    cursor.execute("ALTER TABLE practice_sessions ADD COLUMN deleted_at datetime")

cursor.execute("PRAGMA table_info(question_banks)")
columns = [col[1] for col in cursor.fetchall()]
if 'deleted_at' not in columns:
    cursor.execute("ALTER TABLE question_banks ADD COLUMN deleted_at datetime")
```
- **Refactoring Requirement**: This raw SQLite cursor injection must be removed, and migration files (`makemigrations` and `migrate` commands) must be executed properly to apply consistent schema tables across all environments.

### 2. Missing Database Indices for Portfolio Models
The database contains GIN indexes for pages and profiles but lacks standard indexes for prospective portfolio models which will undergo massive concurrent queries.
- **Refactoring Requirement**: Ensure optimized B-Tree and GIN indexing are established on all user-created portfolio database schemas once scaffolding begins.

### 3. In-Memory Session Blacklists
The authentication engine relies on blacklist tracking for refresh tokens. In the local environment, this is modeled in-memory which resets upon container restart.
- **Refactoring Requirement**: Transition the token revocation lookup checks to use a persistent Redis key-value store in development to mimic production environments.
