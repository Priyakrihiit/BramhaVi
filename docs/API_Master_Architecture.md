# BrahmaVidya Galaxy: API Master Architecture Specification
## Phase 3: Enterprise Data Exchange & Integration Blueprint

This document defines the complete enterprise API master architecture for **BrahmaVidya Galaxy**. Governed by **Python, Django, and Django REST Framework (DRF)**, this architecture establishes the interface standards, security mechanisms, lifecycle guidelines, and precise contracts across all service layers.

---

## Part 1: Core API Design Standards

### 1.1 API Versioning Strategy
- **URI-Based Versioning**: To prevent disruption to client layers (React), BrahmaVidya Galaxy strictly enforces path-based versioning.
  - *Standard*: `/api/v1/...`
- **Deprecation Pathway**: Any modification introducing breaking changes triggers the creation of a new version path (e.g., `/api/v2/...`). Legacy clients are supported according to the API Deprecation Strategy defined in Section 1.20.

### 1.2 URL Naming Standards
- **Case Format**: All URL paths, including endpoints, query variables, and path parameters, must be written in **lowercase spinal-case** (kebab-case):
  - *Correct*: `/api/v1/course-structures/active-enrollments`
  - *Incorrect*: `/api/v1/courseStructures/activeEnrollments` or `/api/v1/course_structures/active_enrollments`

### 1.3 REST Resource Naming
- **Nouns Only (Pluralized)**: Paths must utilize plural nouns representing resource collections:
  - *Correct*: `/api/v1/users`, `/api/v1/certificates`
  - *Incorrect*: `/api/v1/getUser`, `/api/v1/certificate`
- **Sub-resources**: Hierarchy is expressed through nested endpoints matching logical dependencies:
  - *Format*: `/api/v1/courses/<uuid:course_id>/chapters/<uuid:chapter_id>/lessons`

### 1.4 Authentication Flow
BrahmaVidya Galaxy relies on stateless token-based authentication using **JSON Web Tokens (JWT)**. No session state is retained in memory on the Django backend.
- **Header Structure**: All authenticated requests must include the token inside the HTTP `Authorization` header:
  ```http
  Authorization: Bearer <access_token>
  ```
- **Login Endpoint**: Clients post credentials to `/api/v1/auth/token/` to receive a secure token pair.

### 1.5 Authorization Flow (RBAC)
- **Role-Based Access Control (RBAC)**: Enforced via Django REST Framework permissions classes.
- **Granular Privilege Matrix**: The user's role references permission codenames (e.g., `lms:course:publish`, `cms:pages:delete`).
- **Endpoint Gating**: DRF Views or ViewSets dynamically cross-reference the JWT's claims or query the active user database to gate endpoints using custom permission classes:
  ```python
  permission_classes = [IsAuthenticated, HasPrivilege('cms:pages:create')]
  ```

### 1.6 JWT Lifecycle
- **Access Token**:
  - **Lifetime**: 15 minutes.
  - **Payload Claims**:
    - `sub`: User ID (UUID)
    - `role`: Assigned Role Code (e.g., `TEACHER`)
    - `email`: User Email
    - `exp`: Expiry epoch
    - `jti`: Token identifier (for revocation checks)
- **Refresh Token**:
  - **Lifetime**: 7 days.
  - **Payload Claims**: Minimal claims to refresh access (`sub`, `exp`, `jti`).

### 1.7 Refresh Token Strategy
To preserve a frictionless user experience on the React client:
1. **Rotation Pattern**: Whenever a refresh token is submitted to `/api/v1/auth/token/refresh/` to obtain a new access token, a **new refresh token** is also returned, and the old one is blacklisted.
2. **Revocation List**: Blacklisted refresh token identifiers (`jti`) are stored in **Redis** with an expiration time matching the remainder of the token's lifetime. Checks are performed at the middleware layer.

