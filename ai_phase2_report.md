# Sprint 24 — Phase 2: Database Extension Report
## BrahmaVidya Galaxy — AI Learning Platform Database Models

**Sprint:** 24 — Phase 2
**Date:** 2026-07-19
**Status:** COMPLETE ✅

---

## Executive Summary

Created `backend/apps/ai/models.py` with **17 new Django models** covering all
missing AI database entities. Applied and verified migration
`ai.0001_sprint24_phase2_ai_models`. Django system check passes with **0 issues**.

---

## Command Results

```
python backend/manage.py makemigrations ai --name="sprint24_phase2_ai_models"
  → Migrations for 'ai': backend\apps\ai\migrations\0001_sprint24_phase2_ai_models.py
    + 17 models created, 45 indexes/constraints registered

python backend/manage.py migrate
  → Applying ai.0001_sprint24_phase2_ai_models... OK

python backend/manage.py check
  → System check identified no issues (0 silenced)
```

---

## Models Created in `backend/apps/ai/models.py`

| # | Model | DB Table | Purpose |
|---|---|---|---|
| 1 | `AIModelRegistry` | `ai_model_registry` | Persistent AI model catalog (migrated from JSON) |
| 2 | `PromptTemplate` | `ai_prompt_templates` | Versioned prompt library (migrated from JSON) |
| 3 | `AIChatSession` | `ai_chat_sessions` | Per-session tracking (migrated from JSON) |
| 4 | `AIUsageLog` | `ai_usage_logs` | Per-request token+cost log (migrated from JSON list) |
| 5 | `AITokenLog` | `ai_token_logs` | Per-user per-day token rollup for quota |
| 6 | `AIRateLimitQuota` | `ai_rate_limit_quotas` | Per-user tier quota configuration |
| 7 | `AIAgentConfig` | `ai_agent_configs` | Per-feature agent personality+model config |
| 8 | `KnowledgeContext` | `ai_knowledge_context` | Content chunks for RAG grounding |
| 9 | `ConversationMemory` | `ai_conversation_memory` | AI-generated long-term conversation summary |
| 10 | `StudyPlan` | `ai_study_plans` | AI-generated weekly study plans |
| 11 | `StudyPlanSession` | `ai_study_plan_sessions` | Individual sessions within a study plan |
| 12 | `FlashcardDeck` | `ai_flashcard_decks` | AI-generated flashcard deck |
| 13 | `Flashcard` | `ai_flashcards` | Individual flashcard with Leitner spaced repetition |
| 14 | `QuizGeneration` | `ai_quiz_generations` | AI quiz generation record + full output |
| 15 | `QuizQuestion` | `ai_quiz_questions` | Individual question extracted from a QuizGeneration |
| 16 | `LearningRecommendation` | `ai_learning_recommendations` | AI personalized content recommendations |
| 17 | `AITask` | `ai_tasks` | Celery async task tracking and status |

---

## Pre-Existing Models (NOT Modified — Already in `control_center`)

| Model | DB Table | Status |
|---|---|---|
| `AIConversation` | `ai_conversations` | ✅ Exists — 2 rows |
| `AIMessage` | `ai_messages` | ✅ Exists — 4 rows |
| `AIFeedback` | `ai_feedback` | ✅ Exists — 0 rows |

---

## Database Verification

All 20 AI tables confirmed present in SQLite:

```
ai_agent_configs:          0 rows  (new)
ai_chat_sessions:          0 rows  (new)
ai_conversation_memory:    0 rows  (new)
ai_conversations:          2 rows  (pre-existing)
ai_feedback:               0 rows  (pre-existing)
ai_flashcard_decks:        0 rows  (new)
ai_flashcards:             0 rows  (new)
ai_knowledge_context:      0 rows  (new)
ai_learning_recommendations: 0 rows (new)
ai_messages:               4 rows  (pre-existing)
ai_model_registry:         0 rows  (new)
ai_prompt_templates:       0 rows  (new)
ai_quiz_generations:       0 rows  (new)
ai_quiz_questions:         0 rows  (new)
ai_rate_limit_quotas:      0 rows  (new)
ai_study_plan_sessions:    0 rows  (new)
ai_study_plans:            0 rows  (new)
ai_tasks:                  0 rows  (new)
ai_token_logs:             0 rows  (new)
ai_usage_logs:             0 rows  (new)

Total AI Tables: 20
```

---

## Migration File

`backend/apps/ai/migrations/0001_sprint24_phase2_ai_models.py`

- 17 CreateModel operations
- 45 CreateIndex / AddConstraint operations
- No dependencies on other app migrations (self-contained)
- SQLite-compatible (no pgvector, no GIN, no PostgreSQL-specific features)

---

## Design Decisions

| Decision | Rationale |
|---|---|
| SQLite-compatible fields only | `USE_SQLITE=True` is the default; pgvector deferred to PostgreSQL phase |
| `KnowledgeContext.embedding_json` as TextField | Stores 1536-dim embedding as JSON string for SQLite; replace with VectorField when PostgreSQL is used |
| No duplication of `AIConversation`, `AIMessage`, `AIFeedback` | Already exist in `control_center/models.py`; referenced via FK |
| `PromptTemplate` uses `SoftDeleteModel` | Templates are curated assets; hard delete would break prompt history |
| `FlashcardDeck` uses `SoftDeleteModel` | Student data should be soft-deleted to allow recovery |
| `StudyPlan` uses `SoftDeleteModel` | Weekly plans should be archivable, not permanently deleted |
| `AITask` tracks all Celery task IDs | Enables task status polling without hitting Celery backend directly |
| Unique constraint on `AITokenLog(user, log_date)` | Enforces one aggregate row per user per day; use UPDATE or get_or_create |
| `QuizQuestion` extracted from `QuizGeneration` | Enables question reuse and cross-quiz de-duplication |

---

## Index Summary (45 total)

```
AIChatSession:          idx_session_user_date, idx_session_feature_date
AITask:                 idx_aitask_type_status, idx_aitask_user_date, idx_aitask_status_date
AITokenLog:             idx_token_log_user_date + uq_token_log_user_date (constraint)
AIUsageLog:             idx_usage_user_date, idx_usage_feature_date, idx_usage_model_date
FlashcardDeck:          idx_deck_student_date, idx_deck_lesson
Flashcard:              idx_card_deck_review, idx_card_leitner
LearningRecommendation: idx_rec_student_status, idx_rec_student_type, idx_rec_priority
PromptTemplate:         idx_prompt_cat_active, idx_prompt_pub_active
QuizGeneration:         idx_quiz_lesson_diff, idx_quiz_user_date
QuizQuestion:           idx_qq_gen_num
StudyPlan:              idx_study_plan_student_week, idx_study_plan_student_active
StudyPlanSession:       idx_sps_plan_date, idx_sps_completed
KnowledgeContext:       idx_knowledge_source, idx_knowledge_embedded + uq_knowledge_chunk
```

---

## Next Phase

**Sprint 24 — Phase 3: Backend Services**

- `backend/apps/ai/services.py` — GeminiService, RAGService, EmbeddingService, ContextWindowService
- `backend/apps/ai/tasks.py` — Celery async task implementations
- `backend/apps/ai/signals.py` — post_save triggers for embedding + indexing
- `backend/apps/ai/selectors.py` — ORM query selectors
- `backend/apps/ai/validators.py` — Input validators

---

*Generated: Sprint 24 — Phase 2*
*Migration: ai.0001_sprint24_phase2_ai_models*
*Status: COMPLETE — 0 Issues*
