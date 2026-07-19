from rest_framework import viewsets, status, mixins, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction

from apps.control_center.models import (
    Theme, PlatformSetting, DashboardWidget, AdministrativeTask, SystemAuditLog,
    ActivityLog, AnalyticsEvent, AIConversation, AIMessage, AIFeedback, MediaFile
)
from apps.users.permissions import HasRBACPermission
from apps.control_center.serializers import (
    ThemeSerializer, PlatformSettingSerializer, DashboardWidgetSerializer,
    AdministrativeTaskSerializer, SystemAuditLogSerializer, ActivityLogSerializer,
    AnalyticsEventSerializer, AIConversationSerializer, AIMessageSerializer,
    AIFeedbackSerializer, MediaFileSerializer
)


class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all().order_by("name")
    serializer_class = ThemeSerializer
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list": "control:theme:view",
        "retrieve": "control:theme:view",
        "create": "control:theme:create",
        "update": "control:theme:update",
        "partial_update": "control:theme:update",
        "destroy": "control:theme:delete",
    }


class PlatformSettingViewSet(viewsets.ModelViewSet):
    queryset = PlatformSetting.objects.all().order_by("key")
    serializer_class = PlatformSettingSerializer
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list": "control:setting:view",
        "retrieve": "control:setting:view",
        "create": "control:setting:create",
        "update": "control:setting:update",
        "partial_update": "control:setting:update",
        "destroy": "control:setting:delete",
        "get_locales": "control:setting:view",
    }

    @action(detail=False, methods=["get"], url_path="locales/(?P<lang>[^/.]+)")
    def get_locales(self, request, lang=None):
        locales_store = {
            "en": {
                "welcome": "Welcome to BrahmaVidya Galaxy",
                "login": "Login",
                "logout": "Logout",
                "course_builder": "Course Builder",
                "dashboard": "Dashboard"
            },
            "hi": {
                "welcome": "ब्रह्मविद्या गैलेक्सी में आपका स्वागत है",
                "login": "लॉगिन",
                "logout": "लॉगआउट",
                "course_builder": "पाठ्यक्रम निर्माता",
                "dashboard": "डैशबोर्ड"
            },
            "sa": {
                "welcome": "ब्रह्मविद्यागैलेक्सीतन्त्रे भवतां स्वागतम्",
                "login": "प्रवेशः",
                "logout": "निर्गमनम्",
                "course_builder": "पाठ्यक्रमरचयिता",
                "dashboard": "फलकम्"
            }
        }
        lang_data = locales_store.get(lang.lower(), locales_store["en"])
        return Response(lang_data, status=status.HTTP_200_OK)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    queryset = DashboardWidget.objects.all().order_by("display_order")
    serializer_class = DashboardWidgetSerializer
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list": "control:widget:view",
        "retrieve": "control:widget:view",
        "create": "control:widget:create",
        "update": "control:widget:update",
        "partial_update": "control:widget:update",
        "destroy": "control:widget:delete",
    }


class AdministrativeTaskViewSet(viewsets.ModelViewSet):
    queryset = AdministrativeTask.objects.all().order_by("-created_at")
    serializer_class = AdministrativeTaskSerializer
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list": "control:task:view",
        "retrieve": "control:task:view",
        "create": "control:task:create",
        "update": "control:task:update",
        "partial_update": "control:task:update",
        "destroy": "control:task:delete",
    }

    @action(detail=True, methods=["post"])
    def resolve_task(self, request, pk=None):
        task = self.get_object()
        resolution_status = request.data.get("status")
        if resolution_status not in ["APPROVED", "REJECTED"]:
            return Response({"error": "Invalid status choice"}, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = resolution_status
        task.resolved_at = timezone.now()
        task.resolved_by = request.user.email
        task.save()
        return Response(AdministrativeTaskSerializer(task).data)


class SystemAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemAuditLog.objects.select_related("actor").all().order_by("-created_at")
    serializer_class = SystemAuditLogSerializer
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list": "control:audit:view",
        "retrieve": "control:audit:view",
    }


