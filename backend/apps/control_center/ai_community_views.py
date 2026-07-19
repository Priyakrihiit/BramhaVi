import uuid
from datetime import datetime
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import HasRBACPermission
from apps.users.models import User, Notification
from apps.control_center.models import AIConversation, AIMessage, AIFeedback
from apps.control_center.admin_serializers import (
    AIModelSerializer, PromptTemplateSerializer, CommunitySerializer, ModerationItemSerializer
)
from apps.control_center.admin_store import (
    get_admin_collection, save_admin_item, read_admin_store, write_admin_store
)

class AdminVidyaAIViewSet(viewsets.ViewSet):
    """
    Module 8 — Enterprise Vidya AI Assistant Administration.
    Manages active LLM models, system prompts, diagnostic tokens, and feedback logs.
    """
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list_models": "control:ai:view",
        "save_model": "control:ai:update",
        "list_templates": "control:ai:view",
        "save_template": "control:ai:update",
        "list_conversations": "control:ai:view",
        "feedback_logs": "control:ai:view",
        "blocked_prompts_list": "control:ai:view",
        "blocked_prompt_add": "control:ai:create",
    }

    # Models API
    @action(detail=False, methods=["get"], url_path="models")
    def list_models(self, request):
        models = get_admin_collection("ai_models")
        return Response(models, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="models/save")
    def save_model(self, request):
        ser = AIModelSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        model_id = request.data.get("id", f"model-{uuid.uuid4().hex[:8]}")
        model = {
            "id": model_id,
            "name": ser.validated_data["name"],
            "provider": ser.validated_data["provider"],
            "is_active": ser.validated_data.get("is_active", True),
            "token_limit": ser.validated_data["token_limit"],
            "cost_per_million": float(ser.validated_data["cost_per_million"]),
            "average_response_time": float(ser.validated_data["average_response_time"]),
            "deleted_at": None
        }
        save_admin_item("ai_models", model_id, model)
        return Response(model, status=status.HTTP_201_CREATED)

    # Templates API
    @action(detail=False, methods=["get"], url_path="templates")
    def list_templates(self, request):
        templates = get_admin_collection("prompt_templates")
        return Response(templates, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="templates/save")
    def save_template(self, request):
        ser = PromptTemplateSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        temp_id = request.data.get("id", f"prompt-{uuid.uuid4().hex[:8]}")
        template = {
            "id": temp_id,
            "name": ser.validated_data["name"],
            "system_instruction": ser.validated_data["system_instruction"],
            "temperature": float(ser.validated_data.get("temperature", 0.7)),
            "max_tokens": int(ser.validated_data.get("max_tokens", 1024)),
            "deleted_at": None
        }
        save_admin_item("prompt_templates", temp_id, template)
        return Response(template, status=status.HTTP_201_CREATED)

    # Conversation list with Search
    @action(detail=False, methods=["get"], url_path="conversations")
    def list_conversations(self, request):
        qs = AIConversation.objects.select_related("user").all()
        search_q = request.query_params.get("search")
        if search_q:
            qs = qs.filter(Q(title__icontains=search_q) | Q(user__email__icontains=search_q))
            
        data = []
        for c in qs:
            token_count = sum(m.token_count for m in c.messages.all())
            data.append({
                "id": c.id,
                "user_email": c.user.email if c.user else "",
                "title": c.title,
                "message_count": c.messages.count(),
                "token_usage": token_count,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            })
        return Response(data, status=status.HTTP_200_OK)

    # Thumbs up/down Feedbacks
    @action(detail=False, methods=["get"], url_path="feedback")
    def feedback_logs(self, request):
        feedbacks = AIFeedback.objects.select_related("message", "message__conversation").all().order_by("-created_at")
        data = []
        for f in feedbacks:
            data.append({
                "id": f.id,
                "message_id": f.message.id if f.message else "",
                "conversation_title": f.message.conversation.title if f.message and f.message.conversation else "",
                "is_positive": f.is_positive,
                "feedback_text": f.feedback_text,
                "created_at": f.created_at
            })
        return Response(data, status=status.HTTP_200_OK)

    # Blocked Prompts API
    @action(detail=False, methods=["get"], url_path="blocked-prompts")
    def blocked_prompts_list(self, request):
        blocked = get_admin_collection("blocked_prompts")
        return Response(blocked, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="blocked-prompts/add")
    def blocked_prompt_add(self, request):
        phrase = request.data.get("phrase")
        if not phrase:
            return Response({"error": "phrase is a required field."}, status=status.HTTP_400_BAD_REQUEST)
        item = {
            "id": f"block-{uuid.uuid4().hex[:8]}",
            "phrase": phrase,
            "action": "BLOCK",
            "created_at": datetime.now().isoformat(),
            "deleted_at": None
        }
        save_admin_item("blocked_prompts", item["id"], item)
        return Response(item, status=status.HTTP_201_CREATED)


