from permissions.base import BasePermission

class CanEditContent(BasePermission):
    """
    Ensures writing edits to CMS and system content blocks is restricted to authorized authors or role permissions.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role:
            if user.role.name in ["SUPERADMIN", "ADMIN"]:
                return True
            return user.role.role_permissions.filter(permission__codename="cms:content:edit").exists()
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
            return True

        # Original creator check
        if hasattr(obj, "author") and obj.author == user:
            return True
        if hasattr(obj, "creator") and obj.creator == user:
            return True

        return False
