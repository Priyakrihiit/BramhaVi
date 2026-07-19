from rest_framework import serializers
from apps.search.models import (
    SearchIndex, SearchDocument, SearchTerm, SearchAnalytics,
    SearchHistory, SearchSuggestion, SearchRanking, SearchClick,
    SearchFacet, SearchSynonym, SearchCache
)

class SearchIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchIndex
        fields = "__all__"


class SearchDocumentSerializer(serializers.ModelSerializer):
    index_name = serializers.CharField(source="index.name", read_only=True)
    relevance_score = serializers.FloatField(read_only=True)

    class Meta:
        model = SearchDocument
        fields = [
            "id", "index", "index_name", "entity_type", "entity_id",
            "title", "excerpt", "body", "tags", "categories", "author_name",
            "url_path", "is_published", "published_at", "meta_data", "relevance_score",
            "created_at", "updated_at"
        ]


class SearchTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchTerm
        fields = "__all__"


class SearchAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchAnalytics
        fields = "__all__"


class SearchHistorySerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = SearchHistory
        fields = ["id", "user", "user_email", "query", "filters_applied", "results_count", "searched_at"]
        read_only_fields = ["id", "searched_at"]


class SearchSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchSuggestion
        fields = "__all__"


class SearchRankingSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source="document.title", read_only=True)

    class Meta:
        model = SearchRanking
        fields = ["id", "document", "document_title", "query", "boost_score", "is_pinned", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SearchClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchClick
        fields = "__all__"


class SearchClickInputSerializer(serializers.Serializer):
    history_id = serializers.UUIDField(required=False, allow_null=True)
    document_id = serializers.UUIDField(required=True)
    position = serializers.IntegerField(required=True, min_value=1)


class SearchFacetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchFacet
        fields = "__all__"


class SearchSynonymSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchSynonym
        fields = "__all__"


class SearchCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchCache
        fields = "__all__"