### 1.8 Error Response Standards
All API errors return a standard JSON structure with HTTP error codes (400-599).
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CLASSIFIER_STRING",
    "message": "A clear, human-readable summary of the issue.",
    "details": [
      "field_name: Specific validation details or diagnostic context."
    ]
  }
}
```

### 1.9 Validation Standards
- **Schema Validation**: DRF Serializers validate input constraints, returning a `400 Bad Request` with field-level details.
- **Payload Sanitization**: Custom validator layers strip dangerous scripting tags (XSS prevention) and normalize inputs (trimming whitespaces, lowercasing email values).

### 1.10 Pagination Strategy
- **Cursor Pagination**: Enforced for high-frequency or infinite scrolling collections (e.g., Activity Logs, Community Forum posts) to prevent database offset lag.
- **Offset/Limit Pagination**: Enforced for static collections (e.g., Courses list, CMS Pages admin list).
- **Default Parameters**: `page=1`, `limit=20` (max ceiling value `100`).
- **Response Shape**:
  ```json
  {
    "success": true,
    "data": [],
    "meta": {
      "total_records": 128,
      "page": 1,
      "total_pages": 7,
      "limit": 20
    }
  }
  ```

### 1.11 Filtering Strategy
GET lists support robust filters passed via URL query parameters:
- **Direct Matching**: `/api/v1/courses?status=published`
- **Dynamic Comparators (DRF Filtering)**:
  - `/api/v1/payments?amount__gte=100.00`
  - `/api/v1/certificates?issued_at__gte=2026-01-01`

### 1.12 Search Strategy
Search query structures utilize a standard `q` parameter mapped to PostgreSQL full-text indexing or indexing fields:
- *URL format*: `/api/v1/blogs?q=brahmavidya+meditation`

### 1.13 Sorting Strategy
Sorting utilizes a single `sort` parameter. Descending values are marked with a leading minus `-` sign:
- *Ascending*: `/api/v1/transactions?sort=created_at`
- *Descending*: `/api/v1/transactions?sort=-created_at`

### 1.14 Rate Limiting Strategy
To safeguard resources and prevent brute-force attacks, rate-limiting is implemented at the Nginx and Django (DRF) layers:
- **Public endpoints (Auth/Token)**: Max 5 requests/minute per IP address.
- **Authenticated APIs**: Max 100 requests/minute per User ID.
- **Failure Status**: Returns `429 Too Many Requests`.

### 1.15 API Throttling
In addition to standard rate limits, systemic API throttling kicks in during excessive peak loads:
- **Search and RAG operations**: Limit heavy operations (e.g., dynamic Vidya AI prompts) to 10 per minute per account to contain model execution overhead.

### 1.16 File Upload Strategy
- **Two-Step Direct Uploads (Presigned URLs)**:
  1. Client sends a POST request with asset metadata (file name, mime type) to `/api/v1/media/upload-urls/`.
  2. The server authenticates user privileges, issues a secure Cloud Storage presigned URL, and registers a pending transaction row in the `media_attachments` table.
  3. The React client uploads the raw binary directly to Object Storage via a PUT request. This bypasses Django server performance constraints entirely.

### 1.17 Media Serving Strategy
- **Public Assets**: Static images, default avatar blocks, and theme visual elements are served directly via Cloud Content Delivery Networks (CDNs).
- **Protected Course Media**: Premium lecture videos, PDF manuals, and course project documents use short-lived presigned URLs generated on-demand only after validating active enrollments.

### 1.18 Bulk Operations
To reduce network latency, endpoints that manage collections allow bulk changes through custom routes:
- **Endpoint**: `/api/v1/navigation-menus/bulk-reorder`
- **Payload**:
  ```json
  {
    "items": [
      { "id": "uuid-1", "display_order": 0 },
      { "id": "uuid-2", "display_order": 1 }
    ]
  }
  ```

### 1.19 Idempotency
All mutating calls (POST, PUT, DELETE) must yield predictable, identical states if executed repeatedly.
- **Idempotency Headers**: Critical transaction routes (such as payment processing or ledger deductions) require an `Idempotency-Key: <UUIDv4>` header.
- **Backend Isolation**: Django checks Redis for the key:
  - If the operation is completed, Nginx returns the cached response.
  - If the operation is currently running, Nginx blocks the duplicate request with a `409 Conflict`.

### 1.20 API Deprecation Strategy
- **Sunset Header**: Legacy endpoints scheduled for removal transmit a standard HTTP `Sunset` and `Deprecation` header on every call:
  ```http
  Deprecation: @1799193600
  Sunset: Tue, 01 Dec 2026 23:59:59 GMT
  ```
- **Cycle Duration**: Deprecated routes must survive a minimum of 180 days before actual network deactivation.

### 1.21 API Documentation Strategy
- **Dynamic OpenAPI Specs**: The Django REST Framework exposes an auto-generated, interactive OpenAPI v3 specification.
- **Interactive UI Panel**: The endpoints `/api/docs/` (Swagger UI) and `/api/redoc/` (Redoc) serve as the development interfaces for developers.

### 1.22 Webhook Architecture
- **Outbound Webhooks**: BrahmaVidya Galaxy can broadcast event alerts to external platforms (e.g., student portals, enterprise identity logs).
- **Validation Signatures**: Payload deliveries include a signature header constructed using HMAC-SHA256 hashed with a shared secret:
  ```http
  X-BrahmaVidya-Signature: <hmac_sha256_hash>
  ```

### 1.23 API Security Standards
- **TLS Protection**: Strict TLS v1.3 configuration.
- **Header Hardening**:
  ```http
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Content-Security-Policy: default-src 'self'
  ```
- **CORS Constraints**: Origin locks mapping strictly to authorized domains (development vs production domains).

### 1.24 Response Format Standards
The API enforces a standard envelope structure for consistency:
- **Success Format**:
  ```json
  {
    "success": true,
    "data": {} -- Object, Array, or Value payload
  }
  ```

### 1.25 HTTP Status Code Standards
- `200 OK`: Successful read, update, or delete.
- `201 Created`: Successful creation.
- `400 Bad Request`: Validation failure.
- `401 Unauthorized`: Missing/invalid JWT token.
- `403 Forbidden`: Insufficient RBAC permissions.
- `404 Not Found`: Target resource not found.
- `409 Conflict`: Uniqueness lock or racing idempotent keys.
- `429 Too Many Requests`: Rate limit hit.
- `500 Internal Server Error`: Generic application failure.

---

## Part 2: Endpoint Design Contracts

---

### 2.1 Authentication & RBAC

#### `POST /api/v1/auth/token/`
*Generate secure JWT token pair.*
- **Authentication**: Public
- **Request Payload**:
  ```json
  {
    "email": "student@brahmavidya.com",
    "password": "SecurePassword123"
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "access": "eyJhbGciOi...",
      "refresh": "eyJhbGciOi...",
      "expires_in_seconds": 900
    }
  }
  ```

#### `POST /api/v1/auth/token/refresh/`
*Rotate refresh and access tokens.*
- **Authentication**: Public
- **Request Payload**:
  ```json
  {
    "refresh": "eyJhbGciOi..."
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "access": "eyJhbGciOi...",
      "refresh": "eyJhbGciOi..."
    }
  }
  ```

#### `GET /api/v1/auth/me/`
*Fetch current authenticated user profile and roles details.*
- **Authentication**: Bearer Token
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "user_id": "a9b8c7d6-e5f4-3c2b-1a09-876543210fed",
      "email": "student@brahmavidya.com",
      "role": "STUDENT",
      "permissions": ["lms:courses:read", "lms:lessons:view", "community:comments:create"],
      "profile": {
        "first_name": "Siddharth",
        "last_name": "Gautama",
        "avatar_url": "https://cdn.brahmavidya.com/avatars/siddharth.jpg"
      }
    }
  }
  ```

