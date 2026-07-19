from rest_framework import serializers
from apps.notifications.models import NotificationRecord, NotificationPreference, Announcement, NotificationTemplate, NotificationAnalytics

class NotificationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRecord
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class NotificationAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationAnalytics
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
