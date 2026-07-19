# Enterprise DAM System Design Specification (SDS)

## 1. High-Level Design
The system uses a decoupled client-server architecture:
- **Frontend**: Single-Page App built with React, Vite, Lucide icons, and TailwindCSS version 4.
- **Backend API Gateway**: Node.js/Express server proxying calls to Django.
- **Backend Core**: Django REST Framework (DRF) matching Python models, serializers, signals, permissions, and views.

## 2. Platform Integrations
- **Notifications**: Celery background queues dispatcher.
- **SEO Engine**: Hooked sitemap compilations and robots rules updates.
- **Search Indexes**: Sync index tables containing searchable fields.
- **Cache Store**: Cache invalidation triggers via Redis/SQLite.
