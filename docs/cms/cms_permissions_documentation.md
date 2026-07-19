# CMS Permissions Documentation

This document describes the 7 custom authorization gates implemented in `backend/apps/cms/permissions.py` for the Enterprise CMS package of BrahmaVidya Galaxy.

---

## 1. Permission Classes Reference

These gates integrate Role-Based Access Control (RBAC), Content-Based Access Control (CBAC), object ownership validation, and admin overrides.

| Permission Class | Check / Validation | Override Behavior |
| :--- | :--- | :--- |
| **IsCMSEditor** | Verifies if the user is authenticated and has a role with the `cms:content:edit` permission codename. | Granted for superusers, `SUPERADMIN`, and `ADMIN`. |
| **IsCMSAdmin** | Checks if the user has `SUPERADMIN` or `ADMIN` roles or is a superuser. | Strict check. |
| **IsContentOwner** | Asserts that `obj.author`, `obj.uploader`, `obj.user`, or `obj.reporter` matches the authenticated user. | Granted for superusers, `SUPERADMIN`, and `ADMIN`. |
| **WorkflowPermission** | Regulates workflow state mutations. Restricts writes to assigned reviewers (`obj.assigned_to`) or content authors. | Read operations are permitted to any authenticated user. Full bypass for Admins. |
| **MediaPermission** | Implements media library restrictions. Restricts write operations to the file uploader. | Public read operations are allowed on public media assets. Full bypass for Admins. |
| **PublishPermission** | Combines global RBAC and object-level CBAC rules. Checks if user has a global `cms:content:publish` permission, or an explicit matching `ContentPermission` configuration (CBAC) with type `"publish"` or `"admin"`. | Granted for superusers, `SUPERADMIN`, and `ADMIN`. |
| **RevisionPermission** | Restricts revision lookup and content reversion (rollbacks) to the revision author or the author of the original target content. | Granted for superusers, `SUPERADMIN`, and `ADMIN`. |

---

## 2. Access Control Types Supported

### A. Role-Based Access Control (RBAC)
Verified via:
- `request.user.role.name` membership.
- `request.user.role.role_permissions` filtering on specific codenames (e.g. `cms:content:edit`, `cms:content:publish`).

### B. Content-Based Access Control (CBAC)
Verified via the `ContentPermission` model in `PublishPermission`. Permits fine-grained object-level overrides:
- By matching target object UUID (`content_id`).
- Globally for all assets of a model class (when `content_id` is empty `""`).
- Granting specific capability tiers (`publish`, `admin`).
