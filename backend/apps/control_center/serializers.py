from rest_framework import serializers
from apps.control_center.models import (
    Theme, PlatformSetting, DashboardWidget, AdministrativeTask, SystemAuditLog,
    ActivityLog, AnalyticsEvent, AIConversation, AIMessage, AIFeedback, MediaFile
)


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ["id", "name", "colors", "is_active", "created_at", "updated_at"]


class PlatformSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformSetting
        fields = ["id", "key", "value", "description", "updated_at"]


class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = ["id", "title", "metric_type", "query_target", "color_scheme", "icon_name", "display_order", "is_active", "required_role"]


class AdministrativeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministrativeTask
        fields = ["id", "title", "description", "category", "status", "payload", "created_at", "resolved_at", "resolved_by"]


class SystemAuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.ReadOnlyField(source="actor.email")

    class Meta:
        model = SystemAuditLog
        fields = ["id", "actor", "actor_email", "action_type", "target_table", "before_state", "after_state", "ip_address", "created_at"]


class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = ActivityLog
        fields = ["id", "user", "user_email", "event", "details", "created_at"]


class AnalyticsEventSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = AnalyticsEvent
        fields = ["id", "user", "user_email", "metric_name", "metric_value", "context_data", "created_at"]


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ["id", "conversation", "sender_type", "content", "token_count", "created_at", "updated_at"]


class AIConversationSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    messages = AIMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AIConversation
        fields = ["id", "user", "user_email", "title", "messages", "created_at", "updated_at"]


class AIFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIFeedback
        fields = ["id", "message", "is_positive", "feedback_text", "created_at"]


class MediaFileSerializer(serializers.ModelSerializer):
    uploader_email = serializers.ReadOnlyField(source="uploader.email")

    class Meta:
        model = MediaFile
        fields = ["id", "uploader", "uploader_email", "file_name", "file_url", "file_type", "file_size", "purpose", "version", "created_at", "updated_at"]
