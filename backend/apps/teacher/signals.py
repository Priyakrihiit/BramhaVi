"""
Teacher Portal Signals — BrahmaVidya Galaxy
Sprint 21: Event-driven triggers, automation hooks, and cache invalidation.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.teacher.models import (
    TeacherProfile, TeacherEarning, TeachingSession, TeacherSchedule,
    TeacherWallet, TeacherNotificationPreference, TeacherActivityLog, Batch
)
from apps.teacher.services import invalidate_teacher_dashboard_cache, AnalyticsService
from apps.control_center.integration_hub import CentralNotificationEngine

User = get_user_model()


@receiver(post_save, sender=TeacherProfile)
def on_teacher_profile_saved_handler(sender, instance, created, **kwargs):
    """
    Fires whenever a TeacherProfile is saved.
    Ensures default wallet and notification preferences exist.
    """
    if created:
        try:
            # Auto-initialize default Wallet
            TeacherWallet.objects.get_or_create(
                teacher=instance.user,
                defaults={
                    "payout_method": "STRIPE",
                    "payout_address": "",
                }
            )

            # Auto-initialize default Notification Preferences
            TeacherNotificationPreference.objects.get_or_create(
                teacher=instance.user,
                defaults={
                    "email_on_submission": True,
                    "email_on_discussion": True,
                    "sms_on_urgent": False,
                    "push_on_live_class": True,
                }
            )

            # Audit trail logging
            TeacherActivityLog.objects.create(
                teacher=instance.user,
                action="INITIALIZE_TEACHER_PROFILE",
                details="Auto-initialized wallet structure and alert settings profiles."
            )
        except Exception:
            pass

    # Always invalidate cache on profile change
    invalidate_teacher_dashboard_cache(instance.user.id)


@receiver(post_save, sender=TeacherEarning)
def on_teacher_earning_saved_handler(sender, instance, created, **kwargs):
    """
    Fires whenever a teacher earns rewards or payouts.
    Invalidates dashboard summary cache.
    """
    if created:
        invalidate_teacher_dashboard_cache(instance.teacher.id)


@receiver(post_save, sender=TeachingSession)
def on_teaching_session_saved_handler(sender, instance, created, **kwargs):
    """
    Fires whenever a teaching session is scheduled or updated.
    Syncs to TeacherSchedule automatically for agenda consolidated tracking.
    """
    if created:
        try:
            # Create matching schedule entry
            TeacherSchedule.objects.get_or_create(
                teacher=instance.teacher,
                title=f"Tutoring: {instance.title}",
                defaults={
                    "description": f"Type: {instance.session_type}. Meeting link: {instance.meeting_link}",
                    "start_time": instance.start_time,
                    "end_time": instance.end_time,
                    "status": "PENDING"
                }
            )
        except Exception:
            pass

    invalidate_teacher_dashboard_cache(instance.teacher.id)


@receiver(post_save, sender=TeacherSchedule)
def on_teacher_schedule_saved_handler(sender, instance, created, **kwargs):
    """
    Invalidates dashboard caches upon agenda changes.
    """
    invalidate_teacher_dashboard_cache(instance.teacher.id)


@receiver(post_save, sender=Batch)
def on_batch_saved_handler(sender, instance, created, **kwargs):
    """
    Invalidates caches for all assigned instructors in the batch.
    """
    for instructor in instance.instructors.all():
        invalidate_teacher_dashboard_cache(instructor.id)


@receiver(post_delete, sender=TeachingSession)
def on_teaching_session_deleted_handler(sender, instance, **kwargs):
    invalidate_teacher_dashboard_cache(instance.teacher.id)
