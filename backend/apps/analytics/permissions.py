from rest_framework import permissions


class BaseAnalyticsPermission(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        # Bypass checks for system administrators/superusers
        if request.user.is_superuser:
            return True
        if request.user.has_capability("ADMIN"):
            return True
        if hasattr(request.user, "role") and request.user.role:
            if request.user.role.name in ["SUPERADMIN", "ADMIN"]:
                return True
        return False


class HasAnalyticsViewerPermission(BaseAnalyticsPermission):
    """
    CBAC/RBAC permission check verifying view credentials (codename: analytics:view).
    """
    def has_permission(self, request, view) -> bool:
        # Standard admin bypass
        if super().has_permission(request, view):
            return True

        user = request.user
        # 1. Check CBAC Capabilities
        if user.has_capability_permission("analytics:view"):
            return True

        # 2. Check RBAC Role Mapping
        if hasattr(user, "role") and user.role:
            if user.role.role_permissions.filter(permission__codename="analytics:view").exists():
                return True
            # Also allow teachers and organization dashboards views
            if user.role.name in ["TEACHER", "INSTITUTE"]:
                return True

        return False


class HasAnalyticsManagerPermission(BaseAnalyticsPermission):
    """
    CBAC/RBAC permission check verifying operational credentials (codename: analytics:manage).
    """
    def has_permission(self, request, view) -> bool:
        if super().has_permission(request, view):
            return True

        user = request.user
        if user.has_capability_permission("analytics:manage"):
            return True

        if hasattr(user, "role") and user.role:
            if user.role.role_permissions.filter(permission__codename="analytics:manage").exists():
                return True

        return False


class HasAnalyticsAdminPermission(BaseAnalyticsPermission):
    """
    CBAC/RBAC permission check verifying admin configuration permissions (codename: analytics:admin).
    """
    def has_permission(self, request, view) -> bool:
        # Administrative tasks require administrative roles
        return super().has_permission(request, view)
