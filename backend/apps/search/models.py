import uuid
from django.db import models
from django.conf import settings
from apps.base_models import BaseModel

class SearchIndex(BaseModel):
    """
    Search index configuration mapping specific areas of the ecosystem.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Search index name (e.g. articles, courses, books)")
    description = models.TextField(blank=True, null=True, help_text="Description of the index scope.")
    is_active = models.BooleanField(default=True, help_text="Indicates if this index is active and searched.")
    last_indexed_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp of the last full re-indexing execution.")

    class Meta:
        db_table = "search_indexes"
        verbose_name = "Search Index"
        verbose_name_plural = "Search Indexes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SearchDocument(BaseModel):
    """
    Unified search document representing indexed items across the ecosystem.
    """
    index = models.ForeignKey(SearchIndex, on_delete=models.CASCADE, related_name="documents", help_text="The index this document belongs to.")
    entity_type = models.CharField(max_length=100, db_index=True, help_text="The model class name of the source entity (e.g., 'Article', 'Course').")
    entity_id = models.UUIDField(db_index=True, help_text="UUID primary key of the source database record.")
    title = models.CharField(max_length=255, help_text="The main searchable title of the entity.")
    excerpt = models.TextField(blank=True, null=True, help_text="A short teaser or description text.")
    body = models.TextField(blank=True, null=True, help_text="Full text content for deep searching.")
    tags = models.CharField(max_length=1000, blank=True, null=True, help_text="Space-separated list of tag/keyword names.")
    categories = models.CharField(max_length=500, blank=True, null=True, help_text="Comma-separated category names.")
    author_name = models.CharField(max_length=150, blank=True, null=True, help_text="Searchable author name.")
    url_path = models.CharField(max_length=512, help_text="Canonical public relative path or URL to view the detail page.")
    is_published = models.BooleanField(default=True, db_index=True, help_text="Is the content publicly active.")
    published_at = models.DateTimeField(blank=True, null=True, db_index=True, help_text="When this content was published.")
    search_vector = models.TextField(blank=True, null=True, help_text="Pre-computed search tokens/lexemes.")
    meta_data = models.JSONField(default=dict, blank=True, help_text="Additional key-value fields for dynamic facets, filtering, and scoring.")

    class Meta:
        db_table = "search_documents"
        verbose_name = "Search Document"
        verbose_name_plural = "Search Documents"
        ordering = ["-published_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["index", "entity_type", "entity_id"],
                name="uq_search_document_index_entity"
            )
        ]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"], name="idx_search_doc_entity"),
            models.Index(fields=["is_published", "published_at"], name="idx_search_doc_pub_status"),
        ]

    def __str__(self):
        return f"[{self.entity_type}] {self.title}"


class SearchTerm(BaseModel):
    """
    Search terms and phrases queried by users to identify search trends.
    """
    term = models.CharField(max_length=255, unique=True, help_text="The normalized search query string.")
    frequency = models.PositiveIntegerField(default=1, help_text="Count of times this exact query has been searched.")
    last_queried_at = models.DateTimeField(auto_now=True, help_text="The most recent timestamp this query was run.")

    class Meta:
        db_table = "search_terms"
        verbose_name = "Search Term"
        verbose_name_plural = "Search Terms"
        ordering = ["-frequency", "-last_queried_at"]

    def __str__(self):
        return f"{self.term} ({self.frequency})"


class SearchAnalytics(BaseModel):
    """
    Aggregated search behavior analytics for query patterns.
    """
    query_string = models.CharField(max_length=255, unique=True, help_text="Normalized query text.")
    total_queries = models.PositiveIntegerField(default=0, help_text="Total number of searches executed for this query.")
    total_results = models.PositiveIntegerField(default=0, help_text="Average or last returned result count.")
    click_through_rate = models.FloatField(default=0.0, help_text="Percentage of queries resulting in a click (0.0 to 1.0).")
    avg_dwell_time = models.FloatField(default=0.0, help_text="Average time in seconds spent on clicked results.")

    class Meta:
        db_table = "search_analytics"
        verbose_name = "Search Analytics Entry"
        verbose_name_plural = "Search Analytics Entries"
        ordering = ["-total_queries"]

    def __str__(self):
        return f"Analytics for '{self.query_string}' (Queries: {self.total_queries}, CTR: {self.click_through_rate:.2%})"


class SearchHistory(BaseModel):
    """
    An individual record of a search operation performed by a user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_history",
        help_text="Optional link to the authenticated user who performed the search."
    )
    query = models.CharField(max_length=255, help_text="The search query text entered by the user.")
    filters_applied = models.JSONField(default=dict, blank=True, help_text="JSON representation of filter key-values applied.")
    results_count = models.PositiveIntegerField(default=0, help_text="Number of matching documents found.")
    searched_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the search request was executed.")

    class Meta:
        db_table = "search_histories"
        verbose_name = "Search History Record"
        verbose_name_plural = "Search History Records"
        ordering = ["-searched_at"]

    def __str__(self):
        user_str = self.user.email if self.user and hasattr(self.user, 'email') else (self.user.username if self.user else "Anonymous")
        return f"[{user_str}] '{self.query}' at {self.searched_at}"


