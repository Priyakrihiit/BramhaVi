# Database Schema & Index Design: BrahmaVidya Student Portal

**System Entity Relationship & Index Guide**  
**Database Engines**: SQLite (Local / Development), PostgreSQL (Production)

---

## 1. Core Database Schema & Entities

The `apps.student.models` module defines several high-performance entities:

### 1.1 Bookmark
Tracks student bookmarks of various portal items.
*   `id`: UUID (Primary Key)
*   `student`: ForeignKey to User (Cascade on delete)
*   `content_type`: CharField (e.g., 'lesson', 'tutorial')
*   `content_id`: UUID (Reference to the bookmarked item)
*   `title`: CharField
*   `created_at`: DateTimeField

### 1.2 StudentNote
Personal study notebooks managed by students.
*   `id`: UUID (Primary Key)
*   `student`: ForeignKey to User
*   `title`: CharField
*   `content`: TextField (Supports HTML/Markdown markdown data)
*   `created_at` / `updated_at`: DateTimeField

### 1.3 StudyGoal
Tracks personalized, time-bound progress goals.
*   `id`: UUID (Primary Key)
*   `student`: ForeignKey to User
*   `title`: CharField
*   `target_hours`: DecimalField
*   `progress_percentage`: IntegerField (0 to 100)
*   `status`: CharField (pending, in_progress, achieved)
*   `target_date`: DateField

### 1.4 StudentAchievement
Links earned badges to student accounts.
*   `id`: UUID (Primary Key)
*   `student`: ForeignKey to User
*   `achievement`: ForeignKey to Achievement
*   `unlocked_at`: DateTimeField

### 1.5 LearningReminder
Schedule for push alerts.
*   `id`: UUID (Primary Key)
*   `student`: ForeignKey to User
*   `remind_at`: DateTimeField
*   `status`: CharField (pending, sent, cancelled)

---

## 2. Index Optimization Guidelines
To handle intensive high-frequency dashboards, the following custom indices are defined:

```python
indexes = [
    # Fast filtering of user-specific reminders scheduled for active dispatches
    models.Index(fields=["student", "remind_at", "status"], name="idx_rem_student_date_status"),
    # Fast lookup of active global schedules across the portal
    models.Index(fields=["remind_at", "status"], name="idx_reminder_global_schedule"),
]
```

### ⚠️ Constraint Notice
Django / PostgreSQL enforces a strict **30-character length boundary** on index names. Names exceeding this threshold (e.g., `idx_reminder_student_date_status`) will raise schema creation compiler faults. Thus, abbreviated patterns like `idx_rem_student_date_status` are strictly required.
