# CMS API Documentation

## 1. REST Endpoints Mappings

| Method | Endpoint | Description | Auth Scope |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/cms/articles/` | Retrieve articles list. | Authenticated |
| **POST** | `/api/v1/cms/articles/` | Create a new article. | Writer / Creator |
| **POST** | `/api/v1/cms/articles/{id}/publish/` | Publish article immediately. | Publisher / Admin |
| **POST** | `/api/v1/cms/articles/{id}/schedule/` | Schedule publication. | Publisher / Admin |
| **POST** | `/api/v1/cms/workflow/{id}/transition/` | Advance review state. | Assigned Reviewer |
| **POST** | `/api/v1/cms/revisions/{id}/rollback/` | Restore revision save point. | Owner / Admin |

## 2. Sample Request Payload (Publish Scheduling)
```json
{
  "scheduled_at": "2026-07-20T10:00:00Z"
}
```
