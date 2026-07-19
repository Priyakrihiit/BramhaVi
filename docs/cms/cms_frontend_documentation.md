# CMS Frontend Documentation

This document describes the Enterprise CMS portal components and API integration implemented in the frontend of BrahmaVidya Galaxy.

---

## 1. API Services (`src/services/cmsApi.ts`)

The React application uses a unified API client [cmsApi.ts](file:///c:/Users/USER/Downloads/bramhavi/src/services/cmsApi.ts) that integrates with backend REST services:
- **Articles**: CRUD, publish, unpublish, preview rendering, dynamic publish scheduling, bulk publication, and bulk deletion.
- **Categories & Tags**: CRUD operations with custom taxonomy properties.
- **Workflow State**: Progression checks, transitions, and due-date assignments.
- **Editorial Revisions**: Rollbacks and save-point audits.
- **Search Indices & FAQs**: Search queries, Q&A CRUD, and restore checkpoints.

---

## 2. Integrated Dashboard Hub (`EnterpriseCMSShell.tsx`)

All CMS workspaces are loaded under a unified coordinator portal [EnterpriseCMSShell.tsx](file:///c:/Users/USER/Downloads/bramhavi/src/pages/admin/EnterpriseCMSShell.tsx):

| Tab View Component | File Location | Purpose / Features |
| :--- | :--- | :--- |
| **CMSDashboard** | `CMSDashboard.tsx` | Visualizes telemetry charts, traffic counts, and system status logs. |
| **PageBuilder** | `PageBuilder.tsx` | Draggable grid layouts and reusable content block template selectors. |
| **ArticleEditor** | `ArticleEditor.tsx` | Draft editors, publish toggles, scheduling, and bulk actions. |
| **BlogEditor** | `BlogEditor.tsx` | Increments views and edits blog metadata. |
| **MediaLibrary** | `MediaLibrary.tsx` | Drag-and-drop file upload, copies URLs, and triggers deletion. |
| **CategoryManager** | `CategoryManager.tsx` | Organizes taxonomies and restores soft-deleted entries. |
| **TagManager** | `TagManager.tsx` | Organizes tag index maps. |
| **WorkflowManager** | `WorkflowManager.tsx` | Workflow state transitions. |
| **RevisionHistory** | `RevisionHistory.tsx` | Triggers database rollbacks for article updates. |
| **SEODashboard** | `SEODashboard.tsx` | Monitors sitemaps and triggers metadata regenerators. |
| **CMSSettings** | `CMSSettings.tsx` | Caches controls and toggles automatic cleanups. |
| **CommentModeration** | `CommentModeration.tsx` | Flag and moderate comments. |
| **Search** | `Search.tsx` | Direct queries the search indexes database. |
| **FAQManager** | `FAQManager.tsx` | Organizes public Q&As. |

---

## 3. Sidebar Integration

The CMS Workspace is mapped to the sidebar control menu:
- **Label**: Enterprise CMS Hub
- **Path**: `/admin/cms`
- **Icon**: `FolderOpen`
