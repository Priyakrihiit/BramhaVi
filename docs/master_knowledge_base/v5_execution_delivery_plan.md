# BrahmaVidya Galaxy - Version 5.0 Execution & Delivery Plan
## Master Engineering Backlog, Git Strategy, Coding Standards, & CI/CD Pipelines

---

## 1. Master Engineering Backlog (Task Inventory)

### Task ID: AUTH-101
* **Title**: Persistent Redis Session Token Blacklist Setup
* **Description**: Configure token revocation middleware to check Redis blacklists on incoming requests.
* **Story Points**: 5
* **Complexity**: Medium
* **Dependencies**: None
* **Required Skills**: Python, Django REST, Redis
* **Backend Files**: `backend/django_project/settings.py`, `middleware/security.py`
* **Database Migrations**: None
* **API Changes**: `POST /api/v1/users/users/logout/` invalidates the token.
* **Acceptance Criteria**: Logged-out tokens must return `401 Unauthorized` on immediate reuse.

### Task ID: LMS-201
* **Title**: Whiteboard WebSockets Integration
* **Description**: Implement Django Channels live stream coordinate broadcast triggers.
* **Story Points**: 8
* **Complexity**: High
* **Dependencies**: AUTH-101
* **Required Skills**: Python, WebSockets, Redis Channels

---

## 2. Sprint-by-Sprint Delivery Plan

```
[Sprint 0: Platform Foundation] ---> [Sprint 1: Auth & User Profiles] ---> [Sprint 2: LMS Curriculum]
                                                                                   |
                                                                                   v
[Sprint 5: Careers & Resume] <--- [Sprint 4: Creator Wallets] <--- [Sprint 3: Publishing Store]
           |
           v
[Sprint 6: Professional CRM] ---> [Sprint 7: Subscription Coupons] ---> [Sprint 8: AI Agents Hub]
                                                                                   |
                                                                                   v
                               [Sprint 10: White-Label] <--- [Sprint 9: Telemetry Dashboards]
```

* **Sprint 0 (Platform Foundation)**: Docker Compose set up, database indexes, and code lint configurations.
* **Sprint 1 (Authentication & RBAC)**: JWT access tokens, Redis permissions flat caches, and user notification triggers.
* **Sprint 2 (Education Core)**: Adjacency curriculum tree loader, quiz sessions attempt tables, and certificates signature lookup.
* **Sprint 3 (Publishing & Book Store)**: E-book reader controls, printed book inventory tracking, and author layout review states.
* **Sprint 4 (Creator Economy)**: Mentor bookings availability tables, revenue sharing calculations, and double-entry settlements.
* **Sprint 5 (Career Galaxy)**: AI resume builders, portfolio builder custom CNAME domain mappings, and job applications pipeline.
* **Sprint 6 (Professional Services)**: Consulting milestones escrow trackers and client CRM invoicing templates.
* **Sprint 7 (Marketplace)**: Subscription library coupons stacking validations.
* **Sprint 8 (AI Platform)**: Gemini model routing, tutor prompts, and token cost caching rules.
* **Sprint 9 (Analytics)**: Partitioned clickstream log displays and telemetry dashboards.
* **Sprint 10 (Enterprise & White-Label)**: White-label custom subdomains, localization translation resources, and WCAG AA accessibility grids.

---

## 3. Git Strategy (Branching & Workflows)

### 3.1 Branch Layout
* `main`: Production-ready release branches. No direct pushes.
* `develop`: Integration branch. Merges pull requests from feature branches.
* `feature/*`: Short-lived branches targeted for specific Task IDs (e.g. `feature/AUTH-101`).
* `release/*`: Testing candidate releases.
* `hotfix/*`: Quick production fixes.

### 3.2 Commit Message Convention
Enforce Angular-style commit structures:
```
<type>(<scope>): [Task ID] <description>

[body]
```
*Example*: `feat(auth): [AUTH-101] Add Redis session token blacklisting lookup`

---

## 4. Coding Standards

* **REST APIs**: Enforce lowercase spinal-case (kebab-case) path URLs. JSON response keys must match standard camelCase naming schemas.
* **Django Subsystems**:
  * Models must inherit from `SoftDeleteModel` where soft-deletion is required.
  * Avoid raw SQL queries; use Django ORM or recursive CTE managers.
* **Flutter Clients**:
  * All views must utilize state management patterns (BLoC or Riverpod) separating logic from widgets.
  * Enforce strict type validation; avoid `dynamic` types.

---

## 5. Quality Gates

Features cannot merge to `develop` unless:
1. **Unit Tests**: Coverage must meet a minimum of 80%.
2. **Linting Check**: Zero syntax or format violations.
3. **Security Scan**: Zero high-severity vulnerabilities identified by analyzer tools.
4. **API Versioning**: Endpoint changes must increment namespace scopes if breaking changes are introduced.

---

## 6. CI/CD Architecture

```
[Push to feature/*] -> [Lint Checks] -> [Unit & Integration Tests] -> [Docker Build Scan]
                                                                              |
                                                                              v
[Merge to develop] <- [Release Candidate Tagging] <- [Deploy to Staging environment]
```

* **Rollback Rules**: If staging deployments generate health status exceptions, the pipeline automatically rolls back cluster images to the previous stable release tag.

---

## 7. Production Readiness Checklist

### Flutter Web/Mobile
- [ ] Verify asset compression rules are active.
- [ ] Confirm screen layouts meet WCAG AA contrast standards.

### Backend API & Database
- [ ] Disable `DEBUG = True` settings in production config.
- [ ] Configure database connection pooling limits.

---

## 8. Engineering Dashboard Specification

The release team monitors the following telemetry parameters:
* **Sprint Velocity**: Story points completed vs planned.
* **Code Coverage**: Graphical line charts tracking test scopes.
* **Technical Debt Ratio**: Tracking issues flagged by code scanners.
* **Active Bug Counts**: Grouped by severity indexes (Blocker, High, Medium, Low).
