# BrahmaVidya Search: Sequence Diagrams

This document maps sequence execution routes for key search platform procedures.

---

## 1. Search Query Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Client as React Client
    participant GW as Express Gateway (server.ts)
    participant View as Django View (views.py)
    participant DB as SQLite Cache (SearchCache)
    participant Rank as RankingService (services.py)

    Client->>GW: GET /api/v1/search/query/?q=python
    Note over GW: Log request & propagate trace headers
    GW->>View: Forward request
    View->>DB: Check cached MD5 hash entry
    alt Cache hit
        DB-->>View: Return cached JSON results
        View-->>GW: Return HTTP 200 OK
        GW-->>Client: Render search results
    else Cache miss
        View->>View: Run permission filter checks
        View->>Rank: Run RankingService.apply_ranking()
        Rank-->>View: Return scored & pinned documents
        View->>DB: Write computed JSON results to cache
        View-->>GW: Return HTTP 200 OK (with facets & spellcheck)
        GW-->>Client: Render search results
    end
```

---

## 2. Real-Time Indexing Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Creator as Content Author
    participant App as Platform Module (LMS/CMS)
    participant Sig as Search Signals (signals.py)
    participant Queue as Celery Background worker
    participant DB as SQLite (SearchDocument)

    Creator->>App: Save updated article details
    App->>App: Commit transaction
    App->>Sig: Trigger django post_save signal
    Sig->>Queue: Dispatch index_document_task.delay(id)
    Note over Queue: Load instance, calculate search vectors
    Queue->>DB: Save or update SearchDocument
    DB-->>Queue: Acknowledge write
```

---

## 3. Click Tracking CTR Feedback Loop

```mermaid
sequenceDiagram
    autonumber
    actor User as Platform User
    participant Client as React Client
    participant GW as Express Gateway
    participant View as Django View (click endpoint)
    participant DB as SQLite (SearchClick)

    User->>Client: Click result at index position 2
    Client->>GW: POST /api/v1/search/click/ (payload: doc_id, position)
    GW->>View: Forward request
    View->>DB: Create SearchClick record
    Note over DB: Scheduled Celery task aggregates CTR stats
    View-->>GW: Return HTTP 201 Created
    GW-->>Client: Acknowledge successful click log
```
