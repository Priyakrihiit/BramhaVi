# Low-Level System Architecture - BrahmaVidya Galaxy

## 1. Request-Response Lifecycle
The lifecycle of an authorized request targeting an administrative endpoint (e.g., updating a dynamic page block) is governed by the following flow:

```
[Client App] ===(1. PUT /api/pages/:id)===> [Express Backend Router]
                                                    ||
                                                    || (2. CORS & Rate Limiter)
                                                    \/
                                            [Security Filter]
                                                    ||
                                                    || (3. Verify JWT HttpOnly Cookie)
                                                    \/
                                            [Auth Middleware]
                                                    ||
                                                    || (4. Query Database Role Permissions)
                                                    \/
                                            [RBAC Authorization]
                                                    ||
                                                    || (5. Validate Body Schema / Sanitization)
                                                    \/
                                            [Request Validator]
                                                    ||
                                                    || (6. Commit transaction & cache reset)
                                                    \/
                                            [Database Service]
                                                    ||
[Client App] <===(7. HTTP 200 OK Json)==============+
```

---

## 2. Backend Middleware Chain Design
All backend routes are protected by a modular middleware pipeline:

1. **CORS Middleware**: Verifies the origin header against allowed platform configurations.
2. **Body Parser**: Decodes JSON payloads and URL-encoded structures.
3. **Cookie Parser**: Parses incoming HttpOnly cookies to extract session identifiers.
4. **Rate Limiter**: Tracks request frequencies mapped to source IPs.
5. **Session Authenticator (`requireAuth`)**: Decodes the access JWT. If expired, initiates token-rotation using the secure refresh cookie.
6. **Authorization Guard (`requirePermission(code)`)**: Checks the active user session roles against the required permission code.
7. **XSS Sanitizer**: Automatically cleanses input strings matching common HTML tags before routing them to controller handlers.

---

## 3. React Frontend Hooks & Context
To maintain modularity and prevent file bloat in `App.tsx`, state is coordinated across dedicated contexts and hooks:

### 3.1 Context Providers
- **`AuthContext`**: Manages current user profile states, login routines, logout clears, and active session statuses.
- **`CMSContext`**: Orchestrates active menu lists, dynamic navigation states, and page structures.
- **`LMSContext`**: Tracks the selected course node, lesson progression arrays, and active task completions.

### 3.2 Custom UI Hooks
- **`useVidyaAI`**: Wraps backend interactions with Vidya AI services. Offers modular routines:
  - `generateSyllabus(topic)`
  - `generateLessonQuiz(lessonId)`
  - `queryAssistant(prompt)`
- **`useVisualSEO`**: Analyzes Title, Description, and Keywords state instantly, calculating character counters and semantic progress bars.

---

## 4. Class & Boundary Contracts

### 4.1 Standardized API Payload Contract
All REST endpoints must return a predictable payload contract:
```typescript
interface ApiResponse<T> {
  success: boolean;       // True if operation succeeded, false otherwise
  data?: T;               // Strongly-typed response payload
  error?: {               // Standardized error context if success is false
    code: string;         // Unique error classifier (e.g., "UNAUTHORIZED")
    message: string;      // Human-readable summary
    details?: string[];   // Granular field-level errors
  };
  meta?: {                // Auxiliary metadata (e.g., pagination counters)
    totalRecords?: number;
    page?: number;
  };
}
```

### 4.2 Vidya AI Provider Interface
To allow hot-swapping between LLM providers (Gemini, Claude, OpenAI), the backend encapsulates AI operations within a clean interface contract:
```typescript
interface IAiProvider {
  generateSyllabus(prompt: string): Promise<string>; // Returns JSON structure matching course builder schema
  generateQuiz(lessonContent: string): Promise<QuizQuestion[]>;
  chatCompletion(chatHistory: ChatMessage[], newPrompt: string): Promise<string>;
}
```
Our main application maps this contract to the `GeminiProvider` utilizing the `@google/genai` library and `gemini-3.5-flash` for lightweight, low-latency processing.
