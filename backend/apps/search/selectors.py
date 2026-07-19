from django.utils import timezone
from apps.search.models import SearchDocument, SearchHistory, SearchTerm, SearchAnalytics

def get_search_documents(index_name=None, entity_type=None, is_published=True):
    """
    Returns search documents filtered by index, entity type, and publication status.
    """
    qs = SearchDocument.objects.all()
    if index_name:
        qs = qs.filter(index__name=index_name)
    if entity_type:
        qs = qs.filter(entity_type=entity_type)
    if is_published is not None:
        qs = qs.filter(is_published=is_published)
    return qs

def get_user_search_history(user, limit=10):
    """
    Retrieves the most recent search history records for a specific user.
    """
    if not user or not user.is_authenticated:
        return SearchHistory.objects.none()
    return SearchHistory.objects.filter(user=user).order_by("-searched_at")[:limit]

def get_popular_terms(limit=10):
    """
    Retrieves the most frequently searched terms.
    """
    return SearchTerm.objects.all().order_by("-frequency", "-last_queried_at")[:limit]

def get_trending_queries(limit=10):
    """
    Retrieves trending queries sorted by query counts and click-through rates.
    """
    return SearchAnalytics.objects.filter(total_queries__gt=0).order_by("-total_queries", "-click_through_rate")[:limit]