---

### 2.2 User Directory

#### `GET /api/v1/users`
*Administrative list of users, with pagination and roles filtering.*
- **Authentication**: Bearer Token (RBAC Check: `users:list`)
- **Query Parameters**: `page=1`, `limit=20`, `role=TEACHER`
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "23a4b5c6-d7e8-f9a0-b1c2-3d4e5f6a7b8c",
        "email": "guru.ashram@brahmavidya.com",
        "role": "TEACHER",
        "is_active": true,
        "created_at": "2026-01-15T08:00:00Z"
      }
    ],
    "meta": {
      "total_records": 48,
      "page": 1,
      "total_pages": 3,
      "limit": 20
    }
  }
  ```

---

### 2.3 Content Management System (CMS)

#### `GET /api/v1/cms/pages`
*Retrieve dynamic CMS pages.*
- **Authentication**: Public (Internal logic returns active pages only)
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "e0e1e2e3-f4f5-a6a7-b8b9-c0c1c2c3c4c5",
        "slug": "home-welcome",
        "title": "Welcome to BrahmaVidya Galaxy",
        "layout_data": {
          "blocks": [
            { "type": "hero", "heading": "Achieve Enlightenment", "action_url": "/courses" }
          ]
        },
        "is_published": true
      }
    ]
  }
  ```

