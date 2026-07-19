from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from apps.lms.models import LiveClass, CalendarEvent

# Note: In production, 'sender' points to the LearningProgress model class
@receiver(post_save)
def on_course_progress_updated(sender, instance, created, **kwargs) -> None:
    """
    Monitors progress percentage adjustments.
    - If student progress hits 100.00% on a COURSE node, triggers certificate generation tasks.
    """
    if sender.__name__ == "LearningProgress":
        # Check if the node is a COURSE and completion threshold has been reached
        if getattr(instance, "node_type", "") == "COURSE" and getattr(instance, "progress_percentage", 0.0) >= 100.00:
            user_id = instance.user_id
            course_id = instance.structure_id
            
            # TODO: Dispatch async certificate signature generator (apps.wallets.tasks)
            pass


@receiver(post_save, sender=LiveClass)
def on_live_class_scheduled(sender, instance, created, **kwargs) -> None:
    """
    Spins up calendar sync events for the instructing teacher on creation.
    """
    if created:
        CalendarEvent.objects.get_or_create(
            user=instance.teacher,
            live_class=instance,
            defaults={
                "event_title": f"Live Class: {instance.title}",
                "start_time": instance.scheduled_at,
                "end_time": instance.scheduled_at + timezone.timedelta(minutes=instance.duration_minutes)
            }
        )

