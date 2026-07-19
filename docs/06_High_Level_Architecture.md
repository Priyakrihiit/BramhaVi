# High-Level System Architecture - BrahmaVidya Galaxy

## 1. Architectural Principles
BrahmaVidya Galaxy is built upon four fundamental architectural pillars:
1. **Decoupled Data-Driven Rendering**: The frontend React SPA is a stateless visual presentation layer. It possesses no hardcoded menu options, layout blocks, or dynamic content structures. Everything is rendered at runtime based on JSON API specifications.
2. **Unified API Gateway Model**: The client communicates solely with a unified API gateway that handles routing, authentication, authorization checks, and service proxying.
3. **Gateway-Pattern for Vidya AI**: External AI integrations are encapsulated behind a unified backend service. Frontend components do not integrate directly with OpenAI or Google GenAI SDKs; instead, they query the backend's `/api/ai/*` routes.
4. **Relational Database with Document Extensions**: Standard transactional records (users, permissions, course metadata) use highly structured relational tables (3NF), while dynamic structural data (CMS pages, layout blocks) utilize optimized `JSONB` formats.

---

## 2. High-Level System Block Diagram

```
                                +---------------------------+
                                |    Client Web Browser     |
                                | (React Single Page App)   |
                                +---------------------------+
                                              ||
                                              || HTTPS / JSON
                                              \/
                                +---------------------------+
                                |    Nginx Reverse Proxy    |
                                +---------------------------+
                                              ||
                                              || Port 3000 Ingress
                                              \/
                                +---------------------------+
                                |  Unified Express Backend  |
                                |  (Core Router & Gateway)  |
                                +---------------------------+
                                              ||
         +------------------------------------+------------------------------------+
         ||                                   ||                                   ||
         \/                                   v                                    \/
+------------------+                 +------------------+                 +------------------+
|   Auth / Session |                 |   CMS & LMS Core |                 |  Vidya AI Engine |
|   - JWT Validator|                 |   - Menu Manager |                 |  - Gemini Client |
|   - RBAC Checker |                 |   - Layout Parser|                 |  - Syllabus Gen  |
|   - User Store   |                 |   - Course Tree  |                 |  - Quiz Builder  |
+------------------+                 +------------------+                 +------------------+
         ||                                   ||                                   ||
         +------------------------------------+------------------------------------+
                                              ||
                                              \/
                                +---------------------------+
                                |    PostgreSQL Database    |
                                |  (Identity, LMS & Logs)   |
                                +---------------------------+
```

---

## 3. Subsystem Descriptions

### 3.1 Presentation Layer (Frontend SPA)
- **Technology**: React 18+ with Vite, Tailwind CSS, Lucide-React, and Framer Motion.
- **Responsibilities**:
  - Fetch dynamic site parameters (menus, user profiles) upon initialization.
  - Dynamically mount layout widget components based on parsed JSON structures.
  - Manage client routes using React Router and coordinate interactive quiz flows.

### 3.2 Integration & Router Layer (API Gateway)
- **Technology**: Node.js with Express / Django Rest Framework.
- **Responsibilities**:
  - Coordinate security policies (CORS, CSRF, cookie parsers).
  - Inspect requests, validate JWT signatures, and perform RBAC authorization checks.
  - Aggregate API responses and format standardized payloads.

### 3.3 Core Business Logic Layer (Backend Services)
- **CMS Module**: Serves dynamic routing payloads, manages menu trees, and processes layout revisions.
- **LMS Module**: Tracks academic hierarchies (6-tier structures), monitors student lesson completions, and triggers certificate generation ledgers.
- **Vidya AI Gateway**: Wraps the official `@google/genai` TypeScript SDK, supplying structured templates to `gemini-3.5-flash` for deterministic JSON syllabus outputs.
- **Financial Module**: Handles multi-wallet transactions, ledger adjustments, fee-splitting, and balance queries.

### 3.4 Storage & Database Layer
- **Technology**: PostgreSQL.
- **Responsibilities**:
  - Maintain integrity for structural relations via primary/foreign key constraints.
  - Host JSONB document properties to enable fast indexing of dynamic block arrays.
