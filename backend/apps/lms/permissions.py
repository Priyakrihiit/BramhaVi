"""
LMS Enrollment Authorization Gates - BrahmaVidya Galaxy
Purpose: Verifies course enrollment eligibility and teacher administrative scopes.
"""

from rest_framework import permissions

class IsEnrolledInCourse(permissions.BasePermission):
    """
    Grants access only if the student has a validated enrollment record for the course node.
    """
    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin & Teacher exception bypass
        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role:
            if user.role.name in ["SUPERADMIN", "ADMIN", "TEACHER"]:
                return True
            
        from apps.lms.models import StudentEnrollment
        course_id = None
        if hasattr(obj, "course"):
            course_id = obj.course.id if hasattr(obj.course, "id") else obj.course
        elif hasattr(obj, "lesson") and hasattr(obj.lesson, "parent"):
            node = obj.lesson
            while node and getattr(node, "node_type", None) not in ["COURSE", "PROGRAM"]:
                node = node.parent
            if node:
                course_id = node.id
        else:
            course_id = getattr(obj, "id", None)

        if not course_id:
            return False

        return StudentEnrollment.objects.filter(student=user, course_id=course_id, status="ACTIVE").exists()

class IsCourseInstructor(permissions.BasePermission):
    """
    Ensures writing edits to course syllabi is restricted to authorized instructors.
    """
    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
            
        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role:
            if user.role.name in ["SUPERADMIN", "ADMIN"]:
                return True
            
        from apps.lms.models import TeacherClass
        course_id = None
        if hasattr(obj, "course"):
            course_id = obj.course.id if hasattr(obj.course, "id") else obj.course
        else:
            course_id = getattr(obj, "id", None)

        if not course_id:
            return False

        return TeacherClass.objects.filter(teacher=user, course_id=course_id, is_active=True).exists()


class IsTeacherOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission for CourseViewSet to allow only teachers and admins to create/update courses,
    while students and other authenticated users can only read.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write/Update/Delete permissions require ADMIN, SUPERADMIN, or TEACHER role
        if request.user.is_superuser:
            return True
        if hasattr(request.user, "role") and request.user.role:
            if request.user.role.name in ["SUPERADMIN", "ADMIN", "TEACHER"]:
                return True
        return False

