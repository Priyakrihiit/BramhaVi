# CMS Database Design

## 1. Database Schema Mappings

```mermaid
erDiagram
    ARTICLE ||--o{ CATEGORY : categorizes
    ARTICLE ||--o{ TAG : labels
    ARTICLE ||--|| WORKFLOW_STATE : tracks
    ARTICLE ||--o{ REVISION : logs
    ARTICLE ||--o{ PUBLISH_SCHEDULE : plans
    MEDIA_FILE ||--o{ TAG : labels
```

## 2. Table Schemas
- **cms_article**: Stores uuid, title, body, status, author, is_published, and timestamps.
- **cms_category**: Stores hierarchy tree elements (name, slug, parent, display_order).
- **cms_tag**: Stores name, slug, usage_count.
- **cms_workflowstate**: Stores current state status, assigned reviewer, and target article.
- **cms_publishschedule**: Stores target publication date, type, id, and schedule executor.
- **cms_mediafile**: Stores uploader user, caption, alt_text, and path locations.