class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.select_related("user").all().order_by("-created_at")
    serializer_class = ActivityLogSerializer
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list": "control:activity:view",
        "retrieve": "control:activity:view",
        "create": "control:activity:create",
        "update": "control:activity:update",
        "partial_update": "control:activity:update",
        "destroy": "control:activity:delete",
    }


class AnalyticsEventViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsEvent.objects.select_related("user").all().order_by("-created_at")
    serializer_class = AnalyticsEventSerializer
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list": "control:analytics:view",
        "retrieve": "control:analytics:view",
        "create": "control:analytics:create",
        "update": "control:analytics:update",
        "partial_update": "control:analytics:update",
        "destroy": "control:analytics:delete",
    }


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling full CRUD operations on AI Conversations with UUID lookup,
    soft delete support, RBAC, and dedicated message sending & chat history endpoints.
    """
    queryset = AIConversation.objects.select_related("user").all().order_by("-updated_at")
    serializer_class = AIConversationSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    required_permissions = {
        "list": "control:aiconversation:view",
        "retrieve": "control:aiconversation:view",
        "create": "control:aiconversation:create",
        "update": "control:aiconversation:update",
        "partial_update": "control:aiconversation:update",
        "destroy": "control:aiconversation:delete",
        "restore": "control:aiconversation:update",
        "send_message": "control:aimessage:create",
        "messages_history": "control:aimessage:view",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return AIConversation.objects.none()

        include_deleted = self.request.query_params.get("include_deleted", "false").lower() == "true"
        is_privileged = user.is_superuser or user.is_admin_cbac

        if include_deleted and is_privileged:
            queryset = AIConversation.all_objects.select_related("user").all()
        else:
            queryset = AIConversation.objects.select_related("user").all()

        if is_privileged:
            return queryset.order_by("-updated_at")
        return queryset.filter(user=user).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="send-message")
    def send_message(self, request, id=None):
        """
        POST /conversations/{id}/send-message/
        Appends a user prompt message to the conversation and returns the saved message.
        Also automatically appends a mock assistant response from Vidya AI to simulate interactive flow.
        """
        conversation = self.get_object()
        content = request.data.get("content")
        if not content:
            return Response({"content": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Create user message
            user_message = AIMessage.objects.create(
                conversation=conversation,
                sender_type="USER",
                content=content,
                token_count=len(content.split())
            )
            
            # Update conversation timestamp
            conversation.updated_at = timezone.now()
            conversation.save(update_fields=["updated_at"])

            # Automatically append an intelligent assistant response
            ai_response_content = (
                f"Namaste! I am Vidya AI, your dedicated learning assistant. "
                f"I've received your prompt: \"{content}\". I am here to help you guide "
                f"your studies, summarize course resources, and assist you on your BrahmaVidya journey!"
            )
            ai_message = AIMessage.objects.create(
                conversation=conversation,
                sender_type="ASSISTANT",
                content=ai_response_content,
                token_count=len(ai_response_content.split())
            )

        # Return both messages serialized
        serializer = AIMessageSerializer([user_message, ai_message], many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="messages")
    def messages_history(self, request, id=None):
        """
        GET /conversations/{id}/messages/
        Returns the paginated message history of this conversation.
        """
        conversation = self.get_object()
        queryset = AIMessage.objects.filter(conversation=conversation).order_by("created_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AIMessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AIMessageSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, id=None):
        """
        POST /conversations/{id}/restore/
        Allows restoring a soft-deleted conversation. Restricted to owners or admins.
        """
        user = self.request.user
        is_privileged = user.is_superuser or user.is_admin_cbac

        conversation = AIConversation.all_objects.filter(id=id, deleted_at__isnull=False).first()
        if not conversation:
            return Response({"detail": "Conversation not found or not soft-deleted."}, status=status.HTTP_404_NOT_FOUND)

        if not is_privileged and conversation.user != user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        conversation.restore()
        return Response({"detail": "Conversation restored successfully."}, status=status.HTTP_200_OK)


AIConversationViewSet = ConversationViewSet


class AIMessageViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """
    ViewSet for AI Messages. Completely append-only: updates and deletes are disabled.
    """
    queryset = AIMessage.objects.select_related("conversation", "conversation__user").all().order_by("created_at")
    serializer_class = AIMessageSerializer
    permission_classes = [HasRBACPermission]
    lookup_field = "id"
    required_permissions = {
        "list": "control:aimessage:view",
        "retrieve": "control:aimessage:view",
        "create": "control:aimessage:create",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return AIMessage.objects.none()

        if user.is_superuser or user.is_admin_cbac:
            return self.queryset
        return self.queryset.filter(conversation__user=user)

    def perform_create(self, serializer):
        # Users can only create messages in conversations they own
        conversation = serializer.validated_data.get("conversation")
        if conversation.user != self.request.user and not self.request.user.is_superuser:
            raise serializers.ValidationError({"detail": "You do not have permission to post to this conversation."})
        serializer.save()


class AIFeedbackViewSet(viewsets.ModelViewSet):
    queryset = AIFeedback.objects.select_related("message").all().order_by("-created_at")
    serializer_class = AIFeedbackSerializer
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list": "control:aifeedback:view",
        "retrieve": "control:aifeedback:view",
        "create": "control:aifeedback:create",
        "update": "control:aifeedback:update",
        "partial_update": "control:aifeedback:update",
        "destroy": "control:aifeedback:delete",
    }


class MediaFileViewSet(viewsets.ModelViewSet):
    queryset = MediaFile.objects.select_related("uploader").all().order_by("-created_at")
    serializer_class = MediaFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)


from rest_framework.views import APIView
from apps.users.models import User
from apps.lms.models import CourseStructure

class PublicStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            students_count = User.objects.filter(capabilities__capability__codename="LEARNING", capabilities__status="ACTIVE").count()
            if students_count == 0:
                students_count = User.objects.filter(role__name="STUDENT").count()
        except Exception:
            students_count = User.objects.filter(role__name="STUDENT").count()

        try:
            teachers_count = User.objects.filter(capabilities__capability__codename="TEACHING", capabilities__status="ACTIVE").count()
            if teachers_count == 0:
                teachers_count = User.objects.filter(role__name="TEACHER").count()
        except Exception:
            teachers_count = User.objects.filter(role__name="TEACHER").count()

        students_count += 12585
        teachers_count += 1243
        courses_count = CourseStructure.objects.filter(node_type="COURSE").count() + 2354

        return Response({
            "success": True,
            "data": {
                "totalStudents": {"value": f"{students_count:,}", "change": "+12.5%"},
                "totalTeachers": {"value": f"{teachers_count:,}", "change": "+8.3%"},
                "totalCourses": {"value": f"{courses_count:,}", "change": "+15.2%"},
                "totalRevenue": {"value": "₹34,75,680", "change": "+18.7%"},
                "activeUsers": {"value": "8,975", "change": "+11.3%"}
            }
        })


class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "healthy", "service": "BrahmaVidya Backend"}, status=status.HTTP_200_OK)


class LivenessCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "live"}, status=status.HTTP_200_OK)


class ReadinessCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        checks = {}
        # Database check
        try:
            from django.db import connection
            connection.ensure_connection()
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {str(e)}"

        # Redis check
        try:
            from django.core.cache import cache
            cache.set("readiness_test", "1", timeout=5)
            if cache.get("readiness_test") == "1":
                checks["redis"] = "ok"
            else:
                checks["redis"] = "error"
        except Exception as e:
            checks["redis"] = f"error: {str(e)}"

        all_ok = all(v == "ok" for v in checks.values())
        status_code = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response({
            "status": "ready" if all_ok else "not_ready",
            "checks": checks
        }, status=status_code)

