# Sprint 20 — Phase 3 Validation Report (Student Dashboard)

**Date:** 2026-07-13  
**Sprint:** 20 — Student Portal & Learning Dashboard  
**Phase:** 3 — Backend Services, Selectors, Validators, Filters, Tasks, and Signals  
**Auditor:** AI Platform Engineering  
**Global Status:** ❌ Missing (Not Implemented)

---

## 1. File-by-File Review

As of the current audit, there are no physical files for Phase 3 within `/backend/apps/student/` other than `apps.py` and `models.py`. Therefore, all required Phase 3 files are currently **Missing**.

Below is the detailed review of each expected file, identifying what must be implemented, what is currently missing, and potential integration points.

### A. services.py
* **Status:** ❌ Missing
* **Implemented Classes:** None
* **Implemented Methods:** None
* **Missing Classes & Methods:**
  * `LearningHistoryService`:
    * `log_lesson_visit(user, lesson_id: int) -> LearningHistory`: Records a lesson access event and triggers LRU recently viewed updates.
  * `ContinueLearningService`:
    * `update_progress_pointer(user, course_id: int, lesson_id: int, completion_percentage: float) -> ContinueLearning`: Creates or updates a learner's progress resume bookmark.
  * `BookmarkService`:
    * `toggle_bookmark(user, content_type: str, object_id: int) -> Bookmark`: Favorites/unfavorites a lesson, course, or book.
  * `NoteService`:
    * `save_lesson_note(user, lesson_id: int, content: str) -> StudentNote`: Saves or updates markdown format notes taken during a lecture.
  * `GoalService`:
    * `create_study_goal(user, title: str, target_hours: float, deadline: datetime) -> StudyGoal`: Sets a personal learning schedule threshold.
    * `track_goal_progress(user, goal_id: int) -> float`: Evaluates and returns target goal achievement rate.
  * `SessionService`:
    * `start_study_session(user, goal_id: int = None) -> StudySession`: Initializes a focused, timed session timer.
    * `end_study_session(session_id: int, actual_minutes: int) -> StudySession`: Stops timer and logs progress.
  * `StreakService`:
    * `update_login_streak(user) -> LearningStreak`: Validates and increments consecutive daily login loops.
    * `decay_streaks() -> None`: Daily cron check to reset active streaks on expired boundaries.
  * `AchievementService`:
    * `evaluate_achievements(user) -> List[Achievement]`: Scans user metrics and awards badges.
* **Broken Imports:** None (File is missing)
* **Duplicate Code:** None
* **Unused Code:** None

---

### B. selectors.py
* **Status:** ❌ Missing
* **Implemented Classes:** None
* **Implemented Methods:** None
* **Missing Classes & Methods:**
  * `DashboardSelector`:
    * `get_student_dashboard_context(user) -> dict`: Compiles active streaks, weekly stats, progress bookmarks, and recent lessons into a single payload.
  * `ProgressSelector`:
    * `get_weekly_metrics(user) -> List[dict]`: Fetches aggregated learning metrics for Recharts rendering.
    * `get_monthly_timeline(user) -> List[dict]`: Returns MonthlyProgress trends.
  * `BookmarkSelector`:
    * `get_user_bookmarks(user, filter_type: str = None) -> QuerySet`: Fetches lists of user bookmarks.
  * `NoteSelector`:
    * `get_notes_by_course(user, course_id: int) -> QuerySet`: Retrieves Markdown notes grouped by lecture block.
  * `CalendarSelector`:
    * `get_events_range(user, start_date: date, end_date: date) -> List[dict]`: Compiles personalized events, scheduled exams, and live classes.
* **Broken Imports:** None (File is missing)
* **Duplicate Code:** None
* **Unused Code:** None

---

### C. validators.py
* **Status:** ❌ Missing
* **Implemented Classes:** None
* **Implemented Methods:** None
* **Missing Classes & Methods:**
  * `GoalValidator`:
    * `validate_goal_dates(start_date: datetime, deadline: datetime) -> None`: Asserts deadlines occur in the future.
  * `NoteValidator`:
    * `validate_note_length(content: str) -> None`: Validates safety thresholds (e.g. max 10,000 characters).
  * `SessionValidator`:
    * `validate_session_active(user) -> None`: Prevents starting parallel timed study blocks.
