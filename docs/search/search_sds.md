# Software Design Specification (SDS): Unified Enterprise Search Platform

## 1. System Architecture
The search platform is implemented using a service-oriented structure within the Django backend, routed via Node/Express gateway, and rendered dynamically in the React frontend.

### Subsystems Map
* **Express Gateway:** Intercepts client search routes and forwards to Django.
* **REST API Controller:** Exposes Query, Autocomplete, Clicks tracking, history, and administrative viewsets.
* **Services Layer:** Contains `IndexService`, `RankingService`, `SuggestionService`, `AnalyticsService`, `AutocompleteService`, and `PermissionSearchService`.
* **Database Models:** Mapped in SQLite (SearchIndex, SearchDocument, SearchTerm, SearchHistory, SearchSuggestion, SearchRanking, SearchClick, SearchFacet, SearchSynonym, SearchCache).
* **Asynchronous Queue:** Celery background tasks executing indexing scripts.

## 2. Dynamic Scoring & Relevance Ranking
relevance score calculations are performed dynamically using SQLite filters and custom query overrides:
$$\text{Relevance Score} = \text{Base Text Match Score} \times \text{Synonym Match Score} \times \text{Ranking Boost Factor}$$
* Pinned results are forced to the top position with an override placement logic.
* Base search matches count title, excerpt, body, and tags matches.

## 3. Caching Protocol
Search results are cached in the database using MD5 key hashing over sorted query parameter permutations:
$$\text{Cache Key} = \text{MD5}(q + \text{index} + \text{type} + \text{facets} + \text{page})$$
Entries are automatically deleted on expiration by a scheduled celery task.
