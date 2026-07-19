# BrahmaVidya Galaxy: Control Center Backend Architecture Specification

This document specifies the server-side architecture of the BrahmaVidya Control Center app. The design adheres strictly to the rule: **Zero hardcoding, complete dynamicity, and unified administration driven exclusively by the backend.**

---

## 1. Architectural Philosophy

Traditional administration portals hardcode core pages, statistics, configuration keys, navigation layouts, and system features on the client. In BrahmaVidya Galaxy, the client serves purely as a **declarative renderer shell** that builds menus, metrics cards, layout blocks, and forms from real-time JSON schemas and dynamic model definitions received from the backend API.

```
┌────────────────────────────────────────────────────────┐
│               React Client Portal (Shell)              │
└───────────────────────────┬────────────────────────────┘
                            │ (1) GET /api/v1/control-center/telemetry/widgets/
                            │ (2) GET /api/v1/control-center/settings/
                            ▼
┌────────────────────────────────────────────────────────┐
│       BrahmaVidya Django Control Center Engine         │
├────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐    ┌──────────────────────┐  │
│  │ PlatformConfigService│    │DashboardTelemetryServ│  │
│  └──────────┬───────────┘    └──────────┬───────────┘  │
│             │                           │              │
│             ▼                           ▼              │
│     [PlatformSettings]          [DashboardWidget]      │
│             │                           │              │
│             └─────────────┬─────────────┘              │
│                           ▼                            │
│                  PostgreSQL Database                   │
└────────────────────────────────────────────────────────┘
```

---

## 2. Core Schema Models (`control_center`)

### 2.1 `PlatformSetting`
Hosts global features, system gates, and customization constants.
- `id` (UUID, Primary Key)
- `key` (String, Unique Index) – Variable descriptor (e.g., `COMMISSION_RATE`, `MAINTENANCE_MODE_ACTIVE`).
- `value_type` (Enum: `STRING`, `INTEGER`, `DECIMAL`, `BOOLEAN`, `JSON`) – Ensures accurate type casting during retrieval.
- `value` (TextField) – Serialized configuration parameter.
- `category` (Enum: `BRANDING`, `FINANCE`, `AI_INTEGRATION`, `SECURITY`, `MAINTENANCE`).
- `is_public` (Boolean) – If `True`, the variable is exposed to public routing layers. If `False`, it requires specific `SUPER_ADMIN` auth.

### 2.2 `DashboardWidget`
Configures metric cards on the administrator dashboard dynamically.
- `id` (UUID, Primary Key)
- `title` (String) – Heading displayed to the user.
- `metric_type` (Enum: `DB_COUNT`, `DB_SUM`, `TELEMETRY_RATE`, `STATIC_VALUE`).
- `query_target` (String) – Fully qualified package name pointing to a model class or reflection method (e.g. `lms.CourseStructure.count`).
- `color_scheme` (String) – CSS styling metadata class.
- `icon_name` (String) – Lucide Icon designation.
- `display_order` (Integer) – Sort ordering in the UI grid.
- `required_role` (String) – RBAC visibility lock string.

### 2.3 `AdministrativeTask`
Manages approval-gated actions requiring supervisor authorization and digital validation signatures.
- `id` (UUID, Primary Key)
- `title` (String) – Task header.
- `description` (Text) – Task details.
- `category` (Enum: `PAYOUT_APPROVAL`, `SYLLABUS_AUDIT`, `CERTIFICATE_SIGNING`, `USER_SUSPENSION`).
- `status` (Enum: `PENDING`, `APPROVED`, `REJECTED`, `EXECUTED`).
- `payload` (JSONB) – Parameter bag including digital keys, ledger entries, or draft certificates.

### 2.4 `SystemAuditLog`
An immutable, secure audit log of all management modifications, creating clear trace trails.
- `id` (UUID, Primary Key)
- `timestamp` (DateTime)
- `actor_email` (String)
- `action` (String) – Executed API routine identifier.
- `entity_type` (String) – Target collection or class.
- `entity_id` (String) – Unique ID of the affected record.
- `pre_state` (JSONB) – State snapshot *before* the action was executed.
- `post_state` (JSONB) – State snapshot *after* the action was completed.

---

## 3. Dynamic Resolution Strategy

The `DashboardTelemetryService` maps widget queries using Python reflections and Django apps registries. 

### Resolution Pipeline
1. Query active `DashboardWidget` models sorted by `display_order`.
2. Inspect the `metric_type`:
   - If `DB_COUNT`: Split the `query_target` (e.g., `lms.CourseStructure`). Query the model dynamically from the Django registry, check for soft-deletion flags, and return the row count.
   - If `STATIC_VALUE`: Read raw data directly from `query_target`.
3. Assemble and return a fully resolved list of widget cards directly to the client.

---

## 4. REST Endpoint Structure (v1 Namespace)

| Endpoint | Method | Required Permission | Description |
|---|---|---|---|
| `/api/v1/control-center/settings/` | `GET` | Public / Standard | Retrieves public global config flags. |
| `/api/v1/control-center/settings/` | `POST`/`PUT` | `SUPER_ADMIN` | Configures or edits a dynamic setting parameter. |
| `/api/v1/control-center/settings/update-by-key/` | `PUT` | `SUPER_ADMIN` | Modifies setting values dynamically by key. |
| `/api/v1/control-center/telemetry/widgets/` | `GET` | `SUPER_ADMIN` | Returns fully resolved active dashboard metric widgets. |
| `/api/v1/control-center/tasks/` | `GET` | `SUPER_ADMIN` | Views active and historic workflow actions. |
| `/api/v1/control-center/tasks/:id/resolve/` | `POST` | `SUPER_ADMIN` | Processes actions, approving payouts or signing digital certificates. |
| `/api/v1/control-center/audits/` | `GET` | `AUDIT_READ` | Chronological tracking of system activities. |
