# Platform Integrations Manual: Enterprise Analytics Platform

This manual details the integrations of the analytics event trackers across the BrahmaVidya Galaxy platform.

---

## 1. Event Tracking Integrations

All actions, transactions, and state changes automatically create `AnalyticsEvent` records via Django Signals registered in [signals.py](file:///c:/Users/USER/Downloads/bramhavi/backend/apps/analytics/signals.py):

| Target Django Model | Event Classification | Metric Name | Captured Context Data |
|---|---|---|---|
| `users.User` | Session Logins / Logouts | `User Login Success` / `User Logout` | User IP address, user-agent details. |
| `lms.LearningProgress` | Lesson starts and course completions | `Lesson Started` / `Course Completed` | Dynamic UUID of course curriculum nodes. |
| `lms.AssignmentSubmission` | Submitting tasks | `Assignment Submitted` | Assignment ID. |
| `lms.PracticeSession` | Completing questions | `Practice Completed` | Score value. |
| `lms.ExamAttempt` | Exam attempts | `Exam Completed` | Score value, exam ID. |
| `lms.Certificate` | Issuing certificates | `Certificate Issued` | Verified course title. |
| `lms.UserBadge` | Awarding achievements | `Badge Awarded` | Badge name. |
| `cms.ForumPost` | Community threads replies | `Forum Post Created` | Discussion topic ID. |
| `cms.Comment` | Comment additions | `Blog Comment Added` | Post blog ID. |
| `publishing.Book` | Publishing author titles | `Book Published` | Book title, publisher user ID. |
| `wallets.Payment` | Completed payouts / checkouts | `Payment Success` | Payment amounts, gateway code, currency. |
| `search.SearchHistory` | Search queries | `Search Query Run` | Query text value. |
| `notifications.NotificationRecord` | Message dispatches | `Notification Broadcasted` | Delivery channels, alert event name. |
| `seo.SEOPage` | Modifying SEO parameters | `SEO Page Updated` | Page target URL paths. |
| `control_center.MediaFile` | Digital library uploads | `Media File Uploaded` | Media file size. |
| `control_center.AIMessage` | Chat bot prompt usage | `AI Message Logged` | Conversational tokens count, sender role. |

---

## 2. Ingestion Mechanics & Design

To prevent performance drops:
1. **Lazy Class Resolution:** Signals are registered using lazy string references (e.g. `sender="lms.LearningProgress"`), preventing circular import locks during Django initialization.
2. **Telemetry Queue Offloading:** Raw events are handled asynchronously by Celery task workers to keep page load times fast for client operations.
