# Developer Onboarding Guide: Unified Enterprise Search Platform

This guide helps developers understand the search codebase structure and how to extend indexing capabilities.

---

## 1. Directory Structure

The search module code is organized as follows:

```
backend/apps/search/
├── models.py      # Mappings for the 11 search index tables (SearchDocument, SearchCache, etc.)
├── selectors.py   # Database query handlers (get_search_documents, get_popular_terms)
├── services.py    # Core services (IndexService, RankingService, SuggestionService)
├── tasks.py       # Celery task definitions for asynchronous indexing
├── signals.py     # Signal listeners that queue indexing tasks on save/delete
├── views.py       # REST API viewsets (Query, History, Click logging, Admin panels)
└── serializers.py # REST request/response serializer definitions
```

---

## 2. Dynamic Indexing Signals

To extend automated search indexing to a new Django model:
1. Open [signals.py](file:///c:/Users/USER/Downloads/bramhavi/backend/apps/search/signals.py) and define a `post_save` and `post_delete` receiver.
2. In the post-save receiver, queue the Celery task:
   `index_document_task.delay(entity_type_name, str(instance.id))`
3. Open [tasks.py](file:///c:/Users/USER/Downloads/bramhavi/backend/apps/search/tasks.py) and update `index_document_task` to handle your model. Add an `elif` branch to load the model by ID, compile its text fields into a search vector, and register it:
   ```python
   IndexService.index_document(
       index_name="new_index",
       entity_type=entity_type,
       entity_id=entity_id,
       title=instance.title,
       excerpt=instance.description[:200],
       body=instance.description,
       url_path=f"/module/url/{instance.id}"
   )
   ```
4. Verify your changes compile correctly by running:
   ```bash
   python backend/manage.py check
   ```