#### `POST /api/v1/cms/pages`
*Create new layout configuration.*
- **Authentication**: Bearer Token (RBAC Check: `cms:pages:create`)
- **Request Payload**:
  ```json
  {
    "slug": "advanced-meditation-retreat",
    "title": "Advanced Meditation Retreat",
    "layout_data": {
      "blocks": [
        { "type": "banner", "image": "https://cdn.com/retreat.jpg" }
      ]
    },
    "is_published": false
  }
  ```
- **Response Payload (201 Created)**:
  ```json
  {
    "success": true,
    "data": {
      "id": "d0d1d2d3-f4f5-a6a7-b8b9-c0c1c2c3c4c5",
      "slug": "advanced-meditation-retreat",
      "title": "Advanced Meditation Retreat",
      "is_published": false,
      "created_at": "2026-07-06T10:30:00Z"
    }
  }
  ```

#### `GET /api/v1/cms/navigation-menus`
*Dynamic header lists, supporting RBAC visibility constraints.*
- **Authentication**: Public
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        "label": "Control Center",
        "url": "/admin/dashboard",
        "icon": "LayoutDashboard",
        "display_order": 0,
        "children": []
      }
    ]
  }
  ```

#### `GET /api/v1/cms/tutorials`
*Retrieve quick tutorials.*
- **Authentication**: Public
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "7f8g9h0i-1j2k-3l4m-5n6o-7p8q9r0s1t2u",
        "title": "How to Start Vidya AI Sessions",
        "slug": "start-vidya-ai",
        "content": "# Guided Steps\n1. Log into your dashboard\n2. Click the star icon...",
        "created_at": "2026-06-12T14:20:00Z"
      }
    ]
  }
  ```

---

### 2.4 Learning Management System (LMS)

#### `GET /api/v1/lms/programs`
*Dynamic root program catalogs.*
- **Authentication**: Public
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "11111111-2222-3333-4444-555555555555",
        "node_type": "PROGRAM",
        "title": "BrahmaVidya Foundation Series",
        "slug": "foundation-series",
        "description": "The primary paths to inner peace.",
        "display_order": 0
      }
    ]
  }
  ```

#### `GET /api/v1/lms/courses`
*Dynamic lists of child courses, subjects, chapters, topics, subtopics, and lessons using unified `course_structures` CTE lookup.*
- **Authentication**: Public
- **Query Parameters**: `parent_id=11111111-2222-3333-4444-555555555555`
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "c9c8c7c6-b5b4-a3a2-9190-876543210fed",
        "parent_id": "11111111-2222-3333-4444-555555555555",
        "node_type": "SUBJECT",
        "title": "Mindfulness & Breathing",
        "slug": "mindfulness-breathing",
        "display_order": 0,
        "metadata": {
          "estimated_hours": 12
        }
      }
    ]
  }
  ```

