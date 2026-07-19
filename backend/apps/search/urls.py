from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.search.views import (
    SearchQueryViewSet, SearchHistoryViewSet, PopularTermsViewSet,
    SearchRankingViewSet, SearchAnalyticsViewSet, SearchFacetViewSet,
    SearchSynonymViewSet
)

app_name = "search"

router = DefaultRouter()
router.register("history", SearchHistoryViewSet, basename="history")
router.register("popular", PopularTermsViewSet, basename="popular")
router.register("ranking", SearchRankingViewSet, basename="ranking")
router.register("analytics", SearchAnalyticsViewSet, basename="analytics")
router.register("facets", SearchFacetViewSet, basename="facets")
router.register("synonyms", SearchSynonymViewSet, basename="synonyms")

urlpatterns = [
    # Search Action controllers
    path("query/", SearchQueryViewSet.as_view({"get": "query"}), name="query"),
    path("autocomplete/", SearchQueryViewSet.as_view({"get": "autocomplete"}), name="autocomplete"),
    path("suggestions/", SearchQueryViewSet.as_view({"get": "suggestions"}), name="suggestions"),
    path("click/", SearchQueryViewSet.as_view({"post": "click"}), name="click"),
    
    # Admin settings and dashboards
    path("", include(router.urls)),
]
