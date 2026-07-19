from permissions.base import BasePermission

class IsOwner(BasePermission):
    """
    Object-level permission to allow only owners of an object to access/modify it.
    """
    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
            return True

        # Dynamically check standard owner/creator/student/reporter relationship attributes
        for attr in ["user", "author", "student", "reporter", "creator", "owner"]:
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                if val == user:
                    return True
                if hasattr(val, "id") and val.id == user.id:
                    return True

        # Wallet specific check
        if hasattr(obj, "wallet") and hasattr(obj.wallet, "user") and obj.wallet.user == user:
            return True

        return False


class IsCourseOwner(BasePermission):
    """
    Allows access only to assigned instructors or course creators of a Course unit/node.
    """
    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
            return True

        from apps.lms.models import TeacherClass
        
        # Get course_id
        course_id = None
        if hasattr(obj, "course"):
            course_id = obj.course.id if hasattr(obj.course, "id") else obj.course
        else:
            course_id = getattr(obj, "id", None)

        if not course_id:
            return False

        return TeacherClass.objects.filter(teacher=user, course_id=course_id, is_active=True).exists()
