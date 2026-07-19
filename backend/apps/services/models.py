import uuid
from django.db import models
from django.conf import settings

class ProfessionalService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=100,
        choices=[
            ("WEBSITE_DEVELOPMENT", "Website Development"),
            ("APPLICATION_DEVELOPMENT", "Application Development"),
            ("UI_UX_DESIGN", "UI/UX Design"),
            ("SEO", "SEO & Digital Marketing"),
            ("BUSINESS_CONSULTING", "Business Consulting"),
            ("CAREER_CONSULTING", "Career Consulting"),
            ("CUSTOM_ENTERPRISE", "Custom Enterprise Solutions"),
        ],
        default="WEBSITE_DEVELOPMENT"
    )
    pricing_model = models.CharField(
        max_length=50,
        choices=[
            ("FIXED", "Fixed Price"),
            ("HOURLY", "Hourly Rate")
        ],
        default="FIXED"
    )
    estimated_delivery_days = models.IntegerField(default=7)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provided_services"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("DRAFT", "Draft"),
            ("PUBLISHED", "Published"),
            ("ARCHIVED", "Archived")
        ],
        default="DRAFT"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "professional_services"

    def __str__(self):
        return f"{self.name} ({self.category})"


class ServiceLead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_leads"
    )
    service = models.ForeignKey(
        ProfessionalService,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="leads"
    )
    source = models.CharField(
        max_length=50,
        choices=[
            ("WEBSITE", "Website Form"),
            ("CAMPAIGN", "Marketing Campaign"),
            ("MANUAL", "Manual Entry"),
            ("REFERRAL", "Referral Link")
        ],
        default="WEBSITE"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("NEW", "New Prospect"),
            ("CONTACTED", "Contacted/Nurturing"),
            ("CONVERTED", "Converted to Project"),
            ("LOST", "Closed Lost")
        ],
        default="NEW"
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_leads"

    def __str__(self):
        return f"Lead for {self.client.email} - Status: {self.status}"


class ServiceProject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        ProfessionalService,
        on_delete=models.CASCADE,
        related_name="projects"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_projects"
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_projects"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("IN_PROGRESS", "In Progress"),
            ("IN_REVISION", "In Revision"),
            ("COMPLETED", "Completed"),
            ("CANCELLED", "Cancelled")
        ],
        default="IN_PROGRESS"
    )
    agreed_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_projects"

    def __str__(self):
        return f"Project: {self.service.name} for {self.client.email}"


class ProjectMilestone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        ServiceProject,
        on_delete=models.CASCADE,
        related_name="milestones"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=[
            ("PENDING", "Pending"),
            ("COMPLETED", "Completed")
        ],
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "project_milestones"

    def __str__(self):
        return f"{self.title} - Status: {self.status}"
