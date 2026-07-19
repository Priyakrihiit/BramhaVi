from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth import get_user_model
from django.utils import timezone
from .services import EventCollectorService

User = get_user_model()


@receiver(user_logged_in)
def handle_login_session(sender, request, user, **kwargs):
    """
    Hooks standard django login to record user session logs.
    """
    if request:
        session_key = getattr(request.session, "session_key", None) or f"sess_{user.id}_{timezone.now().timestamp()}"
        ip_addr = request.META.get("REMOTE_ADDR")
        agent = request.META.get("HTTP_USER_AGENT")
        
        EventCollectorService.start_session(
            user=user,
            session_key=session_key,
            ip_address=ip_addr,
            user_agent=agent,
            device_type="Desktop",
            browser_type="Chrome"
        )
        
        # Log metric event
        EventCollectorService.track_event(
            user=user,
            metric_name="User Login Success",
            metric_value=1.0,
            context_data={"ip_address": ip_addr}
        )


@receiver(user_logged_out)
def handle_logout_session(sender, request, user, **kwargs):
    """
    Hooks standard django logout to mark session inactive.
    """
    if request and user:
        session_key = getattr(request.session, "session_key", None)
        if session_key:
            EventCollectorService.end_session(session_key)
            
        # Log metric event
        EventCollectorService.track_event(
            user=user,
            metric_name="User Logout",
            metric_value=1.0
        )


@receiver(post_save, sender="lms.LearningProgress")
def handle_course_progress_metric(sender, instance, created, **kwargs):
    """
    Logs lesson starts and course completions telemetry metrics.
    """
    if created:
        EventCollectorService.track_event(
            user=instance.student,
            metric_name="Lesson Started",
            metric_value=1.0,
            context_data={"course_id": str(instance.node.id) if instance.node else None}
        )
    elif instance.is_completed:
        EventCollectorService.track_event(
            user=instance.student,
            metric_name="Course Completed",
            metric_value=1.0,
            context_data={"course_id": str(instance.node.id) if instance.node else None}
        )


@receiver(post_save, sender="wallets.Payment")
def handle_payment_transaction_metric(sender, instance, created, **kwargs):
    """
    Logs financial sales metrics to the events collection.
    """
    if instance.status in ["COMPLETED", "SUCCESS"]:
        EventCollectorService.track_event(
            user=instance.user,
            metric_name="Payment Success",
            metric_value=float(instance.amount),
            context_data={"payment_id": str(instance.id), "currency": instance.currency}
        )


@receiver(post_save, sender="lms.AssignmentSubmission")
def handle_assignment_submission_metric(sender, instance, created, **kwargs):
    """
    Logs student assignment submissions.
    """
    if created:
        EventCollectorService.track_event(
            user=instance.student,
            metric_name="Assignment Submitted",
            metric_value=1.0,
            context_data={"assignment_id": str(instance.assignment.id) if instance.assignment else None}
        )


@receiver(post_save, sender="lms.PracticeSession")
def handle_practice_session_metric(sender, instance, created, **kwargs):
    """
    Logs practice set completions metrics.
    """
    if instance.is_completed:
        EventCollectorService.track_event(
            user=instance.student,
            metric_name="Practice Completed",
            metric_value=1.0,
            context_data={"score": float(instance.score)}
        )


@receiver(post_save, sender="lms.ExamAttempt")
def handle_exam_attempt_metric(sender, instance, created, **kwargs):
    """
    Logs completed exam scores.
    """
    if instance.completed_at:
        EventCollectorService.track_event(
            user=instance.student,
            metric_name="Exam Completed",
            metric_value=1.0,
            context_data={
                "exam_id": str(instance.exam.id) if instance.exam else None,
                "score": float(instance.score_obtained)
            }
        )


@receiver(post_save, sender="lms.Certificate")
def handle_certificate_metric(sender, instance, created, **kwargs):
    """
    Logs certificate issuances.
    """
    if created:
        EventCollectorService.track_event(
            user=instance.user,
            metric_name="Certificate Issued",
            metric_value=1.0,
            context_data={"course_title": instance.course.title if instance.course else None}
        )


@receiver(post_save, sender="lms.UserBadge")
def handle_badge_metric(sender, instance, created, **kwargs):
    """
    Logs badge award events.
    """
    if created:
        EventCollectorService.track_event(
            user=instance.user,
            metric_name="Badge Awarded",
            metric_value=1.0,
            context_data={"badge_title": instance.badge.title if instance.badge else None}
        )


@receiver(post_save, sender="cms.ForumPost")
def handle_forum_post_metric(sender, instance, created, **kwargs):
    """
    Logs community posts.
    """
    if created:
        EventCollectorService.track_event(
            user=instance.author,
            metric_name="Forum Post Created",
            metric_value=1.0,
            context_data={"topic_id": str(instance.topic.id) if instance.topic else None}
        )


@receiver(post_save, sender="cms.Comment")
def handle_comment_metric(sender, instance, created, **kwargs):
    """
    Logs blog comments additions.
    """
    if created:
        EventCollectorService.track_event(
            user=instance.author,
            metric_name="Blog Comment Added",
            metric_value=1.0,
            context_data={"blog_id": str(instance.blog.id) if instance.blog else None}
        )


@receiver(post_save, sender="publishing.Book")
def handle_book_metric(sender, instance, created, **kwargs):
    """
    Logs published bookstore textbook entries.
    """
    if created or instance.status == "PUBLISHED":
        EventCollectorService.track_event(
            user=instance.author,
            metric_name="Book Published",
            metric_value=1.0,
            context_data={"book_id": str(instance.id), "title": instance.title}
        )


@receiver(post_save, sender="search.SearchHistory")
def handle_search_query_metric(sender, instance, created, **kwargs):
    """
    Logs run search query logs.
    """
    if created:
        EventCollectorService.track_event(
            user=instance.user,
            metric_name="Search Query Run",
            metric_value=1.0,
            context_data={"query": instance.query}
        )


@receiver(post_save, sender="notifications.NotificationRecord")
def handle_notification_broadcast_metric(sender, instance, created, **kwargs):
    """
    Logs alert dispatches.
    """
    if created:
        EventCollectorService.track_event(
            user=instance.user,
            metric_name="Notification Broadcasted",
            metric_value=1.0,
            context_data={"category": instance.category}
        )


@receiver(post_save, sender="seo.SEOPage")
def handle_seo_page_metric(sender, instance, created, **kwargs):
    """
    Logs sitemaps updates.
    """
    if created or instance.meta_title:
        EventCollectorService.track_event(
            user=None,
            metric_name="SEO Page Updated",
            metric_value=1.0,
            context_data={"url_path": getattr(instance, 'url_path', getattr(instance, 'slug', ''))}
        )


@receiver(post_save, sender="control_center.MediaFile")
def handle_media_upload_metric(sender, instance, created, **kwargs):
    """
    Logs digital assets uploads.
    """
    if created:
        EventCollectorService.track_event(
            user=instance.uploaded_by,
            metric_name="Media File Uploaded",
            metric_value=1.0,
            context_data={"file_size": instance.file_size}
        )


@receiver(post_save, sender="control_center.AIMessage")
def handle_ai_message_metric(sender, instance, created, **kwargs):
    """
    Logs chatbot prompt conversions and tokens loads.
    """
    if created:
        EventCollectorService.track_event(
            user=instance.conversation.user if instance.conversation else None,
            metric_name="AI Message Logged",
            metric_value=float(instance.token_count),
            context_data={"sender_type": instance.sender_type}
        )
