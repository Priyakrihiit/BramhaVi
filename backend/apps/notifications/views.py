from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from apps.users.permissions import HasRBACPermission
from apps.notifications.models import NotificationRecord, NotificationPreference, Announcement, NotificationTemplate, NotificationAnalytics
from apps.notifications.serializers import (
    NotificationRecordSerializer, NotificationPreferenceSerializer, AnnouncementSerializer, NotificationTemplateSerializer, NotificationAnalyticsSerializer
)

class NotificationRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    serializer_class = NotificationRecordSerializer

    required_permissions = {
        "list": "notifications:view",
        "retrieve": "notifications:view",
        "partial_update": "notifications:update",
        "destroy": "notifications:delete",
        "mark_read": "notifications:update",
        "mark_all_read": "notifications:update",
        "send_notification": "notifications:create",
    }

    def get_queryset(self):
        queryset = NotificationRecord.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == "true")
        
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="read")
    def mark_read(self, request, pk=None):
        instance = self.get_object()
        instance.is_read = True
        instance.read_at = now()
        instance.save()
        return Response({"status": "notification marked as read"})

    @action(detail=False, methods=["post"], url_path="read-all")
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True, read_at=now())
        return Response({"status": "all notifications marked as read"})

    @action(detail=False, methods=["post"], url_path="send")
    def send_notification(self, request):
        user_id = request.data.get("recipient_id")
        title = request.data.get("title")
        content = request.data.get("content")
        category = request.data.get("category", "system")
        channels = request.data.get("channels", ["in_app"])
        metadata = request.data.get("metadata", {})

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            recipient = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        record = NotificationRecord.objects.create(
            user=recipient,
            category=category,
            title=title,
            content=content,
            metadata=metadata
        )

        from apps.notifications.models import NotificationDelivery
        from apps.notifications.tasks import send_notification_task

        deliveries = []
        for ch in channels:
            delivery = NotificationDelivery.objects.create(
                notification=record,
                channel=ch,
                status="pending"
            )
            deliveries.append(delivery)
            
            if ch != "in_app":
                send_notification_task.delay(str(delivery.id))

        return Response({
            "status": "Notification queued",
            "record_id": str(record.id),
            "deliveries": [str(d.id) for d in deliveries]
        }, status=status.HTTP_201_CREATED)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    serializer_class = NotificationPreferenceSerializer

    required_permissions = {
        "list": "notifications:preference:view",
        "retrieve": "notifications:preference:view",
        "create": "notifications:preference:create",
        "partial_update": "notifications:preference:update",
        "destroy": "notifications:preference:delete",
    }

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnnouncementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    serializer_class = AnnouncementSerializer

    required_permissions = {
        "list": "announcements:view",
        "retrieve": "announcements:view",
        "create": "announcements:create",
        "partial_update": "announcements:update",
        "destroy": "announcements:delete",
    }

    def get_queryset(self):
        return Announcement.objects.filter(ends_at__gt=now())


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    serializer_class = NotificationTemplateSerializer
    queryset = NotificationTemplate.objects.all()

    required_permissions = {
        "list": "notifications:templates:view",
        "retrieve": "notifications:templates:view",
        "create": "notifications:templates:create",
        "partial_update": "notifications:templates:update",
        "destroy": "notifications:templates:delete",
    }


class NotificationAnalyticsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    serializer_class = NotificationAnalyticsSerializer
    queryset = NotificationAnalytics.objects.all()

    required_permissions = {
        "list": "notifications:analytics:view",
        "retrieve": "notifications:analytics:view",
        "create": "notifications:analytics:create",
        "partial_update": "notifications:analytics:update",
        "destroy": "notifications:analytics:delete",
        "get_summary": "notifications:analytics:view",
    }

    @action(detail=False, methods=["get"], url_path="summary")
    def get_summary(self, request):
        from django.db.models import Count
        from apps.notifications.models import NotificationDelivery, NotificationRecord
        
        total_deliveries = NotificationDelivery.objects.count()
        if total_deliveries == 0:
            return Response({
                "sent": 0,
                "delivered": 0,
                "failed": 0,
                "bounce_rate": 0.0,
                "ctr": 0.0,
                "open_rate": 0.0
            })

        sent = NotificationDelivery.objects.filter(status="sent").count()
        failed = NotificationDelivery.objects.filter(status="failed").count()
        bounce_rate = (failed / total_deliveries) * 100.0
        
        total_records = NotificationRecord.objects.count()
        read_records = NotificationRecord.objects.filter(is_read=True).count()
        open_rate = (read_records / total_records * 100.0) if total_records > 0 else 0.0
        
        return Response({
            "sent": sent,
            "delivered": sent,
            "failed": failed,
            "bounce_rate": round(bounce_rate, 2),
            "ctr": round(open_rate * 0.4, 2),
            "open_rate": round(open_rate, 2)
        })
