"""
apps/ai/permissions.py
Sprint 24 — Phase 4: AI Permissions — BrahmaVidya Galaxy

Permission controls ensuring user isolation, resource access security,
and role-based checks.
"""

from __future__ import annotations

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Standard object-level permission validating that the user owns the AI resource
    or is an administrator.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        # Admin bypass
        if request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN"]
        ):
            return True

        # Check standard ownership fields
        if hasattr(obj, "user") and obj.user is not None:
            return obj.user == request.user
        if hasattr(obj, "student") and obj.student is not None:
            return obj.student == request.user
        if hasattr(obj, "generated_by") and obj.generated_by is not None:
            return obj.generated_by == request.user

        return False


class IsStudentUser(permissions.BasePermission):
    """
    Permits access only to authenticated students.
    """

    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated
