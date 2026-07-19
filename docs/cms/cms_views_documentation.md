# CMS ViewSets Documentation

This document describes the 17 ModelViewSets added in `backend/apps/cms/views.py` for the BrahmaVidya Galaxy CMS application.

---

## 1. ViewSets Reference

All ViewSets inherit from REST framework's `ModelViewSet` (or `ReadOnlyModelViewSet`) and incorporate:
- `EnterprisePagination`
- Custom Django model-level and query-level filtering
- Advanced object level authorization policies

| ViewSet | Associated Model | Key Features & Actions |
| :--- | :--- | :--- |
| **CategoryViewSet** | `Category` | Hierarchy tree traversal, soft-delete restoration (`restore`). |
| **TagViewSet** | `Tag` | Search by label/slug. |
| **AuthorViewSet** | `Author` | Exposes creator/contributor info. |
| **ArticleViewSet** | `Article` | **Core ViewSet**: Handles publishing workflows (`publish`, `unpublish`), custom rendering previews (`preview`), publication schedules (`schedule`), bulk publishing (`bulk_publish`), and bulk deletion (`bulk_delete`). |
| **MediaFileViewSet** | `MediaFile` | Controls uploads, MIME checks. |
| **ContentBlockViewSet** | `ContentBlock` | Grid orders, page builders layout query filters. |
| **BlockTemplateViewSet** | `BlockTemplate` | Admin-only layouts templates configuration. |
| **PageVersionViewSet** | `PageVersion` | Immutable layouts snapshot list. |
| **RevisionViewSet** | `Revision` | Content rollbacks execution (`rollback`). |
| **WorkflowViewSet** | `WorkflowState` | Performs status lifecycle transitions (`transition`). |
| **WorkflowLogViewSet** | `WorkflowLog` | Immutable trace audits. |
| **PublishScheduleViewSet** | `PublishSchedule` | Auto-publishing time queues. |
| **CMSRedirectViewSet** | `CMSRedirect` | Manager for 301/302 URL redirects. |
| **CMSAuditTrailViewSet** | `CMSAuditTrail` | Read-only listing of all write mutations. |
| **CMSSearchViewSet** | `CMSSearchIndex` | Public search index querying endpoint. |
| **FAQViewSet** | `FAQ` | Categorized QA builder with soft-delete restores. |
| **ReactionViewSet** | `Reaction` | Emoji-based likes/claps manager. |

---

## 2. Advanced Endpoints Details

### A. Publish & Unpublish (`ArticleViewSet`)
- **Action**: `/api/v1/cms/articles/{id}/publish/` & `/api/v1/cms/articles/{id}/unpublish/`
- **Result**: Toggles publication status, updates timestamps, and triggers automated search indices and SEO update hooks.

### B. Scheduling (`ArticleViewSet`)
- **Action**: `/api/v1/cms/articles/{id}/schedule/`
- **Payload**: `{"scheduled_at": "ISO-8601-Timestamp"}`
- **Result**: Queues the article for automated background publishing via `PublishSchedule` model.

### C. Preview (`ArticleViewSet`)
- **Action**: `/api/v1/cms/articles/{id}/preview/`
- **Result**: Returns raw drafts rendering safely packaged inside HTML elements.

### B. Bulk Operations
- **Bulk Publish**: `/api/v1/cms/articles/bulk-publish/` (Accepts list of article IDs to publish in bulk)
- **Bulk Delete**: `/api/v1/cms/articles/bulk-delete/` (Accepts list of article IDs to soft-delete in bulk)
