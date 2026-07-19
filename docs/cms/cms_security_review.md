# CMS Security Review

## 1. Authentication & Session Validation
- JWT verification runs on every incoming client route.
- Token validation pass-through allows Django backend to assert user roles and credentials.

## 2. Authorization Design (RBAC + CBAC)
- **Role-Based Access Control (RBAC)**: Checks specific user role permission codes (e.g. `cms:content:publish`).
- **Content-Based Access Control (CBAC)**: Checks object-level mappings inside the `ContentPermission` model to authorize specific UUID targets.
- **Admin Overrides**: Administrators (`SUPERADMIN` or `ADMIN` roles) automatically bypass constraint blocks.
