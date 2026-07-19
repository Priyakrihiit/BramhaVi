# Sprint 24 — AI Platform Analysis Report
## BrahmaVidya Galaxy — Enterprise AI Learning Platform Audit

**Date:** 2026-07-19  
**Sprint:** 24 — Phase 0  
**Scope:** Complete repository audit — NO code changes made  
**Analyst:** Antigravity Agent (Re-analysis from current state)

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Repository Topology](#2-repository-topology)
3. [Backend AI Audit — backend/apps/ai](#3-backend-ai-audit)
4. [Control Center AI Models](#4-control-center-ai-models)
5. [Integration Audit](#5-integration-audit)
6. [Frontend AI Audit](#6-frontend-ai-audit)
7. [Gateway AI Audit — server.ts](#7-gateway-ai-audit)
8. [Infrastructure Audit — Redis, Celery](#8-infrastructure-audit)
9. [Gap Analysis Matrix](#9-gap-analysis-matrix)
10. [Recommended Target Architecture](#10-recommended-target-architecture)
11. [Implementation Priority Roadmap](#11-implementation-priority-roadmap)
12. [Risk Register](#12-risk-register)

---

## 1. Executive Summary

The BrahmaVidya Galaxy platform contains a **partial, foundational AI implementation** that provides conversation management, message threading, prompt templates, model registry, session tracking, and usage logging. However, the current implementation has several critical limitations that prevent it from qualifying as an **Enterprise AI Learning Platform**.

| Dimension | Current State | Target State |
|---|---|---|
| AI Conversation Persistence | Split: DB (AIConversation) + JSON file (ai_store.json) | Fully PostgreSQL-backed |
| AI Response Generation | Mock responses (generate_mock_assistant_response) | Real Gemini API streaming |
| Search Grounding | Not implemented | Vector search + Semantic retrieval |
| Context Window Management | Static 5-message window (hardcoded) | Dynamic token-budget-aware context |
| Streaming | Not implemented | Server-Sent Events / WebSocket |
| Multimodal | Not implemented | Gemini Vision for document/image analysis |
| Student AI Integration | Partial (frontend-only mock timeout) | Deep LMS context injection |
| Teacher AI Integration | Not implemented | Curriculum AI generation, Quiz AI, Analytics AI |
| AI Analytics | JSON list only (usage_tracking) | Full PostgreSQL-backed AI analytics |
| Frontend AI Service | 3 basic endpoints in api.ts | Full AI SDK covering all enterprise features |

**Verdict: Approximately 30% complete** for an enterprise AI learning platform. The architecture is sound but real Gemini integration, streaming, vector embeddings, semantic search grounding, multimodal support, and deep LMS/Student/Teacher integration are entirely absent.

---

## 2. Repository Topology

```
bramhavi/
-- backend/
   -- apps/
      -- ai/                    <- Primary AI app
         -- ai_store.json       <- JSON-based persistence (CRITICAL GAP)
         -- ai_store.py         <- JSON CRUD interface
         -- serializers.py      <- AI serializers
         -- urls.py             <- AI endpoint router
         -- utils.py            <- Mock generation + token estimation
         -- views.py            <- ViewSets (944 lines)
      -- control_center/
         -- models.py           <- AIConversation, AIMessage, AIFeedback
      -- student/               <- No AI integration
      -- teacher/               <- No AI integration
      -- lms/                   <- No AI integration
      -- search/                <- Partial AI bridge (one-way)
      -- analytics/             <- No AI events
      -- notifications/         <- No AI triggers
      -- cms/                   <- No AI integration
-- src/
   -- pages/public/
      -- CoursesShell.tsx       <- Frontend AI sidebar (mock timeout)
   -- components/               <- No dedicated AI components
   -- services/
      -- api.ts                 <- 3 AI endpoints only
-- server.ts                    <- Gemini SDK imported, lazy-init, AI routes mapped
```

---

## 3. Backend AI Audit

### 3.1 What Exists in backend/apps/ai

#### DONE: AI URLs (urls.py)
Eight registered ViewSet routes:
- /api/v1/ai/conversations/  -> ConversationViewSet
- /api/v1/ai/messages/       -> MessageViewSet
- /api/v1/ai/feedback/       -> FeedbackViewSet
- /api/v1/ai/prompts/        -> PromptTemplateViewSet
- /api/v1/ai/models/         -> AIModelViewSet
- /api/v1/ai/sessions/       -> ChatSessionViewSet
- /api/v1/ai/usage/          -> UsageTrackingViewSet
- /api/v1/ai/analytics/      -> AnalyticsViewSet

#### DONE: ViewSets (views.py — 944 lines)
- ConversationViewSet: Full CRUD via AIConversation PostgreSQL model. Supports pagination, search, restore (soft delete), export (json/markdown/text), context memory view + cleanup.
- MessageViewSet: Retrieve + partial update (pin/important) + feedback. Message responses use generate_mock_assistant_response() — NOT real Gemini.
- FeedbackViewSet: Admin read-only list/retrieve. Feedback stored in JSON.
- PromptTemplateViewSet: Full CRUD backed by JSON. Category filters, search, sort, public/private toggle, versioning, favorites.
- AIModelViewSet: Registry CRUD backed by JSON. Enable/disable actions.
- ChatSessionViewSet: Session tracking backed by JSON. Start/end/duration.
- UsageTrackingViewSet: Usage log backed by JSON list.
- AnalyticsViewSet: Aggregates from JSON usage list.

#### DONE: Serializers (serializers.py — 169 lines)
- ConversationSerializer, MessageSerializer, FeedbackSerializer
- PromptTemplateSerializer, AIModelSerializer, ChatSessionSerializer
- AIUsageTrackingSerializer, ConversationExportSerializer, TokenAccountingSerializer
- Rich metadata serializers: AttachmentMetadataSerializer, ImageMetadataSerializer, ReferenceSerializer, CitationSerializer

#### DONE: ai_store.py — JSON Store Interface (360 lines)
Thread-safe (mutex-locked) flat-file JSON persistence for conversations, messages, feedback, prompts (pre-seeded with 12 category templates), models (pre-seeded: Gemini 1.5 Pro, Gemini 1.5 Flash, GPT-4o, Claude 3.5 Sonnet, Llama 3 70B, Mistral Large), sessions, usage_tracking.

The store dispatches Celery tasks (index_ai_item_task) on conversation/prompt save for search indexing.

#### DONE: utils.py — Utility Layer (179 lines)
- filter_list(), search_list(), order_list() — Generic list manipulation
- estimate_tokens() — Character-based token approximation (4 chars/token)
- calculate_cost() — Token cost calculator
- generate_mock_assistant_response() — Rich mock response with markdown, code blocks, references, citations (NOT real AI)

### 3.2 Critical Gaps in backend/apps/ai

| Gap | Severity | Details |
|---|---|---|
| No real Gemini API calls anywhere in the backend | CRITICAL | All AI responses are mocks |
| No streaming support | CRITICAL | No SSE, no websocket, no chunked responses |
| Hybrid persistence architecture | HIGH | Conversations in PostgreSQL, but messages/feedback/prompts/models/sessions in flat JSON |
| No vector embeddings | HIGH | No pgvector, no Pinecone, no Weaviate integration |
| No semantic search grounding | HIGH | No RAG pipeline, no document retrieval |
| No function calling | MEDIUM | Gemini function calling not implemented |
| No multimodal input | MEDIUM | No image/PDF/document ingestion to Gemini Vision |
| Token estimation is inaccurate | MEDIUM | len(text)/4 — no tiktoken or Gemini token counting API |
| No conversation summarization | MEDIUM | Long conversations not auto-summarized |
| Missing models.py in apps/ai | LOW | All Django models live in control_center |

---

## 4. Control Center AI Models

Located in backend/apps/control_center/models.py:

### DONE: AIConversation(SoftDeleteModel)
- db_table: ai_conversations
- Fields: user (FK->users.User), title (CharField)
- Inherits: id (UUID), created_at, updated_at, deleted_at
- Used by ConversationViewSet for CRUD operations

### DONE: AIMessage(BaseModel)
- db_table: ai_messages
- Fields: conversation (FK->AIConversation), sender_type (USER/ASSISTANT), content (TextField), token_count (IntegerField, always 0)
- Used by ConversationViewSet.messages() for creating user + assistant messages

### DONE: AIFeedback(models.Model)
- db_table: ai_feedback
- Fields: message (OneToOne->AIMessage), is_positive (BooleanField), feedback_text, created_at
- EXISTS IN DB but feedback in views is saved to ai_store.json, NOT to this model — DATA SPLIT

### Missing DB Models (Needed for Enterprise):
- AIPromptTemplate — currently in JSON only
- AIModelRegistry — currently in JSON only
- AIChatSession — currently in JSON only
- AIUsageLog — currently in JSON list only
- AIEmbedding — not exists (vector store)
- AIDocument — not exists (RAG documents)
- AIAgentConfig — not exists
- AIToolCall — not exists
- AIRateLimitQuota — not exists

---

## 5. Integration Audit

### 5.1 Student App (backend/apps/student)
- Files: models.py (32KB, 901 lines), services.py (14KB), views.py (16KB)
- What Exists: LearningHistory, bookmarks, notes, goals, streaks, achievements, calendar events, progress
- AI Integration Status: NONE
- No AI service calls. Student learning history data (rich behavioral signals) is completely unused by AI.
- Potential AI Hooks: LearningHistory -> personalized recommendations, streaks/goals -> AI-generated study plans, notes -> AI summarization

### 5.2 Teacher App (backend/apps/teacher)
- Files: models.py (20KB), integrations.py (13KB), services.py (16KB), views.py (34KB)
- What Exists: TeacherProfile (bio, qualifications, specialties, rating), TeacherAnalytics, TeachingSession
- AI Integration Status: NONE
- Potential AI Hooks: Curriculum generation, quiz generation, auto-grading, session summaries, student performance analysis

### 5.3 LMS App (backend/apps/lms)
- Files: models.py (27KB, 777 lines), views.py (144KB — very large)
- What Exists: CourseStructure (hierarchical adjacency list Program->Lesson), LearningProgress, StudentEnrollment
- AI Integration Status: NONE
- The LMS is the core content graph — entirely disconnected from the AI layer.
- Potential AI Hooks: Lesson content summarization, quiz generation from lesson content, prerequisite gap detection, auto-tagging

### 5.4 Search App (backend/apps/search)
- Files: models.py (11KB), services.py (28KB), tasks.py (19KB) — mature search layer
- What Exists: SearchIndex, SearchDocument, SearchTerm, SearchAnalytics, SearchHistory, SearchSuggestion, SearchRanking, SearchClick, SearchFacet, SearchSynonym, SearchCache; IndexService, SuggestionService
- AI Integration Status: PARTIAL — one-way bridge. ai_store.py dispatches index_ai_item_task for conversations + prompts. However, AI does NOT query the search index for grounding.
- Critical Gap: search_vector field is text-only. No pgvector, no embedding storage. Cannot power RAG/semantic search.

### 5.5 Analytics App (backend/apps/analytics)
- Files: models.py (15KB, 450 lines), services.py (9KB)
- What Exists: AnalyticsEvent (generic telemetry), UserSession, PageView
- AI Integration Status: NONE
- No AI-specific analytics events. AI usage data only logged to ai_store.json.

### 5.6 Notifications App (backend/apps/notifications)
- Files: models.py (4KB, 119 lines), services.py (8KB)
- What Exists: NotificationTemplate, NotificationPreference, NotificationRecord, NotificationDelivery, Announcement, NotificationAnalytics
- Redis pub/sub on NotificationRecord.save() -> publishes to notifications_pubsub
- AI Integration Status: NONE
- Notification system is mature and Redis-connected, but AI events do not trigger notifications.

### 5.7 CMS App (backend/apps/cms)
- Files: models.py (48KB, 1303 lines), services.py (52KB) — very large, rich CMS
- What Exists: Pages, Articles, Categories, Tags, Media, DAM, Revisions, Workflow, Reactions, Redirects, SEO
- AI Integration Status: NONE
- No AI content generation, no AI-assisted writing, no auto-tagging, no AI SEO optimization.

---

## 6. Frontend AI Audit

### 6.1 src/services/api.ts — AI Service Layer

Current AI endpoints (3 total):
```typescript
api.ai = {
  chat: (message: string) => POST /api/ai/chat,
  generateCurriculum: (title: string) => POST /api/ai/generate-curriculum,
  generateQuiz: (topic: string) => POST /api/ai/generate-quiz,
}
```

Status: EXTREMELY LIMITED. None of the 8 backend AI ViewSets are exposed here.

Missing Frontend API Endpoints:
- api.ai.conversations (CRUD)
- api.ai.messages (create, list, feedback)
- api.ai.prompts (library management)
- api.ai.models (model selection)
- api.ai.sessions (session management)
- api.ai.usage (usage dashboard)
- api.ai.stream (streaming chat)

### 6.2 src/pages/public/CoursesShell.tsx — AI Sidebar

What Exists:
- isAiOpen sidebar state with AI panel toggle
- aiLog array with initial Vidya AI greeting
- handleSendAiMessage() — uses a 1200ms setTimeout MOCK with hardcoded string. Does NOT call api.ai.chat.
- handleGenerateQuiz() — correctly calls api.ai.generateQuiz(activeLesson.title)

Status: PARTIAL — quiz generation connected to API, but chat is entirely mocked.

### 6.3 src/components/ — AI Components

No dedicated AI components exist. The entire AI UI lives inside CoursesShell.tsx. Missing:
- AIAssistant standalone component
- AIConversationPanel component
- AIPromptLibrary component
- AIModelSelector component
- AIUsageDashboard component
- TeacherAITools component
- StudentAIRecommendations component

### 6.4 Admin AI Pages

No admin AI management pages exist. Missing:
- AI Model Registry management UI
- AI Prompt Template library admin
- AI Usage Analytics dashboard
- AI Conversation audit viewer

---

## 7. Gateway AI Audit

### 7.1 server.ts — Gemini SDK

```typescript
import { GoogleGenAI } from '@google/genai';
let geminiClient: GoogleGenAI | null = null;
function getGemini(): GoogleGenAI | null {
  // Lazy-init using GEMINI_API_KEY env var
}
```

Status: SDK imported and lazy-initialized correctly. HOWEVER, getGemini() is NEVER CALLED anywhere in server.ts.

### 7.2 PATH_MAP — AI Route Registration (DONE)

All 8 Django AI ViewSet routes are registered in PATH_MAP and proxied correctly:
- /api/ai/conversations -> /api/v1/ai/conversations/
- /api/ai/messages -> /api/v1/ai/messages/
- /api/ai/feedback -> /api/v1/ai/feedback/
- /api/ai/prompts -> /api/v1/ai/prompts/
- /api/ai/models -> /api/v1/ai/models/
- /api/ai/sessions -> /api/v1/ai/sessions/
- /api/ai/usage -> /api/v1/ai/usage/
- /api/ai/analytics -> /api/v1/ai/analytics/

### 7.3 CRITICAL: Missing Gateway Handlers

The frontend calls these routes — NONE have any handler:
- /api/ai/chat — Not in PATH_MAP, no Express handler
- /api/ai/generate-curriculum — Not in PATH_MAP, no Express handler
- /api/ai/generate-quiz — Not in PATH_MAP, no Express handler
- /api/ai/stream — Not implemented anywhere

The Gemini SDK is imported but NEVER invoked. These requests fall into the Express mock DB fallback.

---

## 8. Infrastructure Audit

### 8.1 Redis
- Gateway: Redis client initialized (redis://127.0.0.1:6379). Used for distributed rate limiting.
- Notifications: NotificationRecord.save() publishes to notifications_pubsub.
- AI Usage: NOT used for AI features (no caching, no streaming pub/sub).
- Available for: AI response caching, AI quota enforcement, SSE pub/sub, conversation state caching.

### 8.2 Celery
- Search app has index_ai_item_task (dispatched from ai_store.py).
- apps/ai/ has NO tasks.py.
- Missing async AI tasks:
  - process_ai_response_task
  - summarize_conversation_task
  - generate_embeddings_task
  - ai_analytics_rollup_task
  - notify_ai_event_task

---

## 9. Gap Analysis Matrix

| Feature | Backend | Frontend | Gateway | Verdict |
|---|---|---|---|---|
| Conversation CRUD | DONE (PostgreSQL + Views) | MISSING in api.ts | DONE (Proxied) | Needs Frontend |
| Message Creation | DONE (mock response) | MISSING in api.ts | DONE (Proxied) | Needs real Gemini + Frontend |
| Real Gemini Chat | MISSING — mock only | MISSING — setTimeout | MISSING — no handler | CRITICAL |
| Streaming SSE | MISSING | MISSING | MISSING | CRITICAL |
| Curriculum Generation | MISSING endpoint | DONE in api.ts | MISSING — no handler | Build Gateway + Django view |
| Quiz Generation | MISSING endpoint | DONE in api.ts | MISSING — no handler | Build Gateway + Django view |
| Prompt Library | DONE (JSON-backed) | MISSING | DONE (Proxied) | Migrate to DB + Frontend |
| Model Registry | DONE (JSON-backed) | MISSING | DONE (Proxied) | Migrate to DB + Frontend |
| Session Tracking | DONE (JSON-backed) | MISSING | DONE (Proxied) | Migrate to DB + Frontend |
| Usage Analytics | DONE (JSON list) | MISSING | DONE (Proxied) | Migrate to DB + Frontend |
| AI Feedback (DB) | SPLIT (model exists, saves to JSON) | MISSING | DONE (Proxied) | Unify to DB |
| Vector Embeddings | MISSING | N/A | N/A | Build: pgvector |
| Semantic Search Grounding | MISSING | MISSING | MISSING | Build: RAG pipeline |
| Student AI Features | MISSING | MISSING | MISSING | Build entirely |
| Teacher AI Features | MISSING | MISSING | MISSING | Build entirely |
| Multimodal (PDF/Image) | MISSING | MISSING | MISSING | Build: Gemini Vision |
| AI Notifications | MISSING | MISSING | MISSING | Build: signals + service |
| AI Analytics Events | MISSING | MISSING | MISSING | Build: AnalyticsEvent integration |
| AI Admin Dashboard | MISSING | MISSING | MISSING | Build: Admin UI |
| Celery AI Tasks | MISSING (no tasks.py in ai app) | N/A | N/A | Build: async task layer |
| Redis AI Caching | MISSING | N/A | N/A | Build: response cache + quota |

---

## 10. Recommended Target Architecture

### 10.1 Architecture Overview

```
Frontend React (src/)
    |
    +-- api.ai.* (expanded API client)
    |   +-- /api/ai/conversations/*
    |   +-- /api/ai/stream           (SSE)
    |   +-- /api/ai/messages/*
    |   +-- /api/ai/prompts/*
    |   +-- /api/ai/models/*
    |   +-- /api/ai/sessions/*
    |   +-- /api/ai/usage/*
    |   +-- /api/ai/curriculum, quiz, summarize, embed
    |
Express Gateway (server.ts)
    |
    +-- PATH_MAP proxies -> Django for CRUD (existing)
    +-- /api/ai/stream -> SSE handler -> Gemini API (NEW)
    +-- /api/ai/chat   -> Express handler -> Gemini API (NEW)
    +-- /api/ai/curriculum -> Express -> Gemini (NEW)
    +-- /api/ai/generate-quiz -> Express -> Gemini (NEW)
    |
Redis
    +-- Rate limiting (existing)
    +-- AI response cache (NEW)
    +-- AI SSE pub/sub (NEW)
    +-- AI quota counters per user (NEW)
    |
Celery Workers (new tasks in apps/ai/tasks.py)
    +-- process_ai_response_task
    +-- summarize_conversation_task
    +-- generate_embeddings_task
    +-- ai_analytics_rollup_task
    +-- notify_ai_event_task
    |
Django Backend (backend/)
    |
    +-- apps/ai/
    |   +-- models.py (NEW — migrate prompts/models/sessions/usage to PostgreSQL)
    |   |   +-- AIPromptTemplate
    |   |   +-- AIModelRegistry
    |   |   +-- AIChatSession
    |   |   +-- AIUsageLog
    |   |   +-- AIEmbedding (pgvector, 1536-dim)
    |   |   +-- AIDocument
    |   |   +-- AIAgentConfig
    |   |   +-- AIRateLimitQuota
    |   +-- services.py (NEW — real Gemini service layer)
    |   |   +-- GeminiService (generate, stream, function_call)
    |   |   +-- RAGService (retrieve + ground)
    |   |   +-- EmbeddingService (generate + store)
    |   |   +-- ContextWindowService (manage token budget)
    |   +-- tasks.py (NEW — async Celery tasks)
    |   +-- signals.py (NEW — post_save signals)
    |   +-- views.py (EXTEND — add real generation endpoints)
    |
    +-- apps/student/ (EXTEND — AI recommendation integration)
    +-- apps/teacher/ (EXTEND — AI curriculum + quiz + analytics integration)
    +-- apps/lms/ (EXTEND — Lesson content -> AI context injection)
    +-- apps/search/ (EXTEND — Add vector search + semantic ranking)
    +-- apps/analytics/ (EXTEND — AI-specific analytics events)
    +-- apps/notifications/ (EXTEND — AI event notification triggers)
```

### 10.2 Data Layer Changes

#### New Django Models Required in apps/ai/models.py

| Model | Purpose |
|---|---|
| AIPromptTemplate | Migrate from JSON store to PostgreSQL |
| AIModelRegistry | Migrate from JSON store to PostgreSQL |
| AIChatSession | Migrate from JSON store to PostgreSQL |
| AIUsageLog | Migrate from JSON list to PostgreSQL |
| AIEmbedding | pgvector column for semantic search (1536-dim) |
| AIDocument | Source documents for RAG (course content, lesson text) |
| AIAgentConfig | Per-tenant/user agent personality and system prompt configs |
| AIRateLimitQuota | Per-user token quota and daily usage limits |

#### Existing Models to Enhance

| Model | Enhancement |
|---|---|
| AIConversation | Add: model_id, system_prompt, summary, language, context_window, is_archived |
| AIMessage | Add: token_count (populate), references (JSONField), citations (JSONField), latency_ms |
| AIFeedback | Extend: add category, rating (1-5), response_quality, correctness fields |

### 10.3 Service Layer

New apps/ai/services.py:

```python
class GeminiService:
    """Real Gemini API integration."""
    def generate(prompt, model_id, system_instruction, history, temperature) -> dict
    def stream(prompt, model_id, system_instruction, history) -> Iterator
    def function_call(prompt, tools) -> dict
    def count_tokens(content) -> int
    def embed(text, model="text-embedding-004") -> List[float]

class RAGService:
    """Retrieval-Augmented Generation."""
    def retrieve(query, top_k=5, filters=None) -> List[AIDocument]
    def ground_prompt(base_prompt, retrieved_docs) -> str
    def index_document(source_type, source_id, content) -> AIEmbedding

class ContextWindowService:
    """Manages conversation context within token budget."""
    def build_context(conversation_id, new_message, max_tokens=120000) -> List[dict]
    def should_summarize(conversation_id) -> bool
    def summarize(conversation_id) -> str
```

### 10.4 Gateway Handlers (New in server.ts)

Three routes must be implemented directly in Express for performance:

```typescript
// 1. Real AI Chat (non-streaming)
app.post('/api/ai/chat', async (req, res) => {
  const client = getGemini();
  if (!client) return res.json({ text: mockFallback(req.body.message) });
  const result = await client.models.generateContent({...});
  res.json({ text: result.text });
});

// 2. Streaming Chat (SSE)
app.post('/api/ai/stream', async (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  const stream = await client.models.generateContentStream({...});
  for await (const chunk of stream) {
    res.write(`data: ${JSON.stringify({chunk: chunk.text})}\n\n`);
  }
  res.end();
});

// 3. Curriculum Generation
app.post('/api/ai/generate-curriculum', async (req, res) => {
  const result = await client.models.generateContent({...});
  res.json({ success: true, data: parsedCurriculum });
});

// 4. Quiz Generation
app.post('/api/ai/generate-quiz', async (req, res) => {
  const result = await client.models.generateContent({...});
  res.json({ success: true, data: parsedQuiz });
});
```

---

## 11. Implementation Priority Roadmap

### Phase 1 — Foundation (Sprint 24, Phase 1)
Goal: Real Gemini integration end-to-end

1. Add GEMINI_API_KEY to .env
2. Implement /api/ai/chat Express handler with real Gemini API
3. Implement /api/ai/generate-curriculum with structured Gemini output
4. Implement /api/ai/generate-quiz with structured Gemini output
5. Wire CoursesShell.tsx chat to real API (remove setTimeout mock)
6. Implement SSE streaming endpoint /api/ai/stream

### Phase 2 — Database Migration (Sprint 24, Phase 2)
Goal: Move all AI persistence from JSON to PostgreSQL

1. Create apps/ai/models.py with all missing models
2. Create migrations
3. Migrate JSON store data to PostgreSQL
4. Update ViewSets to use Django ORM instead of ai_store.py
5. Unify AIFeedback (DB model and views must use same table)
6. Create apps/ai/tasks.py with Celery async tasks

### Phase 3 — Student + Teacher AI Integration (Sprint 24, Phase 3)
Goal: Deep LMS context injection and personalization

1. Student AI recommendations from LearningHistory
2. AI-powered study plans from goals/streaks
3. Teacher curriculum AI generation from CourseStructure
4. Teacher quiz AI from lesson content
5. Teacher student analytics AI summaries

### Phase 4 — Vector Search + RAG (Sprint 24, Phase 4)
Goal: Grounded, accurate AI responses

1. Add pgvector extension to PostgreSQL
2. Create AIEmbedding model with vector column
3. Implement EmbeddingService using text-embedding-004
4. Index LMS lesson content
5. Implement RAG pipeline in GeminiService
6. Extend search to support vector similarity queries

### Phase 5 — Frontend + Admin UI (Sprint 24, Phase 5)
Goal: Full enterprise AI frontend

1. Expand api.ts with full AI SDK
2. Create standalone AIAssistant component
3. Create AIPromptLibrary component
4. Create AI admin dashboard pages
5. AI usage analytics dashboard

### Phase 6 — Analytics + Notifications Integration (Sprint 24, Phase 6)
Goal: AI events in platform ecosystem

1. Fire AnalyticsEvent for AI interactions
2. AI quota warnings via NotificationRecord
3. AI model change announcements
4. AI usage reports

---

## 12. Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| GEMINI_API_KEY not configured | HIGH | CRITICAL | Add key check + graceful mock fallback |
| JSON -> DB migration data loss | MEDIUM | HIGH | Export ai_store.json before migration; one-time import script |
| pgvector not installed on PostgreSQL | MEDIUM | HIGH | Document installation; fallback to text search |
| Token budget overflow (long conversations) | MEDIUM | MEDIUM | Implement ContextWindowService with summarization |
| Gemini API rate limits hit in production | MEDIUM | MEDIUM | Per-user quota + Redis throttling |
| Streaming SSE connection drops | LOW | MEDIUM | Client-side reconnect + partial response cache in Redis |
| ai_store.json race conditions under load | HIGH | MEDIUM | Migrate to DB immediately; threading lock is not production-safe |
| Views.py split persistence (DB vs JSON) | HIGH | HIGH | Identified — resolve in Phase 2 database migration |

---

## Appendix A — File Inventory

| File | Size | Status | Priority |
|---|---|---|---|
| backend/apps/ai/views.py | 38.9KB (944L) | EXTEND — add real Gemini calls | HIGH |
| backend/apps/ai/ai_store.py | 11.4KB (360L) | DEPRECATE — migrate to ORM | HIGH |
| backend/apps/ai/ai_store.json | 39.7KB | EXPORT + DEPRECATE | HIGH |
| backend/apps/ai/serializers.py | 7.9KB (169L) | KEEP — extend with new fields | MEDIUM |
| backend/apps/ai/utils.py | 6.4KB (179L) | EXTEND — add real token counting | MEDIUM |
| backend/apps/ai/urls.py | 1.2KB (29L) | EXTEND — add stream, curriculum, quiz | MEDIUM |
| backend/apps/control_center/models.py | 12KB (322L) | EXTEND — enhance AI models | HIGH |
| backend/apps/ai/models.py | MISSING | CREATE | CRITICAL |
| backend/apps/ai/services.py | MISSING | CREATE | CRITICAL |
| backend/apps/ai/tasks.py | MISSING | CREATE | HIGH |
| backend/apps/ai/signals.py | MISSING | CREATE | MEDIUM |
| src/services/api.ts | 17KB (482L) | EXTEND — add AI SDK | HIGH |
| src/pages/public/CoursesShell.tsx | 23.8KB (486L) | FIX — remove mock timeout | HIGH |
| src/components/ | N/A | CREATE AI components | MEDIUM |
| server.ts | 74KB (2075L) | EXTEND — add AI route handlers | CRITICAL |

---

*Report generated: Sprint 24 — Phase 0 Audit*
*Classification: Internal — Architecture Review*
*Next Step: Sprint 24 Phase 1 — Foundation Implementation*
