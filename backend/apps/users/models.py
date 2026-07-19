import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.indexes import GinIndex
from apps.base_models import BaseModel, SoftDeleteModel, SoftDeleteManager


class Role(BaseModel):
    """
    Stores system permission roles (Admin, Student, Teacher, etc.).
    """
    name = models.CharField(max_length=50, unique=True, help_text="Role name (e.g., STUDENT, TEACHER, SUPERADMIN).")
    description = models.TextField(blank=True, null=True, help_text="Description of the role's responsibilities.")

    class Meta:
        db_table = "roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name


class Permission(models.Model):
    """
    Defines granular security permission keys/action tokens.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codename = models.CharField(max_length=100, unique=True, help_text="Permission unique code (e.g., lms:course:publish).")
    description = models.TextField(blank=True, null=True, help_text="Description of what this permission allows.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when permission was registered.")

    class Meta:
        db_table = "permissions"
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    def __str__(self):
        return self.codename


class RolePermission(models.Model):
    """
    Bridge table mapping roles to precise permissions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions", help_text="Linked role.")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="role_permissions", help_text="Linked permission.")

    class Meta:
        db_table = "role_permissions"
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="uq_role_permissions_role_permission"
            )
        ]

    def __str__(self):
        return f"{self.role.name} -> {self.permission.codename}"


class UserManager(BaseUserManager):
    """
    Custom user manager for handling email-based user creation and soft-deleted records.
    """
    def get_queryset(self):
        # Default queryset filters out soft-deleted users
        from apps.base_models import SoftDeleteQuerySet
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a Superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Bootstrapping SUPERADMIN role automatically if not exists
        role, _ = Role.objects.get_or_create(
            name="SUPERADMIN",
            defaults={"description": "Platform owner with total system sovereignty."}
        )
        extra_fields.setdefault("role", role)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, SoftDeleteModel):
    """
    Core system user accounts, holding email credentials and role link.
    """
    email = models.EmailField(max_length=255, unique=True, help_text="User primary login email address.")
    role = models.ForeignKey(Role, on_delete=models.RESTRICT, related_name="users", help_text="Primary RBAC role assigned to user.")
    is_active = models.BooleanField(default=True, help_text="Indicates whether the user account is active.")
    is_staff = models.BooleanField(default=False, help_text="Designates whether the user can log into Django admin panel.")
    failed_login_attempts = models.IntegerField(default=0, help_text="Failed authentication counts.")
    locked_until = models.DateTimeField(blank=True, null=True, help_text="Timestamp blocking login access.")

    objects = UserManager()
    all_objects = BaseUserManager()  # Manager that can query all users, including soft-deleted ones

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_users_email"
            )
        ]

    def __str__(self):
        return self.email

    def has_capability(self, capability_codename: str) -> bool:
        """Check if user has an ACTIVE capability."""
        return self.capabilities.filter(
            capability__codename=capability_codename,
            status="ACTIVE"
        ).exists()

    def has_capability_permission(self, permission_codename: str) -> bool:
        """Check if any of user's ACTIVE capabilities grant this permission."""
        if self.is_superuser:
            return True
        return CapabilityPermission.objects.filter(
            capability__user_capabilities__user=self,
            capability__user_capabilities__status="ACTIVE",
            permission__codename=permission_codename
        ).exists()

    def get_active_capabilities(self):
        """Return all active capabilities for this user."""
        return self.capabilities.filter(status="ACTIVE").select_related("capability")

    def get_all_permissions_set(self) -> set:
        """Return flat set of all permission codenames from active capabilities and legacy roles."""
        perms = set()
        if self.is_superuser:
            return set(Permission.objects.values_list("codename", flat=True))
        
        cap_perms = set(
            CapabilityPermission.objects.filter(
                capability__user_capabilities__user=self,
                capability__user_capabilities__status="ACTIVE"
            ).values_list("permission__codename", flat=True)
        )
        perms.update(cap_perms)

        if hasattr(self, "role") and self.role:
            role_perms = set(self.role.role_permissions.values_list("permission__codename", flat=True))
            perms.update(role_perms)

        return perms

    @property
    def is_teacher_cbac(self) -> bool:
        return self.has_capability("TEACHING") or (
            hasattr(self, "role") and self.role and self.role.name in ["SUPERADMIN", "ADMIN", "TEACHER"]
        )

    @property
    def is_student_cbac(self) -> bool:
        return self.has_capability("LEARNING") or (
            hasattr(self, "role") and self.role and self.role.name in ["SUPERADMIN", "ADMIN", "STUDENT"]
        )

    @property
    def is_admin_cbac(self) -> bool:
        return self.has_capability("ADMIN") or (
            hasattr(self, "role") and self.role and self.role.name in ["SUPERADMIN", "ADMIN"]
        )


