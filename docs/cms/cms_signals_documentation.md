# CMS Signals & Platforms Integration Documentation

This document describes the event signals implemented in `backend/apps/cms/signals.py` for the BrahmaVidya Galaxy CMS application. These signals automate critical operations such as audit trail creation, notification dispatches, SEO metadata updates, search index updates, revision histories, workflow states, and media cleanup.

---

## 1. Overview of Signal Types & Receivers

Four types of signals are utilized to monitor lifecycle events on CMS models:

1. **`pre_save`**: Captures state snapshots of updated database records before mutations occur. Used for auditing changes (`before_state`).
2. **`post_save`**: Automates active hooks immediately after creation or modification.
3. **`post_delete`**: Performs cascading cleanups, search de-indexing, physical file deletion, cache invalidations, and logs deletion events.
4. **`m2m_changed`**: Captures many-to-many relationship changes (e.g. category/tag assignments on articles) to update search indexes and audits.

---

## 2. Supported Automations & Integrations

The signals module coordinates and automatically triggers integrations across **10 distinct areas**:

| Automation | Target Models | Action Triggered | Details / Integrations |
| :--- | :--- | :--- | :--- |
| **Notification** | `WorkflowState` | Send workflow state notification | Integrates with the **existing Notification Platform** via Celery `send_cms_notification_task`. Triggers push/email/SMS alerts to authors when articles are approved/rejected/published. |
| **SEO** | `Article`, `Blog`, `Page` | Auto-generate/sync SEO entries | Integrates with the **existing SEO Platform** via `sync_seo_for_content_task` and `sync_seo_record` to maintain `SEOPage` metrics. |
| **Search Index** | `Article`, `Blog` | Re-index or remove from index | Calls Celery `index_single_content_task` to compute search vectors and `SearchIndexService.remove_from_index` on deletion. |
| **Audit Trail** | `Page`, `Article`, `Blog`, `Comment`, `MediaFile`, `WorkflowState` | Track mutations | Records changes into `CMSAuditTrail` including `before_state`, `after_state`, request IDs, and actors. |
| **Revision** | `Article`, `Blog` | Auto-save content snapshot | Invokes `RevisionService.create_revision` on `post_save` to record sequential content snap-shots. |
| **Workflow** | `Article` | Auto-provision workflow | Creates draft `WorkflowState` for new Articles via `WorkflowService.get_or_create_workflow`. |
| **Version History** | `Page` | Auto-version layout | Triggers `VersionService.create_version` on `post_save` of layouts to save page structure histories. |
| **Analytics** | All CMS models | Refresh stats counters | Queues `refresh_analytics_task` to keep performance metrics up to date. |
| **Cache** | `Page`, `Article`, `Blog` | Clear/refresh active cache | Invalidates menu trees (`global_navigation_menu_tree`) and runs Celery `refresh_cms_cache_task`. |
| **Media Cleanup** | `MediaFile` | Physical file deletion | Deletes the underlying file from the filesystem/storage backend on record delete (`post_delete`). |

---

## 3. Implementation Details

- **Circular Dependency Protection**: Model and service imports are isolated within the signal receiver functions.
- **Asynchronous Execution**: High-latency tasks (e.g., SEO metadata generations, notification dispatching, search indexing, analytics runs) are offloaded to Celery task queues.
- **Audit Traceability**: Integrated with `middleware.request_id` to capture `X-Request-ID` from thread locals, linking HTTP requests directly to database audits.
