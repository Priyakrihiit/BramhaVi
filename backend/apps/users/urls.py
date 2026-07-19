"""
User Endpoints Router - BrahmaVidya Galaxy
Purpose: Maps routing paths to user views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import (
    PermissionViewSet, RolePermissionViewSet, RoleViewSet,
    UserViewSet, UserProfileViewSet, SessionViewSet, DeviceViewSet, NotificationViewSet,
    OrganizationViewSet, OrganizationMemberViewSet, LoginHistoryViewSet,
    CapabilityViewSet, UserCapabilityViewSet, CapabilityApplicationViewSet, AdminUserCapabilityViewSet
)

router = DefaultRouter()
router.register("permissions", PermissionViewSet, basename="permission")
router.register("role-permissions", RolePermissionViewSet, basename="role-permission")
router.register("roles", RoleViewSet, basename="role")
router.register("users", UserViewSet, basename="user")
router.register("profiles", UserProfileViewSet, basename="profile")
router.register("sessions", SessionViewSet, basename="session")
router.register("devices", DeviceViewSet, basename="device")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("organization-members", OrganizationMemberViewSet, basename="organization-member")
router.register("login-history", LoginHistoryViewSet, basename="login-history")
router.register("capabilities", CapabilityViewSet, basename="capability")
router.register("me/capabilities", UserCapabilityViewSet, basename="user-capability")
router.register("admin/capability-applications", CapabilityApplicationViewSet, basename="admin-capability-application")
router.register("admin/users", AdminUserCapabilityViewSet, basename="admin-user-capability")

app_name = "users"

urlpatterns = [
    path("", include(router.urls)),
]
