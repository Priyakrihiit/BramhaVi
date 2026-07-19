from django.db import models
from django.conf import settings
from apps.base_models import BaseModel, SoftDeleteModel

class NotificationTemplate(SoftDeleteModel):
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    body_html = models.TextField()
    body_text = models.TextField(blank=True)

    class Meta:
        db_table = "notification_templates"

    def __str__(self):
        return f"{self.name} ({self.code})"


class NotificationPreference(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences")
    category = models.CharField(max_length=100, db_index=True)  # e.g., 'auth', 'lms', 'wallet', 'marketing'
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_preferences"
        unique_together = ("user", "category")


class NotificationRecord(SoftDeleteModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_records")
    category = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "notification_records"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            try:
                import redis
                import json
                r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=2)
                payload = {
                    "user_id": str(self.user.id),
                    "event": "notification",
                    "data": {
                        "id": str(self.id),
                        "title": self.title,
                        "content": self.content,
                        "category": self.category,
                        "is_read": self.is_read,
                        "created_at": self.created_at.isoformat() if self.created_at else None
                    }
                }
                r.publish("notifications_pubsub", json.dumps(payload))
            except Exception:
                pass


class NotificationDelivery(BaseModel):
    CHANNEL_CHOICES = (
        ("email", "Email"),
        ("sms", "SMS"),
        ("push", "Push"),
        ("in_app", "In-App"),
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    )
    notification = models.ForeignKey(NotificationRecord, on_delete=models.CASCADE, related_name="deliveries")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "notification_deliveries"


class Announcement(SoftDeleteModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    starts_at = models.DateTimeField(db_index=True)
    ends_at = models.DateTimeField(db_index=True)
    is_pinned = models.BooleanField(default=False, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "announcements"
        ordering = ["-is_pinned", "-created_at"]


class NotificationAnalytics(BaseModel):
    category = models.CharField(max_length=100, db_index=True)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    retry_count = models.IntegerField(default=0)
    avg_delivery_time_ms = models.FloatField(default=0.0)
    date = models.DateField(db_index=True)

    class Meta:
        db_table = "notification_analytics"
        ordering = ["-date"]
