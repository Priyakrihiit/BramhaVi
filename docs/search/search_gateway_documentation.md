# BrahmaVidya Search: Gateway Integration Guide

This document details the configuration, security delegation, and telemetry features of the Node/Express API Gateway for the Unified Search Platform.

---

## 1. Gateway Routing Architecture

All client requests sent to `/api/v1/search/...` are intercepted by the Express server router inside [server.ts](file:///c:/Users/USER/Downloads/bramhavi/server.ts) and dynamically proxied to the Django REST framework application on port `8000`.

### Path Mapping
The prefix mapping has been registered in the centralized gateway configuration registry:
```typescript
PATH_MAP: {
  ...
  '/api/v1/search': '/api/v1/search/',
}
```

* **Client Path Example:** `/api/v1/search/query/?q=python`
* **Proxied Backend Path:** `http://127.0.0.1:8000/api/v1/search/query/?q=python`

---

## 2. Telemetry and Security Preservation

### 1. Authentication & RBAC (JWT Propagation)
The gateway copies client session credentials (`Authorization: Bearer <token>`) from incoming requests and propagates them directly to Django headers.
Django receives the token, validates the JWT signature, resolves the user profile, and applies role-based access checks (e.g. `IsAuthenticated`, `IsAdminOrReadOnly`).

### 2. Request Tracing
Tracing headers are forwarded dynamically from Node to Django:
* `x-request-id`
* `x-correlation-id`
* `x-trace-id`
* `x-span-id`

This ensures that requests can be correlated across the Node gateway logs and Django backend logs during root-cause analytics.

### 3. Rate Limiting
All search endpoints benefit from the global Express rate limiter middleware.
* Identifies clients by IP or bearer token signature.
* Implements sliding window limiter (default: 100 requests per minute) backed by Redis (or in-memory fallback).
* Returns `HTTP 429 Too Many Requests` if thresholds are exceeded.

### 4. Logging & Diagnostics
The gateway logs all proxies requests to stdout:
`[GATEWAY INFO] Proxying GET request to Django: /api/v1/search/query/?q=python`
This logs telemetry diagnostics for all search queries, histories, click analytics, and override updates.
