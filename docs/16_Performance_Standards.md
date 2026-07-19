# Performance Standards - BrahmaVidya Galaxy

## 1. Metric Targets & Latency Budgets
To guarantee excellent learning outcomes, BrahmaVidya Galaxy sets strict performance thresholds across our platforms:

| Metric Class | Target Threshold | Method of Measurement |
| :--- | :--- | :--- |
| **First Contentful Paint (FCP)**| < 0.8 seconds | Lighthouse Audit / Chrome Web Vitals |
| **Largest Contentful Paint (LCP)**| < 1.5 seconds | Lighthouse Audit / Chrome Web Vitals |
| **Interaction to Next Paint (INP)**| < 80 milliseconds | Real-User Performance Monitoring (RUM) |
| **API Response (CMS Layouts)** | < 150 milliseconds | APM Trace Logs (Mean under load) |
| **API Response (AI Gen Gateway)**| < 3.0 seconds | APM Trace Logs (Gemini Stream completion) |

---

## 2. Server-Side Caching Policies
We implement hierarchical caching strategies to bypass redundant database operations:
- **Layer 1: In-Memory / Redis Caching**: Active layouts, configuration values, and navigation menus are held in high-speed cache. If layouts do not change, GET requests bypass PostgreSQL.
- **Layer 2: CDN Edge Caching**: Dynamic page files and public marketing views are cached at global edge CDNs (e.g., Cloudflare, Cloud CDN) with `stale-while-revalidate` caching headers.
- **Cache Eviction**: Modifying layouts or reordering menus in the Control Center instantly fires eviction hooks, clearing the cache.

---

## 3. Front-End Optimizations
- **Code Bundling**: The React core leverages Vite to split bundles by view and dynamic route.
- **Asset Formats**: Images, icons, and illustrations are loaded as lightweight vector SVGs or optimized Next-Gen formats (WebP / AVIF) with appropriate browser caching parameters.
- **SVG Lucide Integration**: The `DynamicIcon` helper only loads icons on demand to keep bundle sizes minimal.

---

## 4. Query Compilations & Optimizations
- **N+1 Avoidance**: ORM operations querying hierarchical LMS courses must preload child references (Django `select_related` or Express pre-joins) to prevent excessive database queries.
- **Execution Analyzers**: Backend telemetry scripts periodically log queries exceeding 500ms, triggering automated optimizations.
