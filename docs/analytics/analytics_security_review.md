# Security Review: Enterprise Analytics Platform

This document reviews the security architecture, role authorization, and data privacy policies for the analytics platform.

---

## 1. Authentication & Role Permissions

### 1. Simple JWT Verification
The gateway forwards client requests with the `Authorization: Bearer <JWT>` header to the backend, where Django simple JWT authenticates the user.

### 2. Role-Based Access Controls (RBAC) & Capabilities (CBAC)
Endpoints are protected by custom permission classes defined in `permissions.py`:
* **Viewer Access (`analytics:view`):** Scoped to Superadmins, Admins, Teachers, and Institutes to view dashboard widgets, charts, and summaries. Standard students can access their personal dashboards, but cannot query other users' data.
* **Manager Access (`analytics:manage`):** Allows triggering custom file exports and setting up report schedules.
* **Admin Access (`analytics:admin`):** Allows configuring KPI targets and dashboard widgets layout settings.

---

## 2. Ingestion Protection & Sanitization

* **SQL Injection Prevention:** Parameterized SQL binds in Django ORM prevent SQL injection attacks.
* **Rate Limiting:** Gateway rate-limiting restricts clients to 100 requests per minute per IP, protecting the collection endpoints from DoS flooding attempts.
* **Data Privacy:** Raw user-agent details are parsed for device types and browser metrics, but personal IP addresses and names are filtered out of public analytics views.
