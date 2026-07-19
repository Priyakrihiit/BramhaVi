from decimal import Decimal
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.services.models import ProfessionalService, ServiceLead, ServiceProject, ProjectMilestone
from apps.services.serializers import (
    ProfessionalServiceSerializer, ServiceLeadSerializer, ServiceProjectSerializer, ProjectMilestoneSerializer
)
from apps.wallets.services import SettlementEngineService
from apps.users.permissions import HasRBACPermission

class ProfessionalServiceViewSet(viewsets.ModelViewSet):
    queryset = ProfessionalService.objects.select_related("provider").all().order_by("-created_at")
    serializer_class = ProfessionalServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class ServiceLeadViewSet(viewsets.ModelViewSet):
    queryset = ServiceLead.objects.select_related("client", "service").all().order_by("-created_at")
    serializer_class = ServiceLeadSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class ServiceProjectViewSet(viewsets.ModelViewSet):
    queryset = ServiceProject.objects.select_related("service", "client", "provider").all().order_by("-created_at")
    serializer_class = ServiceProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=True, methods=["post"], url_path="accept-and-settle")
    def accept_and_settle(self, request, id=None):
        """
        Deducts the agreed price from the client's wallet, splits GST (18%) and Platform commission (10%),
        and credits the remainder to the provider's wallet.
        """
        project = self.get_object()
        user = request.user
        if project.client != user and not user.is_superuser:
            return Response({"detail": "Only the project client can accept and settle."}, status=status.HTTP_403_FORBIDDEN)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user = User.objects.filter(role__name="SUPERADMIN").first() or User.objects.filter(is_superuser=True).first()
        if not admin_user:
            return Response({"detail": "Platform superadmin wallet not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        platform_wallet = admin_user.wallet

        try:
            settlement = SettlementEngineService.process_purchase_settlement(
                buyer_user_id=str(project.client.id),
                price=project.agreed_price,
                product_type="SERVICE",
                product_id=str(project.provider.id),
                platform_wallet_id=str(platform_wallet.id)
            )

            project.status = "COMPLETED"
            project.save()

            return Response({
                "success": True,
                "project_status": project.status,
                "settlement": settlement
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProjectMilestoneViewSet(viewsets.ModelViewSet):
    queryset = ProjectMilestone.objects.select_related("project").all().order_by("due_date")
    serializer_class = ProjectMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
