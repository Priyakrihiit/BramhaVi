# BrahmaVidya Galaxy — Live Classes Phase 2 Database Models & Migrations Report

This document reports the implementation, migration execution, and verification of the database layer for the **Live Classes Platform** (Sprint 22).

---

## 1. Implemented Database Models

All database structures have been registered and verified inside the `apps.lms` and `apps.teacher` modules:

| Model Name | Table Name | Purpose | Primary Key | Relations |
| :--- | :--- | :--- | :---: | :--- |
| **[LiveClass](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L573)** (Extended) | `live_classes` | Links live streams to course syllabus modules and teachers. Includes dynamic state mapping. | UUID | ForeignKey to `CourseStructure`, `users.User` |
| **[LiveSession](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L614)** | `live_sessions` | Tracks duration, timestamps, and isActive stream intervals. | UUID | ForeignKey to `LiveClass` |
| **[MeetingParticipant](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L628)** | `live_meeting_participants`| Tracks connected users and presenter/attendee role maps. | UUID | ForeignKey to `LiveClass`, `users.User` |
| **[Recording](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L643)** | `live_recordings` | Stores MP4 and stream archive files and sizes. | UUID | ForeignKey to `LiveClass` |
| **[Whiteboard](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L657)** | `live_whiteboards` | Stores serialized coordinate drawing command logs. | UUID | ForeignKey to `LiveClass` |
| **[ChatMessage](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L669)** | `live_chat_messages` | In-class chat logs. | UUID | ForeignKey to `LiveClass`, `users.User` |
| **[Poll](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L683)** | `live_polls` | Class quiz prompts created by presenters. | UUID | ForeignKey to `LiveClass`, `users.User` |
| **[PollOption](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L698)** | `live_poll_options` | Available option selections mapping to a Poll. | UUID | ForeignKey to `Poll` |
| **[PollVote](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L710)** | `live_poll_votes` | Maps specific voter selections to option targets. | UUID | ForeignKey to `Poll`, `PollOption`, `users.User` |
| **[BreakoutRoom](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L723)** | `live_breakout_rooms` | Sub-channels partitions configuration mapping. | UUID | ForeignKey to `LiveClass` |
| **[CalendarEvent](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L736)** | `live_calendar_events` | Synchronized schedule alerts. | UUID | ForeignKey to `users.User`, `LiveClass` |
| **[Reminder](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L751)** | `live_reminders` | Launch reminder cues for users. | UUID | ForeignKey to `users.User`, `LiveClass` |
| **[MeetingAnalytics](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py#L765)** | `live_meeting_analytics` | Consolidated analytics reports (concurrent users, watch duration). | UUID | ForeignKey to `LiveClass` |
| **[Attendance](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/teacher/models.py#L123)** (Teacher Portal) | `attendance` | Main attendance record logging synchronous presence mapping live_class join/leave events. | UUID | ForeignKey to `LiveClass`, `users.User` |

---

## 2. Migration Details & Execution Logs

### 2.1. Migration Validation
*   Command: `python backend/manage.py makemigrations`
*   Result: `No changes detected`
*   Reason: All models are fully migrated under migration file `backend/apps/lms/migrations/0006_liveclass_meeting_id_liveclass_status_breakoutroom_and_more.py`.

### 2.2. Migration Application
*   Command: `python backend/manage.py migrate`
*   Result: `No migrations to apply.`
*   Reason: The SQLite/Postgres database contains all current model tables fully created and synced to the schema dependencies.

### 2.3. System Integrity Checks
*   Command: `python backend/manage.py check`
*   Result: `System check identified no issues (0 silenced).`
*   Status: **SUCCESS**