#### `GET /api/v1/lms/lessons/<uuid:lesson_id>`
*Lesson details, protected by user course enrollment check.*
- **Authentication**: Bearer Token
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "id": "99999999-8888-7777-6666-555555555555",
      "node_type": "LESSON",
      "title": "Breathing Technique Level 1",
      "slug": "breathing-level-1",
      "description": "Guided breathing patterns.",
      "metadata": {
        "video_url": "https://protected-media.brahmavidya.com/video/level1.mp4",
        "duration_seconds": 1200,
        "is_interactive": true
      }
    }
  }
  ```

#### `POST /api/v1/lms/learning-progress`
*Register student lesson/topic progress.*
- **Authentication**: Bearer Token (RBAC Check: `lms:progress:write`)
- **Request Payload**:
  ```json
  {
    "node_id": "99999999-8888-7777-6666-555555555555",
    "progress_percentage": 100.00,
    "is_completed": true
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "id": "e0e1e2e3-f4f5-a6a7-b8b9-c0c1c2c3c4c5",
      "progress_percentage": 100.00,
      "is_completed": true,
      "completed_at": "2026-07-06T10:45:12Z"
    }
  }
  ```

#### `POST /api/v1/lms/practice-sessions/submit`
*Submit student practice results.*
- **Authentication**: Bearer Token (RBAC Check: `lms:practice:submit`)
- **Request Payload**:
  ```json
  {
    "course_id": "c9c8c7c6-b5b4-a3a2-9190-876543210fed",
    "answers": [
      { "question_id": "q1", "selected_options": ["opt_a"] }
    ]
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "score": 90.00,
      "passed": true,
      "feedback_summary": "Excellent understanding."
    }
  }
  ```

#### `POST /api/v1/lms/assignments/<uuid:assignment_id>/submit`
*Submit lesson assignments.*
- **Authentication**: Bearer Token (RBAC Check: `lms:assignment:submit`)
- **Request Payload**:
  ```json
  {
    "submission_payload": {
      "notes": "Here is my reflection essay.",
      "attachment_url": "https://cdn.brahmavidya.com/attachments/student_essay.pdf"
    }
  }
  ```
- **Response Payload (201 Created)**:
  ```json
  {
    "success": true,
    "data": {
      "submission_id": "a9b8c7d6-e5f4-3c2b-1a09-876543210fed",
      "submitted_at": "2026-07-06T10:50:00Z"
    }
  }
  ```

#### `POST /api/v1/lms/projects`
*Post new hands-on capstone student projects.*
- **Authentication**: Bearer Token (RBAC Check: `lms:project:create`)
- **Request Payload**:
  ```json
  {
    "course_id": "c9c8c7c6-b5b4-a3a2-9190-876543210fed",
    "title": "Community Yoga Circle Creation",
    "description": "Construct a local meditation platform.",
    "requirements": ["Plan syllabus", "Gather feedback"]
  }
  ```
- **Response Payload (21 Created)**:
  ```json
  {
    "success": true,
    "data": {
      "project_id": "a9b8c7d6-e5f4-3c2b-1a09-ffffffffffff",
      "title": "Community Yoga Circle Creation",
      "created_at": "2026-07-06T11:00:00Z"
    }
  }
  ```

---

### 2.5 Dynamic Certificates

#### `GET /api/v1/certificates/verify/<string:signature_hash>`
*Public verification endpoint.*
- **Authentication**: Public
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "signature_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "recipient_name": "Siddharth Gautama",
      "course_title": "Advanced Breathing & Mindfulness Path",
      "issued_at": "2026-05-20T12:00:00Z",
      "verified": true
    }
  }
  ```

---

### 2.6 Communities, Blogs & Collaboration

