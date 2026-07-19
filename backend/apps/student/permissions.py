"""
Student Dashboard Permissions — BrahmaVidya Galaxy
Sprint 20: Secure RBAC, CBAC, and object ownership checkers.
"""

from __future__ import annotations

from permissions.base import BasePermission
from permissions.ownership import IsOwner
from apps.lms.models import StudentEnrollment, CourseStructure


class IsStudentOwner(IsOwner):
    """
    DRF permissions class validating that obj.student == request.user on all detail view routes
    (crucial for bookmarks, notes, goals, calendar events, and study sessions).
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
            return True

        if hasattr(obj, "student"):
            return obj.student == user or obj.student_id == user.id

        return super().has_object_permission(request, view, obj)


class IsEnrolledInCourse(BasePermission):
    """
    Verifies that a student has an active StudentEnrollment for the requested course/lesson
    before logging history, starting a session, or creating notes.
    """

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
            return True

        # Check write payload
        node_id = request.data.get("node") or request.data.get("node_id")
        enrollment_id = request.data.get("enrollment") or request.data.get("enrollment_id")

        if enrollment_id:
            return StudentEnrollment.objects.filter(
                id=enrollment_id,
                student=user,
                status="ACTIVE"
            ).exists()

        if node_id:
            try:
                node = CourseStructure.objects.get(id=node_id)
                current = node
                course_node = None
                for _ in range(5):  # Limit depth to prevent infinite loops
                    if current.node_type == "COURSE":
                        course_node = current
                        break
                    if not current.parent:
                        break
                    current = current.parent

                if course_node:
                    return StudentEnrollment.objects.filter(
                        student=user,
                        course=course_node,
                        status="ACTIVE"
                    ).exists()
                else:
                    ancestor_ids = []
                    curr = node
                    for _ in range(5):
                        if curr.parent_id:
                            ancestor_ids.append(curr.parent_id)
                            curr = curr.parent
                        else:
                            break
                    return StudentEnrollment.objects.filter(
                        student=user,
                        course_id__in=ancestor_ids,
                        status="ACTIVE"
                    ).exists()
            except (CourseStructure.DoesNotExist, ValueError):
                return False

        return True

    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
            return True

        # If object has enrollment, verify active owner
        if hasattr(obj, "enrollment") and obj.enrollment:
            return obj.enrollment.student == user and obj.enrollment.status == "ACTIVE"

        # If object has node, verify enrollment in that node's course
        if hasattr(obj, "node") and obj.node:
            node = obj.node
            current = node
            course_node = None
            for _ in range(5):
                if current.node_type == "COURSE":
                    course_node = current
                    break
                if not current.parent:
                    break
                current = current.parent

            if course_node:
                return StudentEnrollment.objects.filter(
                    student=user,
                    course=course_node,
                    status="ACTIVE"
                ).exists()

        return True


# ─── ADDITIONAL SPRINT 20 COMPLIANCE PERMISSIONS ─────────────────────────────

class IsStudent(BasePermission):
    """
    Allows access to Students, Admins, and Super Admins.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "STUDENT"]
        )


class IsStudentOrAdmin(BasePermission):
    """
    Allows access only to students or admin staff.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "STUDENT"]
        )


class DashboardPermission(BasePermission):
    """
    Validates access permissions for student dashboard queries.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "STUDENT"]
        )


class GoalPermission(BasePermission):
    """
    Checks student tenancy/access permissions for study goals.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "STUDENT"]
        )

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True
        return hasattr(obj, "student") and (obj.student == user or obj.student_id == user.id)


class NotePermission(BasePermission):
    """
    Checks student tenancy/access permissions for personal learning notes.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "STUDENT"]
        )

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True
        return hasattr(obj, "student") and (obj.student == user or obj.student_id == user.id)


class BookmarkPermission(BasePermission):
    """
    Checks student tenancy/access permissions for student bookmarks.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "STUDENT"]
        )

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True
        return hasattr(obj, "student") and (obj.student == user or obj.student_id == user.id)

