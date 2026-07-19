import hashlib
import json
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.search.models import (
    SearchIndex, SearchDocument, SearchTerm, SearchAnalytics,
    SearchHistory, SearchSuggestion, SearchRanking, SearchClick,
    SearchFacet, SearchSynonym, SearchCache
)
from apps.search.serializers import (
    SearchIndexSerializer, SearchDocumentSerializer, SearchHistorySerializer,
    SearchTermSerializer, SearchSuggestionSerializer, SearchRankingSerializer,
    SearchAnalyticsSerializer, SearchFacetSerializer, SearchSynonymSerializer,
    SearchCacheSerializer, SearchClickInputSerializer
)
from apps.search.services import (
    IndexService, RankingService, SuggestionService, AnalyticsService,
    AutocompleteService, PermissionSearchService
)
from apps.search.selectors import (
    get_search_documents, get_user_search_history, get_popular_terms, get_trending_queries
)
from apps.search.validators import validate_query_string

class SearchPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100
    page_size_query_param = "page_size"


class SearchQueryViewSet(viewsets.ViewSet):
    """
    Unified search controller executing global search, module search,
    autocomplete, spelling suggestions, and click aggregations.
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["get"], url_path="query")
    def query(self, request):
        """
        Unified search endpoint supporting faceted filtering, custom ranking, and caching.
        """
        q = request.query_params.get("q", "").strip()
        index_name = request.query_params.get("index", "").strip() or None
        entity_type = request.query_params.get("entity_type", "").strip() or None
        facets_param = request.query_params.get("facets", "").strip()

        # Get page param for cache index hashing
        page_num = request.query_params.get("page", "1")

        # 1. Check SearchCache
        cache_key_raw = f"q:{q};index:{index_name};type:{entity_type};page:{page_num};facets:{facets_param}"
        cache_key = hashlib.md5(cache_key_raw.encode("utf-8")).hexdigest()
        
        try:
            cached_entry = SearchCache.objects.get(query_key=cache_key, expires_at__gt=timezone.now())
            return Response(cached_entry.results_json, status=status.HTTP_200_OK)
        except SearchCache.DoesNotExist:
            pass

        # 2. Input Validation
        try:
            validate_query_string(q)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Retrieve Base Search Documents
        queryset = get_search_documents(index_name=index_name, entity_type=entity_type)

        # 4. Enforce Permission-Aware Search
        queryset = PermissionSearchService.filter_by_permissions(queryset, request.user)

        # 5. Apply Lexical + Override Ranking Score
        queryset = RankingService.apply_ranking(queryset, q)

        # 6. Pagination
        paginator = SearchPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        # 7. Dynamic Facets Aggregations
        facet_counts = {}
        active_facets = SearchFacet.objects.filter(is_active=True)
        # Scan matching documents (limit scan to top 1000 matched items for performance safety)
        matched_sample = list(queryset.values("entity_type", "categories", "tags", "meta_data")[:1000])
        
        for facet in active_facets:
            field_name = facet.field_name
            counts = {}
            for doc in matched_sample:
                val = None
                if field_name in ["entity_type", "categories", "tags"]:
                    val = doc.get(field_name)
                else:
                    meta = doc.get("meta_data") or {}
                    val = meta.get(field_name)

                if val is not None:
                    # Parse delimited attributes
                    if field_name == "categories" and val:
                        elements = [c.strip() for c in val.split(",")]
                    elif field_name == "tags" and val:
                        elements = [t.strip() for t in val.split()]
                    else:
                        elements = [val]

                    for elem in elements:
                        if elem:
                            counts[str(elem)] = counts.get(str(elem), 0) + 1
            facet_counts[facet.name] = counts

        # 8. Spelling Correction Check
        spelling_suggestion = None
        if queryset.count() == 0:
            spelling_suggestion = SuggestionService.get_spelling_suggestion(q)

        # 9. Serialization
        serializer = SearchDocumentSerializer(page, many=True)
        results = paginator.get_paginated_response(serializer.data).data

        # Package payload response
        response_data = {
            "results": results.get("results"),
            "count": results.get("count"),
            "next": results.get("next"),
            "previous": results.get("previous"),
            "facets": facet_counts,
            "spelling_suggestion": spelling_suggestion
        }

        # 10. Log Analytics (Asynchronously in production, synchronous write for history trace)
        AnalyticsService.log_search(
            user=request.user,
            query_string=q,
            filters_applied={
                "index": index_name,
                "entity_type": entity_type,
                "facets": facets_param
            },
            results_count=results.get("count", 0)
        )

        # 11. Write to SearchCache
        try:
            SearchCache.objects.update_or_create(
                query_key=cache_key,
                defaults={
                    "results_json": response_data,
                    "expires_at": timezone.now() + timedelta(minutes=15)
                }
            )
        except Exception as e:
            logger_err = json.dumps({"error": f"Cache write failed: {e}"})
            # Safe fail if caching error

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="autocomplete")
    def autocomplete(self, request):
        """
        Instant prefix typeahead autocomplete suggest list.
        """
        q = request.query_params.get("q", "").strip()
        suggestions = AutocompleteService.get_autocomplete(q)
        return Response({"suggestions": suggestions}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="suggestions")
    def suggestions(self, request):
        """
        Gets full SearchSuggestion objects matching query.
        """
        q = request.query_params.get("q", "").strip()
        qs = SuggestionService.get_suggestions(q)
        serializer = SearchSuggestionSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="click")
    def click(self, request):
        """
        Logs result selection interaction metrics to build click-through statistics.
        """
        serializer = SearchClickInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        click = AnalyticsService.log_click(
            history_id=serializer.validated_data.get("history_id"),
            document_id=serializer.validated_data.get("document_id"),
            position=serializer.validated_data.get("position")
        )
        if not click:
            return Response({"error": "Click registration failed."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "recorded", "id": click.id}, status=status.HTTP_201_CREATED)


class SearchHistoryViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    API Viewset allowing users to list and clear their search history records.
    """
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_user_search_history(self.request.user)

    def destroy(self, request, *args, **kwargs):
        # Allow users to delete a history item
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PopularTermsViewSet(viewsets.ViewSet):
    """
    Endpoint returning top searched terms.
    """
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        limit = int(request.query_params.get("limit", "10"))
        qs = get_popular_terms(limit=limit)
        serializer = SearchTermSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# =============================================================================
# ADMIN INTERFACE OVERRIDES AND CONFIGURATIONS (STAFF ONLY WRITES)
# =============================================================================

from apps.search.permissions import IsAdminOrReadOnly

class SearchRankingViewSet(viewsets.ModelViewSet):
    """
    CRUD controls enabling staff to configure boost values and pins.
    """
    queryset = SearchRanking.objects.all()
    serializer_class = SearchRankingSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = SearchPagination


class SearchAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides dashboards logs for keyword performance and CTR charts.
    """
    queryset = SearchAnalytics.objects.all().order_by("-total_queries")
    serializer_class = SearchAnalyticsSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = SearchPagination


class SearchFacetViewSet(viewsets.ModelViewSet):
    """
    Administrative mapping registers setting which keys in meta_data aggregate facets.
    """
    queryset = SearchFacet.objects.all()
    serializer_class = SearchFacetSerializer
    permission_classes = [IsAdminOrReadOnly]


class SearchSynonymViewSet(viewsets.ModelViewSet):
    """
    Admin layout mapping equivalence lists (synonym sets).
    """
    queryset = SearchSynonym.objects.all()
    serializer_class = SearchSynonymSerializer
    permission_classes = [IsAdminOrReadOnly]
