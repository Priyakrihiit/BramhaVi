# Live Classes Platform — Sequence Diagrams
**Sprint 22 — Phase 9 Documentation**

## 1. Class Scheduled Event Flow

```mermaid
sequence_code
sequenceDiagram
    participant T as Teacher (Client)
    participant GW as API Gateway (Node)
    participant DJ as LMS Engine (Django)
    participant DB as Database
    
    T->>GW: POST /api/v1/live/live-classes/
    GW->>DJ: POST /api/v1/lms/live-classes/
    DJ->>DB: Save LiveClass (status=SCHEDULED)
    DJ->>DB: Save CalendarEvent (Triggered by Signals)
    DJ-->>GW: HTTP 201 Created
    GW-->>T: Scheduled Live Class JSON
```

## 2. Interactive Poll Casting Flow

```mermaid
sequence_code
sequenceDiagram
    participant S as Student (Client)
    participant GW as API Gateway (Node)
    participant DJ as LMS Engine (Django)
    participant DB as Database
    
    S->>GW: POST /api/v1/live/polls/{id}/vote/
    GW->>DJ: POST /api/v1/lms/polls/{id}/vote/
    DJ->>DB: Create PollVote
    DJ-->>GW: HTTP 200 OK
    GW-->>S: Vote Registered Response
```
