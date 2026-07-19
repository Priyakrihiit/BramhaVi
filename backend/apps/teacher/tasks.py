"""
Teacher Portal Tasks — BrahmaVidya Galaxy
Sprint 21: Celery background workers for analytics aggregation, billing digests, and notifications.
"""

from __future__ import annotations

import logging
import datetime
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.teacher.models import TeacherProfile, TeacherWallet, TeacherEarning
from apps.teacher.services import AnalyticsService, WalletService, invalidate_teacher_dashboard_cache
from apps.lms.models import LiveClass, StudentEnrollment

logger = logging.getLogger("teacher.tasks")
User = get_user_model()


@shared_task(
    bind=True,
    acks_late=True,
    queue="teacher-bulk",
    name="apps.teacher.tasks.compute_teacher_analytics_task",
)
def compute_teacher_analytics_task(self, teacher_id: int) -> dict:
    """
    Recalculates profile summaries, aggregates rating, and logs milestones for a teacher.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Running aggregates recompute for teacher_id: {teacher_id}")

    try:
        teacher = User.objects.get(id=teacher_id)
        analytics = AnalyticsService.recompute_teacher_aggregates(teacher)
        return {
            "status": "success",
            "teacher_id": teacher_id,
            "total_students": analytics.total_students_taught,
            "avg_rating": float(analytics.average_course_rating),
            "teaching_hours": float(analytics.total_teaching_hours)
        }
    except User.DoesNotExist:
        logger.error(f"[{task_id}] User with id {teacher_id} does not exist.")
        return {"status": "error", "message": "User not found"}
    except Exception as exc:
        logger.error(f"[{task_id}] Error recomputing teacher analytics: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


@shared_task(
    bind=True,
    acks_late=True,
    queue="teacher-bulk",
    name="apps.teacher.tasks.recompute_all_teachers_aggregates_task",
)
def recompute_all_teachers_aggregates_task(self) -> dict:
    """
    Nightly/periodic sync running recalculations over all verified platform instructors.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Starting global teacher analytics updates.")

    try:
        teachers = User.objects.filter(teacher_profile__is_verified=True)
        processed = 0

        for teacher in teachers:
            AnalyticsService.recompute_teacher_aggregates(teacher)
            processed += 1

        logger.info(f"[{task_id}] Successfully recomputed analytics for {processed} teachers.")
        return {"status": "success", "processed_count": processed}
    except Exception as exc:
        logger.error(f"[{task_id}] Error in recompute_all_teachers_aggregates_task: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=120)


@shared_task(
    bind=True,
    acks_late=True,
    queue="teacher-bulk",
    name="apps.teacher.tasks.send_upcoming_class_reminders_task",
)
def send_upcoming_class_reminders_task(self) -> dict:
    """
    Scans for LiveClasses starting in the next 30 minutes and dispatches alert notifications.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Scanning upcoming streaming classes.")

    try:
        now = timezone.now()
        thirty_minutes_later = now + datetime.timedelta(minutes=30)

        # Retrieve live classes in window
        upcoming_classes = LiveClass.objects.filter(
            scheduled_at__gte=now,
            scheduled_at__lte=thirty_minutes_later
        )

        sent_count = 0
        for live in upcoming_classes:
            # Send notification to teacher
            from apps.control_center.integration_hub import CentralNotificationEngine
            CentralNotificationEngine.send_notification(
                user=live.teacher,
                event_type="LIVE_CLASS_REMINDER",
                title="Live Stream Broadcast starting soon!",
                message=f"Your lecture '{live.title}' is scheduled to start in less than 30 minutes.",
                channels=["IN_APP"]
            )

            # Send notification to enrolled students
            enrolled_students = StudentEnrollment.objects.filter(
                course=live.course,
                status="ACTIVE"
            ).select_related("student")

            for enrollment in enrolled_students:
                CentralNotificationEngine.send_notification(
                    user=enrollment.student,
                    event_type="STUDENT_LIVE_REMINDER",
                    title="Live Stream Class Starting!",
                    message=f"'{live.title}' is about to begin. Prepare your questions!",
                    channels=["IN_APP"]
                )
                sent_count += 1

        return {"status": "success", "notifications_dispatched": sent_count}
    except Exception as exc:
        logger.error(f"[{task_id}] Error sending class reminders: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=180)


@shared_task(
    bind=True,
    acks_late=True,
    queue="teacher-bulk",
    name="apps.teacher.tasks.compile_monthly_payout_digest_task",
)
def compile_monthly_payout_digest_task(self) -> dict:
    """
    End of month payout digest tracking and simulation report.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Starting monthly payouts digest compiler.")

    try:
        wallets = TeacherWallet.objects.filter(balance_amount__gt=0.00)
        payouts_count = 0

        for wallet in wallets:
            # Log audit payout
            logger.info(f"MTD Payout eligible: Teacher {wallet.teacher.email} Balance: {wallet.balance_amount}")
            payouts_count += 1

        return {"status": "success", "eligible_payout_wallets": payouts_count}
    except Exception as exc:
        logger.error(f"[{task_id}] Error compiling monthly payout digest: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=120)