class AdminCommunityViewSet(viewsets.ViewSet):
    """
    Module 9 — Enterprise Community Moderation & Communities.
    Manages study circles, student forums, reported content queue and blocked words list.
    """
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "list_communities": "control:community:view",
        "create_community": "control:community:create",
        "moderation_queue": "control:community:view",
        "moderate_item": "control:community:update",
        "get_blocked_words": "control:community:view",
        "add_blocked_word": "control:community:create",
    }

    @action(detail=False, methods=["get"], url_path="list")
    def list_communities(self, request):
        comms = get_admin_collection("communities")
        return Response(comms, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="create")
    def create_community(self, request):
        ser = CommunitySerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        comm = {
            "id": f"comm-{uuid.uuid4().hex[:8]}",
            "name": ser.validated_data["name"],
            "description": ser.validated_data.get("description", ""),
            "member_count": int(ser.validated_data.get("member_count", 0)),
            "is_active": ser.validated_data.get("is_active", True),
            "deleted_at": None
        }
        save_admin_item("communities", comm["id"], comm)
        return Response(comm, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="moderation")
    def moderation_queue(self, request):
        queue = get_admin_collection("moderation_queue")
        return Response(queue, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="moderate")
    def moderate_item(self, request, pk=None):
        queue = get_admin_collection("moderation_queue")
        resolution = request.data.get("status") # APPROVED or REJECTED
        if resolution not in ["APPROVED", "REJECTED"]:
            return Response({"error": "status (APPROVED/REJECTED) parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        for item in queue:
            if item["id"] == str(pk):
                item["status"] = resolution
                save_admin_item("moderation_queue", pk, item)
                return Response(item, status=status.HTTP_200_OK)
                
        return Response({"error": "Reported item not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], url_path="blocked-words")
    def get_blocked_words(self, request):
        store = read_admin_store()
        return Response(store.get("blocked_words", []), status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="blocked-words/add")
    def add_blocked_word(self, request):
        word = request.data.get("word")
        if not word:
            return Response({"error": "word field is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        store = read_admin_store()
        words = store.get("blocked_words", [])
        if word not in words:
            words.append(word)
        store["blocked_words"] = words
        write_admin_store(store)
        return Response(words, status=status.HTTP_201_CREATED)


class AdminNotificationViewSet(viewsets.ViewSet):
    """
    Module 10 — Enterprise Broadcast & Notification Centre.
    Dispatches mass push announcements, emails, or in-app alerts with campaign tracking.
    """
    permission_classes = [HasRBACPermission]
    required_permissions = {
        "broadcast": "control:notifications:create",
        "history": "control:notifications:view",
    }

    @action(detail=False, methods=["post"], url_path="broadcast")
    def broadcast(self, request):
        title = request.data.get("title")
        message = request.data.get("message")
        channel = request.data.get("channel", "IN_APP") # EMAIL, SMS, IN_APP
        
        if not title or not message:
            return Response({"error": "title and message are required fields."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Dispatch to all users in database as in-app notifications
        users = User.objects.all()
        for u in users:
            Notification.objects.create(
                user=u,
                title=title,
                message=message,
                is_read=False
            )
            
        # Log in JSON notification history
        history_item = {
            "id": f"notif-{uuid.uuid4().hex[:8]}",
            "channel": channel,
            "recipient": "ALL_STUDENTS",
            "title": title,
            "message": message,
            "status": "SENT",
            "sent_at": datetime.now().isoformat(),
            "deleted_at": None
        }
        save_admin_item("notifications_history", history_item["id"], history_item)
        return Response(history_item, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        history = get_admin_collection("notifications_history")
        return Response(history, status=status.HTTP_200_OK)
