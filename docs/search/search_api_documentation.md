# BrahmaVidya Search: API Reference Manual

This document details the RESTful API endpoints for the Unified Enterprise Search Platform in BrahmaVidya Galaxy, mounted under `/api/v1/search/`.

---

## 1. API Endpoints Catalog

| Endpoint | Method | Permission | Purpose |
|---|---|---|---|
| `/api/v1/search/query/` | `GET` | AllowAny | Execute global and module search queries. |
| `/api/v1/search/autocomplete/` | `GET` | AllowAny | Prefix-matching typeahead word strings. |
| `/api/v1/search/suggestions/` | `GET` | AllowAny | Complete suggestion phrases objects list. |
| `/api/v1/search/click/` | `POST` | AllowAny | Log click positions to update CTR metrics. |
| `/api/v1/search/history/` | `GET` | IsAuthenticated | Retrieve recent searches history for user. |
| `/api/v1/search/history/<id>/` | `DELETE` | IsAuthenticated | Clear a specific search history entry. |
| `/api/v1/search/popular/` | `GET` | AllowAny | Retrieve top queried search terms. |
| `/api/v1/search/ranking/` | `GET`/`POST`/`DELETE` | IsAdminOrReadOnly | Manage custom boost and pin configurations. |
| `/api/v1/search/analytics/` | `GET` | IsAdminUser | Query keyword CTR metrics performance list. |
| `/api/v1/search/facets/` | `GET`/`POST`/`DELETE` | IsAdminOrReadOnly | Configuration metadata registers for facets. |
| `/api/v1/search/synonyms/` | `GET`/`POST`/`DELETE` | IsAdminOrReadOnly | Register query synonyms expansion charts. |

---

## 2. Search Query API (`GET /api/v1/search/query/`)

Performs text search checks over all indexed document categories. Returns results, aggregations, and suggestions.

### Parameters
* **`q`** (String, required): Normal keyword text (e.g. `python`).
* **`index`** (String, optional): Scoped index name (e.g. `courses`, `articles`).
* **`entity_type`** (String, optional): Model class name filter (e.g. `Article`, `CourseStructure`).
* **`facets`** (String, optional): Comma-separated list of metadata attributes to aggregate counts.
* **`page`** (Integer, optional): Page index value.

### Sample Request
`GET /api/v1/search/query/?q=python&index=courses&facets=level`

### Sample Response (HTTP 200 OK)
```json
{
  "results": [
    {
      "id": "7bf3b680-2a25-4a3b-8401-69095d9f9f17",
      "index_name": "courses",
      "entity_type": "CourseStructure",
      "entity_id": "3af4b680-2a25-4a3b-8401-69095d9f9f17",
      "title": "Introduction to Python Programming",
      "excerpt": "Learn variables, syntax, loops and dictionaries.",
      "body": "This curriculum course covers everything from simple variables to object-oriented constructs.",
      "tags": "python coding basic",
      "categories": "LMS",
      "author_name": "Admin",
      "url_path": "/lms/courses/python-intro",
      "is_published": true,
      "published_at": "2026-07-12T09:42:00Z",
      "meta_data": {
        "level": "Beginner",
        "duration_hours": 12
      },
      "relevance_score": 15.0
    }
  ],
  "count": 1,
  "next": null,
  "previous": null,
  "facets": {
    "Level": {
      "Beginner": 1,
      "Advanced": 0
    }
  },
  "spelling_suggestion": null
}
```

---

## 3. Autocomplete API (`GET /api/v1/search/autocomplete/`)

Returns instant typeahead suggestion strings based on prefix match.

### Parameters
* **`q`** (String, required): Current query prefix characters.

### Sample Request
`GET /api/v1/search/autocomplete/?q=py`

### Sample Response (HTTP 200 OK)
```json
{
  "suggestions": [
    "python programming",
    "python variables",
    "pycharm tutorial"
  ]
}
```

---

## 4. Search Click API (`POST /api/v1/search/click/`)

Captures result interactions to evaluate click-through rate statistics.

### Request Body JSON
* **`history_id`** (UUID, optional): Search history log tracking code.
* **`document_id`** (UUID, required): The target search document id.
* **`position`** (Integer, required): Rank placement index of clicked result (starts at 1).

### Sample Request
`POST /api/v1/search/click/`
```json
{
  "history_id": "174b1880-2a25-4a3b-8401-69095d9f9f17",
  "document_id": "7bf3b680-2a25-4a3b-8401-69095d9f9f17",
  "position": 1
}
```

### Sample Response (HTTP 201 Created)
```json
{
  "status": "recorded",
  "id": "1d8f1880-2a25-4a3b-8401-69095d9f9f17"
}
```
