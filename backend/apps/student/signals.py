"""
Student Dashboard Signals — BrahmaVidya Galaxy
Sprint 20: Event handlers and automated trigger conditions.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.core.cache import cache

from apps.student.models import (
    LearningHistory, StudySession, RecentlyViewedLesson,
    Bookmark, StudentNote, StudyGoal, StudentAchievement
)
from apps.student.services import StreakService, AchievementService
from apps.control_center.integration_hub import CentralNotificationEngine, CentralAnalyticsTracker
from apps.control_center.models import AIConversation, AIMessage
from apps.search.tasks import index_document_task


@receiver(user_logged_in)
def on_user_logged_in_handler(sender, request, user, **kwargs):
    """
    Triggers automatically when a student logs into the platform.
    Calculates/updates consecutive days studied counters.
    """
    try:
        StreakService.update_login_streak(user)
    except Exception:
        # Prevent login flow breakage if streak calculation fails
        pass


@receiver(post_save, sender=LearningHistory)
def on_history_logged_handler(sender, instance, created, **kwargs):
    """
    Fires whenever a learning history item is recorded.
    Updates streak days and performs automatic badge check.
    """
    if created:
        try:
            # Refresh login streak
            StreakService.update_login_streak(instance.student)
            # Scan criteria for unlocked achievements
            AchievementService.evaluate_achievements(instance.student)
        except Exception:
            pass


@receiver(post_save, sender=StudySession)
def on_session_saved_handler(sender, instance, created, **kwargs):
    """
    Fires whenever a study session concludes or gets saved.
    Updates progress aggregations and evaluates achievements.
    """
    if not created and not instance.is_active:
        try:
            # Scan criteria for unlocked achievements
            AchievementService.evaluate_achievements(instance.student)
        except Exception:
            pass


@receiver(post_save, sender=RecentlyViewedLesson)
def on_recently_viewed_lesson_saved_handler(sender, instance, created, **kwargs):
    """
    Ensures RecentlyViewedLesson ring buffer is capped at 20 elements.
    Removes the least recently used elements.
    """
    if created:
        try:
            student = instance.student
            # Fetch elements beyond index 20 (chronologically ordered descending)
            excess = RecentlyViewedLesson.objects.filter(
                student=student
            ).order_by("-viewed_at")[20:]
            if excess:
                RecentlyViewedLesson.objects.filter(
                    id__in=[item.id for item in excess]
                ).delete()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# NEW SPRINT 20 PHASE 8 INTEGRATION HOOKS
# ─────────────────────────────────────────────────────────────────────────────

def invalidate_student_dashboard_cache(student):
    """
    Clears cached entries in Redis cache prior to database state mutations.
    """
    if not student:
        return
    cache_keys = [
        f"dashboard_context_{student.id}",
        f"student_stats_{student.id}",
        f"weekly_metrics_{student.id}",
    ]
    for key in cache_keys:
        try:
            cache.delete(key)
        except Exception:
            pass


def update_ai_conversation_context(student, event_description):
    """
    Appends a context trace in the student's active Vidya AI Conversation
    to dynamically ground subsequent LLM tutoring sessions in live learning activities.
    """
    try:
        conversation, _ = AIConversation.objects.get_or_create(
            user=student,
            title="Vidya Learning Companion"
        )
        AIMessage.objects.create(
            conversation=conversation,
            sender_type="USER",
            content=f"[SYSTEM_CONTEXT_UPDATE] Student {student.email} completed study activity: {event_description}.",
            token_count=len(event_description) // 4
        )
    except Exception:
        pass


@receiver(post_save, sender=Bookmark)
def on_bookmark_saved(sender, instance, created, **kwargs):
    if created:
        try:
            CentralAnalyticsTracker.track_event(
                user=instance.student,
                metric_name="Bookmark Added",
                metric_value=1.0,
                context_data={
                    "bookmark_id": str(instance.id),
                    "content_type": instance.content_type,
                    "content_id": str(instance.content_id),
                    "title": instance.title
                }
            )
            CentralNotificationEngine.send_notification(
                user=instance.student,
                event_type="BOOKMARK_CREATED",
                title="Resource Bookmarked",
                message=f"Successfully bookmarked '{instance.title}' to your learning hub.",
                channels=["IN_APP"]
            )
            invalidate_student_dashboard_cache(instance.student)
            update_ai_conversation_context(instance.student, f"Bookmarked a {instance.content_type} item titled '{instance.title}'.")
        except Exception:
            pass


@receiver(post_delete, sender=Bookmark)
def on_bookmark_deleted(sender, instance, **kwargs):
    try:
        CentralAnalyticsTracker.track_event(
            user=instance.student,
            metric_name="Bookmark Removed",
            metric_value=1.0,
            context_data={
                "content_type": instance.content_type,
                "content_id": str(instance.content_id),
                "title": instance.title
            }
        )
        invalidate_student_dashboard_cache(instance.student)
    except Exception:
        pass


@receiver(post_save, sender=StudentNote)
def on_note_saved(sender, instance, created, **kwargs):
    try:
        event_name = "Note Created" if created else "Note Modified"
        CentralAnalyticsTracker.track_event(
            user=instance.student,
            metric_name=event_name,
            metric_value=1.0,
            context_data={
                "note_id": str(instance.id),
                "lesson_title": instance.node.title if instance.node else "General"
            }
        )
        invalidate_student_dashboard_cache(instance.student)
        index_document_task.delay("StudentNote", str(instance.id))
        update_ai_conversation_context(
            instance.student,
            f"Saved a personal learning note for lesson '{instance.node.title if instance.node else 'General'}': '{instance.title or 'Note'}'."
        )
    except Exception:
        pass


@receiver(post_save, sender=StudyGoal)
def on_goal_saved(sender, instance, created, **kwargs):
    try:
        if created:
            CentralAnalyticsTracker.track_event(
                user=instance.student,
                metric_name="Goal Set",
                metric_value=1.0,
                context_data={"goal_id": str(instance.id), "title": instance.title}
            )
        elif instance.status == "COMPLETED" or instance.progress_percentage >= 100.0:
            CentralAnalyticsTracker.track_event(
                user=instance.student,
                metric_name="Goal Achieved",
                metric_value=1.0,
                context_data={"goal_id": str(instance.id), "title": instance.title}
            )
            CentralNotificationEngine.send_notification(
                user=instance.student,
                event_type="STUDY_GOAL_COMPLETED",
                title="Study Goal Achieved! 🎯",
                message=f"Outstanding! You completed your study goal: '{instance.title}'. Keep up the brilliant pace!",
                channels=["IN_APP", "EMAIL"]
            )
            update_ai_conversation_context(instance.student, f"Achieved the academic study goal: '{instance.title}'.")
        invalidate_student_dashboard_cache(instance.student)
    except Exception:
        pass


@receiver(post_save, sender=StudentAchievement)
def on_achievement_saved(sender, instance, created, **kwargs):
    try:
        if instance.is_unlocked:
            CentralAnalyticsTracker.track_event(
                user=instance.student,
                metric_name="Achievement Awarded",
                metric_value=1.0,
                context_data={
                    "achievement_code": instance.achievement.code,
                    "title": instance.achievement.title
                }
            )
            CentralNotificationEngine.send_notification(
                user=instance.student,
                event_type="ACHIEVEMENT_UNLOCKED",
                title="New Achievement Unlocked! 🏆",
                message=f"Huzzah! You've earned the '{instance.achievement.title}' achievement: {instance.achievement.description}.",
                channels=["IN_APP", "EMAIL"]
            )
            update_ai_conversation_context(
                instance.student,
                f"Earned and unlocked the milestone badge: '{instance.achievement.title}'."
            )
        invalidate_student_dashboard_cache(instance.student)
    except Exception:
        pass

