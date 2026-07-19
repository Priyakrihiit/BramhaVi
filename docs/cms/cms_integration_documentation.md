# CMS Platform Integration Documentation

This document describes the automated integration mechanisms connecting BrahmaVidya Galaxy's CMS with existing system-wide platforms: the Notification Service, the SEO Optimizer, and the Search Index Engine.

---

## 1. Notification Triggers

All notification events are dispatched asynchronously using Celery task queues when models undergo state changes:

| Event Trigger | Monitored Condition | Dispatched Notification | Target User |
| :--- | :--- | :--- | :--- |
| **Article Published** | `is_published` transitions `False -> True` on `Article` post-save. | *"Article Published 🎉"* | Content Author |
| **Page Published** | `is_published` transitions `False -> True` on `Page` post-save. | *"Page Published 🌐"* | Layout Creator |
| **Workflow Approved** | `status` transitions to `"approved"` on `WorkflowState`. | *"Content Approved ✅"* | Content Author |
| **Workflow Rejected** | `status` transitions to `"rejected"` on `WorkflowState`. | *"Content Rejected ❌"* | Content Author |
| **Scheduled Publish** | `status` transitions to `"completed"` on `PublishSchedule`. | *"Scheduled Publish Complete ⏰"* | Scheduled Publisher |

---

## 2. Automated SEO Generation

- **Hook**: Triggered on `Article`, `Blog`, or `Page` saved.
- **Action**: Django signals queue async Celery tasks targeting the SEO module.
- **Outcome**: Auto-builds `SEOMeta` parameters (dynamic meta descriptions, tags, and keywords), and adds indices to sitemaps (`sitemap.xml`) and web robots files (`robots.txt`).

---

## 3. Automated Search Indexing

- **Hook**: Triggered on `Article` or `Blog` post-save and category/tag associations changes (`m2m_changed`).
- **Action**: Invokes `index_single_content_task` in the search service.
- **Outcome**: Parses markdown bodies and headers, building matching records in the `CMSSearchIndex` query database.
