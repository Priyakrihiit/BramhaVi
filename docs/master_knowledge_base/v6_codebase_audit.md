# BrahmaVidya Galaxy - Version 6.0 Codebase Audit & Refactoring Blueprint
## Technical Debt Register, Security Assessment, & Clean-up Roadmap

---

## 1. Repository Audit Report

We analyzed all directories and configuration layers in the monorepo:
* **Node.js Gateway Router (`server.ts`)**: Acts as a reverse-proxy translating kebab-case URLs to Django's nested API structures. If the Django subprocess fails, it falls back to in-memory mock JSON structures in `src/db.ts`.
* **Django REST Backend (`backend/`)**: Domain-driven sub-applications (`users`, `cms`, `lms`, `wallets`, `control_center`, `ai`, `portfolio`, `publishing`). DB queries use recursive CTE structures.
* **React Client (`src/`)**: Layout scaffolds defined. Redundant routes exist that bypass backend authentication checks.

---

## 2. Architecture Alignment Report

* **Implemented**: JWT logins, 6-tier recursive tree fetching, soft-deletes via native model migrations.
* **Partially Implemented**: Dynamic page builder templates (backend ready, frontend rendering blocks pending), AI context prompts utility structures.
* **Missing**: Stripe/Razorpay webhook gateways, mentor schedule tables, clickstream quarters partitions, co-branded tenancies.

---

## 3. Technical Debt Register

### Debt 3.1: Duplicate In-Memory Mocks
* **Location**: `src/db.ts` duplicates model properties defined in `backend/apps/*/models.py`.
* **Impact**: Double maintenance burden; risk of schema desynchronization.
* **Refactoring Plan**: Remove the Node Express mock DB bypass entirely once the Django container setup stabilizes.

### Debt 3.2: Hardcoded REST Endpoints
* **Location**: `server.ts` maps exact URLs inside the `PATH_MAP` dictionary.
* **Impact**: Restricts dynamic REST expansions.

---

## 4. Security Findings

* **Session Token Invalidation**: Logout requests do not invalidate access tokens on active systems. Access tokens remain valid for their 15-minute lifespan.
* **No API Rate Limiting**: The Node gateway lacks IP-based throttling, exposing authentication views to credential brute-forcing.

---

## 5. Performance Findings

* **Curriculum Tree Fetching**: The custom tree fetch is optimized via database CTEs. However, client-side caching of syllabus nodes is missing, causing redundant SQL queries during active learning sessions.
* **Clickstream Log Scalability**: Clickstream tables lack database partition definitions, leading to table scan locks as records scale past $10^6$ entries.

---

## 6. Feature Alignment Matrix

| Feature | Blueprint Status | Repository Status | Gap | Priority | Owner Module |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Token Blacklist** | Redis Key Lookups | In-memory only | Resets on reboot | **Critical** | `apps.users` |
| **White-Labeling** | org_id row filter | Missing | Tenancy filters absent | **High** | `apps.control_center` |
| **Stripe Webhooks** | Verify webhook signature | Planned | Integration missing | **High** | `apps.wallets` |

---

## 7. Migration & Clean-up Roadmap

### Task ID: REFACTOR-001 - Token Blacklist Redis Integration
* **Files**: `backend/apps/users/views.py`, `backend/django_project/settings.py`
* **Risk**: Low.
* **Rollback Plan**: Fall back to simple JWT local validation if Redis connections fail.

### Task ID: CLEANUP-002 - Remove Express Mock Database
* **Files**: `server.ts`, `src/db.ts`
* **Risk**: Medium (breaks local mock testing if backend subprocess is down).
* **Mitigation**: Ensure the Docker environment automatically boots the DRF container.

---

## 8. Implementation Readiness Report

* **Overall Score**: **72%**.
* **Rationale**: Database models are clean and migrations are aligned. However, rate limits, session blacklists, and cross-platform grid adaptivities require configuration prior to launch.
