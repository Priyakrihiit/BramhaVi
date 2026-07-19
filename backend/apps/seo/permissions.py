from rest_framework import permissions
from apps.users.permissions import HasRBACPermission

class HasSEORBACPermission(HasRBACPermission):
    """
    Subclass of HasRBACPermission to provide SEO-specific defaults or customizations.
    """
    pass
