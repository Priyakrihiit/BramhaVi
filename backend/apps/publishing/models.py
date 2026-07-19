import uuid
from django.db import models
from apps.base_models import BaseModel, SoftDeleteModel

class AuthorProfile(SoftDeleteModel):
    """
    Bio portfolios and verification details of authors/teachers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.RESTRICT,
        related_name="author_profiles",
        help_text="The system user account owning this author profile."
    )
    name = models.CharField(max_length=255, help_text="Author public display name.")
    bio = models.TextField(blank=True, null=True, help_text="Biographical summary.")
    avatar_url = models.CharField(max_length=512, blank=True, null=True, help_text="Avatar picture link.")
    verified = models.BooleanField(default=False, help_text="Is this author verified by the platform?")
    metadata = models.JSONField(default=dict, blank=True, help_text="Custom attributes.")

    class Meta:
        db_table = "author_profiles"
        verbose_name = "Author Profile"
        verbose_name_plural = "Author Profiles"

    def __str__(self):
        return self.name


class PublisherProfile(SoftDeleteModel):
    """
    Bio profile representing standard publishing houses.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, help_text="Publisher company name.")
    description = models.TextField(blank=True, null=True, help_text="Details of publisher.")
    website_url = models.CharField(max_length=512, blank=True, null=True)
    logo_url = models.CharField(max_length=512, blank=True, null=True)
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = "publisher_profiles"
        verbose_name = "Publisher Profile"
        verbose_name_plural = "Publisher Profiles"

    def __str__(self):
        return self.name


class Book(SoftDeleteModel):
    """
    Catalog of ebooks and physical books available in bookstore.
    """
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("UNDER_REVIEW", "Under Review"),
        ("APPROVED", "Approved"),
        ("PUBLISHED", "Published"),
        ("ARCHIVED", "Archived"),
        ("REJECTED", "Rejected"),
    ]
    
    TYPE_CHOICES = [
        ("EBOOK", "E-Book"),
        ("PHYSICAL", "Physical Book"),
        ("AUDIOBOOK", "Audiobook"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text="Book header title.")
    slug = models.CharField(max_length=255, unique=True, help_text="URL slug identifier.")
    description = models.TextField(blank=True, null=True)
    isbn = models.CharField(max_length=50, blank=True, null=True, help_text="ISBN index value.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    book_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="EBOOK")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    author = models.ForeignKey(AuthorProfile, on_delete=models.RESTRICT, related_name="books")
    publisher = models.ForeignKey(PublisherProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name="books")
    cover_image_url = models.CharField(max_length=512, blank=True, null=True)
    preview_file_url = models.CharField(max_length=512, blank=True, null=True, help_text="Sample booklet file link.")
    full_file_url = models.CharField(max_length=512, blank=True, null=True, help_text="Complete content file link.")
    inventory_count = models.IntegerField(default=0, help_text="Stock count for physical books.")
    metadata = models.JSONField(default=dict, blank=True, help_text="Metadata including tags, categories, languages.")

    class Meta:
        db_table = "books"
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return self.title


class ProductOwnership(BaseModel):
    """
    Tracks creator revenue ownership, commission rates, and payouts destinations.
    """
    OWNER_CHOICES = [
        ("PLATFORM", "Platform"),
        ("TEACHER", "Teacher"),
        ("AUTHOR", "Author"),
        ("ORGANIZATION", "Organization"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True, related_name="ownerships")
    course = models.ForeignKey("lms.CourseStructure", on_delete=models.CASCADE, blank=True, null=True, related_name="ownerships")
    owner_type = models.CharField(max_length=20, choices=OWNER_CHOICES, default="PLATFORM")
    owner_user = models.ForeignKey("users.User", on_delete=models.SET_NULL, blank=True, null=True, related_name="owned_products")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.10, help_text="Percentage commission for platform (e.g. 0.10 for 10%).")
    wallet_destination = models.ForeignKey("wallets.Wallet", on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = "product_ownerships"
        verbose_name = "Product Ownership"
        verbose_name_plural = "Product Ownerships"

    def __str__(self):
        target = self.book.title if self.book else (self.course.title if self.course else "Unknown")
        return f"Ownership for {target} ({self.owner_type})"


class Order(BaseModel):
    """
    Tracks transactions and purchases for books/courses in Book Store.
    """
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("REFUNDED", "Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.RESTRICT, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    class Meta:
        db_table = "orders"
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.id} ({self.user.email} - {self.status})"


class OrderItem(models.Model):
    """
    Atomic items in a transaction order.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, blank=True, null=True)
    course = models.ForeignKey("lms.CourseStructure", on_delete=models.SET_NULL, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_items"
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        target = self.book.title if self.book else (self.course.title if self.course else "Unknown")
        return f"{target} @ {self.price}"


class ReadingProgress(BaseModel):
    """
    Tracks bookmark, notes, and pagination details for E-books readers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reading_progress")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reading_progress")
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    current_location = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "reading_progress"
        verbose_name = "Reading Progress"
        verbose_name_plural = "Reading Progresses"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="uq_reading_progress_user_book"
            )
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.book.title} ({self.progress_percentage}%)"
