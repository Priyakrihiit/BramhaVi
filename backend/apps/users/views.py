from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

from apps.users.models import Role, Permission, RolePermission, Session, Device, UserProfile, Notification, Organization, OrganizationMember, LoginHistory, Capability, UserCapability, CapabilityPermission, CapabilityApplication
from apps.users.permissions import HasRBACPermission, IsAdminOrSelf, IsAdminOrOwner
from apps.users.serializers import (
    PermissionSerializer, RolePermissionSerializer, RoleSerializer,
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    SessionSerializer, DeviceSerializer, NotificationSerializer,
    OrganizationSerializer, OrganizationMemberSerializer, LoginHistorySerializer,
    CapabilitySerializer, UserCapabilitySerializer
)

User = get_user_model()


class EnterprisePagination(PageNumberPagination):
    """
    Standard enterprise pagination class specifying default page size and size override parameter.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all().order_by("codename")
    serializer_class = PermissionSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["codename", "description"]
    ordering_fields = ["codename", "created_at"]
    ordering = ["codename"]
    required_permissions = {
        "list": "users:permission:view",
        "retrieve": "users:permission:view",
        "create": "users:permission:create",
        "update": "users:permission:update",
        "partial_update": "users:permission:update",
        "destroy": "users:permission:delete",
    }


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.select_related("role", "permission").all()
    serializer_class = RolePermissionSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["role__name", "permission__codename"]
    ordering_fields = ["role__name"]
    ordering = ["role__name"]
    required_permissions = {
        "list": "users:role_permission:view",
        "retrieve": "users:role_permission:view",
        "create": "users:role_permission:create",
        "update": "users:role_permission:update",
        "partial_update": "users:role_permission:update",
        "destroy": "users:role_permission:delete",
    }


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by("name")
    serializer_class = RoleSerializer
    permission_classes = [HasRBACPermission]
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    required_permissions = {
        "list": "users:role:view",
        "retrieve": "users:role:view",
        "create": "users:role:create",
        "update": "users:role:update",
        "partial_update": "users:role:update",
        "destroy": "users:role:delete",
    }


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSelf]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email", "profile__first_name", "profile__last_name"]
    ordering_fields = ["email", "created_at"]
    ordering = ["email"]
    required_permissions = {
        "list": "users:user:view",
        "retrieve": "users:user:view",
        "create": "users:user:create",
        "update": "users:user:update",
        "partial_update": "users:user:update",
        "destroy": "users:user:delete",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return User.objects.none()

        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_admin = user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])

        # Soft delete filtering based on include_deleted and admin privileges
        if include_deleted and is_admin:
            queryset = User.all_objects.select_related("role", "profile").all()
        else:
            queryset = User.objects.select_related("role", "profile").all()

        # Field-based Filtering
        # 1. is_active
        is_active_param = self.request.query_params.get("is_active")
        if is_active_param is not None:
            queryset = queryset.filter(is_active=is_active_param.lower() == "true")

        # 2. role (UUID or exact name)
        role_param = self.request.query_params.get("role")
        if role_param:
            queryset = queryset.filter(Q(role__id=role_param) | Q(role__name__iexact=role_param))

        # 3. email (icontains)
        email_param = self.request.query_params.get("email")
        if email_param:
            queryset = queryset.filter(email__icontains=email_param)

        return queryset.order_by("email")

    def get_serializer_class(self):
        if self.action == "register":
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"success": False, "message": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({
                "success": False, 
                "message": "Invalid credentials. Please use admin@brahmavidya.edu, teacher@brahmavidya.edu or student@brahmavidya.edu."
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        from django.utils import timezone
        if user.locked_until and user.locked_until > timezone.now():
            diff = user.locked_until - timezone.now()
            mins = int(diff.total_seconds() / 60) or 1
            return Response({
                "success": False,
                "message": f"Account locked due to multiple failed login attempts. Try again in {mins} minutes."
            }, status=status.HTTP_403_FORBIDDEN)
            
        if not user.check_password(password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                from datetime import timedelta
                user.locked_until = timezone.now() + timedelta(minutes=15)
            user.save()
            
            # Log failed attempt
            LoginHistory.objects.create(
                user=user,
                email_attempted=email,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT"),
                is_successful=False
            )
            return Response({
                "success": False,
                "message": "Invalid password."
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        # Reset counters on success
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save()
        
        # Log successful attempt
        LoginHistory.objects.create(
            user=user,
            email_attempted=email,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT"),
            is_successful=True
        )
        
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        permissions_list = list(user.get_all_permissions_set())
        
        return Response({
            "success": True,
            "token": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "profileId": str(user.profile.id) if hasattr(user, "profile") else "",
                "email": user.email,
                "fullName": f"{user.profile.first_name} {user.profile.last_name}" if hasattr(user, "profile") else user.email,
                "roleId": str(user.role.id) if user.role else "",
                "roleName": user.role.name if user.role else "",
                "status": "ACTIVE",
                "avatarUrl": user.profile.avatar_url if hasattr(user, "profile") else "",
                "walletBalance": float(user.wallet.balance) if hasattr(user, "wallet") else 0.0,
                "capabilities": UserCapabilitySerializer(user.capabilities.filter(status="ACTIVE"), many=True).data
            },
            "permissions": permissions_list
        })

    @action(detail=False, methods=["get", "put", "patch"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == "GET":
            permissions_list = list(user.get_all_permissions_set())
            
            return Response({
                "success": True,
                "user": {
                    "id": str(user.id),
                    "profileId": str(user.profile.id) if hasattr(user, "profile") else "",
                    "email": user.email,
                    "fullName": f"{user.profile.first_name} {user.profile.last_name}" if hasattr(user, "profile") else user.email,
                    "roleId": str(user.role.id) if user.role else "",
                    "roleName": user.role.name if user.role else "",
                    "status": "ACTIVE",
                    "avatarUrl": user.profile.avatar_url if hasattr(user, "profile") else "",
                    "walletBalance": float(user.wallet.balance) if hasattr(user, "wallet") else 0.0,
                    "capabilities": UserCapabilitySerializer(user.capabilities.filter(status="ACTIVE"), many=True).data
                },
                "permissions": permissions_list
            })
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Invalidate the access token by blacklisting its JTI
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header.split(" ")[1]
                from rest_framework_simplejwt.tokens import AccessToken
                try:
                    token = AccessToken(access_token)
                    jti = token.get("jti")
                    exp = token.get("exp")
                    if jti and exp:
                        from django.core.cache import cache
                        from django.utils.timezone import now
                        remaining = exp - int(now().timestamp())
                        if remaining > 0:
                            cache.set(f"blacklist:{jti}", "true", timeout=remaining)
                except Exception:
                    pass

            return Response({"success": True, "message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def restore(self, request, id=None):
        # Allow restoring soft-deleted user (admins only)
        user = self.request.user
        is_admin = user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        if not is_admin:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        target_user = User.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not target_user:
            return Response({"detail": "User not found or not deleted."}, status=status.HTTP_404_NOT_FOUND)
        target_user.restore()
        return Response({"detail": "User restored successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def forgot_password(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"success": False, "message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"success": True, "message": "If the email exists, a reset code has been sent."}, status=status.HTTP_200_OK)
        
        reset_code = "123456"
        print(f"[RESET CODE SIMULATION] Reset code for {email} is {reset_code}")
        
        user.profile.settings["reset_code"] = reset_code
        user.profile.save()
        
        from apps.control_center.models import SystemAuditLog
        SystemAuditLog.objects.create(
            actor=user,
            action_type="PASSWORD_RESET_REQUESTED",
            target_table="users",
            after_state={"email": email}
        )
        return Response({"success": True, "message": "If the email exists, a reset code has been sent."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def reset_password(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("new_password")
        
        if not email or not code or not new_password:
            return Response({"success": False, "message": "Email, code, and new_password are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.filter(email=email).first()
        if not user or user.profile.settings.get("reset_code") != code:
            return Response({"success": False, "message": "Invalid email or reset code"}, status=status.HTTP_400_BAD_REQUEST)
            
        from apps.users.validators import validate_password_complexity
        from django.core.exceptions import ValidationError
        try:
            validate_password_complexity(new_password)
        except ValidationError as e:
            return Response({"success": False, "message": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)
            
        user.set_password(new_password)
        user.profile.settings.pop("reset_code", None)
        user.profile.save()
        user.save()
        
        from apps.control_center.models import SystemAuditLog
        SystemAuditLog.objects.create(
            actor=user,
            action_type="PASSWORD_RESET_COMPLETED",
            target_table="users"
        )
        return Response({"success": True, "message": "Password reset completed successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        
        if not old_password or not new_password:
            return Response({"success": False, "message": "old_password and new_password are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if not user.check_password(old_password):
            return Response({"success": False, "message": "Invalid old password"}, status=status.HTTP_400_BAD_REQUEST)
            
        from apps.users.validators import validate_password_complexity
        from django.core.exceptions import ValidationError
        try:
            validate_password_complexity(new_password)
        except ValidationError as e:
            return Response({"success": False, "message": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)
            
        user.set_password(new_password)
        user.save()
        
        from apps.control_center.models import SystemAuditLog
        SystemAuditLog.objects.create(
            actor=user,
            action_type="PASSWORD_CHANGED",
            target_table="users"
        )
        return Response({"success": True, "message": "Password changed successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def verify_email(self, request):
        user = request.user
        code = request.data.get("code")
        if not code:
            return Response({"success": False, "message": "Code is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if code != "123456":
            return Response({"success": False, "message": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
            
        user.profile.settings["is_email_verified"] = True
        user.profile.save()
        
        from apps.control_center.models import SystemAuditLog
        SystemAuditLog.objects.create(
            actor=user,
            action_type="EMAIL_VERIFIED",
            target_table="users"
        )
        return Response({"success": True, "message": "Email verified successfully."}, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminOrSelf]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "bio"]
    ordering_fields = ["first_name", "last_name", "created_at"]
    ordering = ["first_name", "last_name"]
    required_permissions = {
        "list": "users:profile:view",
        "retrieve": "users:profile:view",
        "create": "users:profile:create",
        "update": "users:profile:update",
        "partial_update": "users:profile:update",
        "destroy": "users:profile:delete",
    }

    def get_queryset(self):
        queryset = self.queryset
        # Filtering by user
        user_param = self.request.query_params.get("user")
        if user_param:
            queryset = queryset.filter(user_id=user_param)

        # Filtering by first_name/last_name
        first_name = self.request.query_params.get("first_name")
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        last_name = self.request.query_params.get("last_name")
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.select_related("user").all()
    serializer_class = SessionSerializer
    permission_classes = [IsAdminOrOwner]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["ip_address", "user_agent"]
    ordering_fields = ["created_at", "expires_at"]
    ordering = ["-created_at"]
    required_permissions = {
        "list": "users:session:view",
        "retrieve": "users:session:view",
        "create": "users:session:create",
        "update": "users:session:update",
        "partial_update": "users:session:update",
        "destroy": "users:session:delete",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Session.objects.none()

        is_admin = user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])

        # Filter by user owner unless admin
        if is_admin:
            queryset = self.queryset
            # Admins can filter by custom user
            user_param = self.request.query_params.get("user")
            if user_param:
                queryset = queryset.filter(user_id=user_param)
        else:
            queryset = self.queryset.filter(user=user)

        # Field-based Filtering
        ip_param = self.request.query_params.get("ip_address")
        if ip_param:
            queryset = queryset.filter(ip_address=ip_param)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        is_admin = user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        if is_admin and "user" in self.request.data:
            serializer.save()
        else:
            serializer.save(user=user)


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related("user").all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAdminOrOwner]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["device_token", "device_type"]
    ordering_fields = ["created_at", "device_type"]
    ordering = ["-created_at"]
    required_permissions = {
        "list": "users:device:view",
        "retrieve": "users:device:view",
        "create": "users:device:create",
        "update": "users:device:update",
        "partial_update": "users:device:update",
        "destroy": "users:device:delete",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Device.objects.none()

        is_admin = user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])

        # Filter by user owner unless admin
        if is_admin:
            queryset = self.queryset
            user_param = self.request.query_params.get("user")
            if user_param:
                queryset = queryset.filter(user_id=user_param)
        else:
            queryset = self.queryset.filter(user=user)

        # Field-based Filtering
        device_type_param = self.request.query_params.get("device_type")
        if device_type_param:
            queryset = queryset.filter(device_type__iexact=device_type_param)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        is_admin = user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        if is_admin and "user" in self.request.data:
            serializer.save()
        else:
            serializer.save(user=user)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related("user").all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminOrOwner]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "is_read"]
    ordering = ["-created_at"]
    required_permissions = {
        "list": "users:notification:view",
        "retrieve": "users:notification:view",
        "create": "users:notification:create",
        "update": "users:notification:update",
        "partial_update": "users:notification:update",
        "destroy": "users:notification:delete",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Notification.objects.none()

        is_admin = user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])

        # Filter by user owner unless admin
        if is_admin:
            queryset = self.queryset
            user_param = self.request.query_params.get("user")
            if user_param:
                queryset = queryset.filter(user_id=user_param)
        else:
            queryset = self.queryset.filter(user=user)

        # Field-based Filtering
        is_read_param = self.request.query_params.get("is_read")
        if is_read_param is not None:
            queryset = queryset.filter(is_read=is_read_param.lower() == "true")

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        is_admin = user.is_superuser or (hasattr(user, "role") and user.role and user.role.name in ["SUPERADMIN", "ADMIN"])
        if is_admin and "user" in self.request.data:
            serializer.save()
        else:
            serializer.save(user=user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, id=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response({"status": "read", "id": notification.id}, status=status.HTTP_200_OK)


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    pagination_class = EnterprisePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "subdomain"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    @action(detail=True, methods=["post"])
    def invite(self, request, id=None):
        org = self.get_object()
        email = request.data.get("email")
        role_name = request.data.get("role_name", "MEMBER")
        if not email:
            return Response({"success": False, "message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        target_user = User.objects.filter(email=email).first()
        if not target_user:
            return Response({"success": False, "message": "Invited user does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
        member, created = OrganizationMember.objects.get_or_create(
            organization=org,
            user=target_user,
            defaults={"role_name": role_name}
        )
        return Response({"success": True, "message": "User invited/added successfully.", "member_id": str(member.id)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="resolve-tenant")
    def resolve_tenant(self, request):
        subdomain = request.query_params.get("subdomain")
        if not subdomain:
            return Response({"detail": "subdomain query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        org = Organization.objects.filter(subdomain=subdomain).first()
        if not org:
            return Response({"detail": "Tenant not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrganizationSerializer(org).data, status=status.HTTP_200_OK)


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    queryset = OrganizationMember.objects.select_related("organization", "user").all()
    serializer_class = OrganizationMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    pagination_class = EnterprisePagination


class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LoginHistory.objects.select_related("user").all()
    serializer_class = LoginHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    pagination_class = EnterprisePagination

    def get_queryset(self):
        user = self.request.user
        is_admin = user.is_superuser or user.is_admin_cbac
        if is_admin:
            return self.queryset
        return self.queryset.filter(user=user)


class CapabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and retrieve all system capabilities.
    """
    queryset = Capability.objects.filter(is_active=True).order_by("display_order")
    serializer_class = CapabilitySerializer
    permission_classes = [permissions.AllowAny]


