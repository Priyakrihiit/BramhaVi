# Sprint 20 — Phase 6 Validation Report (API Gateway & Proxy Integration)

**Date:** 2026-07-13  
**Sprint:** 20 — Student Portal & Learning Dashboard  
**Phase:** 6 — API Gateway Routing, JWT Forwarding, Rate Limiting, and Tracing  
**Auditor:** AI Platform Engineering  
**Global Status:** ⚠️ Substantially Complete (Production Hardening Recommended)

---

## 1. Gateway Overview

The application utilizes a custom Node.js Express server (`/server.ts`) acting as an API Gateway and Reverse Proxy to route incoming `/api/*` traffic to a downstream Django REST Framework (DRF) backend running in the background on `http://127.0.0.1:8000`.

Below is the detailed design validation across all required audit parameters.

---

## 2. Parameter-by-Parameter Review

### A. PATH_MAP
* **Status:**  Passed
* **Analysis:** The `PATH_MAP` constant provides a comprehensive lookup mapping client-side request patterns directly to Django REST Framework URL namespaces.
* **Mappings Present:**
  * Authentication: `/api/auth/login` ➔ `/api/v1/users/users/login/` and `/api/auth/me` ➔ `/api/v1/users/users/me/`
  * CMS / DAM Gateways: Mappings for pages, menus, articles, categories, tags, workflow, DAM folders, collections, etc.
  * LMS: `/api/courses` ➔ `/api/v1/lms/courses/`, `/api/certificates` ➔ `/api/v1/lms/certificates/`, exams, and live classes.
  * Control Center: Settings, activities, tasks, and administrative dashboard metrics.
* **Verification:** The lookup successfully registers all core platform services.

### B. Proxy Routes (Dynamic Middleware)
* **Status:**  Passed
* **Analysis:** The Express gateway intercepts routing requests on the `/api` prefix using custom-built matching middleware.
* **Matching Logic:**
  1. **Exact Matching:** If the incoming `req.baseUrl + req.path` matches an exact key in `PATH_MAP`, it proxies directly with query parameters preserved.
  2. **Prefix-Prefix Dynamic Matching:** If an exact match isn't found, the middleware iterates through the `PATH_MAP` keys. If the path starts with a mapped key followed by a slash (e.g., `/api/courses/1/`), it strips the prefix, appends the remainder to the mapped Django target path, and preserves the query string.
  3. **Fallback:** If no match occurs, it yields control (`next()`) to local Express-based mock databases and simulation routes.
* **Risk/Improvement:** The custom regex/prefix crawler works but could be vulnerable to trailing-slash discrepancies between the React client and DRF endpoints. Standardizing trailing slashes on prefix substitution is recommended.

### C. Headers
* **Status:**  Passed
* **Analysis:** The `proxyToDjango` helper sets a default `Content-Type: application/json` and selectively passes relevant headers.
* **Observed Headers:**
  * Automatically sets standard content types.
  * Preserves tracing identifiers (see Tracing section).
  * Forwards standard JWT/Token bearer structures.

### D. Cookies
* **Status:** ⚠️ Missing / Not Proxied
* **Analysis:** Inspecting the `proxyToDjango` method reveals that **cookies are not forwarded** to the Django backend.
  ```typescript
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (req.headers.authorization) {
    headers['Authorization'] = req.headers.authorization;
  }
  ```
* **Impact:** If any downstream Django views or session middleware rely on standard HTTP-only cookies (e.g., `csrftoken` or standard session IDs), these requests will fail or miss validation. 
* **Recommendation:** If the application scales to use cookie-based auth or needs DRF CSRF cookie compliance, modify `proxyToDjango` to forward the `Cookie` header:
  ```typescript
  if (req.headers.cookie) {
    headers['Cookie'] = req.headers.cookie as string;
  }
  ```

### E. JWT Forwarding
* **Status:**  Passed
* **Analysis:** Token authentication is successfully forwarded. If an incoming client request carries an `Authorization` header, the proxy injects it directly into the outgoing `fetch` options:
  ```typescript
  if (req.headers.authorization) {
    headers['Authorization'] = req.headers.authorization;
  }
  ```
* **Mechanism:** This ensures that JWT bearer tokens are transparently passed to Django's JWT authentication backends, preserving user session context and RBAC/CBAC claims.

### F. Rate Limiting
* **Status:**  Passed (Excellent Design)
* **Analysis:** Features a multi-tiered rate limiting middleware (`rateLimiter`) connected to a Redis backend, with a robust fallback mechanism.
* **Redis Mode:** Uses a Redis sorted set (`ZSET`) to implement an accurate sliding-window log. It trims stale logs with `zRemRangeByScore`, adds the current timestamp, and reads the window count via `zCard` inside a Redis transaction pipeline (`redisClient.multi()`).
* **Memory Fallback Mode:** If Redis is down or unavailable during bootstrap, it falls back gracefully to a standard Node-local `Map` (`ipRequestCounts`) tracking counts in simple window buckets to prevent server crashes.
* **Token-Aware Identification:** Instead of rate-limiting purely by IP address (which harms users behind NATs/VPNs), the middleware inspects the `Authorization` bearer token and uses the JWT string as the identifier if available.

### G. Tracing
* **Status:**  Passed
* **Analysis:** Promotes transaction traceability by capturing and forwarding standard correlation identifiers.
* **Implementation:**
  ```typescript
  const traceHeaders = ['x-request-id', 'x-correlation-id', 'x-trace-id', 'x-span-id'];
  traceHeaders.forEach(h => {
    if (req.headers[h]) {
      headers[h] = req.headers[h] as string;
    }
  });
  ```
* **Benefit:** Allows backend engineers to trace transactions from the browser through the gateway into Django logs under a single unified correlation/trace ID.

---

## 3. Platform Integrations Verification

* **LMS Integration:** API paths like `/api/courses`, `/api/certificates`, and `/api/exams` proxy seamlessly to Django's LMS database schema.
* **Analytics/Audit Pipeline:** Access requests to `/api/v1/analytics` map straight to Django analytics logging endpoints.
* **Notifications Engine:** `/api/notifications/*` routing paths support notification CRUD proxying.
* **Search Engine:** Dynamic searches on `/api/v1/search` and `/api/v1/cms/media-search` route requests to Django indexers.
* **AI (Vidya AI):** While `/api/gemini/tutor` and `/api/ai/chat` use server-side Node SDK logic to query Gemini models directly, student history retrieval routes to the Django backend.

---

## 4. Summary & Action Plan

To fully harden Phase 6 for production:
1. **Cookie Forwarding:** Add forwarding for the `Cookie` header in `proxyToDjango` to ensure CSRF and cookie-based authorization robustness.
2. **Trailing Slash Normalization:** Ensure the dynamic path prefix matcher gracefully handles cases where matching URLs end with or without trailing slashes.
