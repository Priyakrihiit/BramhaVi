# BrahmaVidya Search: Backend Developer Reference

This document details the backend architecture, services, signals, selectors, and Celery tasks implemented for the Unified Enterprise Search Platform in `backend/apps/search`.

---

## 1. App Components Map

The search platform is split into modular layers:

```
backend/apps/search/
├── __init__.py         # Package entry
├── apps.py             # App config & signals bootstrapping
├── models.py           # Database layout (11 tables)
├── validators.py       # Core input constraints
├── selectors.py        # Database lookup queries
├── services.py         # Business logic & engines (Index, Ranking, Suggestions, Permissions)
├── filters.py          # DRF query parameter parser
├── tasks.py            # Celery background workers
└── signals.py          # Django post_save/post_delete event hooks
```

---

## 2. Service Layer Reference (`services.py`)

### 1. `IndexService`
Manages the indexing operations of search document records.
* **`index_document(...)`**: Creates or updates a `SearchDocument` mapping. Generates a normalized `search_vector` from textual fields.
* **`delete_document(...)`**: Deletes search documents matching a source record's entity classifier and UUID.
* **`reindex_all()`**: Full batch reindexer parsing:
  - LMS `CourseStructure` curriculum nodes.
  - CMS `Article`, `Blog`, `Tutorial`, `FAQ`, and DAM `MediaFile` structures.
  - Marketplace `Book` publishing records.
  - Portfolio, Resume, and Job JSON models stored inside `portfolio_store.json`.

### 2. `RankingService`
Core relevance scoring engine applying lexical match scoring and overrides.
* **`apply_ranking(queryset, query_string)`**: Parses search terms, applies synonym expansion mappings (`SearchSynonym`), computes a weighted sum for field hits (Title weighted highest, followed by Tags, Excerpt, and Body), merges `SearchRanking` boost weights, enforces top-pinned results (`is_pinned=True`), and returns query results sorted by rank.

### 3. `SuggestionService`
* **`get_suggestions(...)`**: Prefix autocomplete suggestions from `SearchSuggestion`.
* **`get_spelling_suggestion(...)`**: Recommends correction alternatives using `difflib.get_close_matches` against active terms in `SearchTerm`.

### 4. `AnalyticsService`
* **`log_search(...)`**: Logs history logs (`SearchHistory`) and updates terms frequencies (`SearchTerm`).
* **`log_click(...)`**: Connects clicked results (`SearchClick`) to search sessions to evaluate CTR metrics in `SearchAnalytics`.
* **`aggregate_analytics()`**: Cron worker to recalculate CTR metrics globally.

### 5. `PermissionSearchService`
* **`filter_by_permissions(queryset, user)`**: Excludes draft resources (`is_published=False`) unless requested by an administrator.

---

## 3. Asynchronous Tasks (`tasks.py`) & Event Signals (`signals.py`)

Celery is hooked to automatically update search indexes asynchronously on model updates.

### Async Indexing Flow
1. User saves or deletes a Django record (e.g., updates a CMS `Article` to published).
2. Django receiver in [signals.py](file:///c:/Users/USER/Downloads/bramhavi/backend/apps/search/signals.py) intercepts the `post_save` or `post_delete` transaction event.
3. The signal triggers `index_document_task.delay(entity_type, entity_id)` or `delete_document_task.delay(entity_type, entity_id)`.
4. Celery worker picks up the job and maps/writes the new search record.

### Periodic Jobs (Celery Beat)
* **`reindex_all_task`**: Rebuilds search documents to align references.
* **`aggregate_search_analytics_task`**: Compiles search terms CTR metrics.
* **`clear_expired_cache_task`**: Deletes expired search query cache entries.

---

## 4. Query Selectors & Input Validators

### Selectors (`selectors.py`)
* **`get_search_documents(...)`**: Standard querying interface applying base filters.
* **`get_user_search_history(user)`**: Resolves recent query terms executed by a user.
* **`get_popular_terms()`**: Returns trending terms sorted by frequency.

### Validators (`validators.py`)
* **`validate_query_string(...)`**: Raises `ValidationError` if query string is empty, null, or exceeds 255 characters.
* **`validate_boost_score(...)`**: Verifies boost overrides are non-negative.
