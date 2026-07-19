"""
Custom RBAC Permissions - BrahmaVidya Galaxy
Purpose: Handles endpoint access verification using dynamic Database Roles and Permissions.
"""

from rest_framework import permissions

from rest_framework import permissions
from apps.users.cbac_permissions import HasCapabilityPermission

class HasRBACPermission(HasCapabilityPermission):
    """
    Validates that the authenticated user possesses the required permission token inside their dynamic database profile.
    """
    def __init__(self, required_permission: str = None):
        self.required_permission = required_permission

    def has_permission(self, request, view) -> bool:
        """
        Determines request permission eligibility.
        """
        if getattr(view, 'allow_visitor', False) and request.method in permissions.SAFE_METHODS:
            return True

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

        # Determine permission required for the action
        required = self.required_permission
        if not required:
            # Fallback to check view's required_permission attribute
            required = getattr(view, "required_permission", None)

        if not required:
            # Fallback to view's action-specific permissions map
            required_permissions = getattr(view, "required_permissions", {})
            required = required_permissions.get(view.action) if hasattr(view, "action") else None

        if not required:
            # If no permission is specified, allow authenticated users by default
            return True

        # Check CBAC first
        if request.user.has_capability_permission(required):
            return True

        # Query the database to check if user's role has this permission
        if not hasattr(request.user, "role") or not request.user.role:
            return False

        return request.user.role.role_permissions.filter(permission__codename=required).exists()


class IsAdminOrSelf(permissions.BasePermission):
    """
    Object-level permission to allow admins to manage any user/profile,
    but restricts regular users to viewing or updating only their own user/profile.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin / Superuser bypasses all checks
        if request.user.is_superuser:
            return True
        if request.user.has_capability("ADMIN"):
            return True
        if hasattr(request.user, "role") and request.user.role:
            if request.user.role.name in ["SUPERADMIN", "ADMIN"]:
                return True

        # For list or create, enforce standard RBAC permissions.
        if hasattr(view, "action") and view.action in ["list", "create"]:
            required_permissions = getattr(view, "required_permissions", {})
            required = required_permissions.get(view.action)
            if not required:
                return True
            
            # Check CBAC first
            if request.user.has_capability_permission(required):
                return True
                
            if not hasattr(request.user, "role") or not request.user.role:
                return False
            return request.user.role.role_permissions.filter(permission__codename=required).exists()

        # For object-level operations (retrieve, update, partial_update, destroy, restore),
        # allow moving to has_object_permission check.
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin / Superuser bypasses all checks
        if request.user.is_superuser:
            return True
        if request.user.has_capability("ADMIN"):
            return True
        if hasattr(request.user, "role") and request.user.role:
            if request.user.role.name in ["SUPERADMIN", "ADMIN"]:
                return True

        # Check if target object is the request user or is associated with the request user
        is_self = False
        if hasattr(obj, "user"):
            is_self = obj.user == request.user
        else:
            is_self = obj == request.user

        # Users can retrieve/update/partial_update their own profile/user object
        action = getattr(view, "action", None)
        if action in ["retrieve", "update", "partial_update"]:
            return is_self

        # Regular users cannot delete or do other administrative actions on themselves or others
        required_permissions = getattr(view, "required_permissions", {})
        required = required_permissions.get(action) if action else None
        if not required:
            return is_self

        if request.user.has_capability_permission(required):
            return True

        if not hasattr(request.user, "role") or not request.user.role:
            return False

        return request.user.role.role_permissions.filter(permission__codename=required).exists()


class IsAdminOrOwner(permissions.BasePermission):
    """
    Object-level permission allowing superusers/admins to manage any object,
    but restricts regular users to objects they own (via user, student, author, creator, owner fields).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        if user.has_capability("ADMIN"):
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
            return True

        if obj == user:
            return True

        for attr in ["user", "student", "author", "creator", "owner"]:
            if hasattr(obj, attr) and getattr(obj, attr) == user:
                return True

        # Handle specific cases like a profile or wallet
        if hasattr(obj, "wallet") and hasattr(obj.wallet, "user") and obj.wallet.user == user:
            return True

        return False


