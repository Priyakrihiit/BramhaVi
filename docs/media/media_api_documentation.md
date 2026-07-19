# Enterprise DAM API Documentation

This document describes the REST API endpoints, HTTP methods, authorization levels, and request payloads for the Enterprise Digital Asset Management (DAM) subsystem.

---

## 1. REST Endpoints Mappings

| Method | Endpoint | Description | Auth Scope |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/cms/folders/` | List all active folders. | Authenticated |
| **POST** | `/api/v1/cms/folders/` | Create a new folder. | Authenticated |
| **GET** | `/api/v1/cms/collections/` | List collections. | Authenticated |
| **POST** | `/api/v1/cms/collections/` | Create a new logical collection. | Authenticated |
| **POST** | `/api/v1/cms/media/{id}/favorite/` | Bookmark/favorite an asset. | Authenticated |
| **POST** | `/api/v1/cms/media/{id}/download/` | Log download telemetry. | Authenticated |
| **POST** | `/api/v1/cms/media/{id}/share/` | Share a file with another user. | Owner / Admin |
| **GET** | `/api/v1/cms/media-versions/` | List all file version histories. | Authenticated |
| **GET** | `/api/v1/cms/media-audits/` | View asset audit histories. | Owner / Admin |
| **GET** | `/api/v1/cms/media-search/` | Query matching metadata/tags. | Authenticated |

---

## 2. Sample Request Payload & Response Examples

### A. Sharing an Asset (`POST /api/v1/cms/media/{id}/share/`)
- **Request Payload**:
```json
{
  "shared_with_email": "teacher@brahmavidya.edu"
}
```
- **Response Example (201 Created)**:
```json
{
  "detail": "Shared successfully.",
  "share_id": "403dbfe1-5320-42be-bac3-8bf229db5da5"
}
```

### B. Favoriting an Asset (`POST /api/v1/cms/media/{id}/favorite/`)
- **Response Example (200 OK)**:
```json
{
  "detail": "Favorited"
}
```
