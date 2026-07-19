# Sprint 24 — Phase 3: Backend Services Report

## Completed Work
Implemented the core business logic services, query abstraction layers, input validation rules, custom filters, background Celery tasks, and signal handlers for the AI feature module of BrahmaVidya Galaxy.

### 1. `services.py`
- **Gemini SDK Integration**: Wrapper around `google-generativeai` with a high-fidelity mock fallback mechanism when `GEMINI_API_KEY` is not present in Django settings. Supports chat context execution, streaming mock simulations, and schema-guided JSON outputs.
- **Context Window Service**: Multi-layered conversation memory management (Redis caches recent N active items with TTL, DB logs history, and Summarisation is triggered when tokens exceed limit).
- **Embedding & RAG Services**: Splitting of documents into overlapping chunk windows, persistence of chunks in `KnowledgeContext`, and keyword/pgvector retrieval mechanisms to feed context-grounded context into system prompts.
- **Academic Generators**: Core services for study planning, Leitner-spaced flashcard scheduling, Bloom's Taxonomy-based quiz/question generation, and personalised learning recommendation pipelines.
- **Usage & Quotas**: Logs tokens, estimates costs, caches usage, and enforces rate limit quotas per membership tier.

### 2. `selectors.py`
- Clear read-only query abstractions for model registry, prompts, chat histories, active study plans/sessions, due flashcards, generated quizzes, recommendations, and execution tasks with Redis caches.

### 3. `validators.py`
- Payload schema validation for all API inputs: chat message lengths, model availability, quiz parameters, flashcard structures, Leitner reviews, study plans, embeddings, and formats.

### 4. `filters.py`
- Django FilterSets for prompt categories, active plans, deck metadata, flashcard boxes, quiz difficulties, recommendation statuses, usage features, and Celery tasks.

### 5. `tasks.py`
- Celery worker tasks for calculating text embeddings asynchronously (`async_embed_context_task`) and compiling conversation summaries (`summarize_conversation_task`).

### 6. `signals.py`
- Automated post-save event hooks on `KnowledgeContext` ingestion to kick off background embedding runs and on `AIMessage` inputs to invalidate memory cache and schedule auto-summarisation.
- Registered signals under `AiConfig.ready()` in `apps/ai/apps.py`.

---

## Verification & Status
- Executed `python backend/manage.py check`:
  - **Result**: `System check identified no issues (0 silenced).`
- All modules integrate correctly with external services (Redis, Celery, and Gemini AI).
