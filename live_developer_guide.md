# Live Classes Platform — Developer Guide
**Sprint 22 — Phase 9 Documentation**

## 1. Directory Tree Organization
*   **Models**: [backend/apps/lms/models.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/models.py) (Declares `LiveClass` extensions and 12 live class models).
*   **Services**: [backend/apps/lms/services.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/services.py) (Business rules: `LiveClassService`).
*   **Selectors**: [backend/apps/lms/selectors.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/selectors.py) (Read queries: `LiveClassSelector`).
*   **Views**: [backend/apps/lms/views.py](file:///c:/Users/USER/Downloads/bramhavi%20(3)/backend/apps/lms/views.py) (Rest controllers).
*   **Gateway**: [server.ts](file:///c:/Users/USER/Downloads/bramhavi%20(3)/server.ts) (Route maps: `PATH_MAP`).
*   **UI Components**: [src/components/live/LiveDashboard.tsx](file:///c:/Users/USER/Downloads/bramhavi%20(3)/src/components/live/LiveDashboard.tsx).

## 2. Setting Up Third-Party Video Streams
To integrate a custom WebRTC stream client (e.g. Jitsi / Zoom Web SDK):
1.  Extend the `stream_url` string inside `LiveClassService.schedule_live_class` to fetch meeting room creation hashes.
2.  Hook the meeting room identifiers into the Jitsi layout container inside `src/components/live/LiveDashboard.tsx`.
