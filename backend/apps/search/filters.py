import django_filters
from apps.search.models import SearchDocument

class SearchDocumentFilter(django_filters.FilterSet):
    """
    Search parameter filter definitions.
    """
    index_name = django_filters.CharFilter(field_name="index__name", lookup_expr="iexact")
    entity_type = django_filters.CharFilter(field_name="entity_type", lookup_expr="iexact")
    tag = django_filters.CharFilter(field_name="tags", lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="categories", lookup_expr="icontains")
    published_from = django_filters.DateTimeFilter(field_name="published_at", lookup_expr="gte")
    published_to = django_filters.DateTimeFilter(field_name="published_at", lookup_expr="lte")

    class Meta:
        model = SearchDocument
        fields = ["index", "entity_type", "is_published"]
