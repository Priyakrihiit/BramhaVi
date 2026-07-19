import csv
from io import StringIO
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import HasRBACPermission
from apps.users.models import User, Role, Permission, RolePermission, Session, Device, UserProfile
from apps.control_center.models import ActivityLog
from apps.control_center.admin_serializers import (
    UserAdminSerializer, RoleSerializer, PermissionSerializer, BulkActionSerializer,
    SessionAdminSerializer
)

class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Module 2 — Enterprise User Management Control Tower.
    Comprehensive administrative capabilities for platform accounts.
    """
    queryset = User.all_objects.select_related("role", "profile").all()
    serializer_class = UserAdminSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email", "profile__first_name", "profile__last_name"]
    ordering_fields = ["email", "created_at"]
    ordering = ["-created_at"]

    required_permissions = {
        "list": "control:users:view",
        "retrieve": "control:users:view",
        "create": "control:users:create",
        "update": "control:users:update",
        "partial_update": "control:users:update",
        "destroy": "control:users:delete",
        "restore": "control:users:update",
        "suspend_user": "control:users:update",
        "activate_user": "control:users:update",
        "block_user": "control:users:update",
        "unblock_user": "control:users:update",
        "verify_user": "control:users:update",
        "unverify_user": "control:users:update",
        "force_logout": "control:users:update",
        "reset_password": "control:users:update",
        "assign_role": "control:users:update",
        "remove_role": "control:users:update",
        "assign_permission": "control:users:update",
        "remove_permission": "control:users:update",
        "devices": "control:users:view",
        "login_history": "control:users:view",
        "activity_timeline": "control:users:view",
        "sessions": "control:users:view",
        "revoke_session": "control:users:update",
        "bulk_action": "control:users:update",
        "export": "control:users:view",
    }

    def get_queryset(self):
        qs = super().get_queryset()
        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        if not include_deleted:
            qs = qs.filter(deleted_at__isnull=True)
        
        # Simple Filter prefixes
        role_name = self.request.query_params.get("role")
        if role_name:
            qs = qs.filter(role__name=role_name.upper())
            
        is_active = self.request.query_params.get("is_active")
        if is_active:
            qs = qs.filter(is_active=is_active.lower() == "true")
            
        return qs

    def perform_destroy(self, instance):
        instance.delete()  # soft delete

    @action(detail=True, methods=["post"])
    def restore(self, request, id=None):
        instance = User.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not instance:
            return Response({"detail": "User not found or not deleted."}, status=status.HTTP_404_NOT_FOUND)
        instance.restore()
        return Response({"detail": "User successfully restored."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend_user(self, request, id=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        ActivityLog.objects.create(user=request.user, event="USER_SUSPENDED", details={"target_user": user.email})
        return Response({"detail": f"User {user.email} suspended successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate_user(self, request, id=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active"])
        ActivityLog.objects.create(user=request.user, event="USER_ACTIVATED", details={"target_user": user.email})
        return Response({"detail": f"User {user.email} activated successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="block")
    def block_user(self, request, id=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        ActivityLog.objects.create(user=request.user, event="USER_BLOCKED", details={"target_user": user.email})
        return Response({"detail": f"User {user.email} blocked successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unblock")
    def unblock_user(self, request, id=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active"])
        ActivityLog.objects.create(user=request.user, event="USER_UNBLOCKED", details={"target_user": user.email})
        return Response({"detail": f"User {user.email} unblocked successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="verify")
    def verify_user(self, request, id=None):
        user = self.get_object()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.settings["is_verified"] = True
        profile.save()
        ActivityLog.objects.create(user=request.user, event="USER_VERIFIED", details={"target_user": user.email})
        return Response({"detail": f"User {user.email} verified successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unverify")
    def unverify_user(self, request, id=None):
        user = self.get_object()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.settings["is_verified"] = False
        profile.save()
        ActivityLog.objects.create(user=request.user, event="USER_UNVERIFIED", details={"target_user": user.email})
        return Response({"detail": f"User {user.email} unverified successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="force-logout")
    def force_logout(self, request, id=None):
        user = self.get_object()
        Session.objects.filter(user=user).delete()
        ActivityLog.objects.create(user=request.user, event="USER_FORCE_LOGOUT", details={"target_user": user.email})
        return Response({"detail": f"User {user.email} sessions revoked successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, id=None):
        user = self.get_object()
        new_password = request.data.get("password")
        if not new_password:
            return Response({"error": "Password parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        ActivityLog.objects.create(user=request.user, event="USER_PASSWORD_RESET_ADMIN", details={"target_user": user.email})
        return Response({"detail": "User password reset successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="assign-role")
    def assign_role(self, request, id=None):
        user = self.get_object()
        role_name = request.data.get("role")
        if not role_name:
            return Response({"error": "Role name parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            role = Role.objects.get(name=role_name.upper())
            user.role = role
            user.save(update_fields=["role"])
            ActivityLog.objects.create(user=request.user, event="USER_ROLE_ASSIGNED", details={"target_user": user.email, "role": role.name})
            return Response({"detail": f"Role {role.name} assigned successfully."}, status=status.HTTP_200_OK)
        except Role.DoesNotExist:
            return Response({"error": f"Role {role_name} does not exist."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], url_path="remove-role")
    def remove_role(self, request, id=None):
        user = self.get_object()
        # Fallback to student role
        try:
            student_role, _ = Role.objects.get_or_create(name="STUDENT")
            user.role = student_role
            user.save(update_fields=["role"])
            ActivityLog.objects.create(user=request.user, event="USER_ROLE_REVOKED", details={"target_user": user.email})
            return Response({"detail": "Role reset to STUDENT successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def devices(self, request, id=None):
        user = self.get_object()
        devices = Device.objects.filter(user=user)
        data = [{"id": d.id, "token": d.device_token, "type": d.device_type, "created_at": d.created_at} for d in devices]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="login-history")
    def login_history(self, request, id=None):
        user = self.get_object()
        activities = ActivityLog.objects.filter(user=user, event="USER_LOGIN").order_by("-created_at")[:50]
        data = [{"id": a.id, "ip_address": a.details.get("ip_address", "Unknown"), "user_agent": a.details.get("user_agent", "Unknown"), "created_at": a.created_at} for a in activities]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="activity-timeline")
    def activity_timeline(self, request, id=None):
        user = self.get_object()
        activities = ActivityLog.objects.filter(user=user).order_by("-created_at")[:50]
        data = [{"id": a.id, "event": a.event, "details": a.details, "created_at": a.created_at} for a in activities]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def sessions(self, request, id=None):
        user = self.get_object()
        sessions = Session.objects.filter(user=user)
        return Response(SessionAdminSerializer(sessions, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="revoke-session")
    def revoke_session(self, request, id=None):
        sid = request.data.get("session_id")
        if not sid:
            return Response({"error": "session_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        Session.objects.filter(id=sid, user_id=id).delete()
        return Response({"detail": "Session revoked successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="bulk-action")
    def bulk_action(self, request):
        ser = BulkActionSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_ids = ser.validated_data["user_ids"]
        action_type = ser.validated_data["action_type"]
        
        users = User.objects.filter(id__in=user_ids)
        with transaction.atomic():
            if action_type == "SUSPEND" or action_type == "BLOCK":
                users.update(is_active=False)
            elif action_type == "ACTIVATE" or action_type == "UNBLOCK":
                users.update(is_active=True)
            elif action_type == "DELETE":
                # soft delete
                for u in users:
                    u.delete()
            elif action_type == "FORCE_LOGOUT":
                Session.objects.filter(user__id__in=user_ids).delete()
            elif action_type == "VERIFY":
                for u in users:
                    profile, _ = UserProfile.objects.get_or_create(user=u)
                    profile.settings["is_verified"] = True
                    profile.save()
            elif action_type == "UNVERIFY":
                for u in users:
                    profile, _ = UserProfile.objects.get_or_create(user=u)
                    profile.settings["is_verified"] = False
                    profile.save()

        ActivityLog.objects.create(user=request.user, event="BULK_ACTION_EXECUTE", details={"action": action_type, "count": users.count()})
        return Response({"detail": f"Bulk action {action_type} executed on {users.count()} users."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def export(self, request):
        users = self.get_queryset()
        
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["ID", "Email", "Role", "Is Active", "Is Staff", "Created At"])
        for u in users:
            writer.writerow([u.id, u.email, u.role.name if u.role else "", u.is_active, u.is_staff, u.created_at])
            
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="exported_users.csv"'
        return response


class AdminRBACViewSet(viewsets.ViewSet):
    """
    Module 3 — Enterprise RBAC Management Control Centre.
    Configures platform-wide security policies, permission matrix, and role hierarchy.
    """
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list_roles": "control:rbac:view",
        "create_role": "control:rbac:create",
        "list_permissions": "control:rbac:view",
        "permission_matrix": "control:rbac:view",
        "assign_permissions": "control:rbac:update",
        "role_hierarchy": "control:rbac:view",
        "permission_audit": "control:rbac:view",
    }

    @action(detail=False, methods=["get"], url_path="roles")
    def list_roles(self, request):
        roles = Role.objects.all().order_by("name")
        return Response(RoleSerializer(roles, many=True).data)

    @action(detail=False, methods=["post"], url_path="roles/create")
    def create_role(self, request):
        ser = RoleSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        role, created = Role.objects.get_or_create(
            name=ser.validated_data["name"].upper(),
            defaults={"description": ser.validated_data.get("description", "")}
        )
        return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="permissions")
    def list_permissions(self, request):
        permissions = Permission.objects.all().order_by("codename")
        return Response(PermissionSerializer(permissions, many=True).data)

    @action(detail=False, methods=["get"], url_path="matrix")
    def permission_matrix(self, request):
        roles = Role.objects.all()
        perms = Permission.objects.all()
        mappings = RolePermission.objects.select_related("role", "permission").all()
        
        matrix = {}
        for r in roles:
            matrix[r.name] = []
            
        for m in mappings:
            if m.role.name in matrix:
                matrix[m.role.name].append(m.permission.codename)
                
        return Response({
            "roles": [r.name for r in roles],
            "permissions": [p.codename for p in perms],
            "matrix": matrix
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="assign-permissions")
    def assign_permissions(self, request):
        role_name = request.data.get("role")
        perm_codenames = request.data.get("permissions", [])
        if not role_name:
            return Response({"error": "role parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            role = Role.objects.get(name=role_name.upper())
            with transaction.atomic():
                # Clear existing mappings for role and re-insert
                RolePermission.objects.filter(role=role).delete()
                for cn in perm_codenames:
                    perm, _ = Permission.objects.get_or_create(codename=cn)
                    RolePermission.objects.get_or_create(role=role, permission=perm)
            ActivityLog.objects.create(user=request.user, event="ROLE_PERMISSIONS_UPDATED", details={"role": role.name, "count": len(perm_codenames)})
            return Response({"detail": "Role permissions synchronized successfully."}, status=status.HTTP_200_OK)
        except Role.DoesNotExist:
            return Response({"error": f"Role {role_name} does not exist."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], url_path="hierarchy")
    def role_hierarchy(self, request):
        # Human-readable hierarchical visual design layout
        hierarchy = [
            {
                "role": "SUPERADMIN",
                "inherits_from": [],
                "privilege_level": 100,
                "description": "Total system sovereignty"
            },
            {
                "role": "ADMIN",
                "inherits_from": ["TEACHER", "MODERATOR"],
                "privilege_level": 80,
                "description": "Administrative supervision"
            },
            {
                "role": "TEACHER",
                "inherits_from": ["STUDENT"],
                "privilege_level": 50,
                "description": "Curriculum management & assessment evaluation"
            },
            {
                "role": "MODERATOR",
                "inherits_from": ["STUDENT"],
                "privilege_level": 40,
                "description": "Forum & blog post community moderation"
            },
            {
                "role": "STUDENT",
                "inherits_from": [],
                "privilege_level": 10,
                "description": "Standard portal study accesses"
            }
        ]
        return Response(hierarchy, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="audit")
    def permission_audit(self, request):
        # Scans for dangling permissions, roles without permission or users with administrative roles
        roles_with_no_perms = []
        for r in Role.objects.all():
            if not r.role_permissions.exists():
                roles_with_no_perms.append(r.name)
                
        admin_users_count = User.objects.filter(role__name__in=["SUPERADMIN", "ADMIN"]).count()
        return Response({
            "roles_with_no_permissions": roles_with_no_perms,
            "total_admin_users": admin_users_count,
            "compliance_status": "SECURE" if admin_users_count < 10 else "WARNING_HIGH_ADMIN_COUNT",
            "last_audit_run": datetime.now().isoformat()
        }, status=status.HTTP_200_OK)
