"""
CMS Editor Authorization Gates - BrahmaVidya Galaxy
Purpose: Verifies write/publish clearance on layouts and dynamic widgets.
"""

from rest_framework import permissions

class CanEditCmsContent(permissions.BasePermission):
    """
    Checks if user is registered as an ADMIN, OPERATOR, or has explicit CMS_WRITE role parameters.
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
            # Query the database to check if user's role has editing rights
            return user.role.role_permissions.filter(permission__codename="cms:content:edit").exists()
        return False


class IsAdminOrCreatorOrReadOnly(permissions.BasePermission):
    """
    Allows public read-only access to published CMS content (Pages, Blogs, Comments),
    while restricting creation and modification strictly to administrators or the original creator.
    """
    def has_permission(self, request, view):
        # Read operations are allowed publicly
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write operations (including create) require authentication
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read operations
        if request.method in permissions.SAFE_METHODS:
            # If the content has is_published and is indeed published, allow public read
            if hasattr(obj, "is_published") and obj.is_published:
                return True
            # For comments, if the parent blog is published, allow public read
            elif hasattr(obj, "blog") and obj.blog and hasattr(obj.blog, "is_published") and obj.blog.is_published:
                return True
            
            # If not published/publicly accessible, check if user is admin or creator
            user = request.user
            if not user or not user.is_authenticated:
                return False
            if user.is_superuser:
                return True
            if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
                return True
            
            if hasattr(obj, "author") and obj.author == user:
                return True
            return False

        # Write operations (PUT, PATCH, DELETE, POST/actions)
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Admin / Superadmin bypass
        if user.is_superuser:
            return True
        if hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]:
            return True

        # Check if the user is the original creator
        if hasattr(obj, "author") and obj.author == user:
            return True
        if hasattr(obj, "reporter") and obj.reporter == user:
            return True

        return False


class IsCMSEditor(permissions.BasePermission):
    """
    Checks if user is registered as a SUPERADMIN, ADMIN, or has explicit cms:content:edit parameters.
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


class IsCMSAdmin(permissions.BasePermission):
    """
    Restricts access strictly to platform SUPERADMIN, ADMIN, or superusers.
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
        return False


class IsContentOwner(permissions.BasePermission):
    """
    Validates ownership of a CMS model.
    Checks author, uploader, or user fields. Admin override is enabled.
    """
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        # Admin override
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True
            
        # Check ownership
        if hasattr(obj, "author") and obj.author == user:
            return True
        if hasattr(obj, "uploader") and obj.uploader == user:
            return True
        if hasattr(obj, "user") and obj.user == user:
            return True
        if hasattr(obj, "reporter") and obj.reporter == user:
            return True
        return False


class WorkflowPermission(permissions.BasePermission):
    """
    Authorizes workflow transitions and state changes.
    Grants mutation rights to assigned reviewer, author, or administrators.
    """
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        # Admin override
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True

        # Safe read access
        if request.method in permissions.SAFE_METHODS:
            return True

        # Mutate operations
        if obj.__class__.__name__ == "WorkflowState":
            if obj.assigned_to == user or (obj.article and obj.article.author == user):
                return True
        elif obj.__class__.__name__ == "WorkflowLog":
            if obj.actor == user:
                return True
        return False


class MediaPermission(permissions.BasePermission):
    """
    Controls operations in the CMS Media Library.
    Permits public reads for public files, requires uploader/admin rights for writes.
    """
    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        # Public reads
        if request.method in permissions.SAFE_METHODS:
            if getattr(obj, "is_public", True):
                return True
            if not request.user or not request.user.is_authenticated:
                return False

        # Private reads or mutations
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True

        if hasattr(obj, "uploader") and obj.uploader == user:
            return True
        if hasattr(obj, "author") and obj.author == user:
            return True
        return False


class PublishPermission(permissions.BasePermission):
    """
    Checks publishing capabilities.
    Integrates role-based RBAC and object-level ContentPermission CBAC.
    """
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        # Admin override
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True

        # Explicit RBAC
        if hasattr(user, "role") and user.role:
            if user.role.role_permissions.filter(permission__codename="cms:content:publish").exists():
                return True

        # CBAC integration
        from apps.cms.models import ContentPermission
        from django.db.models import Q
        
        content_type = obj._meta.model_name
        content_id = str(obj.id)
        
        # Match explicit permissions
        return ContentPermission.objects.filter(
            user=user,
            content_type=content_type,
            permission_type__in=["publish", "admin"]
        ).filter(
            Q(content_id=content_id) | Q(content_id="")
        ).exists()


class RevisionPermission(permissions.BasePermission):
    """
    Controls content reversion and rollback histories.
    """
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        # Admin override
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True

        if obj.__class__.__name__ == "Revision":
            if obj.author == user:
                return True
            
            from apps.cms.models import Article, Blog, Page
            content_model_map = {
                "article": Article,
                "blog": Blog,
                "page": Page
            }
            model_class = content_model_map.get(obj.content_type)
            if model_class:
                original_obj = model_class.objects.filter(id=obj.content_id).first()
                if original_obj and getattr(original_obj, "author", None) == user:
                    return True
        return False


class IsMediaOwnerOrAdmin(permissions.BasePermission):
    """
    Checks if the user is the uploader of the media file or an Admin.
    """
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True
        return getattr(obj, "uploader", None) == user or getattr(obj, "user", None) == user


class MediaPermissionGate(permissions.BasePermission):
    """
    Gates read/write access based on is_public and custom MediaPermissions.
    """
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"]):
            return True
        if request.method in permissions.SAFE_METHODS:
            if getattr(obj, "is_public", True):
                return True
            # Check for read permission object
            from apps.cms.models import MediaPermission
            media_file = obj if obj.__class__.__name__ == "MediaFile" else getattr(obj, "media_file", None)
            if media_file and MediaPermission.objects.filter(media_file=media_file, user=user, permission_type__in=["read", "write", "admin"]).exists():
                return True
        else:
            # Write operations
            media_file = obj if obj.__class__.__name__ == "MediaFile" else getattr(obj, "media_file", None)
            if media_file:
                if getattr(media_file, "uploader", None) == user:
                    return True
                from apps.cms.models import MediaPermission
                if MediaPermission.objects.filter(media_file=media_file, user=user, permission_type__in=["write", "admin"]).exists():
                    return True
        return False