class UserCapabilityViewSet(viewsets.ViewSet):
    """
    Manage capabilities for the currently authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def me(self, request):
        user = request.user
        caps = user.capabilities.all()
        return Response(UserCapabilitySerializer(caps, many=True).data)

    @action(detail=False, methods=["post"], url_path="(?P<code>[^/.]+)/request")
    def request_capability(self, request, code=None):
        user = request.user
        try:
            capability = Capability.objects.get(codename=code, is_active=True)
        except Capability.DoesNotExist:
            return Response({"detail": f"Capability {code} not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

        user_cap, created = UserCapability.objects.get_or_create(
            user=user,
            capability=capability,
            defaults={"status": "PENDING"}
        )

        if not created:
            if user_cap.status == "ACTIVE":
                return Response({"detail": "Capability is already active."}, status=status.HTTP_400_BAD_REQUEST)
            elif user_cap.status == "PENDING":
                return Response({"detail": "Capability request is already pending review."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user_cap.status = "PENDING"
                user_cap.save()

        # If it is an instant capability, auto-approve it immediately!
        if capability.category == "INSTANT":
            user_cap.status = "ACTIVE"
            user_cap.activated_at = timezone.now()
            user_cap.save()
            return Response({"detail": f"Capability {code} auto-activated instantly.", "status": "ACTIVE"})

        # Else, create a CapabilityApplication record
        application_data = request.data.get("application_data", {})
        CapabilityApplication.objects.create(
            user=user,
            capability=capability,
            status="PENDING",
            application_data=application_data
        )

        return Response({"detail": f"Capability {code} request submitted.", "status": "PENDING"})

    @action(detail=False, methods=["post"], url_path="(?P<code>[^/.]+)/deactivate")
    def deactivate_capability(self, request, code=None):
        user = request.user
        user_cap = UserCapability.objects.filter(user=user, capability__codename=code).first()
        if not user_cap or user_cap.status != "ACTIVE":
            return Response({"detail": "Active capability not found."}, status=status.HTTP_404_NOT_FOUND)

        user_cap.status = "DEACTIVATED"
        user_cap.deactivated_at = timezone.now()
        user_cap.save()
        return Response({"detail": f"Capability {code} voluntarily deactivated.", "status": "DEACTIVATED"})

    @action(detail=False, methods=["post"], url_path="(?P<code>[^/.]+)/reactivate")
    def reactivate_capability(self, request, code=None):
        user = request.user
        user_cap = UserCapability.objects.filter(user=user, capability__codename=code).first()
        if not user_cap or user_cap.status != "DEACTIVATED":
            return Response({"detail": "Deactivated capability not found."}, status=status.HTTP_404_NOT_FOUND)

        user_cap.status = "ACTIVE"
        user_cap.activated_at = timezone.now()
        user_cap.save()
        return Response({"detail": f"Capability {code} reactivated.", "status": "ACTIVE"})


from apps.users.cbac_permissions import HasCapabilityPermission

class CapabilityApplicationViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for reviewing and managing capability applications.
    """
    queryset = CapabilityApplication.objects.select_related("user", "capability").all().order_by("-submitted_at")
    permission_classes = [HasCapabilityPermission]
    required_permission = "admin:capability:approve"
    pagination_class = EnterprisePagination

    def get_serializer_class(self):
        class CapabilityApplicationSerializer(serializers.ModelSerializer):
            user_email = serializers.ReadOnlyField(source="user.email")
            capability_codename = serializers.ReadOnlyField(source="capability.codename")
            class Meta:
                model = CapabilityApplication
                fields = "__all__"
        return CapabilityApplicationSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        app = self.get_object()
        if app.status != "PENDING":
            return Response({"detail": "Application is already processed."}, status=status.HTTP_400_BAD_REQUEST)

        app.status = "APPROVED"
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.review_notes = request.data.get("notes", "")
        app.save()

        # Activate the user capability
        user_cap, _ = UserCapability.objects.get_or_create(user=app.user, capability=app.capability)
        user_cap.status = "ACTIVE"
        user_cap.activated_at = timezone.now()
        user_cap.approved_by = request.user
        user_cap.save()

        return Response({"status": "APPROVED"})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        app = self.get_object()
        if app.status != "PENDING":
            return Response({"detail": "Application is already processed."}, status=status.HTTP_400_BAD_REQUEST)

        app.status = "REJECTED"
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.review_notes = request.data.get("notes", "")
        app.save()

        # Reject the user capability
        user_cap, _ = UserCapability.objects.get_or_create(user=app.user, capability=app.capability)
        user_cap.status = "REJECTED"
        user_cap.rejection_reason = request.data.get("notes", "")
        user_cap.save()

        return Response({"status": "REJECTED"})


