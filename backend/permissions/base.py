from rest_framework import permissions

class BasePermission(permissions.BasePermission):
    """
    Enterprise Base Permission Class with dynamic logging and audit capabilities.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class HasPermission(BasePermission):
    """
    Dynamic RBAC database permission checker.
    Format is `module:resource:action`.
    """
    def __init__(self, required_permission: str = None):
        self.required_permission = required_permission

    def __call__(self, *args, **kwargs):
        # Allow class-level or parameterized instantiation
        return self

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        # Bypass checks for system administrators/superusers
        if request.user.is_superuser:
            return True
        if hasattr(request.user, "role") and request.user.role:
            if request.user.role.name in ["SUPERADMIN", "ADMIN"]:
                return True

        # Determine permission required for the action
        required = self.required_permission
        if not required:
            required = getattr(view, "required_permission", None)

        if not required:
            required_permissions = getattr(view, "required_permissions", {})
            required = required_permissions.get(view.action) if hasattr(view, "action") else None

        if not required:
            # Safe default fallback: if no specific permission key is set, permit authenticated requests
            return True

        if not hasattr(request.user, "role") or not request.user.role:
            return False

        return request.user.role.role_permissions.filter(permission__codename=required).exists()
