# Performance Review: Unified Enterprise Search Platform

This document details the search platform's performance optimizations, caching protocols, database indices, and background queue strategies.

---

## 1. Query Caching Protocol

Database search results are cached using MD5 hashes computed over query parameter permutations (query string, index filter, entity type, facets list, and page index).
* **Latency Profile:** Cache hits return results immediately in under 10ms, bypassing database search scans and ranking computations.
* **Expiration Sliding Window:** Cache entries are set to expire after 5 minutes (300 seconds). A scheduled Celery task runs periodically to purge expired cache records and keep the database lightweight.

---

## 2. Database Indexing & Optimizations

Database queries are optimized using structured indices on primary filter columns:
* `SearchDocument`: Indexes are defined on `index` foreign key, `entity_type`, `entity_id` and `is_published`.
* `SearchHistory`: Indexed on `user` and `searched_at`.
* `SearchTerm`: Indexed on `frequency`.
* `SearchCache`: Unique indexed key on `query_key` for high-speed cache lookups.

---

## 3. Asynchronous Offloading

Resource-intensive tasks are processed asynchronously to ensure fast page response times:
* **Background Indexing:** Modifying database records triggers background indexing via **Celery**. This shifts processing load away from client requests, so updates are processed in the background without affecting the user's interface.
* **Periodic Aggregations:** Popular query terms, search analytics tables, and cache updates are computed periodically in the background rather than on every query request.
