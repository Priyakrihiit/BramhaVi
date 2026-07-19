from rest_framework import serializers
from apps.services.models import ProfessionalService, ServiceLead, ServiceProject, ProjectMilestone

class ProfessionalServiceSerializer(serializers.ModelSerializer):
    provider_email = serializers.ReadOnlyField(source="provider.email")

    class Meta:
        model = ProfessionalService
        fields = [
            "id", "name", "description", "category", "pricing_model",
            "estimated_delivery_days", "price", "provider", "provider_email",
            "status", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "provider", "created_at", "updated_at"]


class ServiceLeadSerializer(serializers.ModelSerializer):
    client_email = serializers.ReadOnlyField(source="client.email")
    service_name = serializers.ReadOnlyField(source="service.name")

    class Meta:
        model = ServiceLead
        fields = [
            "id", "client", "client_email", "service", "service_name",
            "source", "status", "notes", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "client", "created_at", "updated_at"]


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMilestone
        fields = [
            "id", "project", "title", "description", "due_date", "amount", "status", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ServiceProjectSerializer(serializers.ModelSerializer):
    client_email = serializers.ReadOnlyField(source="client.email")
    provider_email = serializers.ReadOnlyField(source="provider.email")
    service_name = serializers.ReadOnlyField(source="service.name")
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceProject
        fields = [
            "id", "service", "service_name", "client", "client_email",
            "provider", "provider_email", "status", "agreed_price",
            "milestones", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "client", "created_at", "updated_at"]
