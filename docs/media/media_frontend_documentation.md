# Enterprise DAM React Frontend Documentation

This document describes the design, API mappings, and structure of BrahmaVidya Galaxy's Enterprise Digital Asset Management (DAM) interface.

---

## 1. API Client Mapping (`mediaApi.ts`)

The React application communicates with backend DAM services using a centralized fetch-based client wrapper:

- **Folders**: Handles folder listings, creation, and deletion via `folders` endpoint groups.
- **Collections**: Manages logical collections grouping across folders.
- **Media Files**: Manages file creation using `FormData` uploads, deletes, and action hooks (`favorite`, `download`, `share`).
- **Workflow State**: Monitors state workflows and processes approvals/revisions transitions.

---

## 2. Component Hierarchy & Interfaces

All features are bundled into a premium, responsive dashboard widget:

- **Folder Tree Manager (`FolderManager`)**: Rendered in the left sidebar to support nested folder directories and collections filtering.
- **Summary Metrics Dashboard (`MediaDashboard`)**: A summary bar highlighting asset counts, total storage, and type distributions.
- **Asset Toolbar (`MediaSearch`)**: A search bar filter coordinating text search query parameters.
- **Asset Grid (`MediaLibrary` Upgraded)**: A clean image/video card grid featuring tag badges and anti-virus scan status logs.
- **Side Drawer Inspector (`AssetInspector`)**: Displays filename, UUID identifiers, size metadata, alt text, and action links.
