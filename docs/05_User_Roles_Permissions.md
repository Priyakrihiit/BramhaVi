# User Roles and Permissions - BrahmaVidya Galaxy

## 1. Dynamic RBAC Architecture
BrahmaVidya Galaxy features a database-driven Role-Based Access Control (RBAC) engine. Rather than hardcoding authorization checks (e.g., `if (user.role === 'Admin')`), endpoints and views verify granular, condition-based permission nodes mapped to the user's role:

```
[User Session] ===> [User Role] ===> [Permission Code Checklist] ===> [Action Approved]
```

---

## 2. Primary Role Definitions

### 2.1 Platform Administrator (Superuser)
- **Scope**: Complete sovereignty over system state, configurations, templates, menus, security logs, and tenant variables.
- **Key Purpose**: Maintain system health, configure global integrations (such as AI API keys), and handle escalations.

### 2.2 School Operator (Tenant Operator)
- **Scope**: Manages a sub-portal, localized course packages, regional teacher onboarding approval queues, and localized fee structures.
- **Key Purpose**: Supervise high-level academic pipelines, manage registrations, and monitor financial balances.

### 2.3 Instructor / Teacher
- **Scope**: Create and manage course syllabi, lessons, dynamic tasks, track student scores, participate in forum moderations, and manage wallet withdrawals.
- **Key Purpose**: Author course material and support student learning.

### 2.4 Student / Learner
- **Scope**: Search courses, enroll, complete lessons/tasks, track course progress percentages, participate in chat forums, and generate verified certificates.
- **Key Purpose**: Consume educational curriculum and verify achievements.

### 2.5 Guest / Public Anonymous
- **Scope**: Read published layout pages (`/p/:slug`), navigate open menus, view general course catalogs, and utilize the certificate verification endpoint.
- **Key Purpose**: Explore public platform properties.

---

## 3. Granular Permission Mapping Matrix

| Permission Code | Description | Platform Admin | School Operator | Instructor | Student | Guest |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `MENU_READ` | Read dynamic navigation hierarchy | ✅ | ✅ | ✅ | ✅ | ✅ |
| `MENU_WRITE` | Create/edit/reorder navigation tree | ✅ | ✅ | ❌ | ❌ | ❌ |
| `PAGE_WRITE` | Create/edit dynamic layout blocks | ✅ | ✅ | ❌ | ❌ | ❌ |
| `RBAC_MANAGE` | Edit role-permission mappings | ✅ | ❌ | ❌ | ❌ | ❌ |
| `COURSE_CREATE` | Author courses and modular nodes | ✅ | ✅ | ✅ | ❌ | ❌ |
| `COURSE_PUBLISH`| Publish courses to public catalogs | ✅ | ✅ | ✅ (Own) | ❌ | ❌ |
| `TASK_SUBMIT` | Submit quizzes and complete lessons | ❌ | ❌ | ❌ | ✅ | ❌ |
| `CERT_ISSUE` | Generate digital course certificates | ✅ (System) | ❌ | ❌ | ❌ | ❌ |
| `CERT_VERIFY` | Access cryptographic verification endpoint | ✅ | ✅ | ✅ | ✅ | ✅ |
| `AI_GATEWAY` | Query Vidya AI endpoints | ✅ | ✅ | ✅ | ✅ (Limited) | ❌ |
| `FINANCE_READ` | Access financial wallets and ledgers | ✅ | ✅ (Tenant) | ✅ (Own) | ✅ (Own) | ❌ |
| `FINANCE_WRITE`| Authorize wallet withdrawals | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## 4. Middleware Enforcement Pattern
Whenever an API request hits the server, security filters verify token claims:
1. Parse JWT payload to extract user `role_id` and active `permission` strings.
2. Intercept requests targeting REST endpoints (e.g., `POST /api/courses`) and confirm the presence of the respective required privilege (`COURSE_CREATE`).
3. If unauthorized, stop request progression and return a standard HTTP `403 Forbidden` JSON contract.
