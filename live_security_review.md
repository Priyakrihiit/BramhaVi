# Live Classes Platform — Security Review
**Sprint 22 — Phase 9 Documentation**

## 1. Authentication & JWT Validation
*   All endpoints under `/api/v1/live/` are protected via Central Gateway filters validating bearer JWT tokens.
*   Decrypted user payloads are appended to headers as authorized credentials passed down to the Django backend.

## 2. Authorization Scopes (RBAC & CBAC)
*   **Role-Based Access Control (RBAC)**: Only users possessing a `TEACHER` or `ADMIN` role can schedule broadcasts, activate/terminate streams, or publish interactive polls.
*   **Capability-Based Access Control (CBAC)**: Course stream URLs and attendance panels are restricted to students with an active enrollment record on the course node.

## 3. Input Validations
*   `validate_live_class_timing` restricts scheduled start dates to future timestamps.
*   `validate_poll_options` enforces a minimum count of 2 answers per poll item to prevent corrupted inputs.
