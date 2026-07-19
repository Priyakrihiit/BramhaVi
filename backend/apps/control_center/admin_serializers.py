from rest_framework import serializers

# ==========================================
# SERIALIZERS FOR SYSTEM ADMIN CONTROL CENTER
# ==========================================

class DashboardWidgetSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField(max_length=100)
    metric_type = serializers.CharField(max_length=30)
    query_target = serializers.CharField(max_length=255)
    color_scheme = serializers.CharField(max_length=50)
    icon_name = serializers.CharField(max_length=50)
    display_order = serializers.IntegerField()
    is_active = serializers.BooleanField()
    required_role = serializers.CharField(max_length=100)


class RoleSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)


class PermissionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    codename = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)


class UserAdminSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    role_name = serializers.CharField(read_only=True, source="role.name")
    is_active = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)


class UserProfileAdminSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    avatar_url = serializers.CharField(max_length=512, required=False, allow_blank=True)
    bio = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    settings = serializers.JSONField(default=dict)


class SessionAdminSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    ip_address = serializers.IPAddressField(read_only=True)
    user_agent = serializers.CharField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class CertificateSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    student_id = serializers.CharField()
    student_email = serializers.EmailField()
    course_title = serializers.CharField()
    issued_at = serializers.DateTimeField(read_only=True)
    certificate_url = serializers.URLField()
    status = serializers.CharField(default="ACTIVE")


class BadgeSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    student_id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()
    awarded_at = serializers.DateTimeField(read_only=True)


class CouponAdminSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    code = serializers.CharField(max_length=50)
    discount_percentage = serializers.FloatField()
    is_active = serializers.BooleanField(default=True)
    expires_at = serializers.DateTimeField()


class SubscriptionAdminSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    website_id = serializers.CharField()
    tier = serializers.CharField()
    status = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = serializers.CharField()
    expires_at = serializers.DateTimeField()


class AIModelSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    provider = serializers.CharField()
    is_active = serializers.BooleanField(default=True)
    token_limit = serializers.IntegerField()
    cost_per_million = serializers.FloatField()
    average_response_time = serializers.FloatField()


class PromptTemplateSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    system_instruction = serializers.CharField()
    temperature = serializers.FloatField(default=0.7)
    max_tokens = serializers.IntegerField(default=1024)


class CommunitySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    member_count = serializers.IntegerField(default=0)
    is_active = serializers.BooleanField(default=True)


class ModerationItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    entity_type = serializers.CharField()
    entity_id = serializers.CharField()
    reported_by = serializers.CharField()
    reason = serializers.CharField()
    status = serializers.CharField(default="PENDING")
    created_at = serializers.DateTimeField(read_only=True)


class PlatformSettingAdminSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    key = serializers.CharField()
    value = serializers.JSONField()
    description = serializers.CharField(required=False, allow_blank=True)


class BackupSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    backup_type = serializers.CharField()
    status = serializers.CharField(read_only=True)
    file_size_mb = serializers.FloatField(read_only=True)
    file_name = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class SystemAuditLogAdminSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    actor_email = serializers.EmailField(source="actor.email", read_only=True)
    action_type = serializers.CharField()
    target_table = serializers.CharField()
    before_state = serializers.JSONField()
    after_state = serializers.JSONField()
    ip_address = serializers.CharField()
    created_at = serializers.DateTimeField()


class BulkActionSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.CharField())
    action_type = serializers.ChoiceField(choices=["SUSPEND", "ACTIVATE", "BLOCK", "UNBLOCK", "VERIFY", "UNVERIFY", "DELETE", "FORCE_LOGOUT"])


class ExportRequestSerializer(serializers.Serializer):
    entity_type = serializers.ChoiceField(choices=["USERS", "REVENUE", "COURSES", "CERTIFICATES", "TRANSACTIONS", "ANALYTICS"])
    format = serializers.ChoiceField(choices=["CSV", "EXCEL", "PDF", "JSON"])