* **Broken Imports:** None (File is missing)
* **Duplicate Code:** None
* **Unused Code:** None

---

### D. filters.py
* **Status:** ❌ Missing
* **Implemented Classes:** None
* **Implemented Methods:** None
* **Missing Classes & Methods:**
  * `BookmarkFilter` (Django-filter class): Filters favorites by entity_type (`course`, `lesson`, `book`) or date added.
  * `StudentNoteFilter`: Groups notes by `course_id`, `is_shared`, or full-text keywords.
  * `LearningHistoryFilter`: Scans visits within customized date ranges or specific programs.
* **Broken Imports:** None (File is missing)
* **Duplicate Code:** None
* **Unused Code:** None

---

### E. tasks.py
* **Status:** ❌ Missing
* **Implemented Classes:** None
* **Implemented Methods:** None
* **Missing Classes & Methods:**
  * `decay_inactive_streaks_task` (Celery background cron): Runs nightly at 00:00 UTC to evaluate streak thresholds and reset non-consecutive accounts.
  * `compile_weekly_progress_digest_task`: Compiles weekly analytics indices into email templates and schedules notifications.
  * `generate_study_reminders_task`: Delivers notifications to students missing daily goals.
* **Broken Imports:** None (File is missing)
* **Duplicate Code:** None
* **Unused Code:** None

---

### F. signals.py
* **Status:** ❌ Missing
* **Implemented Classes:** None
* **Implemented Methods:** None
* **Missing Classes & Methods:**
  * `on_lesson_completed_handler` (Signal receiver): Triggers automatically on LMS completion events to advance progress, update achievements, and increment streak points.
  * `on_session_saved_handler`: Captures finalized session events to recalculate daily, weekly, and monthly indices in real-time.
  * `on_achievement_unlocked_handler`: Logs activities and delivers in-app toast/push announcements.
* **Broken Imports:** None (File is missing)
* **Duplicate Code:** None
* **Unused Code:** None

---

## 2. Platform Integrations Audit (Target Architectures)

The table below describes the target architecture connections required for Phase 3 and how they connect to current subsystems:

| Target System | Integration Mode | Expected Data Flow / Actions | Status |
| :--- | :--- | :--- | :--- |
| **LMS Module** | Signal Triggers / Models | Core enrollment updates from `lms.models` trigger progress advances in `student.models.ContinueLearning`. | ❌ Missing |
| **Analytics** | Service Triggers | Completed study sessions and progress thresholds dispatch events to `apps.analytics.services` to populate enterprise tables. | ❌ Missing |
| **Notifications** | Signal Listeners | Earned streaks and unlocked achievements dispatch tasks to the Notification system to send in-app alerts and digest emails. | ❌ Missing |
| **Search** | Model Observers | Key user notes marked as "public" or custom bookmark metadata index updates must refresh Elasticsearch or database indices. | ❌ Missing |
| **AI (Vidya AI)** | Service Hooks | Selectors extract notes and learning histories as a prompt context vector to deliver tailored student recommendations. | ❌ Missing |
| **Redis** | Client Store | Cached active sessions, lockouts, and live login stats to ensure sub-millisecond response rates. | ❌ Missing |
| **Celery** | Task Brokers | Offloads periodic calculations (streak resets, reminder dispatches, weekly summaries) to background queue networks. | ❌ Missing |

---

## 3. Summary & Action Plan

Currently, **Phase 3 is 0% implemented**. 

### Immediate Action Plan to Unlock Phase 3:
1. **Initialize Phase 3 Files:** Create the physical files under `/backend/apps/student/`:
   * `services.py`
   * `selectors.py`
   * `validators.py`
   * `filters.py`
   * `tasks.py`
   * `signals.py`
2. **Draft Models Migration:** Run `makemigrations` and `migrate` for the 15 models defined in Phase 2 to ensure database schema compatibility before coding services.
3. **Register Signals:** Register `signals.py` inside the `ready()` block of `apps.py` to orchestrate event triggers.
