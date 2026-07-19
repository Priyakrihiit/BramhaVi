# API Reference Manual: BrahmaVidya Student Portal

**API Protocol**: RESTful (JSON) over HTTPS  
**Authentication**: JWT Token Bearer Headers (`Authorization: Bearer <token>`)

---

## 1. Student Dashboard Endpoints

### 1.1 Fetch Dashboard Overview Context
Fetches the cached, aggregated overview metrics for the active student account.

*   **URL**: `/api/student/dashboard/`
*   **Method**: `GET`
*   **Headers**: 
    *   `Authorization: Bearer <JWT_ACCESS_TOKEN>`
*   **Response Structure (200 OK)**:
```json
{
  "student_info": {
    "email": "test_sprint20_student@example.com",
    "name": "Test Student"
  },
  "metrics": {
    "bookmarks_count": 4,
    "notes_count": 2,
    "goals_completed": 1,
    "active_streak": 5
  },
  "recent_bookmarks": [
    {
      "id": "da314fcf-c0a1-488c-b05d-9da8162d324e",
      "title": "Verification Test Lesson",
      "content_type": "lesson",
      "created_at": "2026-07-13T13:10:20Z"
    }
  ],
  "recent_notes": [
    {
      "id": "9b28f030-0c8e-4a54-8d01-5311b30eb60b",
      "title": "My Notes on Advanced Philosophy",
      "updated_at": "2026-07-13T13:11:15Z"
    }
  ],
  "active_goals": [
    {
      "id": "f512db47-49f3-42cc-a052-19e481c81cb0",
      "title": "Read 5 Spiritual Passages",
      "progress_percentage": 60,
      "status": "in_progress"
    }
  ]
}
```

---

## 2. Bookmarking API

### 2.1 Add Bookmark
*   **URL**: `/api/student/bookmarks/`
*   **Method**: `POST`
*   **Payload**:
```json
{
  "content_type": "lesson",
  "content_id": "da314fcf-c0a1-488c-b05d-9da8162d324e",
  "title": "Verification Test Lesson"
}
```
*   **Response Structure (201 Created)**:
```json
{
  "id": "da314fcf-c0a1-488c-b05d-9da8162d324e",
  "title": "Verification Test Lesson",
  "created_at": "2026-07-13T13:10:20Z"
}
```

### 2.2 Delete Bookmark
*   **URL**: `/api/student/bookmarks/<bookmark_id>/`
*   **Method**: `DELETE`
*   **Response Structure (204 No Content)**: Empty body.

---

## 3. Student Notes API

### 3.1 Create Note
*   **URL**: `/api/student/notes/`
*   **Method**: `POST`
*   **Payload**:
```json
{
  "title": "My Notes on Advanced Philosophy",
  "content": "This is content of the note describing non-dualism and other core ideas."
}
```
*   **Response Structure (201 Created)**:
```json
{
  "id": "9b28f030-0c8e-4a54-8d01-5311b30eb60b",
  "title": "My Notes on Advanced Philosophy",
  "created_at": "2026-07-13T13:11:15Z"
}
```
*   *Side Effect*: This asynchronous write automatically schedules index tasks on celery to ensure note contents are globally discoverable within search bars.
