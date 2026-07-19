# Sprint 24 — Phase 1: Enterprise AI Learning Platform Architecture
## BrahmaVidya Galaxy — Complete Design Specification

**Sprint:** 24 — Phase 1  
**Date:** 2026-07-19  
**Type:** DESIGN ONLY — No implementation  
**Depends on:** `ai_platform_analysis.md` (Phase 0)  
**Author:** Antigravity Architecture Agent

---

## Table of Contents

1. [Platform Vision & Design Principles](#1-platform-vision--design-principles)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [AI Feature Designs](#3-ai-feature-designs)
   - 3.1 AI Tutor
   - 3.2 AI Lesson Explainer
   - 3.3 AI Quiz Generator
   - 3.4 AI Assignment Generator
   - 3.5 AI Code Assistant
   - 3.6 AI Roadmap Generator
   - 3.7 AI Notes Generator
   - 3.8 AI Flashcards
   - 3.9 AI Doubt Solver
   - 3.10 AI Study Planner
   - 3.11 AI Resume Assistant
   - 3.12 AI Interview Assistant
   - 3.13 AI Teacher Assistant
   - 3.14 AI Analytics
   - 3.15 AI Prompt Engine
4. [Conversation Memory Architecture](#4-conversation-memory-architecture)
5. [Semantic Search Architecture](#5-semantic-search-architecture)
6. [Vector Search Architecture](#6-vector-search-architecture)
7. [Redis Cache Architecture](#7-redis-cache-architecture)
8. [Celery Task Architecture](#8-celery-task-architecture)
9. [API Design — 36 Endpoints](#9-api-design)
10. [Frontend Architecture](#10-frontend-architecture)
11. [Gateway Architecture](#11-gateway-architecture)
12. [Data Model Specifications](#12-data-model-specifications)
13. [Integration Map](#13-integration-map)
14. [Implementation Constraints](#14-implementation-constraints)

---

## 1. Platform Vision & Design Principles

### 1.1 Vision Statement

The BrahmaVidya Galaxy Enterprise AI Learning Platform transforms a traditional LMS into an **adaptive, AI-augmented academic ecosystem** where every student receives a personalized Socratic tutor, every teacher has an AI teaching assistant, and every learning interaction is enriched by real-time Gemini intelligence — grounded in the platform's own course content and learning data.

### 1.2 Design Principles

| Principle | Description |
|---|---|
| **Gemini-Native** | All AI generation uses Google Gemini (Pro/Flash) as the primary model. No mocks in production. |
| **Context-Grounded** | AI responses are grounded in the platform's own LMS content via RAG. Generic hallucinations are suppressed. |
| **Token-Budget-Aware** | Every AI feature manages its own token window. Long contexts are auto-summarized via Celery. |
| **Streaming-First** | All conversational AI endpoints stream via Server-Sent Events (SSE). Non-streaming is the fallback only. |
| **Async-by-Default** | Heavy generation tasks (embeddings, batch analysis, report generation) run via Celery, not request-response. |
| **Redis-Accelerated** | Frequently requested AI outputs (quiz questions, roadmaps, flashcards) are cached in Redis with TTL. |
| **Role-Aware** | AI behavior adapts based on RBAC role: Student, Teacher, Admin see different AI features and data. |
| **Preserve Architecture** | All new AI features extend existing apps (student, teacher, lms, search, analytics, notifications). Zero replacements. |
| **Idempotent Caching** | Same prompt + same context → same Redis cache hit. Prevents duplicate Gemini API calls. |
| **Audit-Logged** | Every AI interaction (model used, tokens consumed, latency, cost) is persisted in `AIUsageLog` (PostgreSQL). |

### 1.3 Technology Stack

| Layer | Technology |
|---|---|
| AI Model (Primary) | Google Gemini 1.5 Pro (`gemini-1.5-pro`) |
| AI Model (Fast) | Google Gemini 1.5 Flash (`gemini-1.5-flash`) |
| AI SDK (Gateway) | `@google/genai` (Node.js) |
| AI SDK (Backend) | `google-genai` (Python) |
| Embedding Model | `text-embedding-004` (1536 dimensions) |
| Vector Storage | PostgreSQL + `pgvector` extension |
| Cache | Redis 7+ (existing infrastructure) |
| Task Queue | Celery + Redis broker (existing infrastructure) |
| Streaming | Server-Sent Events (SSE) via Express gateway |
| Persistence | PostgreSQL (all new AI models migrate from JSON) |
| Backend Framework | Django REST Framework (existing) |
| Frontend Framework | React + TypeScript (existing) |
| API Gateway | Express + TypeScript (existing `server.ts`) |

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     BROWSER (React + TypeScript)                │
│                                                                 │
│  AIAssistantPanel  AIPromptLibrary  AIUsageDashboard           │
│  TeacherAITools    StudentAIHub     AdminAIControl              │
│  AICodeEditor      AIFlashcards     AIRoadmapViewer             │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / SSE
┌────────────────────────────▼────────────────────────────────────┐
│              EXPRESS GATEWAY (server.ts)                        │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  JWT Auth        │  │ RBAC Guard   │  │  Rate Limiter     │  │
│  │  Middleware      │  │ Middleware   │  │  (Redis-backed)   │  │
│  └─────────────────┘  └──────────────┘  └───────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          AI GATEWAY HANDLERS (Express)                    │  │
│  │                                                           │  │
│  │  /api/ai/stream         → Gemini SSE streaming            │  │
│  │  /api/ai/chat           → Gemini chat (non-stream)        │  │
│  │  /api/ai/generate-quiz  → Structured quiz output          │  │
│  │  /api/ai/generate-curriculum → Structured curriculum      │  │
│  │  /api/ai/explain        → Lesson explanation              │  │
│  │  /api/ai/code-assist    → Code completion/review          │  │
│  │  /api/ai/roadmap        → Learning roadmap                │  │
│  │  /api/ai/interview      → Interview simulation            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          DJANGO PROXY ROUTES (PATH_MAP)                   │  │
│  │  /api/ai/* → /api/v1/ai/* (conversations, prompts, etc.)  │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────┬───────────────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────┐    ┌─────────────────────────────────────┐
│   GOOGLE GEMINI API  │    │       DJANGO REST FRAMEWORK         │
│                      │    │                                     │
│  gemini-1.5-pro      │    │  apps/ai/         (AI Core)         │
│  gemini-1.5-flash    │    │  apps/student/    (Student AI)      │
│  text-embedding-004  │    │  apps/teacher/    (Teacher AI)      │
│                      │    │  apps/lms/        (Content Graph)   │
│  generateContent()   │    │  apps/search/     (Search + RAG)    │
│  generateContentStream│   │  apps/analytics/  (AI Events)       │
│  embedContent()      │    │  apps/notifications/ (AI Alerts)    │
└──────────────────────┘    └─────────────┬───────────────────────┘
                                          │
              ┌───────────────────────────┼──────────────────────┐
              ▼                           ▼                      ▼
┌─────────────────────┐   ┌─────────────────────┐  ┌────────────────────┐
│      POSTGRESQL     │   │       REDIS 7        │  │   CELERY WORKERS   │
│                     │   │                      │  │                    │
│  ai_conversations   │   │  ai:cache:quiz:{h}   │  │  embed_content     │
│  ai_messages        │   │  ai:cache:roadmap:{h}│  │  summarize_convo   │
│  ai_usage_logs      │   │  ai:cache:explain:{h}│  │  generate_report   │
│  ai_embeddings      │   │  ai:quota:user:{id}  │  │  batch_embed       │
│  ai_documents       │   │  ai:session:{id}     │  │  ai_analytics      │
│  ai_prompt_templates│   │  ai:stream:pub/{id}  │  │  notify_ai_event   │
│  ai_model_registry  │   │  rate:limit:{token}  │  │  index_embeddings  │
│  ai_agent_configs   │   │  notifications_pubsub│  │                    │
│  vector column      │   │  (existing)          │  │                    │
│  (pgvector 1536-dim)│   └─────────────────────┘  └────────────────────┘
└─────────────────────┘
```

---

## 3. AI Feature Designs

### 3.1 AI Tutor

**Purpose:** Primary conversational academic tutor. Socratic dialogue, step-by-step teaching, concept reinforcement.

**Model:** `gemini-1.5-pro` (deep reasoning) with streaming

**Context Sources:**
- Active enrolled course (`CourseStructure` node tree via LMS)
- Current lesson content (lesson metadata + `body` text from `SearchDocument`)
- Student learning history (last 10 accessed lessons from `LearningHistory`)
- Student weaknesses (quiz failure patterns from `QuizAttempt`)
- Conversation history (last N messages within token budget)

**System Prompt Template:**
```
You are Vidya, the academic tutor for BrahmaVidya Galaxy — India's premier 
AI-powered learning platform. You are teaching {student_name} who is currently 
studying [{course_title}] at the [{lesson_title}] level.

STUDENT CONTEXT:
- Learning history: {recent_lessons}
- Current progress: {progress_percentage}%
- Known weak areas: {weak_topics}

LESSON CONTENT (use this as your primary knowledge source):
{lesson_grounding_context}

RULES:
1. Teach in a Socratic style — ask guiding questions, don't just give answers.
2. Use examples relevant to the Indian academic context where applicable.
3. Reference specific parts of the lesson content above.
4. If asked something outside the lesson scope, acknowledge it and redirect.
5. Keep explanations under 300 words unless the student asks for more detail.
6. Always end with a follow-up question to check understanding.
```

**API Endpoint:** `POST /api/ai/stream` (SSE) + `POST /api/ai/chat`

**Frontend Component:** `<AITutorPanel />` — persistent right sidebar in `CoursesShell`

**Redis Cache:** None (conversational — every session is unique)

**Celery Tasks:**
- `summarize_conversation_task` — triggered when token count > 80,000
- `log_ai_usage_task` — async usage logging after each response

**Token Budget:** 120,000 tokens (context) + 4,096 (output max)

---

### 3.2 AI Lesson Explainer

**Purpose:** On-demand deep explanation of any lesson concept. Not conversational — single-shot structured output.

**Model:** `gemini-1.5-flash` (speed) with streaming

**Input:** `lesson_id` (UUID) + `concept` (string) + `explanation_level` (beginner/intermediate/advanced)

**Context Sources:**
- Lesson full text body (`SearchDocument.body` where `entity_type='lesson'`)
- Parent course description (`CourseStructure.description`)
- RAG retrieval: top-3 related documents by vector similarity to the concept

**Output Schema (Structured JSON):**
```json
{
  "concept": "string",
  "eli5": "string",           // Explain Like I'm 5
  "standard": "string",       // Main explanation
  "advanced": "string",       // For depth seekers
  "analogy": "string",        // Real-world analogy
  "formula_or_steps": ["string"],
  "common_mistakes": ["string"],
  "related_concepts": ["string"],
  "practice_question": "string"
}
```

**API Endpoint:** `POST /api/ai/explain`

**Frontend Component:** `<AIExplainerModal />` — triggered via "Explain This" button on any lesson

**Redis Cache:** `ai:explain:{sha256(lesson_id + concept + level)}` → TTL 24h

**Celery Tasks:** `embed_lesson_task` — ensures lesson has vector embedding for RAG retrieval

---

### 3.3 AI Quiz Generator

**Purpose:** Generate contextually grounded quiz questions from any lesson or topic.

**Model:** `gemini-1.5-flash` (structured output mode)

**Input:** `lesson_id` OR `topic` (string) + `difficulty` (easy/medium/hard) + `count` (5–20) + `question_type` (MCQ/TRUE_FALSE/SHORT_ANSWER/FILL_BLANK)

**Context Sources:**
- Lesson body text from `SearchDocument`
- Existing quiz questions for the lesson (de-duplication)
- Lesson learning objectives (from `CourseStructure.metadata`)

**Output Schema (Structured JSON):**
```json
{
  "quiz_title": "string",
  "lesson_id": "uuid",
  "difficulty": "medium",
  "questions": [
    {
      "id": "uuid",
      "question": "string",
      "type": "MCQ",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "explanation": "string",
      "concept_tag": "string",
      "bloom_level": "remember|understand|apply|analyze|evaluate|create"
    }
  ]
}
```

**Gemini System Prompt Design:**
- Use `response_mime_type: "application/json"` for structured output
- Include `response_schema` matching the JSON schema above
- Inject lesson content as grounding
- Explicitly instruct: "Never repeat existing questions: {existing_questions}"

**API Endpoint:** `POST /api/ai/generate-quiz`

**Frontend Component:** `<AIQuizGenerator />` in Teacher Portal + `<AdaptiveQuizPanel />` in Student Portal

**Redis Cache:** `ai:quiz:{sha256(lesson_id + difficulty + count + type)}` → TTL 6h

**Celery Tasks:** `batch_quiz_generation_task` — pre-generate quizzes for top-enrolled lessons nightly

---

### 3.4 AI Assignment Generator

**Purpose:** Generate structured assignments, problem sets, and project briefs for teachers.

**Model:** `gemini-1.5-pro` (complex reasoning required)

**Input:** `course_id`, `topic`, `assignment_type` (PROBLEM_SET/PROJECT/ESSAY/LAB_REPORT), `difficulty`, `due_days` (int), `learning_objectives` (array)

**Context Sources:**
- Full course structure (parent course and all child lesson titles)
- Teacher profile specialties (`TeacherProfile.specialties`)
- Previous assignments for this course (to avoid repetition)

**Output Schema:**
```json
{
  "title": "string",
  "assignment_type": "PROBLEM_SET",
  "course_id": "uuid",
  "estimated_hours": 3,
  "learning_objectives": ["string"],
  "instructions": "string",          // Markdown formatted
  "problems": [
    {
      "number": 1,
      "problem_statement": "string",
      "hints": ["string"],
      "marks": 10,
      "solution_approach": "string"  // Teacher-only field
    }
  ],
  "rubric": [
    { "criterion": "string", "max_marks": 10, "description": "string" }
  ],
  "resources": ["string"]
}
```

**API Endpoint:** `POST /api/ai/generate-assignment`

**Frontend Component:** `<AIAssignmentBuilder />` in Teacher Portal

**Redis Cache:** `ai:assignment:{sha256(course_id + topic + type)}` → TTL 12h

**Permission:** Teacher role only (`RBAC: teacher_ai:assignment:create`)

---

### 3.5 AI Code Assistant

**Purpose:** Context-aware code completion, debugging, review, and explanation inside the platform's coding exercises.

**Model:** `gemini-1.5-pro` (code-specialized prompting)

**Modes:**
| Mode | Description | Trigger |
|---|---|---|
| `COMPLETE` | Auto-complete partial code | User pauses typing |
| `EXPLAIN` | Explain selected code block | User highlights + clicks |
| `DEBUG` | Find and explain bugs | User submits with errors |
| `REVIEW` | Code quality review | User requests review |
| `REFACTOR` | Suggest refactoring | User requests |
| `TEST` | Generate unit tests | User requests |

**Input:** `code` (string), `language` (python/js/java/c++), `mode` (above), `context` (assignment description or lesson topic), `error_message` (optional)

**Output (COMPLETE/REFACTOR):** Streaming code diff
**Output (EXPLAIN/DEBUG/REVIEW):** Streaming markdown

**System Prompt Design:**
```
You are an expert {language} programming assistant integrated into 
BrahmaVidya Galaxy. The student is working on: {assignment_context}

MODE: {mode}
LANGUAGE: {language}
ERROR (if any): {error_message}

CODE:
{code}

For COMPLETE: provide only the completion, starting exactly where the code ends.
For DEBUG: identify the bug, explain it clearly, provide the corrected code.
For EXPLAIN: explain line-by-line in simple language suitable for a {difficulty} level student.
For REVIEW: provide structured feedback (correctness, efficiency, style, best practices).
```

**API Endpoint:** `POST /api/ai/code-assist`

**Frontend Component:** `<AICodeEditor />` — Monaco Editor integration with AI sidebar

**Redis Cache:** `ai:code:debug:{sha256(code + error)}` → TTL 30min (debugging answers are ephemeral)

**Supported Languages:** Python, JavaScript, TypeScript, Java, C++, SQL, HTML/CSS

---

### 3.6 AI Roadmap Generator

**Purpose:** Generate personalized learning roadmaps for any career goal or skill target.

**Model:** `gemini-1.5-pro` with structured JSON output

**Input:** `goal` (string — e.g., "Become a Full Stack Developer"), `current_skills` (array), `timeline_weeks` (int), `learning_style` (VISUAL/READING/PRACTICE), `available_hours_per_week` (int)

**Context Sources:**
- Platform's course catalog (`CourseStructure` tree)
- Student's completed courses from `LearningHistory`
- Student's enrolled courses from `StudentEnrollment`

**Output Schema:**
```json
{
  "goal": "string",
  "total_weeks": 24,
  "phases": [
    {
      "phase_number": 1,
      "phase_title": "string",
      "duration_weeks": 4,
      "focus": "string",
      "milestones": ["string"],
      "courses": [
        {
          "title": "string",
          "platform_course_id": "uuid|null",
          "is_on_platform": true,
          "estimated_hours": 20,
          "priority": "MUST|SHOULD|COULD"
        }
      ],
      "skills_gained": ["string"],
      "weekly_plan": {
        "monday": "string",
        "tuesday": "string",
        "wednesday": "string",
        "thursday": "string",
        "friday": "string",
        "weekend": "string"
      }
    }
  ],
  "final_project": "string",
  "career_readiness_indicators": ["string"]
}
```

**API Endpoint:** `POST /api/ai/roadmap`

**Frontend Component:** `<AIRoadmapViewer />` — visual timeline with Gantt-style progress tracking

**Redis Cache:** `ai:roadmap:{sha256(goal + current_skills + timeline + hours)}` → TTL 48h

**Celery Tasks:** `refresh_roadmap_task` — weekly refresh as student completes courses

---

### 3.7 AI Notes Generator

**Purpose:** Auto-generate structured study notes from lesson content.

**Model:** `gemini-1.5-flash` (speed for batch generation)

**Input:** `lesson_id` (UUID) + `format` (CORNELL/OUTLINE/MINDMAP_TEXT/SUMMARY/BULLET_POINTS)

**Context Sources:**
- Lesson full body text from `SearchDocument`
- Student's existing manual notes (from `StudentNote` model) — for merging

**Output per Format:**

**CORNELL format:**
```json
{
  "cue_column": ["Key question or term"],
  "notes_column": "Main notes text",
  "summary": "2-3 sentence summary at bottom"
}
```

**OUTLINE format:**
```json
{
  "title": "string",
  "sections": [
    { "heading": "I. Main Topic", "points": ["A. Detail", "1. Sub-detail"] }
  ]
}
```

**MINDMAP_TEXT format:**
```json
{
  "central_topic": "string",
  "branches": [
    { "branch": "string", "sub_branches": ["string"] }
  ]
}
```

**API Endpoint:** `POST /api/ai/generate-notes`

**Frontend Component:** `<AINotesPanel />` in Student Portal — displays alongside lesson

**Redis Cache:** `ai:notes:{sha256(lesson_id + format)}` → TTL 24h

**Integration:** Auto-merge with `StudentNote` model — AI notes saved as a special `source=AI` note type

---

### 3.8 AI Flashcards

**Purpose:** Generate spaced-repetition flashcard decks from lesson content.

**Model:** `gemini-1.5-flash` (structured output)

**Input:** `lesson_id` OR `topic` + `count` (10–50) + `card_type` (TERM_DEFINITION/Q_A/CLOZE/CONCEPT_MAP)

**Context Sources:**
- Lesson body text and key terms from `SearchDocument`
- Lesson metadata (tags, categories) from `SearchDocument`

**Output Schema:**
```json
{
  "deck_title": "string",
  "lesson_id": "uuid",
  "card_count": 20,
  "cards": [
    {
      "id": "uuid",
      "type": "TERM_DEFINITION",
      "front": "string",
      "back": "string",
      "hint": "string",
      "difficulty": 1-5,
      "tags": ["string"],
      "next_review_in_days": 1
    }
  ],
  "spaced_repetition_schedule": {
    "day_1": [0, 1, 2],
    "day_3": [3, 4, 5],
    "day_7": [6, 7, 8]
  }
}
```

**API Endpoint:** `POST /api/ai/flashcards`

**Frontend Component:** `<AIFlashcardDeck />` — swipeable card UI with Leitner box tracking

**Redis Cache:** `ai:flashcards:{sha256(lesson_id + count + type)}` → TTL 12h

**Celery Tasks:** `schedule_flashcard_review_task` — daily review reminder dispatch via `NotificationRecord`

---

### 3.9 AI Doubt Solver

**Purpose:** Instant resolution of specific doubts. Not a full tutor session — targeted single-question answering with source citations.

**Model:** `gemini-1.5-pro` with Google Search grounding (if enabled) + RAG from platform content

**Input:** `doubt` (string) + `context_type` (LESSON/ASSIGNMENT/QUIZ/GENERAL) + `context_id` (optional UUID) + `subject` (string)

**Context Sources (priority order):**
1. Related platform content via vector search (top-5 chunks)
2. Lesson content if `context_id` is a lesson
3. Assignment description if `context_type` is ASSIGNMENT

**Output Schema:**
```json
{
  "doubt": "string",
  "answer": "string",            // Markdown, streaming
  "confidence": "HIGH|MEDIUM|LOW",
  "source_references": [
    {
      "title": "string",
      "url_path": "string",      // Deep link to platform content
      "relevance": "HIGH|MEDIUM"
    }
  ],
  "related_concepts": ["string"],
  "follow_up_suggestions": ["string"],
  "escalate_to_teacher": false   // true if confidence=LOW
}
```

**API Endpoint:** `POST /api/ai/solve-doubt` (SSE streaming)

**Frontend Component:** `<AIDoubtSolver />` — floating action button on any lesson/quiz page

**Redis Cache:** `ai:doubt:{sha256(doubt + subject)}` → TTL 2h (doubts are contextual, short TTL)

**Special Logic:** If `confidence=LOW`, automatically dispatch a `NotificationRecord` to the student's enrolled teacher: "Student [name] has an unresolved doubt on [topic]."

---

### 3.10 AI Study Planner

**Purpose:** Generate and maintain a personalized weekly/monthly study schedule.

**Model:** `gemini-1.5-pro`

**Input:** `student_id`, `enrolled_courses` (array of UUIDs), `exam_dates` (array), `available_hours` (per day), `preferred_study_times` (morning/evening/night), `learning_pace` (slow/moderate/fast)

**Context Sources:**
- Student's enrolled courses and completion status (`LearningProgress`)
- Student's streaks and calendar events (`StudentStreak`, `CalendarEvent`)
- Student's learning history duration data (`LearningHistory.duration_seconds`)
- Upcoming exam dates

**Output Schema:**
```json
{
  "plan_title": "string",
  "week_start": "2026-07-21",
  "total_study_hours": 14,
  "daily_plans": [
    {
      "date": "2026-07-21",
      "day": "Monday",
      "sessions": [
        {
          "time_slot": "18:00-19:30",
          "course_title": "string",
          "course_id": "uuid",
          "lesson_to_cover": "string",
          "lesson_id": "uuid",
          "goal": "string",
          "duration_minutes": 90,
          "session_type": "STUDY|REVISION|PRACTICE|QUIZ"
        }
      ],
      "daily_goal": "string",
      "motivational_message": "string"
    }
  ],
  "weekly_goals": ["string"],
  "risk_alerts": [
    { "course": "string", "risk": "FALLING_BEHIND", "action": "string" }
  ]
}
```

**API Endpoint:** `POST /api/ai/study-plan`

**Frontend Component:** `<AIStudyPlanner />` — calendar view with drag-and-drop adjustment

**Redis Cache:** `ai:studyplan:{student_id}:{week_start}` → TTL 7 days (refreshed on completion events)

**Celery Tasks:**
- `weekly_study_plan_refresh_task` — Monday morning 6 AM IST via cron
- `notify_study_reminder_task` — 15 minutes before each scheduled session

---

### 3.11 AI Resume Assistant

**Purpose:** AI-powered resume builder and optimizer tailored to the student's learning profile.

**Model:** `gemini-1.5-pro`

**Modes:**
| Mode | Input | Output |
|---|---|---|
| `GENERATE` | Student profile + completed courses + skills | Full resume in JSON |
| `OPTIMIZE` | Existing resume text + job description | Improved resume + gap analysis |
| `BULLET_POINTS` | Achievement description (raw) | Professional bullet points |
| `COVER_LETTER` | Job description + resume | Tailored cover letter |
| `ATS_SCORE` | Resume text + job description | ATS compatibility score + fixes |

**Context Sources:**
- Student's completed courses (via `LearningHistory`)
- Student's earned certificates (via `Certificate`)
- Student's portfolio (via Portfolio app)
- Teacher-assessed grades and performance

**Output Schema (GENERATE mode):**
```json
{
  "name": "string",
  "contact": { "email": "string", "linkedin": "string", "github": "string" },
  "summary": "string",
  "skills": { "technical": [], "soft": [] },
  "education": [{ "degree": "string", "institution": "string", "year": "string" }],
  "courses_and_certifications": [
    { "title": "string", "platform": "BrahmaVidya Galaxy", "year": "string", "credential_id": "string" }
  ],
  "projects": [{ "name": "string", "description": "string", "tech_stack": [], "url": "string" }],
  "experience": [],
  "ats_keywords": ["string"],
  "ats_score_estimate": 85
}
```

**API Endpoint:** `POST /api/ai/resume`

**Frontend Component:** `<AIResumeBuilder />` in Student Portal → Portfolio section

**Redis Cache:** `ai:resume:{sha256(student_id + mode + jd_hash)}` → TTL 24h

**Permission:** Student role only

---

### 3.12 AI Interview Assistant

**Purpose:** AI-powered mock interview simulator for technical and behavioral interviews.

**Model:** `gemini-1.5-pro` (conversational + evaluation)

**Interview Types:**
| Type | Description |
|---|---|
| `TECHNICAL` | Coding problems, DSA, system design |
| `BEHAVIORAL` | STAR method questions |
| `DOMAIN` | Subject-specific (Math, Science, Commerce) |
| `HR` | Common HR screening questions |
| `APTITUDE` | Quantitative, logical reasoning |

**Session Flow:**
```
1. Setup Phase (student selects: type, difficulty, topic, duration)
2. Interview Phase (streaming conversational turns)
   - AI asks question
   - Student responds (text or code)
   - AI acknowledges + follow-up question OR next question
3. Evaluation Phase (post-session report)
   - Score per competency (0-100)
   - Detailed feedback per answer
   - Sample ideal answers
   - Areas for improvement
   - Next practice recommendations
```

**System Prompt (Interview Phase):**
```
You are a professional interviewer at a top-tier company conducting a 
{interview_type} interview for the role of {target_role}.

RULES:
1. Ask one question at a time. Do not reveal the answer.
2. If the answer is incomplete, probe with "Can you elaborate on..."
3. Maintain professional but encouraging tone.
4. After each answer, respond with: "Thank you. My next question is..."
5. Do NOT evaluate during the interview. Evaluation happens after.
6. Track all answers internally for the final report.

TOPIC FOCUS: {topic}
DIFFICULTY: {difficulty}
TIME REMAINING: {time_remaining} minutes
```

**Output Schema (Evaluation Report):**
```json
{
  "interview_id": "uuid",
  "session_duration_minutes": 30,
  "overall_score": 72,
  "competency_scores": {
    "technical_accuracy": 75,
    "problem_solving": 70,
    "communication": 80,
    "depth_of_knowledge": 65
  },
  "questions_answered": [
    {
      "question": "string",
      "student_answer": "string",
      "ideal_answer": "string",
      "score": 7,
      "feedback": "string",
      "improvement_tip": "string"
    }
  ],
  "overall_feedback": "string",
  "strengths": ["string"],
  "improvement_areas": ["string"],
  "recommended_resources": ["string"]
}
```

**API Endpoints:**
- `POST /api/ai/interview/start` — Begin session
- `POST /api/ai/stream` (with `mode=interview`) — Conversational turns (SSE)
- `POST /api/ai/interview/evaluate` — Generate post-session report

**Frontend Component:** `<AIInterviewSimulator />` — dedicated page with split view (video placeholder + chat)

**Redis Cache:** `ai:interview:session:{session_id}` → TTL 2h (active session state)

---

### 3.13 AI Teacher Assistant

**Purpose:** Comprehensive AI co-pilot for teachers. Automates lesson planning, student monitoring, grading, and content creation.

**Model:** `gemini-1.5-pro`

**Sub-Features:**

#### 3.13.1 Lesson Plan Generator
- **Input:** Topic, grade level, duration, learning objectives
- **Output:** Complete lesson plan (Bloom's objectives, activities, materials, timeline, assessment)

#### 3.13.2 Student Performance Analyzer
- **Input:** `teacher_id`, `course_id`, date range
- **Context:** `LearningProgress` for all enrolled students, quiz scores, submission rates
- **Output:** Class health report — struggling students flagged, recommended interventions

#### 3.13.3 Assignment Grader Assist
- **Input:** Assignment rubric (JSON) + student submission (text)
- **Output:** Suggested score per rubric criterion + detailed justification (teacher reviews before publishing)

#### 3.13.4 Course Content Improver
- **Input:** `lesson_id` + teacher-specified weak areas (e.g., "students find this confusing")
- **Output:** Suggested additions, rewordings, examples, analogies

#### 3.13.5 Announcement Drafter
- **Input:** Purpose (deadline reminder, class change, achievement) + details
- **Output:** Professional announcement text (ready for `NotificationRecord`)

**API Endpoints:**
- `POST /api/ai/teacher/lesson-plan`
- `POST /api/ai/teacher/student-analysis`
- `POST /api/ai/teacher/grade-assist`
- `POST /api/ai/teacher/improve-content`
- `POST /api/ai/teacher/draft-announcement`

**Frontend Component:** `<AITeacherAssistant />` — dedicated tab in Teacher Portal

**Permission:** Teacher role only (`RBAC: teacher_ai:*`)

---

### 3.14 AI Analytics

**Purpose:** AI-generated insights from platform usage data. Transforms raw analytics into actionable intelligence.

**Model:** `gemini-1.5-flash` (efficient for batch reports)

**Report Types:**
| Report | Audience | Frequency |
|---|---|---|
| Student Progress Report | Student | Weekly (Celery cron) |
| Class Performance Summary | Teacher | Weekly (Celery cron) |
| Platform Health Digest | Admin | Daily (Celery cron) |
| Course Engagement Analysis | Teacher + Admin | Monthly |
| AI Usage & Cost Report | Admin | Monthly |
| Learning Outcome Predictions | Teacher | On-demand |

**Data Sources per Report:**
- `AnalyticsEvent` — page views, lesson completions, quiz attempts
- `LearningProgress` — progress percentages per student per course
- `LearningHistory` — time-on-task data
- `AIUsageLog` — token consumption, model usage, costs
- `StudentStreak` — consistency data
- `TeacherAnalytics` — teacher performance metrics

**Output:** Narrative Markdown report with:
- Executive summary (2-3 sentences)
- Key metrics table
- Trend analysis with period comparison
- Top 3 concerns
- Top 3 opportunities
- Recommended actions

**API Endpoints:**
- `GET /api/ai/analytics/student-report/{student_id}`
- `GET /api/ai/analytics/class-report/{course_id}`
- `GET /api/ai/analytics/platform-digest`
- `POST /api/ai/analytics/custom-query`

**Frontend Component:** `<AIAnalyticsDashboard />` — dedicated admin + teacher page with embedded charts

**Redis Cache:** `ai:analytics:report:{type}:{id}:{date}` → TTL 6h

**Celery Tasks:** `generate_weekly_ai_reports_task` — Sunday night batch generation

---

### 3.15 AI Prompt Engine

**Purpose:** Central prompt management system. Versioned, categorized prompt templates that power all 14 AI features above. Replaces the current JSON-backed prompt store.

**Components:**

#### 3.15.1 Prompt Template Registry
- Stored in `AIPromptTemplate` PostgreSQL model (migrated from JSON)
- Fields: `name`, `description`, `category`, `system_prompt`, `user_prompt_template`, `variables` (JSON), `model_id`, `temperature`, `max_tokens`, `version`, `is_active`, `is_public`
- Versioning: each prompt has a `version` field; older versions retained in `AIPromptTemplateVersion`

#### 3.15.2 Variable Substitution Engine
- Template variables: `{student_name}`, `{lesson_content}`, `{course_title}`, etc.
- Runtime substitution in `GeminiService.build_prompt(template_id, context_dict)`
- Validation: missing variables raise `PromptVariableError` before API call

#### 3.15.3 Prompt Playground (Admin)
- Admin can test any prompt template with sample inputs
- See token count, estimated cost, and response quality
- A/B test two prompt versions side-by-side

#### 3.15.4 System Prompt Categories
| Category | Features |
|---|---|
| TUTORING | AI Tutor, Doubt Solver |
| GENERATION | Quiz, Assignment, Flashcards, Notes |
| CODE | Code Assistant |
| CAREER | Resume, Interview, Roadmap |
| PLANNING | Study Planner |
| ANALYTICS | AI Analytics reports |
| TEACHER | Teacher Assistant sub-features |

**API Endpoints:**
- `GET /api/ai/prompts/` (existing — needs DB migration)
- `POST /api/ai/prompts/` (existing — needs DB migration)
- `POST /api/ai/prompts/{id}/test` (NEW — playground)
- `POST /api/ai/prompts/{id}/version` (NEW — create new version)
- `GET /api/ai/prompts/{id}/versions` (NEW — version history)

**Frontend Component:** `<AIPromptLibrary />` (student-facing) + `<AIPromptPlayground />` (admin-facing)

---

## 4. Conversation Memory Architecture

### 4.1 Memory Layers

The AI Tutor and Doubt Solver require multi-turn memory. Three layers are designed:

```
┌─────────────────────────────────────────────────────────┐
│                  CONVERSATION MEMORY                     │
│                                                         │
│  Layer 1: Working Memory (Redis)                        │
│  - Last 10 messages of active session                   │
│  - Key: ai:session:{conversation_id}:messages           │
│  - TTL: 2 hours from last activity                     │
│  - Format: ordered list of {role, content, tokens}      │
│                                                         │
│  Layer 2: Short-Term Memory (PostgreSQL AIMessage)       │
│  - Full message history in ai_messages table            │
│  - Queried when Redis session expires                   │
│  - Token count stored per message                       │
│                                                         │
│  Layer 3: Long-Term Memory (Summarized)                 │
│  - When token count > 80,000: Celery summarize task     │
│  - Summary stored in AIConversation.summary (TextField) │
│  - Summary injected as first message in next session    │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Context Window Builder (`ContextWindowService`)

```
Algorithm: build_context(conversation_id, new_message, max_tokens=120000)

1. Load summary from AIConversation.summary → budget_used += estimate_tokens(summary)
2. Load system_prompt from AIAgentConfig → budget_used += estimate_tokens(system_prompt)
3. Load grounding_context from RAG → budget_used += estimate_tokens(rag_context)
4. Reserve 4096 tokens for output
5. Remaining budget = max_tokens - budget_used - 4096
6. Load messages from newest → oldest until budget exhausted
7. Return: [system_prompt] + [summary_msg] + [grounding_msg] + [messages] + [new_message]
```

### 4.3 Summarization Trigger

```
Trigger: After each assistant message is saved, check:
  IF sum(token_count for all messages in conversation) > 80,000:
    dispatch summarize_conversation_task.delay(conversation_id)

Summarization prompt:
  "Summarize this conversation history in 200 words, preserving key concepts 
   discussed, student's understanding level, and any unresolved questions."

After summary:
  - Store in AIConversation.summary
  - Mark old messages as archived (is_archived=True)
  - Keep last 5 messages unarchived for continuity
```

### 4.4 Pinned Context Items

- Individual messages can be pinned (`AIMessage.is_pinned=True`)
- Pinned messages are always included in context regardless of token budget
- Maximum 5 pinned messages per conversation (enforced at API level)

---

## 5. Semantic Search Architecture

### 5.1 Overview

Semantic search powers the **grounding layer** for all AI features. When an AI feature needs relevant platform content to answer a question accurately, it calls the `RAGService.retrieve()` method.

### 5.2 Indexing Pipeline

```
LMS Lesson Content (CourseStructure + SearchDocument)
         │
         ▼
  ContentChunker
  - Split lesson body into 512-token chunks with 50-token overlap
  - Each chunk: {text, lesson_id, course_id, chunk_index, title}
         │
         ▼
  EmbeddingService.embed(text, model="text-embedding-004")
  - Returns 1536-dimensional float vector
  - Calls Gemini embedding API (or Google AI Studio)
         │
         ▼
  AIEmbedding (PostgreSQL + pgvector)
  - Stores: vector, source_type, source_id, chunk_text, chunk_index, metadata
         │
         ▼
  pgvector index (ivfflat, lists=100)
  - Enables fast cosine similarity search
```

### 5.3 Retrieval Flow

```
User query or AI context need
         │
         ▼
  EmbeddingService.embed(query)  → query_vector (1536-dim)
         │
         ▼
  AIEmbedding.objects.annotate(distance=CosineDistance(vector, query_vector))
                     .filter(source_type__in=allowed_types)
                     .order_by('distance')
                     .limit(top_k)
         │
         ▼
  Retrieved chunks → formatted into grounding_context string
         │
         ▼
  RAGService.ground_prompt(base_prompt, retrieved_chunks)
  → Returns: base_prompt + "\n\nRELEVANT PLATFORM CONTENT:\n" + chunks
         │
         ▼
  GeminiService.generate(grounded_prompt, ...)
```

### 5.4 Semantic Search Types

| Search Type | Used By | Source Filter |
|---|---|---|
| Lesson Semantic Search | AI Tutor, Doubt Solver, Explainer | `entity_type=lesson` |
| Course Content Search | Roadmap Generator | `entity_type IN (course, lesson)` |
| Question Bank Search | Quiz Generator (de-dup) | `entity_type=quiz_question` |
| Notes Search | Notes Generator merge | `entity_type=student_note` |

---

## 6. Vector Search Architecture

### 6.1 Data Model: `AIEmbedding`

```python
class AIEmbedding(BaseModel):
    source_type = CharField(choices=[
        'lesson', 'course', 'quiz_question', 'student_note',
        'assignment', 'ai_conversation', 'ai_prompt_template'
    ])
    source_id = UUIDField(db_index=True)
    chunk_index = IntegerField(default=0)
    chunk_text = TextField()
    vector = VectorField(dimensions=1536)  # pgvector
    embedding_model = CharField(default="text-embedding-004")
    metadata = JSONField(default=dict)     # title, course_id, lesson_id, etc.
    
    class Meta:
        db_table = "ai_embeddings"
        indexes = [
            IvfflatIndex(fields=['vector'], lists=100)  # pgvector ANN index
        ]
        unique_together = [('source_type', 'source_id', 'chunk_index')]
```

### 6.2 pgvector Query Pattern

```sql
-- Top-5 most similar chunks to query embedding
SELECT 
    id, source_type, source_id, chunk_text,
    1 - (vector <=> '[query_vector]') AS similarity
FROM ai_embeddings
WHERE source_type = 'lesson'
ORDER BY vector <=> '[query_vector]'
LIMIT 5;
```

### 6.3 Batch Embedding Pipeline

```
Celery Task: batch_embed_lessons_task()
  - Query: CourseStructure.objects.filter(node_type='LESSON').exclude(id__in=already_embedded)
  - For each lesson:
    1. Get full text from SearchDocument.body
    2. Chunk into 512-token segments
    3. For each chunk: call EmbeddingService.embed()
    4. Bulk-create AIEmbedding records
  - Rate limit: 100 embeddings/second (Gemini API quota)
  - Estimated time for 10,000 lessons: ~2 hours
```

### 6.4 Incremental Update Triggers

```
Signal: post_save on SearchDocument (entity_type=lesson)
  → dispatch embed_content_task.delay(entity_type, entity_id)

Signal: post_save on StudentNote
  → dispatch embed_student_note_task.delay(note_id)
```

---

## 7. Redis Cache Architecture

### 7.1 Cache Key Namespace Design

All AI cache keys follow the pattern: `ai:{feature}:{hash}` where hash = `sha256` of the deterministic inputs.

```
Key Pattern                              TTL       Feature
─────────────────────────────────────────────────────────────────
ai:quiz:{h}                             6h        Quiz Generator
ai:assignment:{h}                       12h       Assignment Generator
ai:explain:{h}                          24h       Lesson Explainer
ai:notes:{h}                            24h       Notes Generator
ai:flashcards:{h}                       12h       Flashcards
ai:roadmap:{h}                          48h       Roadmap Generator
ai:studyplan:{student_id}:{week}        7d        Study Planner
ai:resume:{h}                           24h       Resume Assistant
ai:interview:session:{id}              2h        Interview Simulator
ai:analytics:report:{type}:{id}:{date} 6h        AI Analytics
ai:doubt:{h}                            2h        Doubt Solver
ai:code:debug:{h}                       30m       Code Assistant (debug)
ai:prompt:test:{id}:{h}                1h        Prompt Playground
─────────────────────────────────────────────────────────────────
ai:quota:user:{user_id}:daily          24h       Per-user token quota
ai:quota:user:{user_id}:monthly        30d       Monthly usage budget
ai:session:{conversation_id}:messages  2h        Working memory
ai:stream:pub:{request_id}             10m       SSE streaming pub/sub
```

### 7.2 Cache Service Design

```python
class AICacheService:
    def get(key: str) -> Optional[dict]
    def set(key: str, value: dict, ttl_seconds: int) -> None
    def delete(key: str) -> None
    def get_or_generate(key: str, ttl: int, generator: Callable) -> dict
    def invalidate_by_pattern(pattern: str) -> None   # SCAN + DEL

    @staticmethod
    def make_key(feature: str, inputs: dict) -> str:
        """SHA-256 hash of sorted JSON of inputs."""
        payload = json.dumps(inputs, sort_keys=True)
        return f"ai:{feature}:{hashlib.sha256(payload.encode()).hexdigest()[:16]}"
```

### 7.3 Per-User Token Quota

```
Quota Model:
  FREE tier:    50,000 tokens/day, 500,000 tokens/month
  STUDENT tier: 200,000 tokens/day, 2,000,000 tokens/month
  TEACHER tier: 500,000 tokens/day, 5,000,000 tokens/month
  ADMIN tier:   Unlimited

Redis Keys:
  ai:quota:{user_id}:daily   → INCR by tokens_used; EXPIRE at midnight IST
  ai:quota:{user_id}:monthly → INCR by tokens_used; EXPIRE at month end

Enforcement:
  Before each Gemini call:
    current = redis.get(ai:quota:{user_id}:daily)
    if current >= tier_limit:
      raise AIQuotaExceededException("Daily AI token limit reached.")
      → Return HTTP 429 with Retry-After header
      → Dispatch notify_quota_warning_task(user_id)
```

### 7.4 SSE Streaming via Redis Pub/Sub

```
Flow:
  1. Client POST /api/ai/stream → Gateway creates stream_id (UUID)
  2. Client SSE GET /api/ai/stream/{stream_id} → Gateway subscribes to ai:stream:{stream_id}
  3. Gateway Gemini handler → publishes chunks to ai:stream:{stream_id}
  4. SSE route → reads from channel → sends to client as text/event-stream
  5. On [DONE] chunk → Gateway sends "event: done\ndata: {}\n\n" → client closes
```

---

## 8. Celery Task Architecture

### 8.1 Task Registry (`apps/ai/tasks.py`)

```python
# ── EMBEDDING TASKS ─────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def embed_content_task(self, source_type: str, source_id: str):
    """Generate and store vector embedding for a single content item."""

@shared_task(bind=True)
def batch_embed_lessons_task(self, course_id: str = None):
    """Batch embed all un-embedded lessons. Optional: filter by course."""

@shared_task(bind=True)
def embed_student_note_task(self, note_id: str):
    """Embed a student note for personalized semantic search."""

# ── CONVERSATION TASKS ───────────────────────────────────────────

@shared_task(bind=True, max_retries=2)
def summarize_conversation_task(self, conversation_id: str):
    """Summarize a long conversation and update AIConversation.summary."""

@shared_task(bind=True)
def archive_old_messages_task(self, conversation_id: str):
    """Mark messages > 5 as is_archived after summarization."""

# ── GENERATION TASKS ─────────────────────────────────────────────

@shared_task(bind=True)
def pre_generate_quiz_task(self, lesson_id: str):
    """Pre-generate and cache quiz for a high-traffic lesson."""

@shared_task(bind=True)
def generate_study_plan_task(self, student_id: str, week_start: str):
    """Generate and cache weekly study plan."""

@shared_task(bind=True)
def generate_flashcards_task(self, lesson_id: str):
    """Pre-generate and cache flashcard deck for a lesson."""

# ── ANALYTICS TASKS ──────────────────────────────────────────────

@shared_task(bind=True)
def generate_student_weekly_report_task(self, student_id: str):
    """Generate and store student AI analytics report."""

@shared_task(bind=True)
def generate_class_report_task(self, course_id: str):
    """Generate teacher class performance report."""

@shared_task(bind=True)
def generate_platform_digest_task(self):
    """Admin platform health digest — runs daily."""

@shared_task(bind=True)
def ai_usage_rollup_task(self):
    """Aggregate AIUsageLog into hourly/daily rollup tables."""

# ── NOTIFICATION TASKS ────────────────────────────────────────────

@shared_task(bind=True)
def notify_quota_warning_task(self, user_id: str, usage_percent: float):
    """Notify user when they reach 80%/100% of AI token quota."""

@shared_task(bind=True)
def notify_study_reminder_task(self, student_id: str, session_data: dict):
    """15-minute pre-session study reminder."""

@shared_task(bind=True)
def notify_doubt_escalation_task(self, student_id: str, teacher_id: str, doubt: str):
    """Notify teacher when AI confidence on a student's doubt is LOW."""

@shared_task(bind=True)
def notify_flashcard_review_task(self, student_id: str, deck_id: str):
    """Daily spaced-repetition review reminder."""

# ── LOGGING TASKS ────────────────────────────────────────────────

@shared_task(bind=True)
def log_ai_usage_task(self, usage_data: dict):
    """Async log AI usage to AIUsageLog. Fire-and-forget."""
```

### 8.2 Celery Beat Schedule

```python
CELERY_BEAT_SCHEDULE = {
    # Daily — 2 AM IST
    'generate-platform-digest': {
        'task': 'apps.ai.tasks.generate_platform_digest_task',
        'schedule': crontab(hour=20, minute=30),  # UTC = 2 AM IST
    },
    # Daily — 3 AM IST
    'ai-usage-rollup': {
        'task': 'apps.ai.tasks.ai_usage_rollup_task',
        'schedule': crontab(hour=21, minute=30),
    },
    # Sunday — 11 PM IST (batch weekly reports)
    'weekly-student-reports': {
        'task': 'apps.ai.tasks.generate_student_weekly_reports_batch',
        'schedule': crontab(hour=17, minute=30, day_of_week=0),
    },
    # Monday — 5:30 AM IST (study plans)
    'weekly-study-plans': {
        'task': 'apps.ai.tasks.batch_generate_study_plans',
        'schedule': crontab(hour=0, minute=0, day_of_week=1),
    },
    # Nightly — batch pre-generate quizzes for top-20 lessons
    'pre-generate-quizzes': {
        'task': 'apps.ai.tasks.batch_quiz_pre_generation',
        'schedule': crontab(hour=22, minute=0),
    },
}
```

### 8.3 Task Priority Queues

```python
CELERY_TASK_ROUTES = {
    'apps.ai.tasks.log_ai_usage_task': {'queue': 'ai_low'},
    'apps.ai.tasks.embed_content_task': {'queue': 'ai_low'},
    'apps.ai.tasks.batch_embed_lessons_task': {'queue': 'ai_batch'},
    'apps.ai.tasks.summarize_conversation_task': {'queue': 'ai_high'},
    'apps.ai.tasks.notify_*': {'queue': 'ai_high'},
    'apps.ai.tasks.generate_*': {'queue': 'ai_medium'},
}
```

---

## 9. API Design

### 9.1 Complete API Endpoint Catalog (36 endpoints)

#### Group A — Conversation & Chat (Existing + Extensions)
```
GET    /api/ai/conversations/                     List user conversations
POST   /api/ai/conversations/                     Create conversation
GET    /api/ai/conversations/{id}/                Retrieve conversation
PATCH  /api/ai/conversations/{id}/                Update conversation title
DELETE /api/ai/conversations/{id}/                Soft-delete conversation
POST   /api/ai/conversations/{id}/restore/        Restore conversation
GET    /api/ai/conversations/{id}/messages/       List messages
POST   /api/ai/conversations/{id}/messages/       Send message (non-stream)
GET    /api/ai/conversations/{id}/context/        View context memory
POST   /api/ai/conversations/{id}/context/cleanup/ Clear context pins
POST   /api/ai/conversations/{id}/export/         Export conversation
```

#### Group B — Streaming & Real-Time (New)
```
POST   /api/ai/stream                            SSE streaming chat (Gateway Express)
POST   /api/ai/chat                              Non-streaming chat (Gateway Express)
```

#### Group C — Content Generation (New)
```
POST   /api/ai/generate-quiz                     Generate quiz questions
POST   /api/ai/generate-curriculum               Generate curriculum structure
POST   /api/ai/generate-assignment               Generate assignment/problem set
POST   /api/ai/explain                           Explain a lesson concept
POST   /api/ai/generate-notes                    Generate study notes
POST   /api/ai/flashcards                        Generate flashcard deck
POST   /api/ai/solve-doubt                       Solve a specific doubt (SSE)
POST   /api/ai/roadmap                           Generate learning roadmap
POST   /api/ai/study-plan                        Generate study plan
POST   /api/ai/code-assist                       Code completion/debug/review
```

#### Group D — Career (New)
```
POST   /api/ai/resume                            Resume generate/optimize/score
POST   /api/ai/interview/start                   Start interview session
POST   /api/ai/interview/evaluate                Get post-session evaluation
```

#### Group E — Teacher AI (New)
```
POST   /api/ai/teacher/lesson-plan               Generate lesson plan
POST   /api/ai/teacher/student-analysis          Class performance analysis
POST   /api/ai/teacher/grade-assist              Grading assistance
POST   /api/ai/teacher/improve-content           Content improvement suggestions
POST   /api/ai/teacher/draft-announcement        Draft announcement text
```

#### Group F — Analytics (New)
```
GET    /api/ai/analytics/student-report/{id}     Student AI analytics report
GET    /api/ai/analytics/class-report/{id}       Class AI analytics report
GET    /api/ai/analytics/platform-digest         Platform AI digest (admin)
POST   /api/ai/analytics/custom-query            Custom AI analytics query
```

#### Group G — Prompt Engine (Existing + Extensions)
```
GET    /api/ai/prompts/                          List prompt templates
POST   /api/ai/prompts/                          Create prompt template
GET    /api/ai/prompts/{id}/                     Retrieve prompt template
PATCH  /api/ai/prompts/{id}/                     Update prompt template
DELETE /api/ai/prompts/{id}/                     Delete prompt template
POST   /api/ai/prompts/{id}/test/                Test prompt in playground
POST   /api/ai/prompts/{id}/version/             Create new version
GET    /api/ai/prompts/{id}/versions/            Version history
```

#### Group H — Registry & Tracking (Existing)
```
GET    /api/ai/models/                           List AI model registry
POST   /api/ai/models/                           Register AI model
GET    /api/ai/usage/                            Usage tracking log
GET    /api/ai/sessions/                         Chat sessions
GET    /api/ai/analytics/                        AI usage analytics
GET    /api/ai/feedback/                         Feedback (admin)
```

### 9.2 Standard Request/Response Envelope

```typescript
// Request
interface AIRequest {
  conversation_id?: string;    // optional threading
  model_id?: string;           // override default model
  stream?: boolean;            // request SSE
  language?: string;           // "en" | "hi" | "ta" etc.
  context?: {
    course_id?: string;
    lesson_id?: string;
    student_id?: string;
  };
  // Feature-specific payload
  [key: string]: any;
}

// Non-streaming Response
interface AIResponse<T> {
  success: boolean;
  data: T;
  metadata: {
    model_id: string;
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    estimated_cost_usd: number;
    latency_ms: number;
    cached: boolean;
    cache_key?: string;
  };
  error?: string;
}

// SSE Event Format
"data: {\"chunk\": \"...text...\", \"is_done\": false}\n\n"
"data: {\"chunk\": \"\", \"is_done\": true, \"metadata\": {...}}\n\n"
```

### 9.3 Authentication & Permissions

All `/api/ai/*` endpoints require:
1. **JWT Bearer token** (validated by gateway middleware)
2. **RBAC permission** per endpoint:

```
GET  /api/ai/conversations/                → vidya_ai:conversation:view
POST /api/ai/stream                        → vidya_ai:chat:create
POST /api/ai/generate-quiz                 → vidya_ai:quiz:create
POST /api/ai/teacher/*                     → teacher_ai:*  (Teacher role only)
GET  /api/ai/analytics/platform-digest     → vidya_ai:admin:analytics (Admin only)
POST /api/ai/prompts/{id}/test             → vidya_ai:prompt:admin (Admin only)
```

---

## 10. Frontend Architecture

### 10.1 Component Tree

```
src/
├── components/
│   ├── ai/                              ← NEW — all AI components
│   │   ├── core/
│   │   │   ├── AIAssistantPanel.tsx     ← Primary AI sidebar (all pages)
│   │   │   ├── AIMessageBubble.tsx      ← Message rendering (markdown, code)
│   │   │   ├── AIStreamingText.tsx      ← SSE stream consumer
│   │   │   ├── AIModelSelector.tsx      ← Model switcher dropdown
│   │   │   └── AIPromptLibrary.tsx      ← Prompt template picker
│   │   ├── student/
│   │   │   ├── AITutorPanel.tsx         ← AI Tutor in lesson view
│   │   │   ├── AIExplainerModal.tsx     ← "Explain This" modal
│   │   │   ├── AIDoubtSolver.tsx        ← Floating doubt button
│   │   │   ├── AINotesPanel.tsx         ← AI notes generation
│   │   │   ├── AIFlashcardDeck.tsx      ← Swipeable flashcard UI
│   │   │   ├── AIStudyPlanner.tsx       ← Weekly calendar planner
│   │   │   ├── AIRoadmapViewer.tsx      ← Visual roadmap timeline
│   │   │   ├── AIResumeBuilder.tsx      ← Resume builder wizard
│   │   │   └── AIInterviewSimulator.tsx ← Interview simulation UI
│   │   ├── teacher/
│   │   │   ├── AITeacherAssistant.tsx   ← Teacher AI hub
│   │   │   ├── AIQuizGenerator.tsx      ← Quiz generation UI
│   │   │   ├── AIAssignmentBuilder.tsx  ← Assignment builder
│   │   │   ├── AIGradeAssist.tsx        ← Grading UI
│   │   │   └── AILessonPlanner.tsx      ← Lesson plan generator
│   │   ├── code/
│   │   │   └── AICodeEditor.tsx         ← Monaco + AI sidebar
│   │   └── admin/
│   │       ├── AIPromptPlayground.tsx   ← Prompt testing admin
│   │       ├── AIUsageDashboard.tsx     ← Cost + usage analytics
│   │       └── AIAnalyticsDashboard.tsx ← AI analytics reports
│   └── ...existing components...
├── services/
│   ├── aiApi.ts                         ← NEW — full AI API client
│   └── ...existing services...
├── stores/
│   ├── aiStore.ts                       ← NEW — Zustand AI state
│   └── ...existing stores...
└── hooks/
    ├── useAIStream.ts                   ← NEW — SSE stream hook
    ├── useAIChat.ts                     ← NEW — chat session hook
    └── useAIQuota.ts                    ← NEW — quota monitoring hook
```

### 10.2 `src/services/aiApi.ts` — Full API Client

```typescript
export const aiApi = {
  // Core Conversations
  conversations: {
    list: (params?) => GET /api/ai/conversations/,
    create: (data) => POST /api/ai/conversations/,
    get: (id) => GET /api/ai/conversations/{id}/,
    update: (id, data) => PATCH /api/ai/conversations/{id}/,
    delete: (id) => DELETE /api/ai/conversations/{id}/,
    restore: (id) => POST /api/ai/conversations/{id}/restore/,
    messages: (id, params?) => GET /api/ai/conversations/{id}/messages/,
    sendMessage: (id, data) => POST /api/ai/conversations/{id}/messages/,
    export: (id, format) => POST /api/ai/conversations/{id}/export/,
    context: (id) => GET /api/ai/conversations/{id}/context/,
  },

  // Streaming
  stream: (payload: AIStreamRequest) => EventSource → SSE,
  chat: (payload) => POST /api/ai/chat,

  // Content Generation
  generateQuiz: (payload) => POST /api/ai/generate-quiz,
  generateCurriculum: (payload) => POST /api/ai/generate-curriculum,
  generateAssignment: (payload) => POST /api/ai/generate-assignment,
  explain: (payload) => POST /api/ai/explain,
  generateNotes: (payload) => POST /api/ai/generate-notes,
  flashcards: (payload) => POST /api/ai/flashcards,
  solveDoubt: (payload) => EventSource → SSE,
  roadmap: (payload) => POST /api/ai/roadmap,
  studyPlan: (payload) => POST /api/ai/study-plan,
  codeAssist: (payload) => POST /api/ai/code-assist,

  // Career
  resume: (payload) => POST /api/ai/resume,
  interviewStart: (payload) => POST /api/ai/interview/start,
  interviewEvaluate: (session_id) => POST /api/ai/interview/evaluate,

  // Teacher
  teacher: {
    lessonPlan: (payload) => POST /api/ai/teacher/lesson-plan,
    studentAnalysis: (payload) => POST /api/ai/teacher/student-analysis,
    gradeAssist: (payload) => POST /api/ai/teacher/grade-assist,
    improveContent: (payload) => POST /api/ai/teacher/improve-content,
    draftAnnouncement: (payload) => POST /api/ai/teacher/draft-announcement,
  },

  // Analytics
  analytics: {
    studentReport: (student_id) => GET /api/ai/analytics/student-report/{id},
    classReport: (course_id) => GET /api/ai/analytics/class-report/{id},
    platformDigest: () => GET /api/ai/analytics/platform-digest,
    customQuery: (payload) => POST /api/ai/analytics/custom-query,
  },

  // Prompts
  prompts: {
    list: (params?) => GET /api/ai/prompts/,
    create: (data) => POST /api/ai/prompts/,
    get: (id) => GET /api/ai/prompts/{id}/,
    update: (id, data) => PATCH /api/ai/prompts/{id}/,
    delete: (id) => DELETE /api/ai/prompts/{id}/,
    test: (id, inputs) => POST /api/ai/prompts/{id}/test/,
    createVersion: (id) => POST /api/ai/prompts/{id}/version/,
    versions: (id) => GET /api/ai/prompts/{id}/versions/,
  },

  // Usage & Models
  usage: { list: (params?) => GET /api/ai/usage/ },
  models: { list: () => GET /api/ai/models/ },
};
```

### 10.3 `useAIStream` Hook Design

```typescript
interface UseAIStreamOptions {
  onChunk: (chunk: string) => void;
  onDone: (metadata: AIResponseMetadata) => void;
  onError: (error: Error) => void;
}

function useAIStream(options: UseAIStreamOptions) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [buffer, setBuffer] = useState('');
  const eventSourceRef = useRef<EventSource | null>(null);

  const startStream = useCallback((payload: AIStreamRequest) => {
    // 1. POST /api/ai/stream → get stream_id
    // 2. Open EventSource to /api/ai/stream/{stream_id}
    // 3. On message: append to buffer, call onChunk
    // 4. On done event: call onDone with metadata
    // 5. Close EventSource
  }, []);

  const stopStream = useCallback(() => {
    eventSourceRef.current?.close();
    setIsStreaming(false);
  }, []);

  return { isStreaming, buffer, startStream, stopStream };
}
```

### 10.4 Zustand AI Store Design

```typescript
interface AIState {
  // Active conversation
  activeConversationId: string | null;
  conversations: AIConversation[];
  messages: Record<string, AIMessage[]>;  // keyed by conversation_id

  // Streaming state
  isStreaming: boolean;
  streamBuffer: string;

  // AI features state
  currentRoadmap: AIRoadmap | null;
  currentStudyPlan: AIStudyPlan | null;
  activeInterviewSession: AIInterviewSession | null;

  // Usage
  dailyTokensUsed: number;
  dailyTokenLimit: number;
  quotaWarningShown: boolean;

  // Settings
  selectedModelId: string;
  preferredLanguage: string;
}
```

---

## 11. Gateway Architecture

### 11.1 Gateway Handler Organization (`server.ts`)

New AI handlers added to `server.ts` — organized in a dedicated section after the existing PATH_MAP middleware:

```typescript
// ─── SECTION: AI GATEWAY HANDLERS ──────────────────────────────────────
// These handlers call Gemini API directly (not proxied to Django).
// Django is only called for persistence (via proxyToDjango at the end).

// 11.1.1 — Common Middleware (applied to all /api/ai/* AI generation routes)
const aiAuthMiddleware = async (req, res, next) => {
  // 1. Validate JWT
  // 2. Extract user_id and role from token
  // 3. Check RBAC permission for the specific AI feature
  // 4. Check Redis token quota for user
  // 5. If all pass → next()
};

// 11.1.2 — Non-streaming chat
app.post('/api/ai/chat', aiAuthMiddleware, async (req, res) => {
  const client = getGemini();
  if (!client) return res.json({ success: true, data: { text: mockFallback(req.body.message) }, metadata: { cached: false } });

  const cacheKey = AICacheService.makeKey('chat', { message: req.body.message });
  const cached = await AICacheService.get(cacheKey);
  if (cached) return res.json({ success: true, data: cached, metadata: { cached: true } });

  const startTime = Date.now();
  const result = await client.models.generateContent({
    model: req.body.model_id || 'gemini-1.5-flash',
    contents: buildChatContents(req.body),
  });

  const response = { text: result.text };
  await AICacheService.set(cacheKey, response, 300);  // 5 min
  await logUsageToRedis(req.user.id, result.usageMetadata);

  res.json({
    success: true,
    data: response,
    metadata: { model_id: req.body.model_id || 'gemini-1.5-flash', cached: false, latency_ms: Date.now() - startTime, ...result.usageMetadata }
  });
});

// 11.1.3 — SSE Streaming
app.post('/api/ai/stream', aiAuthMiddleware, async (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no');

  const client = getGemini();
  if (!client) {
    res.write(`data: ${JSON.stringify({ chunk: mockFallback(req.body.message), is_done: false })}\n\n`);
    res.write(`data: ${JSON.stringify({ chunk: '', is_done: true })}\n\n`);
    return res.end();
  }

  const stream = await client.models.generateContentStream({
    model: req.body.model_id || 'gemini-1.5-pro',
    contents: buildChatContents(req.body),
    systemInstruction: buildSystemInstruction(req.body),
  });

  let fullText = '';
  for await (const chunk of stream) {
    const chunkText = chunk.text || '';
    fullText += chunkText;
    res.write(`data: ${JSON.stringify({ chunk: chunkText, is_done: false })}\n\n`);
  }

  res.write(`data: ${JSON.stringify({ chunk: '', is_done: true, full_text: fullText })}\n\n`);
  res.end();

  // Async: save to Django, log usage
  await proxyToDjango(req, res, '/api/v1/ai/conversations/{id}/messages/');
});

// 11.1.4 — Quiz Generation (structured output)
app.post('/api/ai/generate-quiz', aiAuthMiddleware, async (req, res) => { ... });

// 11.1.5 — Curriculum Generation (structured output)
app.post('/api/ai/generate-curriculum', aiAuthMiddleware, async (req, res) => { ... });

// 11.1.6 — Lesson Explanation (with RAG — calls Django for vector search first)
app.post('/api/ai/explain', aiAuthMiddleware, async (req, res) => {
  // 1. Call Django /api/v1/ai/search/semantic/ to get grounding context
  // 2. Build grounded prompt
  // 3. Call Gemini
  // 4. Return structured explanation
});

// ... (11.1.7 through 11.1.15 for remaining features)
```

### 11.2 Gateway Security Layer

```
Every AI request passes through:

1. JWT Verification
   → Extract: user_id, email, role, permissions[]
   → If invalid → 401 Unauthorized

2. RBAC Check
   → permission = AI_ROUTE_PERMISSIONS[req.path]
   → If user.permissions does not include permission → 403 Forbidden

3. Token Quota Check
   → redis.get(ai:quota:{user_id}:daily)
   → If >= tier_limit → 429 Too Many Requests

4. Input Validation
   → Sanitize all string inputs (max length, no injection)
   → Validate UUIDs for course_id, lesson_id, etc.

5. Tracing Headers
   → Attach X-Request-ID, X-User-ID to all Gemini calls for audit
```

### 11.3 Gateway Route Map Update (PATH_MAP additions)

```typescript
// New Django-proxied AI routes (added to PATH_MAP)
'/api/ai/search/semantic':        '/api/v1/ai/search/semantic/',
'/api/ai/teacher/lesson-plan':    '/api/v1/ai/teacher/lesson-plan/',
'/api/ai/teacher/student-analysis':'/api/v1/ai/teacher/student-analysis/',
'/api/ai/analytics/student-report':'/api/v1/ai/analytics/student-report/',
'/api/ai/analytics/class-report': '/api/v1/ai/analytics/class-report/',
'/api/ai/analytics/platform-digest':'/api/v1/ai/analytics/platform-digest/',
```

---

## 12. Data Model Specifications

### 12.1 `AIPromptTemplate` (Migrated from JSON)

```python
class AIPromptTemplate(SoftDeleteModel):
    name = CharField(max_length=255, unique=True)
    description = TextField(blank=True)
    category = CharField(max_length=50, choices=CATEGORY_CHOICES)
    system_prompt = TextField()
    user_prompt_template = TextField()
    variables = JSONField(default=list)      # ["student_name", "lesson_content"]
    model_id = CharField(max_length=50, default="gemini-1.5-pro")
    temperature = FloatField(default=0.7)
    max_tokens = IntegerField(default=4096)
    version = CharField(max_length=20, default="1.0.0")
    is_active = BooleanField(default=True)
    is_public = BooleanField(default=True)
    is_favorite = BooleanField(default=False)
    owner = ForeignKey("users.User", null=True, blank=True, on_delete=SET_NULL)
    usage_count = IntegerField(default=0)
```

### 12.2 `AIModelRegistry` (Migrated from JSON)

```python
class AIModelRegistry(BaseModel):
    model_id = CharField(max_length=100, unique=True)   # "gemini-1.5-pro"
    name = CharField(max_length=255)
    provider = CharField(max_length=50)                 # "Gemini", "GPT", etc.
    context_window = IntegerField()
    max_output_tokens = IntegerField()
    input_token_rate = DecimalField(max_digits=12, decimal_places=8)
    output_token_rate = DecimalField(max_digits=12, decimal_places=8)
    supports_streaming = BooleanField(default=True)
    supports_function_calling = BooleanField(default=False)
    supports_vision = BooleanField(default=False)
    supports_grounding = BooleanField(default=False)
    is_active = BooleanField(default=True)
    is_default = BooleanField(default=False)
    status = CharField(max_length=20, default="ACTIVE")
    capabilities = JSONField(default=dict)
```

### 12.3 `AIUsageLog` (Migrated from JSON list)

```python
class AIUsageLog(BaseModel):
    user = ForeignKey("users.User", on_delete=CASCADE)
    conversation = ForeignKey(AIConversation, null=True, blank=True, on_delete=SET_NULL)
    model_id = CharField(max_length=100)
    feature = CharField(max_length=100)     # "tutor", "quiz", "explain", etc.
    prompt_tokens = IntegerField()
    completion_tokens = IntegerField()
    total_tokens = IntegerField()
    estimated_cost_usd = DecimalField(max_digits=10, decimal_places=6)
    latency_ms = IntegerField()
    cached = BooleanField(default=False)
    error = BooleanField(default=False)
    error_message = TextField(blank=True)
    request_metadata = JSONField(default=dict)
    
    class Meta:
        indexes = [
            Index(fields=["user", "-created_at"]),
            Index(fields=["feature", "-created_at"]),
            Index(fields=["model_id", "-created_at"]),
        ]
```

### 12.4 `AIChatSession` (Migrated from JSON)

```python
class AIChatSession(BaseModel):
    user = ForeignKey("users.User", on_delete=CASCADE)
    conversation = ForeignKey(AIConversation, null=True, blank=True, on_delete=SET_NULL)
    model_id = CharField(max_length=100, default="gemini-1.5-pro")
    start_time = DateTimeField(auto_now_add=True)
    end_time = DateTimeField(null=True, blank=True)
    duration_seconds = IntegerField(default=0)
    total_messages = IntegerField(default=0)
    total_tokens = IntegerField(default=0)
    device = CharField(max_length=100, blank=True)
    language = CharField(max_length=10, default="en")
    feature_used = CharField(max_length=100, default="tutor")
    is_active = BooleanField(default=True)
```

### 12.5 `AIEmbedding` (New — pgvector)

```python
class AIEmbedding(BaseModel):
    source_type = CharField(max_length=50, db_index=True)
    source_id = UUIDField(db_index=True)
    chunk_index = IntegerField(default=0)
    chunk_text = TextField()
    vector = VectorField(dimensions=1536)   # requires pgvector
    embedding_model = CharField(max_length=100, default="text-embedding-004")
    token_count = IntegerField(default=0)
    metadata = JSONField(default=dict)
    
    class Meta:
        unique_together = [('source_type', 'source_id', 'chunk_index')]
        indexes = [IvfflatIndex(fields=['vector'], lists=100)]
```

### 12.6 `AIAgentConfig` (New)

```python
class AIAgentConfig(BaseModel):
    name = CharField(max_length=100, unique=True)
    agent_type = CharField(max_length=50)     # "tutor", "teacher", "interviewer"
    model_id = CharField(max_length=100, default="gemini-1.5-pro")
    system_prompt_template_id = ForeignKey(AIPromptTemplate, on_delete=PROTECT)
    temperature = FloatField(default=0.7)
    max_output_tokens = IntegerField(default=4096)
    context_window_tokens = IntegerField(default=120000)
    summarization_threshold = IntegerField(default=80000)
    rag_top_k = IntegerField(default=5)
    is_active = BooleanField(default=True)
    config = JSONField(default=dict)           # feature-specific overrides
```

### 12.7 `AIRateLimitQuota` (New)

```python
class AIRateLimitQuota(BaseModel):
    user = OneToOneField("users.User", on_delete=CASCADE)
    tier = CharField(max_length=20, default="STUDENT")
    daily_token_limit = IntegerField(default=200000)
    monthly_token_limit = IntegerField(default=2000000)
    is_unlimited = BooleanField(default=False)
    custom_limits = JSONField(default=dict)
```

---

## 13. Integration Map

```
AI Feature          → Student App Integration
───────────────────────────────────────────────────────────────
AI Tutor            → LearningHistory (recent lessons context)
                      LearningProgress (weak areas detection)
                      StudentEnrollment (course context)
AI Study Planner    → LearningProgress (completion status)
                      StudentStreak (consistency data)
                      CalendarEvent (exam dates)
AI Notes Generator  → StudentNote (merge AI notes as source=AI)
AI Flashcards       → LearningHistory (spaced repetition triggers)
AI Resume Builder   → Certificate (earned credentials)
                      LearningHistory (completed courses)
AI Doubt Solver     → NotificationRecord (escalate to teacher)

AI Feature          → Teacher App Integration
───────────────────────────────────────────────────────────────
AI Quiz Generator   → CourseStructure (lesson content)
AI Assignment Gen   → CourseStructure (course context)
                      TeacherProfile (specialties)
AI Teacher Asst.    → TeacherAnalytics (performance data)
                      LearningProgress (student progress)
AI Lesson Planner   → CourseStructure (existing content)

AI Feature          → LMS Integration
───────────────────────────────────────────────────────────────
ALL features        → CourseStructure (content graph)
                      SearchDocument (lesson body text via RAG)
                      StudentEnrollment (access control)

AI Feature          → Search Integration
───────────────────────────────────────────────────────────────
ALL RAG features    → AIEmbedding (vector search)
                      SearchDocument (text search fallback)
                      index_ai_item_task (new content indexing)

AI Feature          → Analytics Integration
───────────────────────────────────────────────────────────────
ALL features        → AnalyticsEvent (AI interaction events)
                      AIUsageLog (token + cost tracking)

AI Feature          → Notifications Integration
───────────────────────────────────────────────────────────────
AI Doubt Solver     → NotificationRecord (teacher escalation)
AI Study Planner    → NotificationRecord (session reminders)
AI Flashcards       → NotificationRecord (review reminders)
AI Quota System     → NotificationRecord (quota warnings)
AI Analytics        → NotificationRecord (weekly report ready)
```

---

## 14. Implementation Constraints

### 14.1 What MUST NOT Change
- Existing Django model fields in `control_center`, `student`, `teacher`, `lms`, `search`, `analytics`, `notifications`, `cms`
- Existing API response shapes for non-AI endpoints
- Existing gateway PATH_MAP entries
- Existing React component APIs and prop shapes
- Existing RBAC permission names (only ADD new ones)
- Database table names for existing models

### 14.2 What MUST Be Extended
- `server.ts` — add AI handler section AFTER existing PATH_MAP middleware
- `src/services/api.ts` — ADD `ai.*` methods (do not remove existing)
- `backend/apps/control_center/models.py` — ADD fields to `AIConversation`, `AIMessage`
- `backend/apps/ai/views.py` — ADD new ViewSets for teacher, analytics, semantic search
- `backend/apps/ai/urls.py` — ADD new routes

### 14.3 What MUST Be Created (New Files Only)
- `backend/apps/ai/models.py` — New AI models
- `backend/apps/ai/services.py` — GeminiService, RAGService, EmbeddingService, ContextWindowService
- `backend/apps/ai/tasks.py` — All Celery tasks
- `backend/apps/ai/signals.py` — post_save signals for embedding triggers
- `backend/apps/ai/selectors.py` — DB query selectors
- `backend/apps/ai/validators.py` — Input validation
- `src/components/ai/` — All AI React components
- `src/services/aiApi.ts` — Dedicated AI API client
- `src/stores/aiStore.ts` — Zustand AI state
- `src/hooks/useAIStream.ts` — SSE stream hook
- `src/hooks/useAIChat.ts` — Chat session hook
- `src/hooks/useAIQuota.ts` — Quota monitoring hook

### 14.4 Gemini API Key Requirement

> **CRITICAL PREREQUISITE:** The `GEMINI_API_KEY` environment variable must be set in `.env` before any Phase 2 implementation begins. Without it, all AI generation endpoints fall back to mock responses. The `.env.example` file must be updated to document this requirement.

### 14.5 Database Requirements

> **pgvector must be installed** before migrations for `AIEmbedding` can run:
> ```sql
> CREATE EXTENSION IF NOT EXISTS vector;
> ```
> This requires PostgreSQL 14+ and the `pgvector` package installed on the PostgreSQL server.

### 14.6 Python Package Requirements

New packages needed (to be added to `requirements.txt`):
- `google-genai` — Gemini Python SDK
- `pgvector` — pgvector Django integration
- `tiktoken` OR use Gemini's `count_tokens` API — accurate token counting

---

## Appendix: Architecture Decision Records (ADRs)

| # | Decision | Rationale |
|---|---|---|
| ADR-01 | SSE over WebSockets for streaming | SSE is simpler, HTTP/1.1 compatible, no upgrade needed |
| ADR-02 | Gemini in Gateway (Node.js), not Django | Reduces Python/Django latency for streaming; Gateway already has Gemini SDK |
| ADR-03 | pgvector over external vector DB | Zero new infrastructure; PostgreSQL already deployed |
| ADR-04 | Redis for session memory, PostgreSQL for persistence | Fast read for active sessions; durable storage for history |
| ADR-05 | text-embedding-004 (1536-dim) | Google's best text embedding model; consistent with Gemini ecosystem |
| ADR-06 | Celery for batch tasks | Already deployed; reuse over adding a new job runner |
| ADR-07 | SHA-256 cache keys | Deterministic; prevents cache collisions; short enough for Redis key limits |
| ADR-08 | Migrate JSON store to PostgreSQL | Production safety; JSON flat file is not scalable or concurrent-safe |
| ADR-09 | Role-aware AI features (RBAC) | Different features, contexts, and quotas per role (Student/Teacher/Admin) |
| ADR-10 | Teacher AI features server-side only | Sensitive student data must not be exposed to browser; server-side aggregation only |

---

*Document: Sprint 24 — Phase 1 Architecture*  
*Status: DESIGN COMPLETE — No implementation performed*  
*Next: Sprint 24 Phase 2 — Foundation Implementation (Real Gemini + Gateway Handlers)*
