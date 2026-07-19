from typing import Any, Dict, List
from django.utils import timezone
from django.db.models import Count, Q
from apps.lms.models import LiveClass, MeetingParticipant, Poll, PollOption, MeetingAnalytics

class LiveClassSelector:
    @staticmethod
    def get_upcoming_live_classes(user) -> List[LiveClass]:
        """
        Retrieves upcoming classes for courses the student is enrolled in or teacher is conducting.
        """
        now = timezone.now()
        if user.is_anonymous:
            return []
        
        # If user is a teacher, return their assigned scheduled/live classes
        if hasattr(user, "role") and user.role and user.role.name == "TEACHER":
            return list(
                LiveClass.objects.filter(teacher=user)
                .filter(Q(status="SCHEDULED") | Q(status="LIVE"))
                .order_by("scheduled_at")
            )
        
        # Fallback to general list of live classes
        return list(
            LiveClass.objects.filter(scheduled_at__gte=now)
            .filter(Q(status="SCHEDULED") | Q(status="LIVE"))
            .order_by("scheduled_at")
        )

    @staticmethod
    def get_active_participants(live_class_id: str) -> List[MeetingParticipant]:
        """
        Lists actively connected participants in the live stream.
        """
        return list(
            MeetingParticipant.objects.filter(live_class_id=live_class_id, left_at__isnull=True)
            .select_related("user")
        )

    @staticmethod
    def get_poll_results(poll_id: str) -> Dict[str, Any]:
        """
        Returns option vote counts for a poll.
        """
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return {}
        
        options = PollOption.objects.filter(poll=poll).annotate(vote_count=Count("votes"))
        return {
            "poll_id": str(poll.id),
            "question": poll.question,
            "results": [
                {"option_id": str(opt.id), "option_text": opt.option_text, "votes": opt.vote_count}
                for opt in options
            ]
        }

    @staticmethod
    def get_live_class_analytics(live_class_id: str) -> Dict[str, Any]:
        """
        Fetches or computes real-time stream summaries.
        """
        try:
            analytics = MeetingAnalytics.objects.get(live_class_id=live_class_id)
            return {
                "total_participants": analytics.total_participants,
                "average_engagement_score": analytics.average_engagement_score,
                "peak_concurrent_users": analytics.peak_concurrent_users,
            }
        except MeetingAnalytics.DoesNotExist:
            # Aggregate from active participants count
            participant_count = MeetingParticipant.objects.filter(live_class_id=live_class_id).count()
            return {
                "total_participants": participant_count,
                "average_engagement_score": 0.0,
                "peak_concurrent_users": participant_count,
            }
