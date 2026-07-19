"""
Student Dashboard Tasks — BrahmaVidya Galaxy
Sprint 20: Celery background workers for streak decay, report compile, and reminders.
"""

from __future__ import annotations

import logging
import datetime
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.student.models import LearningStreak, WeeklyProgress, LearningReminder, DailyProgress
from apps.student.services import StreakService

logger = logging.getLogger("student.tasks")


@shared_task(
    bind=True,
    acks_late=True,
    queue="student-bulk",
    name="apps.student.tasks.decay_inactive_streaks_task",
)
def decay_inactive_streaks_task(self) -> dict:
    """
    Evaluates student activity and decays inactive learning streaks daily at midnight.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Starting learning streaks decay check.")

    try:
        yesterday = timezone.now().date() - datetime.timedelta(days=1)
        # Reset current streak to 0 for students who haven't studied since before yesterday
        updated_count = LearningStreak.objects.filter(
            last_studied_date__lt=yesterday
        ).update(current_streak=0)

        logger.info(f"[{task_id}] Streak decay completed. Reset {updated_count} inactive streaks.")
        return {"status": "success", "reset_count": updated_count}
    except Exception as exc:
        logger.error(f"[{task_id}] Error occurred while decaying streaks: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


@shared_task(
    bind=True,
    acks_late=True,
    queue="student-bulk",
    name="apps.student.tasks.compile_weekly_progress_digest_task",
)
def compile_weekly_progress_digest_task(self) -> dict:
    """
    Pre-aggregates and logs progress summaries for the week and sends progress alerts.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Starting weekly progress digest compilation.")

    try:
        today = timezone.now().date()
        monday = today - datetime.timedelta(days=today.weekday())

        User = get_user_model()
        students = User.objects.filter(is_active=True)

        processed = 0
        for student in students:
            # Check if there is daily activity this week
            daily_logs = DailyProgress.objects.filter(
                student=student,
                date__gte=monday,
                date__lte=today
            )

            if not daily_logs.exists():
                continue

            total_minutes = sum(log.study_minutes for log in daily_logs)
            total_completed = sum(log.lessons_completed for log in daily_logs)
            total_xp = sum(log.xp_earned for log in daily_logs)

            with transaction.atomic():
                weekly_progress, _ = WeeklyProgress.objects.get_or_create(
                    student=student,
                    week_start=monday
                )
                weekly_progress.study_minutes = total_minutes
                weekly_progress.lessons_completed = total_completed
                weekly_progress.xp_earned = total_xp
                weekly_progress.save()

            processed += 1

        logger.info(f"[{task_id}] Weekly progress digest completed for {processed} active students.")
        return {"status": "success", "processed_count": processed}
    except Exception as exc:
        logger.error(f"[{task_id}] Error in compiling weekly progress digest: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=120)


@shared_task(
    bind=True,
    acks_late=True,
    queue="student-default",
    name="apps.student.tasks.generate_study_reminders_task",
)
def generate_study_reminders_task(self) -> dict:
    """
    Scans pending learning reminders and dispatches notifications for immediate study deadlines.
    """
    task_id = self.request.id
    logger.info(f"[{task_id}] Starting scheduled learning reminders dispatch.")

    try:
        now = timezone.now()
        pending_reminders = LearningReminder.objects.filter(
            status=LearningReminder.ReminderStatus.PENDING,
            remind_at__lte=now
        ).select_related("student")

        dispatched = 0
        from apps.control_center.integration_hub import CentralNotificationEngine
        for reminder in pending_reminders:
            with transaction.atomic():
                reminder.status = LearningReminder.ReminderStatus.SENT
                reminder.sent_at = now
                reminder.save()
                
                try:
                    CentralNotificationEngine.send_notification(
                        user=reminder.student,
                        event_type="STUDY_REMINDER",
                        title=reminder.title or "Time to Study!",
                        message=reminder.message or "Don't break your streak! Jump back in and view your next lesson.",
                        channels=["IN_APP", "EMAIL"]
                    )
                except Exception as n_exc:
                    logger.warning(f"Could not dispatch notification for reminder {reminder.id}: {n_exc}")
            dispatched += 1

        logger.info(f"[{task_id}] Reminders dispatch complete. Sent {dispatched} notifications.")
        return {"status": "success", "dispatched_count": dispatched}
    except Exception as exc:
        logger.error(f"[{task_id}] Error generating study reminders: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
