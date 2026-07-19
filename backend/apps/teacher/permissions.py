"""
Teacher Portal Permissions — BrahmaVidya Galaxy
Sprint 21: Secure RBAC, object ownership, and teaching assignment checkers.
"""

from __future__ import annotations

from permissions.base import BasePermission
from permissions.ownership import IsOwner
from apps.teacher.models import (
    TeacherProfile, TeachingSession, Batch, Attendance, TeacherAnnouncement,
    TeacherSchedule, TeachingGoal, TeacherEarning, TeacherWallet,
    TeacherCertificate, TeacherAchievement, TeacherNotificationPreference,
    TeacherActivityLog
)


class IsTeacher(BasePermission):
    """
    Allows access to Teachers, Admins, and Super Admins.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "TEACHER"]
        )


class IsTeacherOrAdmin(BasePermission):
    """
    Allows access only to teachers or administrative staff.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "TEACHER"]
        )


class IsTeacherOwner(BasePermission):
    """
    Ensures that the requesting user is the owner/teacher of the object.
    Supports profiles, sessions, batches (as instructors), and logs/wallets/earnings.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "TEACHER"]
        )

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
            return True

        # Profiles use user field
        if hasattr(obj, "user"):
            if obj.user == user or obj.user_id == user.id:
                return True

        # Most teacher-specific models use the teacher field
        if hasattr(obj, "teacher"):
            if obj.teacher == user or obj.teacher_id == user.id:
                return True

        # Batches use instructors M2M
        if hasattr(obj, "instructors"):
            if obj.instructors.filter(id=user.id).exists():
                return True

        # Attendance can check session or live_class owners
        if hasattr(obj, "session") and obj.session and hasattr(obj.session, "teacher"):
            if obj.session.teacher == user or obj.session.teacher_id == user.id:
                return True
        if hasattr(obj, "live_class") and obj.live_class and hasattr(obj.live_class, "teacher"):
            if obj.live_class.teacher == user or obj.live_class.teacher_id == user.id:
                return True

        return False


class TeacherDashboardPermission(BasePermission):
    """
    Validates access permissions for teacher dashboard analytics and summaries.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "TEACHER"]
        )


class CoursePermission(BasePermission):
    """
    Validates that a teacher can only manage/view courses they are assigned to teach.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "TEACHER"]
        )

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True

        from apps.lms.models import TeacherClass, CourseStructure
        
        course_id = None
        if isinstance(obj, CourseStructure):
            if obj.node_type == "COURSE":
                course_id = obj.id
            else:
                # Resolve parent node
                curr = obj
                for _ in range(5):
                    if curr.node_type == "COURSE":
                        course_id = curr.id
                        break
                    if not curr.parent:
                        break
                    curr = curr.parent
        elif hasattr(obj, "course") and obj.course:
            course_id = obj.course.id if hasattr(obj.course, "id") else obj.course

        if not course_id:
            return True

        return TeacherClass.objects.filter(teacher=user, course_id=course_id, is_active=True).exists()


class AssignmentPermission(BasePermission):
    """
    Controls access to Assignments and their submissions.
    Teachers should only grade or view submissions for courses they instruct.
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "role") and request.user.role and request.user.role.name in ["SUPERADMIN", "ADMIN", "TEACHER"]
        )

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True

        from apps.lms.models import TeacherClass, Assignment, AssignmentSubmission
        
        course_id = None
        if isinstance(obj, Assignment):
            try:
                lesson = obj.lesson
                if lesson:
                    chapter = lesson.parent
                    if chapter:
                        course = chapter.parent
                        if course and course.node_type == "COURSE":
                            course_id = course.id
            except Exception:
                pass
        elif isinstance(obj, AssignmentSubmission):
            try:
                assignment = obj.assignment
                lesson = assignment.lesson
                if lesson:
                    chapter = lesson.parent
                    if chapter:
                        course = chapter.parent
                        if course and course.node_type == "COURSE":
                            course_id = course.id
            except Exception:
                pass

        if not course_id:
            return True

        return TeacherClass.objects.filter(teacher=user, course_id=course_id, is_active=True).exists()
