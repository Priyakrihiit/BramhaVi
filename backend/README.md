# Backend Services - BrahmaVidya Galaxy

This directory houses the complete corporate backend infrastructure for the **BrahmaVidya Galaxy** hybrid dynamic CMS and LMS engine.

## Directory Structure & Purpose

- **`config/`**: System configuration scripts, server initialization parameters, and database connection pools.
- **`controllers/`**: Core business coordinators maps request arguments to execution logic and compiles HTTP responses.
- **`middleware/`**: Request sanitization filters, cryptographic JWT validation checks, CORS rules, and rate limiters.
- **`models/`**: Database schema descriptors, entity declarations, and indices configs.
- **`routes/`**: Standardized REST endpoint definitions mapping URLs to controller functions.
- **`services/`**: Encapsulates external software system interfaces, including the **Vidya AI Gateway** connecting with Gemini LLM models.

---

## Technical Specifications
- **Runtime**: Node.js / Python-Django
- **API Standard**: RESTful v1 Architecture with standardized error payloads.
- **Access Control**: Dynamic database-driven Role-Based Access Control (RBAC).
- **Security Protocols**: HttpOnly, Secure cookie JWT session management.