#### `GET /api/v1/community/forums`
*Retrieve active forums categories.*
- **Authentication**: Public
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "e0e1e2e3-f4f5-a6a7-b8b9-f0f1f2f3f4f5",
        "name": "General Meditation Chat",
        "description": "A place to discuss breathing experiences."
      }
    ]
  }
  ```

#### `POST /api/v1/community/blogs`
*Publish educational blogs.*
- **Authentication**: Bearer Token (RBAC Check: `community:blogs:create`)
- **Request Payload**:
  ```json
  {
    "title": "The Power of Mindful Silence",
    "slug": "power-mindful-silence",
    "content": "Silence allows us to observe the nature of our thoughts...",
    "is_published": true
  }
  ```
- **Response Payload (201 Created)**:
  ```json
  {
    "success": true,
    "data": {
      "blog_id": "b0b1b2b3-f4f5-a6a7-b8b9-c0c1c2c3c4c5",
      "slug": "power-mindful-silence",
      "is_published": true,
      "published_at": "2026-07-06T11:15:00Z"
    }
  }
  ```

---

### 2.7 Financial Ledgers, Payments, & Wallets

#### `GET /api/v1/wallets/me`
*Retrieve active points wallet balances.*
- **Authentication**: Bearer Token
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "wallet_id": "77777777-6666-5555-4444-333333333333",
      "balance": "145.5000",
      "currency": "VIDYA",
      "last_updated": "2026-07-06T10:45:12Z"
    }
  }
  ```

#### `GET /api/v1/wallets/me/transactions`
*Append-only transaction list audit logs.*
- **Authentication**: Bearer Token
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "88888888-9999-0000-1111-222222222222",
        "type": "CREDIT",
        "amount": "10.0000",
        "description": "Daily Streak Reward",
        "created_at": "2026-07-06T08:00:00Z"
      }
    ],
    "meta": {
      "total_records": 15,
      "page": 1,
      "total_pages": 1,
      "limit": 20
    }
  }
  ```

#### `POST /api/v1/payments/checkout`
*Initiate payment gateways.*
- **Authentication**: Bearer Token (RBAC Check: `payments:checkout`)
- **Request Payload**:
  ```json
  {
    "course_id": "c9c8c7c6-b5b4-a3a2-9190-876543210fed",
    "amount": "49.99",
    "currency": "USD"
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "payment_id": "p0p1p2p3-f4f5-a6a7-b8b9-c0c1c2c3c4c5",
      "checkout_url": "https://checkout.stripe.com/pay/cs_live_123456789",
      "gateway_transaction_id": "cs_live_123456789"
    }
  }
  ```

---

### 2.8 Logistics & Teacher Scheduling

#### `GET /api/v1/logistics/teacher-classes`
*Retrieve assigned classes for teachers.*
- **Authentication**: Bearer Token (RBAC Check: `logistics:classes:read`)
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "class_id": "44444444-5555-6666-7777-888888888888",
        "course_title": "Mindfulness & Breathing Level 2",
        "schedule_info": {
          "days": ["Monday", "Wednesday"],
          "time_utc": "15:00"
        },
        "is_active": true
      }
    ]
  }
  ```

---

### 2.9 Intelligence (Vidya AI)

#### `POST /api/v1/intelligence/conversations`
*Start an AI dialog session thread.*
- **Authentication**: Bearer Token (RBAC Check: `intelligence:conversations:create`)
- **Request Payload**:
  ```json
  {
    "title": "Exploration of Mindful Breathing"
  }
  ```
- **Response Payload (201 Created)**:
  ```json
  {
    "success": true,
    "data": {
      "conversation_id": "c0c1c2c3-1111-2222-3333-444444444444",
      "title": "Exploration of Mindful Breathing",
      "created_at": "2026-07-06T11:30:00Z"
    }
  }
  ```

#### `POST /api/v1/intelligence/conversations/<uuid:conversation_id>/messages`
*Prompt Gemini model, saving the message exchange.*
- **Authentication**: Bearer Token (RBAC Check: `intelligence:messages:create`)
- **Request Payload**:
  ```json
  {
    "content": "Explain prana-yama in brief."
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "prompt": {
        "id": "u0u1u2u3-1111-2222-3333-444444444444",
        "content": "Explain prana-yama in brief.",
        "created_at": "2026-07-06T11:30:05Z"
      },
      "completion": {
        "id": "a0a1a2a3-1111-2222-3333-444444444444",
        "content": "Pranayama is the yogic practice of breath control...",
        "token_count": 145,
        "created_at": "2026-07-06T11:30:08Z"
      }
    }
  }
  ```