class AdminUserCapabilityViewSet(viewsets.ViewSet):
    """
    Admin actions to suspend/reinstate any user's capabilities.
    """
    permission_classes = [HasCapabilityPermission]
    required_permission = "admin:user:manage"

    @action(detail=False, methods=["post"], url_path="(?P<user_id>[^/.]+)/capabilities/(?P<code>[^/.]+)/suspend")
    def suspend_capability(self, request, user_id=None, code=None):
        user_cap = UserCapability.objects.filter(user_id=user_id, capability__codename=code).first()
        if not user_cap or user_cap.status != "ACTIVE":
            return Response({"detail": "Active capability not found for user."}, status=status.HTTP_404_NOT_FOUND)

        user_cap.status = "SUSPENDED"
        user_cap.save()
        return Response({"status": "SUSPENDED"})

    @action(detail=False, methods=["post"], url_path="(?P<user_id>[^/.]+)/capabilities/(?P<code>[^/.]+)/reinstate")
    def reinstate_capability(self, request, user_id=None, code=None):
        user_cap = UserCapability.objects.filter(user_id=user_id, capability__codename=code).first()
        if not user_cap or user_cap.status != "SUSPENDED":
            return Response({"detail": "Suspended capability not found for user."}, status=status.HTTP_404_NOT_FOUND)

        user_cap.status = "ACTIVE"
        user_cap.save()
        return Response({"status": "ACTIVE"})
