# Enterprise DAM Platform Integration Documentation

This document describes the platform integrations connecting Enterprise Digital Asset Management (DAM) with other BrahmaVidya Galaxy platform elements: Notifications, SEO, Search Indexing, and Auditing.

---

## 1. Notification Event Integration
- **Upload Alert**: When a `MediaFile` is successfully saved, `send_cms_notification_task` dispatches a notification alert to the uploader's user dashboard.
- **Workflow Transitions**: Changing the review approval status in `MediaWorkflow` dispatches review updates directly to the uploader.

---

## 2. Automated SEO Mapping
- **Trigger**: Post-save checks evaluate if `MediaFile.is_public == True`.
- **Action**: Invokes `sync_seo_record` in the SEO app.
- **Outcome**: Index public graphics and sheets directly inside the platform's sitemaps structure.

---

## 3. Search Engine Integration
- **Trigger**: Every save operation on `MediaFile`.
- **Action**: Invokes Celery's `index_single_content_task("media_file", str(id))`.
- **Outcome**: Indexes filename, alt text, and EXIF metadata tags to support search querying.

---

## 4. Audit Trail Integration
- **Trigger**: Save actions on `MediaFile`.
- **Action**: Creates database entries inside `CMSAuditTrail` logging file actions (create, update, delete).