class Session(models.Model):
    """
    Tracks active JWT web authentication tokens and login locations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions", help_text="Associated user.")
    token_hash = models.CharField(max_length=255, unique=True, help_text="Unique hash of JWT/refresh token.")
    ip_address = models.CharField(max_length=45, blank=True, null=True, help_text="IP address of login session.")
    user_agent = models.TextField(blank=True, null=True, help_text="Device browser client user agent.")
    expires_at = models.DateTimeField(help_text="Timestamp when login session expires.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when session was initiated.")

    class Meta:
        db_table = "sessions"
        verbose_name = "Session"
        verbose_name_plural = "Sessions"

    def __str__(self):
        return f"Session {self.id} (User: {self.user.email})"


class Device(models.Model):
    """
    User devices authorized for receiving push notifications and security alerts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices", help_text="Associated user.")
    device_token = models.CharField(max_length=255, unique=True, help_text="Push notification gateway device identifier.")
    device_type = models.CharField(max_length=50, help_text="Type of device client (e.g., IOS, ANDROID, CHROME).")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when device was registered.")

    class Meta:
        db_table = "devices"
        verbose_name = "Device"
        verbose_name_plural = "Devices"

    def __str__(self):
        return f"{self.device_type} Device (User: {self.user.email})"


class UserProfile(models.Model):
    """
    Rich biographical details and dynamic settings configuration block.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", help_text="Associated user credentials.")
    first_name = models.CharField(max_length=100, blank=True, null=True, help_text="User first name.")
    last_name = models.CharField(max_length=100, blank=True, null=True, help_text="User last name.")
    avatar_url = models.CharField(max_length=512, blank=True, null=True, help_text="CDN profile picture URL.")
    bio = models.TextField(blank=True, null=True, help_text="User biographical summary.")
    settings = models.JSONField(
        default=dict,
        help_text="Custom settings profile (theme, notifications toggles)."
    )
    cover_image_url = models.CharField(max_length=512, blank=True, null=True, help_text="CDN profile cover picture URL.")
    skills = models.JSONField(default=list, blank=True, help_text="List of user skills.")
    education = models.JSONField(default=list, blank=True, help_text="Dynamic list of education history.")
    experience = models.JSONField(default=list, blank=True, help_text="Dynamic list of professional experience.")
    projects = models.JSONField(default=list, blank=True, help_text="Dynamic list of projects.")
    languages = models.JSONField(default=list, blank=True, help_text="List of languages spoken.")
    achievements = models.JSONField(default=list, blank=True, help_text="List of user achievements.")
    privacy_settings = models.JSONField(default=dict, blank=True, help_text="User privacy settings profile.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        indexes = [
            GinIndex(fields=["settings"], name="idx_user_prof_settings_gin")
        ]

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.user.email


class Notification(models.Model):
    """
    In-app notification queue records.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", help_text="Target recipient of notification.")
    title = models.CharField(max_length=255, help_text="Header message of notification.")
    message = models.TextField(help_text="Body content.")
    is_read = models.BooleanField(default=False, help_text="Whether recipient has viewed notification.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} (User: {self.user.email})"


class Organization(BaseModel):
    """
    Groups users under a shared workspace (Personal, School, Company, NGO, etc.).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Name of the organization/workspace.")
    subdomain = models.CharField(max_length=100, unique=True, blank=True, null=True, help_text="Custom access subdomain.")
    org_type = models.CharField(
        max_length=50,
        choices=[
            ("PERSONAL", "Personal Workspace"),
            ("SCHOOL", "School"),
            ("COLLEGE", "College"),
            ("UNIVERSITY", "University"),
            ("COMPANY", "Company"),
            ("NGO", "NGO"),
            ("COACHING", "Coaching Institute"),
        ],
        default="PERSONAL",
        help_text="Classification type of organization."
    )
    logo_url = models.CharField(max_length=512, blank=True, null=True, help_text="Custom brand logo URL.")
    primary_color = models.CharField(max_length=7, default="#4F46E5", help_text="Brand primary HEX color code.")
    settings = models.JSONField(default=dict, blank=True, help_text="Custom settings profile (allowed domains, security rules).")

    class Meta:
        db_table = "organizations"
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name


class OrganizationMember(BaseModel):
    """
    Maps users to organizations with dynamic role privileges.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="members", help_text="Linked organization.")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organization_memberships", help_text="Linked user.")
    role_name = models.CharField(
        max_length=50,
        choices=[
            ("OWNER", "Workspace Owner"),
            ("ADMIN", "Workspace Admin"),
            ("MEMBER", "Workspace Member"),
            ("GUEST", "Workspace Guest"),
        ],
        default="MEMBER"
    )
    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "organization_members"
        verbose_name = "Organization Member"
        verbose_name_plural = "Organization Members"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="uq_org_member"
            )
        ]

    def __str__(self):
        return f"{self.user.email} in {self.organization.name} ({self.role_name})"


