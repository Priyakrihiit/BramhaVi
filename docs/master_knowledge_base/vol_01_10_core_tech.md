# BrahmaVidya Galaxy - Master Knowledge Base V2.0
## Volumes 1 to 10: Strategic Foundations & Core Infrastructure

---

## Volume 1 - Executive Vision (Production Specifications)

### 1.1 Business Objective
Establish BrahmaVidya Galaxy as a premier digital knowledge, educational, and professional ecosystem. The platform acts as a bridge between spiritual development, scientific disciplines, and advanced enterprise SaaS tools.

### 1.2 Target User Personas
* **Shishya (Learner)**: Seeks certified academic growth, attempts quizzes, uses the AI Tutor, and builds a professional portfolio.
* **Aacharya (Educator)**: Authors complex curriculum structures, schedules live interactive streams, scores student projects, and earns revenue.
* **Super Admin**: Monitors global transaction ledgers, adjusts platform fee percentages, reviews audit trails, and moderates content flag queues.

---

## Volume 2 - Product Requirement Document (PRD)

### 2.1 Core Modules & Complete Screen Inventory
* **Live Classes Portal**: Screen to launch live streams, share whiteboard frames, and view real-time student participation lists.
* **Coding Playground**: Dynamic browser coding IDE supporting Python, JavaScript, and SQL compilation with instant feedback.
* **AI Tutor Panel**: Dedicated chatbot canvas providing context-aware guidance and memory tools mapping weak academic concepts.
* **Parent Dashboard**: Parents monitor attendance rates, test scores, streak counters, and reward point allocations.

---

## Volume 3 - Software Requirement Specification (SRS)

### 3.1 Non-Functional Performance Thresholds
* **Client Interface Response**: Transitions between layout spaces must finish in <16ms (60 FPS rendering target).
* **Database Connection Pooling**: Max query execution time of 50ms for high-velocity lookups.
* **File Ingestion**: Direct-to-bucket S3 uploads using authenticated, short-lived presigned URLs.

---

## Volume 4 - Enterprise Architecture

```
+---------------------------------------------------------------------------------------+
|                                    FLUTTER CLIENTS                                    |
|      Android App   |   iOS App   |   Web App   |   Windows   |   macOS   |   Linux    |
+---------------------------------------------------------------------------------------+
                                           |
                                           v  HTTPS REST API / WebSockets
+---------------------------------------------------------------------------------------+
|                                 NODE.JS API GATEWAY                                   |
|   - Rate Limiting Shield (100 req/min/IP)                                             |
|   - Request Payload Validation Mapping (kebab-case -> snake_case)                    |
|   - Generative API Cost & Token Metering                                              |
+---------------------------------------------------------------------------------------+
                                           |
                                           v  Reverse Proxy (Internal Network)
+---------------------------------------------------------------------------------------+
|                           DJANGO REST FRAMEWORK BACKEND                               |
|   - Row-Level Tenant Security Gating (org_id)                                         |
|   - Double-Entry Account Wallet Balancing                                             |
|   - Custom RBAC Evaluation Engines & Audit Logging Middleware                         |
+---------------------------------------------------------------------------------------+
                                           |
                       +-------------------+-------------------+
                       |                                       |
                       v                                       v
             [PostgreSQL Database]                      [Redis Cluster]
     (Core Ledger, CTE syllabus tree)           (JWT blacklists, RBAC cache)
```

---

## Volume 5 - Flutter Platform (Cross-Platform Strategy)

### 5.1 Responsive Design Constraints
* **Grids System**: Uses `LayoutBuilder` mapping fluid column widths based on device display:
  * Mobile displays (<600dp): 4 columns, bottom navigation bars.
  * Tablet displays (600dp to 1024dp): 8 columns, side navigation rail.
  * Desktop displays (>1024dp): 12 columns, permanent sidebar and layout grids.
* **Offline Synchronization Engine**:
  * Write-Ahead Caching: User actions (e.g., ticking course tasks, updating draft settings) are queued in local Hive stores.
  * Synchronization Scheduler: Automatically pushes stored records to backend REST endpoints sequentially when web connections are restored.

---

## Volume 6 - Backend Architecture

### 6.1 Subsystems Mapping & Operations
* **Middlewares**:
  * `AuditLogMiddleware`: Intercepts modifications to databases and serializes modifications to JSON records in the `system_audit_logs` table.
  * `SecurityHardeningMiddleware`: Enforces HTTPS redirection, content-security security protocols, and frame protection rules.

---

## Volume 7 - Database Architecture

### 7.1 Schema Definitions & Data Partitioning
* **Partitioning Strategy**: Large analytics logs (`analytics_events`) are partitioned by calendar quarters (`PARTITION BY RANGE (created_at)`).
* **Indexes**: GIN indices on JSONB metadata fields.

---

## Volume 8 - Authentication & Organizations

### 8.1 Multi-Tenant Separation
All tenant accounts possess unique `org_id` values. The database layer injects org conditions into queries to prevent multi-tenant data leaks.
* **SSO & MFA**: Supports OAuth2 logins alongside TOTP authentication algorithms.

---

## Volume 9 - Education Galaxy

### 9.1 Database Tables (Education Assets)
```sql
-- Live Classes table
CREATE TABLE live_classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES course_structures(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES users(id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER NOT NULL,
    stream_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Coding Exercises table
CREATE TABLE coding_exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID REFERENCES course_structures(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    instructions TEXT NOT NULL,
    boilerplate_code TEXT,
    test_cases JSONB NOT NULL, -- Inputs and expected outputs validation keys
    max_score INTEGER DEFAULT 100
);
```

### 9.2 API Contracts
* **Start Live Stream**:
  * `POST /api/v1/lms/live-classes/`
  * Request payload: `{"course_id": "<uuid>", "title": "Advanced Quantum Metaphorics", "scheduled_at": "2026-07-09T10:00:00Z", "duration_minutes": 60}`
  * Response: `{"success": true, "live_class_id": "<uuid>", "stream_url": "rtmp://..."}`

---

## Volume 10 - AI Galaxy (Agent Specifications)

### 10.1 AI Coding Assistant Agent
* **Responsibilities**: Evaluates user code inputs inside playgrounds, provides hint cards, and highlights syntax errors.
* **System Prompt**:
  > *You are the BrahmaVidya AI Coding Assistant. Review the user's code snippet against the target problem description. Do not provide the direct solution. Instead, write hint guidelines pointing out logic errors.*
* **Memory Strategy**: Caches the last 5 code submission attempt logs inside local Redis scopes to evaluate the student's problem-solving progress.
* **Tools**: Python compiler checker execution gateways.
