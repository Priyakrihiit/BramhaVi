from rest_framework import permissions

class HasCapabilityPermission(permissions.BasePermission):
    """
    Universal CBAC permission gate.
    Checks if the user's active capabilities collectively grant the required permission.
    """
    def has_permission(self, request, view):
        # 1. Allow public visitor access if explicitly configured on the view
        if getattr(view, 'allow_visitor', False) and request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Super Admin bypasses all checks
        if request.user.is_superuser:
            return True

        # 3. Resolve required permission for this action
        required = self._get_required_permission(view, request)
        if not required:
            return True  # No permission specified = allow authenticated users by default

        # Try CBAC first
        if request.user.has_capability_permission(required):
            return True

        # Fallback to legacy role system during migration
        try:
            if hasattr(request.user, 'role') and request.user.role:
                from apps.users.models import RolePermission
                if RolePermission.objects.filter(
                    role=request.user.role,
                    permission__codename=required
                ).exists():
                    return True
        except Exception:
            pass

        return False

    def _get_required_permission(self, view, request):
        # A. Check action-specific permissions map
        action = getattr(view, 'action', None)
        action_perms = getattr(view, 'capability_permissions', {})
        if action and action in action_perms:
            return action_perms[action]

        # B. Check view-level required_permission attribute
        required = getattr(view, 'required_permission', None)
        if required:
            return required

        # C. Check method-based fallback
        method_perms = getattr(view, 'method_permissions', {})
        return method_perms.get(request.method)