class SearchSuggestion(BaseModel):
    """
    Spelling corrections, autocomplete phrases, and suggested queries.
    """
    phrase = models.CharField(max_length=255, unique=True, help_text="Normalized phrase suggestion.")
    weight = models.FloatField(default=1.0, help_text="Display priority weight for auto-completion suggestions.")
    is_active = models.BooleanField(default=True, help_text="Whether this suggestion is active and visible.")

    class Meta:
        db_table = "search_suggestions"
        verbose_name = "Search Suggestion"
        verbose_name_plural = "Search Suggestions"
        ordering = ["-weight", "phrase"]

    def __str__(self):
        return self.phrase


class SearchRanking(BaseModel):
    """
    Manual overrides or custom score boosts for specific queries targeting specific documents.
    """
    document = models.ForeignKey(SearchDocument, on_delete=models.CASCADE, related_name="rankings", help_text="Target document to boost.")
    query = models.CharField(max_length=255, help_text="The query string that triggers this ranking rule.")
    boost_score = models.FloatField(default=1.0, help_text="Relevance multiplier or score addition for matching search document.")
    is_pinned = models.BooleanField(default=False, help_text="Force document to be pinned as the top search result.")

    class Meta:
        db_table = "search_rankings"
        verbose_name = "Search Ranking Override"
        verbose_name_plural = "Search Ranking Overrides"
        constraints = [
            models.UniqueConstraint(
                fields=["document", "query"],
                name="uq_search_ranking_doc_query"
            )
        ]
        indexes = [
            models.Index(fields=["query"], name="idx_search_rank_query"),
        ]

    def __str__(self):
        prefix = "PINNED" if self.is_pinned else f"BOOST({self.boost_score})"
        return f"{prefix} for '{self.query}' -> {self.document.title}"


class SearchClick(BaseModel):
    """
    Tracking click interactions on search results to compute click-through rates.
    """
    history = models.ForeignKey(
        SearchHistory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="clicks",
        help_text="The historical search session during which this click occurred."
    )
    document = models.ForeignKey(SearchDocument, on_delete=models.CASCADE, related_name="clicks", help_text="The document that was clicked.")
    clicked_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the user clicked the result.")
    position = models.PositiveIntegerField(help_text="The rank position index of the clicked document (e.g. 1 for top result).")

    class Meta:
        db_table = "search_clicks"
        verbose_name = "Search Click Record"
        verbose_name_plural = "Search Click Records"
        ordering = ["-clicked_at"]

    def __str__(self):
        return f"Click position {self.position} on document: {self.document.id}"


class SearchFacet(BaseModel):
    """
    Registrar of dynamic filters/facets mapped to attributes in SearchDocument meta_data.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Human readable facet label (e.g. 'Level', 'Format').")
    field_name = models.CharField(max_length=100, help_text="The JSON key inside SearchDocument.meta_data or model attribute name.")
    is_active = models.BooleanField(default=True, help_text="Whether this facet is active on search queries.")

    class Meta:
        db_table = "search_facets"
        verbose_name = "Search Facet"
        verbose_name_plural = "Search Facets"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.field_name})"


class SearchSynonym(BaseModel):
    """
    Equivalency map to expand terms on search queries (e.g. 'exam' = 'test', 'assessment').
    """
    term = models.CharField(max_length=255, unique=True, help_text="The primary search keyword.")
    synonyms = models.TextField(help_text="Comma-separated synonyms that map to this primary term.")
    is_active = models.BooleanField(default=True, help_text="Whether the synonym mapping is active.")

    class Meta:
        db_table = "search_synonyms"
        verbose_name = "Search Synonym"
        verbose_name_plural = "Search Synonyms"
        ordering = ["term"]

    def __str__(self):
        return f"{self.term} -> {self.synonyms}"


class SearchCache(BaseModel):
    """
    Caches common search queries to prevent heavy database queries.
    """
    query_key = models.CharField(max_length=255, unique=True, help_text="The unique MD5 or string key identifier for query parameters.")
    results_json = models.JSONField(help_text="Cached list of matching document objects.")
    expires_at = models.DateTimeField(db_index=True, help_text="Expiry timestamp for cached results.")

    class Meta:
        db_table = "search_caches"
        verbose_name = "Search Cache Entry"
        verbose_name_plural = "Search Cache Entries"
        ordering = ["expires_at"]

    def __str__(self):
        return f"Cache {self.query_key} (expires {self.expires_at})"
