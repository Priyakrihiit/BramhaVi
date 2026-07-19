# CMS Architecture Specification

## 1. Architectural Map

```mermaid
graph TD
    A[React Client UI] -->|REST / JWT| B[Express API Gateway]
    B -->|Proxy| C[Django REST Framework]
    C -->|ORM| D[(SQLite Database)]
    C -->|Signals| E[Notifications Engine]
    C -->|Signals| F[SEO Optimizer]
    C -->|Signals| G[Search Indexer]
```

## 2. Key Modules
- **Client Side**: Uses `cmsApi.ts` for unified communications. React dispatcher routes requests.
- **API Gateway**: Uses `server.ts` path mappings for proxy routing.
- **Django Core**: Models configure DB constraints. Serializers enforce validation. Custom permissions restrict routes.
