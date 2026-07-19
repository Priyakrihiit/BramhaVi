import uuid
from django.db import models
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
    """
    QuerySet that handles soft deletion of records.
    """
    def delete(self):
        """
        Perform soft delete on the current queryset.
        """
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        """
        Perform actual database deletion.
        """
        return super().delete()


class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted records by default.
    """
    def get_queryset(self):
        """
        Return only active, non-soft-deleted records.
        """
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)


class BaseModel(models.Model):
    """
    Abstract base model representing operational stamps and standard UUID primary keys.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the record was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the record was last updated.")
    created_by = models.UUIDField(null=True, blank=True, help_text="UUID of the user who created this record.")
    updated_by = models.UUIDField(null=True, blank=True, help_text="UUID of the user who updated this record.")

    class Meta:
        abstract = True


class SoftDeleteModel(BaseModel):
    """
    Abstract base model adding soft delete support.
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text="Timestamp of when the record was soft-deleted."
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Fallback to fetch all objects including soft-deleted ones

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """
        Soft delete the record.
        """
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])

    def restore(self):
        """
        Restore a soft-deleted record.
        """
        self.deleted_at = None
        self.save(update_fields=['deleted_at', 'updated_at'])