class LoginHistory(models.Model):
    """
    Tracks all login attempts, successful or failed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_history", null=True, blank=True)
    email_attempted = models.EmailField(max_length=255)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    is_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "login_history"
        verbose_name = "Login History"
        verbose_name_plural = "Login Histories"

    def __str__(self):
        return f"Login for {self.email_attempted} (Success: {self.is_successful}) at {self.created_at}"


class Capability(BaseModel):
    codename = models.CharField(max_length=50, unique=True, help_text="Capability codename (e.g. TEACHING).")
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ("INSTANT", "Instant Activation"),
            ("APPROVAL_REQUIRED", "Requires Approval"),
        ],
        default="INSTANT"
    )
    is_active = models.BooleanField(default=True)
    default_settings = models.JSONField(default=dict, blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = "capabilities"
        verbose_name = "Capability"
        verbose_name_plural = "Capabilities"

    def __str__(self):
        return self.display_name


class UserCapability(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="capabilities")
    capability = models.ForeignKey(Capability, on_delete=models.CASCADE, related_name="user_capabilities")
    status = models.CharField(
        max_length=50,
        choices=[
            ("ACTIVE", "Active"),
            ("PENDING", "Pending Approval"),
            ("SUSPENDED", "Suspended"),
            ("DEACTIVATED", "Voluntarily Deactivated"),
            ("REJECTED", "Application Rejected"),
        ],
        default="PENDING"
    )
    activated_at = models.DateTimeField(blank=True, null=True)
    deactivated_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey("User", blank=True, null=True, on_delete=models.SET_NULL, related_name="approved_capabilities")
    rejection_reason = models.TextField(blank=True, null=True)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "user_capabilities"
        verbose_name = "User Capability"
        verbose_name_plural = "User Capabilities"
        constraints = [
            models.UniqueConstraint(fields=["user", "capability"], name="uq_user_capability")
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.capability.codename} ({self.status})"


class CapabilityPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capability = models.ForeignKey(Capability, on_delete=models.CASCADE, related_name="capability_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="capability_permissions")

    class Meta:
        db_table = "capability_permissions"
        verbose_name = "Capability Permission"
        verbose_name_plural = "Capability Permissions"
        constraints = [
            models.UniqueConstraint(fields=["capability", "permission"], name="uq_capability_permission")
        ]

    def __str__(self):
        return f"{self.capability.codename} -> {self.permission.codename}"


class CapabilityApplication(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="capability_applications")
    capability = models.ForeignKey(Capability, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(
        max_length=50,
        choices=[
            ("PENDING", "Pending Review"),
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected"),
            ("RESUBMITTED", "Re-submitted After Rejection"),
        ],
        default="PENDING"
    )
    application_data = models.JSONField(default=dict, blank=True)
    reviewed_by = models.ForeignKey("User", blank=True, null=True, on_delete=models.SET_NULL, related_name="reviewed_applications")
    review_notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "capability_applications"
        verbose_name = "Capability Application"
        verbose_name_plural = "Capability Applications"

    def __str__(self):
        return f"{self.user.email} application for {self.capability.codename} ({self.status})"
