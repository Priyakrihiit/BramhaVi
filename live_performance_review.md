# Live Classes Platform — Performance Review
**Sprint 22 — Phase 9 Documentation**

## 1. Caching Strategies
*   Active classroom participant lists are stored in Redis under the `liveclass_active_attendees_{id}` cache key with a 600-second expiration.
*   This avoids repetitive, expensive aggregate DB queries while streaming.

## 2. Asynchronous Offloading (Celery Tasks)
*   High-overhead tasks are offloaded to background Celery workers:
    -   `compile_class_recording_task` (Archiving MP4 file sizes).
    -   `generate_ai_class_summary` (AI summarization queries).
*   Prevents blocking client response cycles on session terminations.

## 3. Network Optimization
*   Collaborative whiteboards draw drawing coordinate packets, keeping payload overhead below 1KB per transmission.
