# API Gateway Specifications Manual: Enterprise Analytics Platform

This document describes the gateway configuration, session headers proxy mappings, rate limiting, and request tracing logs for the analytics APIs.

---

## 1. Gateway Proxy Mapping

The Node/Express gateway intercepts API calls and proxies them to the Django REST framework endpoints:

* **Client Access Route:** `/api/v1/analytics/*`
* **Target Proxy Destination:** `http://127.0.0.1:8000/api/v1/analytics/*`
* **Resolution Method:** Slices incoming paths matching the `/api/v1/analytics` prefix key inside `server.ts` and forwards headers and query parameters dynamically to Django.

---

## 2. Request Tracing & Context Propagation

To enable end-to-end request tracing:
1. **Trace Header Propagation:** The gateway forwards the `X-Request-ID` header. If missing, it generates a random UUID and propagates it to Django.
2. **Context Headers:** simple JWT tokens (passed in the `Authorization: Bearer <JWT>` header) are forwarded directly to the backend to support RBAC and CBAC verification checks.
3. **Request Logs:** Proxied requests are logged to stdout by the gateway:
   `[GATEWAY INFO] Proxying POST request to Django: /api/v1/analytics/events/collect/`

---

## 3. Rate Limiting & Protection

All analytics and telemetry collector routes are protected by the gateway's rate-limiter middleware:
* **Limits:** Restricted to 100 requests per minute per IP/token.
* **Throttling Action:** If a client script floods the event collector, the gateway intercepts requests immediately, returning `HTTP 429 Too Many Requests` without touching the backend database.
