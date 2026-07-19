# CMS URLs & Router Documentation

This document describes the URL endpoints registered under `backend/apps/cms/urls.py` using Django REST framework's `DefaultRouter`.

---

## 1. REST Endpoints Overview

All endpoints are prefix-mounted under `/api/v1/cms/` via the project's root URL configurations.

| Resource Name | Endpoint URL | ViewSet Class | Supported HTTP Methods |
| :--- | :--- | :--- | :--- |
| **articles** | `/api/v1/cms/articles/` | `ArticleViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **categories** | `/api/v1/cms/categories/` | `CategoryViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **tags** | `/api/v1/cms/tags/` | `TagViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **authors** | `/api/v1/cms/authors/` | `AuthorViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **media** | `/api/v1/cms/media/` | `MediaFileViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **blocks** | `/api/v1/cms/blocks/` | `ContentBlockViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **templates** | `/api/v1/cms/templates/` | `BlockTemplateViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **revisions** | `/api/v1/cms/revisions/` | `RevisionViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **workflow** | `/api/v1/cms/workflow/` | `WorkflowViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **publish** | `/api/v1/cms/publish/` | `PublishScheduleViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **redirects** | `/api/v1/cms/redirects/` | `CMSRedirectViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **audit** | `/api/v1/cms/audit/` | `CMSAuditTrailViewSet` | `GET` (Read-only log view) |
| **search** | `/api/v1/cms/search/` | `CMSSearchViewSet` | `GET` (Public read-only search) |
| **faq** | `/api/v1/cms/faq/` | `FAQViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **reactions** | `/api/v1/cms/reactions/` | `ReactionViewSet` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |

---

## 2. Dynamic Action Endpoints

Several resources expose specialized sub-routes:

- **Article Actions**:
  - `POST /api/v1/cms/articles/{id}/publish/`: Set article visible.
  - `POST /api/v1/cms/articles/{id}/unpublish/`: Set article to draft.
  - `POST /api/v1/cms/articles/{id}/restore/`: Restore soft-deleted articles.
  - `GET /api/v1/cms/articles/{id}/preview/`: Preview raw article format.
  - `POST /api/v1/cms/articles/{id}/schedule/`: Add publishing schedules.
  - `POST /api/v1/cms/articles/bulk-publish/`: Publish list of articles.
  - `POST /api/v1/cms/articles/bulk-delete/`: Soft-delete list of articles.
- **Workflow State Actions**:
  - `POST /api/v1/cms/workflow/{id}/transition/`: Transition state status.
- **Revision History Actions**:
  - `POST /api/v1/cms/revisions/{id}/rollback/`: Rollback content.
