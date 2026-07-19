# Django Backend Architecture Specification

This document details the corporate backend application design, structural modules, design patterns, and routing models for **BrahmaVidya Galaxy**. It complements the physical schema definitions by outlining the logic layers that process client requests.

---

## 1. Modular Application Architecture (Django Apps)

The backend is composed of four decoupled, domain-specific Django applications structured under the `/backend/apps/` package:

1. **`users` (Identity & RBAC)**: Manages authentication, custom database-driven Roles, Permissions mapping, and password complexity enforcement.
2. **`cms` (Dynamic Layout Engine)**: Manages dynamic layout block schemas, site menu structures, and page content history states.
3. **`lms` (Recursive Curriculum & Progress)**: Dictates the hierarchical 6-tier educational framework (Program -> Degree -> Course -> Module -> Lesson -> Task) and tracks learning progress metrics.
4. **`wallets` (Ledger Transactions & Certification)**: Orchestrates transactional ledger balances, digital wallets, and cryptographic completion certificates.

```
/backend/
├── django_project/          # Project settings, wsgi/asgi, master routing
├── apps/                    # Domain-Specific Applications
│   ├── users/               # Authentication & RBAC App
│   ├── cms/                 # CMS Layout App
│   ├── lms/                 # LMS Curriculum App
│   └── wallets/             # Ledger & Verification App
├── middleware/              # Custom Request / Response Gates
└── utils/                   # General Shared Utilities
```

---

## 2. Decoupled Logic Layers

To ensure modularity and ease of maintainability, the codebase maintains a strict separation of concerns across key specialized layers:

### 2.1 Service Layer (`services.py`)
Encapsulates complex workflows and coordinates business rules. By decoupling services from Django views and database models:
- Views remain lightweight controllers responsible only for HTTP serialization and parameter parsing.
- Business processes (e.g., recursive grade calculation, cryptographic hash signing, multi-wallet balance adjustment) are easily testable in isolation.

### 2.2 Repositories Layer (`repositories.py`)
Standardizes access to data resources. Encapsulating raw Django ORM queries within custom Repository classes:
- Eliminates duplicate query clauses across files.
- Simplifies swapping backend storage engines or adding advanced caching/query-splitting operations.

### 2.3 Middleware (`/backend/middleware/`)
Global request-response hooks enforcing compliance across all API sub-modules:
- **`AuditLogMiddleware`**: Captures payload details during data modifications and logs them for systemic transparency.
- **`SecurityHardeningMiddleware`**: Adds HTTP security headers (CSP, X-Frame-Options) to protect from frame injections and sniffing.

### 2.4 Custom Permissions (`permissions.py`)
Enforces fine-grained, database-driven authorization:
- **`HasRBACPermission`**: Verifies dynamic permission strings assigned to a user's role.
- **`IsWalletOwner`**: Implements object-level security, restricting wallet histories to verified owners.

### 2.5 Validation Layer (`validators.py`)
Guarantees clean, sanitized inputs before data layers are mutated:
- **`validate_page_layout_schema`**: Enforces structure parameters on CMS block elements.
- **`validate_child_tier_transition`**: Protects the sequential integrity of the 6-tier curriculum ladder.

### 2.6 Signals Layer (`signals.py`)
Decouples post-mutation effects using Django's native dispatcher:
- **User Creation** automatically provisions an associated digital payment wallet.
- **Course Completion (100% progress)** triggers cryptographic certificate generation.

### 2.7 Background Tasks Layer (`tasks.py`)
Delegates heavy, long-running operations off the main HTTP thread using **Celery** with **Redis**:
- **`compile_cryptographic_certificate_task`**: Mints secure digital signature hashes.
- **`rebuild_public_sitemap_task`**: Compiles dynamic sitemap files for search optimization.

---

## 3. API Versioning & Routing

API namespaces are routed systematically to prevent breaking changes:
- Endpoints are versioned using **Namespace API Versioning** mapped via the main routing catalog: `/api/v1/`.
- Local app routing files (`urls.py`) bind sub-paths to matching resources under a modular namespace prefix (e.g., `/api/v1/users/`, `/api/v1/cms/`).
