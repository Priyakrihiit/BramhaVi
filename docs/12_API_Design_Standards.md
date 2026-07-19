# API Design Standards - BrahmaVidya Galaxy

## 1. REST Endpoints Naming Conventions
All API endpoints must follow clean RESTful patterns. Routes must represent resources in plural forms, and actions are mapped to specific HTTP verbs:

| HTTP Verb | Path | Action | Payload / Return Code |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/pages` | Fetch all dynamic pages | Array of pages, `200 OK` |
| **GET** | `/api/pages/:id` | Fetch specific page configuration | Single page JSON, `200 OK` |
| **POST** | `/api/pages` | Create a new dynamic layout page | Created page JSON, `21 Created` |
| **PUT** | `/api/pages/:id` | Update complete page settings | Modified page JSON, `200 OK` |
| **DELETE** | `/api/pages/:id` | Remove a dynamic page | `{ success: true }`, `200 OK` |

---

## 2. API Versioning Strategy
API routes must include explicit prefix designations to allow updates without breaking clients:
- Current release: `/api/v1/pages`
- Legacy integrations may bind to specified legacy prefixes if necessary, preventing disruption to active clients.

---

## 3. Standardized Error Payloads
API failures must return structured JSON outputs carrying informative context:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMS",
    "message": "The provided parameters failed validation constraints.",
    "details": [
      "slug: Slug contains invalid URL characters.",
      "seoTitle: Title must not exceed 60 characters."
    ]
  }
}
```

### 3.1 Common Error Classifiers
- `UNAUTHORIZED`: Sessions lacking valid access tokens or expired sessions.
- `FORBIDDEN`: Valid sessions trying to execute actions they do not hold privileges to perform.
- `NOT_FOUND`: Querying resources that do not exist.
- `RESOURCE_CONFLICT`: Trying to register duplicates of unique fields (e.g., matching slugs or emails).
- `RATE_LIMIT_EXCEEDED`: Requests exceeding permitted frequencies.

---

## 4. Query Sorting & Pagination
GET routes serving lists (such as `course_structures` or transaction ledgers) must support standardised query parameters to optimize data transfer:
- `page`: Page index (default: `1`).
- `limit`: Maximum records to return (default: `20`, ceiling: `100`).
- `sort`: Sorting field with sign directives (e.g., `sort=-created_at` for descending orders).

Standard paginated responses are encapsulated as follows:
```json
{
  "success": true,
  "data": [...],
  "meta": {
    "totalRecords": 154,
    "page": 1,
    "totalPages": 8,
    "limit": 20
  }
}
```
This guarantees scalable data transfer patterns.
