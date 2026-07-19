"""
Control Center Permissions - BrahmaVidya Galaxy
Purpose: Enforces dynamic permission checks across the platform's central control gateways.
"""

from rest_framework import permissions


class IsControlCenterSupervisor(permissions.BasePermission):
    """
    Ensures the authenticated user possesses the 'SUPER_ADMIN' or custom administrative capability.
    """
    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
            
        # Bypass or check custom permissions dynamically synced on the user object
        if hasattr(user, "role") and user.role:
            user_permissions = user.role.permissions.values_list("code", flat=True)
            return "SUPER_ADMIN" in user_permissions or "SYSTEM_CONFIG" in user_permissions
            
        return False


class CanAuditTelemetryLogs(permissions.BasePermission):
    """
    Enforces authorization locks specifically for reading or downloading secure database logs.
    """
    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
            
        if hasattr(user, "role") and user.role:
            user_permissions = user.role.permissions.values_list("code", flat=True)
            return "SUPER_ADMIN" in user_permissions or "AUDIT_READ" in user_permissions
            
        return False
