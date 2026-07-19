# BrahmaVidya Galaxy - Version 3.0 Implementation Specification
## Complete Product Design, API Catalogue, Database Schemas, & Workflows

---

## 1. Screen Catalogue (Ecosystem Screen Inventories)

### Screen 1.1: Live Whiteboard & Classroom Stream
* **Purpose**: Allows teachers to stream lectures, write on interactive whiteboard canvas blocks, and chat with students in real time.
* **User Roles**: `TEACHER` (Publisher), `STUDENT` (Viewer).
* **UI Layout & Components**:
  * Left: Dynamic video streaming player widget and whiteboard canvas container.
  * Right: Real-time scrolling message board panel and participant grid rail.
* **Accessibility**: Screen readers describe drawings using structural metadata tags; high-contrast icons for interactive controls.
* **Offline Behavior**: If connections drop, show a fallback overlay ("Reconnecting...") and cache typed chat comments locally.

### Screen 1.2: Coding Playground IDE
* **Purpose**: Dynamic coding workspace for running test cases on exercises.
* **User Roles**: `STUDENT`.
* **UI Components**: Instructions card column, syntax-highlighted editor box, console logs display, and a "Run Tests" trigger button.
* **AI Feature**: "Explain Code" prompt generates side-panel instruction cards highlighting syntax errors.

---

## 2. API Catalogue (API Gateway REST Specifications)

### 2.1 User Session Authentication Gate
* **Route**: `POST /api/v1/users/users/login/`
* **Request Schema**:
  ```json
  {
    "email": "student@brahmavidya.edu",
    "password": "studentpassword123"
  }
  ```
* **Response Schema (200 OK)**:
  ```json
  {
    "success": true,
    "token": "eyJhbGciOi...",
    "user": {
      "id": "c1a938fa-...",
      "email": "student@brahmavidya.edu",
      "fullName": "Shishya Arjuna"
    },
    "permissions": ["lms:lessons:view", "ai:chats:create"]
  }
  ```

### 2.2 Recommender Engine Semantic Search
* **Route**: `GET /api/v1/recommendations/courses/`
* **Parameters**: `user_id=<uuid>`, `limit=5`
* **Response**: Returns matching vector-similarity score course items.

---

## 3. Database Catalogue (Schema DDL & Partition Specifications)

```sql
-- Subdomain Tenancy Table
CREATE TABLE tenant_organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    theme_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Clickstream Events Telemetry (Partitioned)
CREATE TABLE clickstream_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Partition Tables Example
CREATE TABLE clickstream_events_y2026q3 PARTITION OF clickstream_events
    FOR VALUES FROM ('2026-07-01 00:00:00') TO ('2026-10-01 00:00:00');
```

---

## 4. Workflow Library (Sequence Schemas)

### Workflow 4.1: Book Purchase Revenue Split Settlement
```
[Student Pay] -> [Stripe Gate Webhook] -> [Validate Transaction Logs]
                                                   |
                                                   v
                                     [Reconcile Ledger splits]
                                 - 80% to Creator Wallet balance
                                 - 20% to Platform Wallet balance
                                 - GST/Tax allocated to Revenue ledger
```

---

## 5. Flutter UI Design Standards

* **Adaptive Breakpoints**:
  * Desktop Rails: Navigation utilizes persistent collapsible side-drawer bars with expandable nested submenus.
  * Mobile Views: Adapts to bottom navigation icons, displaying action dialog overlays dynamically.
* **Offline Synchronization Engine**:
  * Sync tasks are stored locally via SQLite (using sqflite / floor package wrappers) and processed sequentially using background tasks when online.

---

## 6. AI Agent System Architectures

### 6.1 AI Career Advisor Agent
* **System Prompt**:
  > *You are the BrahmaVidya Career Advisor Agent. Analyze the student's completed courses, test attempt histories, and portfolio projects to determine skill gaps. Suggest next-best courses to take.*
* **Context**: Loads the student's profile, resume markdown text, and career aspirations.

---

## 7. Business & Validation Rules

* **Royalty Splits**: Standard splits are set to 80% Creator / 20% Platform. Adjustments are logged.
* **Refund Window**: Purchases are eligible for refund triggers only within 7 days of payment, provided less than 20% of the educational content has been accessed.

---

## 8. Monetization Matrix

* **Platform Courses**: 100% Platform Owned -> Revenue to Super Admin Wallet.
* **Creator Courses**: 80% Creator Settlement Wallet / 20% Platform Commission.
* **SaaS White-Label Licenses**: Enterprise organizations billing templates set up on quarterly recurring cycles.

---

## 9. Dependency Graph Configuration

```
  +------------------+         +------------------+
  | Education Module | <=====> |    AI Tutor      |
  +------------------+         +------------------+
           ^                            ^
           |                            |
           v                            v
  +------------------+         +------------------+
  |  Wallet Ledger   | <=====> | Payments Gateway |
  +------------------+         +------------------+
```

---

## 10. Sprint Implementation Plan

* **Sprint 1 (Infrastructure & Security)**:
  * Complete Django migration updates for audited models.
  * Establish Redis caching filters for permissions lists.
* **Sprint 2 (LMS & Core Education)**:
  * Connect WebSockets for the interactive whiteboard stream.
  * Deploy the browser-based Coding IDE Playground page.
* **Sprint 3 (Payments & Finance)**:
  * Configure Stripe/Razorpay checkout routes and verify splits ledger webhooks.
* **Sprint 4 (AI Integration)**:
  * Wire up the Gemini API proxy to handle chatbot sessions.

---

## 11. Production Readiness Checklist

- [ ] Verify CORS configurations protect APIs against unauthorized domain access.
- [ ] Enforce SSL certification encryption across WebSockets and REST channels.
- [ ] Schedule database automatic backup scripts to export encrypted snapshots to cold storage every 12 hours.
