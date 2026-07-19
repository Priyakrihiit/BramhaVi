# BrahmaVidya Search: Platform Integration Manual

This document details the cross-module integrations and automated background indexing hooks for the Unified Search Platform.

---

## 1. Integrated Platform Modules

The search indexing service processes data feeds across the entire ecosystem:

| Module | Data Source Type | Target Entity / Collection | Index Category |
|---|---|---|---|
| **LMS** | Django Database | `CourseStructure` | `courses` |
| **CMS** | Django Database | `Article`, `Blog`, `Page`, `Tutorial`, `FAQ` | `articles`, `blogs`, `pages`, `tutorials`, `faqs` |
| **Media** | Django Database | `MediaFile` | `media` |
| **SEO** | Django Database | `SEOPage` | `seo` |
| **Notifications**| Django Database | `Announcement`, `NotificationRecord` | `notifications` |
| **Marketplace** | Django Database | `Book` (status == 'PUBLISHED') | `marketplace` |
| **Publishing** | Django Database | `Book` | `marketplace` |
| **Users** | Django Database | `UserProfile`, `Organization` | `users` |
| **Jobs** | JSON File Store | `jobs` collection | `jobs` |
| **Resume** | JSON File Store | `resumes` collection | `resumes` |
| **Portfolio** | JSON File Store | `websites` collection | `portfolios` |
| **AI** | JSON File Store | `conversations`, `prompts` collections | `ai` |

---

## 2. Automated Real-Time Indexing Flow

To ensure search results are kept fresh, index updates are triggered automatically on content changes:

### 1. Database-Backed Models (Django Signals)
We bind Django's post-save (`post_save`) and post-delete (`post_delete`) signals in [signals.py](file:///c:/Users/USER/Downloads/bramhavi/backend/apps/search/signals.py) for all SQL models:
* On save: Triggers `index_document_task.delay(entity_type, entity_id)` to index the updated record in the background.
* On delete: Triggers `delete_document_task.delay(entity_type, entity_id)` to remove it from index.

### 2. File-Backed JSON Stores (CRUD Wrappers Hooks)
JSON document modifications bypass Django's ORM model triggers. For these, we inject direct hooks into:
* **Portfolios/Resumes/Jobs:** Inside [portfolio_store.py](file:///c:/Users/USER/Downloads/bramhavi/backend/apps/portfolio/portfolio_store.py) save/delete wrappers, calling `index_portfolio_item_task.delay(collection_name, item_id)`.
* **AI Conversations/Prompts:** Inside [ai_store.py](file:///c:/Users/USER/Downloads/bramhavi/backend/apps/ai/ai_store.py) save/delete wrappers, calling `index_ai_item_task.delay(collection_name, item_id)`.

---

## 3. Telemetry and Async Processing

All indexing operations are queued to **Celery background tasks** via Redis brokers:
1. Tasks are offloaded instantly from client HTTP requests to avoid loading request latency.
2. If the backend fails or goes offline, tasks are automatically retried.
3. The periodic job `reindex_all_task` runs on a regular scheduler to build/sync all indexes from scratch.
