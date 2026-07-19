from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.users.models import Role, Permission, RolePermission, Session, Device, UserProfile, Notification, Organization, OrganizationMember, LoginHistory, Capability, UserCapability, CapabilityPermission, CapabilityApplication

User = get_user_model()

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "codename", "description", "created_at"]


class RolePermissionSerializer(serializers.ModelSerializer):
    permission_codename = serializers.ReadOnlyField(source="permission.codename")

    class Meta:
        model = RolePermission
        fields = ["id", "role", "permission", "permission_codename"]


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True, source="role_permissions__permission")

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions", "created_at", "updated_at"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id", "first_name", "last_name", "avatar_url", "bio", "settings",
            "cover_image_url", "skills", "education", "experience", "projects",
            "languages", "achievements", "privacy_settings", "created_at", "updated_at"
        ]


class CapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Capability
        fields = ["id", "codename", "display_name", "category", "is_active", "default_settings", "display_order"]


class UserCapabilitySerializer(serializers.ModelSerializer):
    capability_codename = serializers.ReadOnlyField(source="capability.codename")
    capability_display_name = serializers.ReadOnlyField(source="capability.display_name")

    class Meta:
        model = UserCapability
        fields = ["id", "capability", "capability_codename", "capability_display_name", "status", "activated_at", "settings"]


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source="role.name")
    profile = UserProfileSerializer(read_only=True)
    capabilities = UserCapabilitySerializer(many=True, read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "role", "role_name", "is_active", "is_staff", 
            "profile", "capabilities", "permissions", "created_at", "updated_at"
        ]
        read_only_fields = ["is_staff"]

    def get_permissions(self, obj):
        return list(obj.get_all_permissions_set())


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["email", "password", "role", "first_name", "last_name"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile automatically
        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name
        )

        # Auto-grant instant capabilities
        instant_caps = Capability.objects.filter(category="INSTANT", is_active=True)
        for cap in instant_caps:
            UserCapability.objects.create(
                user=user,
                capability=cap,
                status="ACTIVE"
            )
        
        return user


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ["id", "user", "token_hash", "ip_address", "user_agent", "expires_at", "created_at"]


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "user", "device_token", "device_type", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user", "title", "message", "is_read", "created_at"]


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "subdomain", "org_type", "logo_url", "primary_color", "settings", "created_at", "updated_at"]


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = OrganizationMember
        fields = ["id", "organization", "user", "user_email", "role_name", "invited_at", "joined_at"]


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = ["id", "user", "email_attempted", "ip_address", "user_agent", "is_successful", "created_at"]
