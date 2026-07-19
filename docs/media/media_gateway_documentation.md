# Enterprise DAM Gateway Integration Documentation

This document describes the API gateway proxy configurations connecting client-side requests with backend DAM services.

---

## 1. Gateway Routing Mappings (`server.ts`)

Express routes proxy target paths to the Django REST backend, preserving request contexts, authentication tokens, and headers:

| Client Gateway Route | Proxied DRF Route | Auth Scope |
| :--- | :--- | :--- |
| `/api/v1/cms/folders/` | `/api/v1/cms/folders/` | JWT Pass-through |
| `/api/v1/cms/collections/` | `/api/v1/cms/collections/` | JWT Pass-through |
| `/api/v1/cms/media-versions/` | `/api/v1/cms/media-versions/` | JWT Pass-through |
| `/api/v1/cms/media-shares/` | `/api/v1/cms/media-shares/` | JWT Pass-through |
| `/api/v1/cms/media-audits/` | `/api/v1/cms/media-audits/` | JWT Pass-through |
| `/api/v1/cms/media-favorites/` | `/api/v1/cms/media-favorites/` | JWT Pass-through |
| `/api/v1/cms/media-comments/` | `/api/v1/cms/media-comments/` | JWT Pass-through |
| `/api/v1/cms/media-search/` | `/api/v1/cms/media-search/` | JWT Pass-through |
| `/api/v1/cms/media-workflows/` | `/api/v1/cms/media-workflows/` | JWT Pass-through |

---

## 2. Gateway Security Policy

- **Token Forwarding**: Authorization headers (`Bearer <token>`) are automatically preserved and forwarded to verify signatures on DRF handlers.
- **Rate Limiting**: Integrated Express gateway rate limiters monitor incoming route counters.
- **Trace Auditing**: Correlation ID tags (`request-id`) map logs across client-to-backend calls.
