# CMS Gateway Proxy Documentation

This document describes the API Gateway Proxy configurations implemented in `server.ts` to bridge frontend React requests with the Django REST Framework backend services.

---

## 1. Registered Path Mappings

The Express gateway routes requests targeting `/api/v1/cms/...` directly to the corresponding Django REST Framework resources on `http://127.0.0.1:8000`.

The following paths are added to the centralized `PATH_MAP` directory router:

| Incoming Express Route | Django Destination Target | Purpose |
| :--- | :--- | :--- |
| `/api/v1/cms/articles` | `/api/v1/cms/articles/` | Article listings, draft saves, publish actions. |
| `/api/v1/cms/categories` | `/api/v1/cms/categories/` | Category classifications. |
| `/api/v1/cms/tags` | `/api/v1/cms/tags/` | Tag collections. |
| `/api/v1/cms/workflow` | `/api/v1/cms/workflow/` | Workflow transitions. |
| `/api/v1/cms/media` | `/api/v1/cms/media/` | Media file uploads. |
| `/api/v1/cms/search` | `/api/v1/cms/search/` | Search index queries. |
| `/api/v1/cms/faq` | `/api/v1/cms/faq/` | FAQ mappings. |
| `/api/v1/cms/redirects` | `/api/v1/cms/redirects/` | 301/302 URL redirects. |
| `/api/v1/cms/audit` | `/api/v1/cms/audit/` | Editorial audit trail. |
| `/api/v1/cms/publish` | `/api/v1/cms/publish/` | Scheduled publishing. |
| `/api/v1/cms/revisions` | `/api/v1/cms/revisions/` | Rollbacks and historical lookups. |
| `/api/v1/cms/reactions` | `/api/v1/cms/reactions/` | Article reactions. |
| `/api/v1/cms/authors` | `/api/v1/cms/authors/` | Author profile data. |
| `/api/v1/cms/blocks` | `/api/v1/cms/blocks/` | Page content layout modules. |
| `/api/v1/cms/templates` | `/api/v1/cms/templates/` | Reusable block layouts templates. |

---

## 2. Maintained Security & Operations Controls

### A. JWT Pass-through
- Gateway extracts `Authorization: Bearer <token>` from incoming headers and transparently forwards them to the Django backend to validate permissions.

### B. RBAC & CBAC Enforcement
- Django backend parses authorization parameters, validating roles or Content-Based Access Control filters prior to returning responses.

### C. Rate Limiting
- The gateway's Redis Rate Limiter interceptor applies globally to all `/api/...` sub-paths, preventing brute-force attacks.

### D. Tracing & Logging
- Every forwarded query is logged on the gateway shell process, detailing request paths and proxy status codes.
