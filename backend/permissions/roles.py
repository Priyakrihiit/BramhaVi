from permissions.base import BasePermission

class IsSuperAdmin(BasePermission):
    """
    Allows access only to Super Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name == "SUPERADMIN"
        )


class IsAdmin(BasePermission):
    """
    Allows access to Admins and Super Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        )


class IsTeacher(BasePermission):
    """
    Allows access to Teachers, Admins, and Super Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "TEACHER"]
        )


class IsStudent(BasePermission):
    """
    Allows access to Students, Admins, and Super Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "STUDENT"]
        )


class IsContentCreator(BasePermission):
    """
    Allows access to Content Creators, Admins, and Super Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "CONTENT_CREATOR"]
        )


class IsModerator(BasePermission):
    """
    Allows access to Moderators, Admins, and Super Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "MODERATOR"]
        )


class IsFinance(BasePermission):
    """
    Allows access to Finance users, Admins, and Super Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "FINANCE"]
        )


class IsAnalytics(BasePermission):
    """
    Allows access to Analytics users, Admins, and Super Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "ANALYTICS"]
        )
