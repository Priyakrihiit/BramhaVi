# Feature Walkthrough Guide: BrahmaVidya Student Portal

**System Integration Validation Scenarios**  

---

## 1. Scenario: Bookmarking and Cache Invalidation
This scenario verifies that saving a bookmark successfully invalidates cached student dashboard data, assuring immediate UI updates.

### Step-by-Step Validation:
1.  **Access the Dashboard**: Send a `GET` request to `/api/student/dashboard/`.
    *   *System Action*: The server queries the database, compiles the dashboard context, caches it under the key `dashboard_context_<user_id>`, and returns the JSON payload.
2.  **Add a New Bookmark**: Send a `POST` request to `/api/student/bookmarks/` with your bookmark payload.
    *   *System Action*: The bookmark is created, which fires the `on_bookmark_saved` signal. This immediately deletes the cached dashboard key (`dashboard_context_<user_id>`).
3.  **Verify Cache Invalidation**: Send another `GET` request to `/api/student/dashboard/`.
    *   *System Action*: The server detects a cache miss, pulls the newly updated bookmark list from the database, caches the new context, and returns the updated dashboard JSON.

---

## 2. Scenario: Note Creation & Search Index Syncing
This scenario verifies that saving a study note successfully triggers asynchronous search indexing via Celery background tasks.

### Step-by-Step Validation:
1.  **Create a Study Note**: Send a `POST` request to `/api/student/notes/` containing your note's content.
    *   *System Action*: The note is committed to the database, which triggers the `on_note_saved` signal.
2.  **Verify Asynchronous Indexing**: The signal schedules an indexing task via `index_document_task.delay("StudentNote", note.id)`.
    *   *System Action*: A Celery background worker picks up the task, parses the note content, and updates the search index asynchronously.
3.  **Confirm Search Discoverability**: Query the global search bar on the portal for keywords contained in your note.
    *   *System Action*: The search engine returns your note in the search results.

---

## 3. Scenario: AI Tutoring Grounded Context Updates
This scenario verifies that student progress (such as completing a goal or earning a badge) is successfully shared with the Vidya AI Companion.

### Step-by-Step Validation:
1.  **Complete a Study Goal**: Complete a study goal on your dashboard (progress reaches 100%).
    *   *System Action*: The goal's state changes to `achieved`, firing the `on_goal_saved` signal.
2.  **Trace context injection**: The signal calls the grounding helper function `update_ai_conversation_context(user, description)`.
    *   *System Action*: The system creates a context-grounding message within the student's active `AIConversation`.
3.  **Verify AI Awareness**: Open a chat session with the Vidya AI Companion and ask about your recent achievements.
    *   *System Action*: The AI tutor recognizes your completed goal and congratulates you on your progress.
