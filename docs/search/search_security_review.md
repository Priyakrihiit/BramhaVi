# Security Review: Unified Enterprise Search Platform

This document reviews the security architecture, authentication controls, and data sanitization rules for the search platform.

---

## 1. Authentication & Role-Based Access Controls (RBAC)

### Gateway Session Propagation
The Node/Express gateway handles incoming API calls and passes the client's `Authorization: Bearer <JWT>` header directly to the Django REST framework endpoints.
* Unauthenticated users can search public courses, articles, books, and blogs.
* Authenticated users can access their search history logs. History endpoints enforce ownership checks: users can only view or delete their own search histories.
* Staff/Admin users are granted permission to mutate system-wide settings, configure search facets, register synonym sets, and edit document relevance scores.

### Permission-Aware Filtering
The `PermissionSearchService` filters results returned by database queries before rendering them to users. If a matching document is marked private, it is filtered out of the results list unless the user is the owner of the document or possesses the required administrative permissions.

---

## 2. Input Sanitization & Attack Prevention

### SQL Injection Prevention
All query filters, autocomplete checks, and administrative updates are performed using **Django ORM queries**. Django parameters are escaped automatically by SQLite driver bindings, preventing raw SQL injections.

### Cross-Site Scripting (XSS) Prevention
Text values returned in search result records (titles, excerpts, descriptions) are serialized to JSON in views and output safely in React components using standard interpolation (curly brackets), which escapes HTML entities.

### Rate Limiting
Search endpoints are protected by the global sliding window rate limiter in `server.ts`. This middleware prevents denial-of-service (DoS) attempts, search scrapers, and brute-force query attacks.
* Allowed queries are restricted to 100 requests per minute per IP/Token.
* If thresholds are exceeded, the gateway intercepts requests immediately and returns `HTTP 429 Too Many Requests`.
