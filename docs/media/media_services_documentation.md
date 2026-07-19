# Enterprise DAM Services & Tasks Documentation

This document describes the services, Celery tasks, and signal automations powering the Enterprise Digital Asset Management (DAM) subsystem.

---

## 1. Service Layer (`services.py`)

The business logic is wrapped in static service classes, keeping views thin and reusable:

- **`MediaUploadService`**: Handles validations (extensions, size, virus checks), auto-categorizes file type (`image`, `video`, etc.), and creates `MediaFile` DB entities.
- **`ThumbnailService`**: Spawns async Celery tasks for small, medium, and large thumbnails.
- **`ImageOptimizationService`**: Triggers async compression converting image inputs to optimized WebP.
- **`VideoConversionService`**: Transcodes video uploads to web-friendly MP4 (H.264/AAC).
- **`StorageService`**: Abstraction resolving paths and public urls.
- **`SearchService`**: Performs indexed title searches.
- **`PermissionService`**: Sets folder and file access privileges.
- **`AuditService`**: Logs file uploads, downloads, edits, and deletions.
- **`FavoriteService`**: Toggles file bookmarks for users.
- **`DownloadService`**: Increments counters and logs download histories.

---

## 2. Asynchronous Tasks (`tasks.py`)

Executed in Celery task queues:

- **`generate_thumbnail_task`**: Generates thumbnail sizes.
- **`optimize_image_task`**: Compresses image assets.
- **`extract_metadata_task`**: Extracts EXIF data and updates `MediaMetadata`.
- **`media_cleanup_task`**: Deletes physical files when soft-deleted objects are permanently purged.
- **`scan_file_for_virus_task`**: Integrates antivirus scanner hooks.

---

## 3. Signal Automation Engine (`signals.py`)

Hooked into Django ORM post-save:

- **Upload Handlers**: Save signals on `MediaFile` automatically fire antivirus scans, metadata extractions, and thumbnail generation pipelines.
- **Audit Logs**: Generates entries inside `CMSAuditTrail` for all media uploads/edits.
- **Cache Invalidation**: Automatically clears cache directories on file modifications.