---

### 2.10 Communication, Notifications, & Analytics

#### `GET /api/v1/notifications/me`
*Fetch current user's unread notifications.*
- **Authentication**: Bearer Token
- **Query Parameters**: `is_read=false`
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "n0n1n2n3-0000-1111-2222-333333333333",
        "title": "New Assignment Feedback",
        "message": "Your reflection essay has been graded.",
        "is_read": false,
        "created_at": "2026-07-06T10:55:00Z"
      }
    ]
  }
  ```

#### `POST /api/v1/analytics/events`
*Log user metric telemetry events.*
- **Authentication**: Bearer Token (or Public with guest identifier)
- **Request Payload**:
  ```json
  {
    "metric_name": "video_playback_sec",
    "metric_value": 450.00,
    "context_data": {
      "lesson_id": "99999999-8888-7777-6666-555555555555"
    }
  }
  ```
- **Response Payload (201 Created)**:
  ```json
  {
    "success": true
  }
  ```

---

### 2.11 Dynamic Control Center

#### `GET /api/v1/control-center/settings`
*Fetch active portal settings config parameters block.*
- **Authentication**: Bearer Token (RBAC Check: `settings:read`)
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "platform_maintenance_mode": false,
      "registration_enabled": true,
      "rewards_points_multiplier": "1.50"
    }
  }
  ```

#### `PUT /api/v1/control-center/settings`
*Modify portal configurations.*
- **Authentication**: Bearer Token (RBAC Check: `settings:write`)
- **Request Payload**:
  ```json
  {
    "platform_maintenance_mode": false,
    "registration_enabled": true,
    "rewards_points_multiplier": "1.50"
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "platform_maintenance_mode": false,
      "registration_enabled": true,
      "rewards_points_multiplier": "1.50"
    }
  }
  ```

---

## Part 3: Implementation Status & Log

### Last Updated
- **Date**: July 7, 2026
- **Status Author**: AI Coding Assistant / Architect

### Current Implementation Status
- **Status**: **Phase 3 Complete (60% API Implementation Coverage)**
- **Integrity**: Main REST API endpoints are functional and wired directly into Django views and URL configurations under `backend/apps/lms/`. Standardized filters, searches, soft-delete retrievals, restorations, and pagination are fully validated.

### Completed Components
- **Identity & Authentication Routes**: Token creation, verification, token rotation, and current user retrieval endpoints.
- **LMS Views & ViewSets**: Unified `course-structures` lookups, assignment details, submissions registry, practice session submittals, question bank queries, and project definitions. Includes full soft delete, restore action triggers, and recursive classification filtering.
- **CMS Layout Endpoints**: Layout page fetching, navigation list loads, and public tutorials queries.

### Pending Components
- **Portfolio Builder API**: No-code editor triggers, customized layout saves, section order posts, domain bindings, and navigation builders.
- **Vidya AI Endpoints**: Thread generation, message completions pipelines, text-to-speech triggers, and assistant feedback forms.
- **Financial & Wallet Gateways**: Point transactions listings, peer points transfers, checkout invoice initialization, and Stripe/Razorpay webhook managers.
- **Community Boards Endpoints**: Nested forum threads, topic boards posts, comments feeds, report generation, and reactions likes counts.

### Future Improvements
- **Websockets for Collaborative Workspaces**: Integrate Django Channels to enable real-time collaborative workspaces, chat feeds, and interactive project whiteboarding.
- **AI Streaming Responses (SSE)**: Implement Server-Sent Events (SSE) on the Vidya AI chat prompt routes to support word-by-word real-time text streaming.
- **API Gateways & Rate Limiters**: Introduce Redis-based sliding-window rate limiters at the entry middleware to guarantee maximum platform stability during spikes.
