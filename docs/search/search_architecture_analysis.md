# Enterprise Search Architecture Analysis

This document details the architectural findings, search indices, and design parameters for building the Unified Enterprise Search Platform across BrahmaVidya Galaxy's ecosystem (LMS, CMS, DAM, Marketplace, etc.).

---

## 1. Existing Search Infrastructure Identification

### A. Current Indexing & Models
- **Database Model**: `CMSSearchIndex` in [models.py:L1064-1102](file:///c:/Users/USER/Downloads/bramhavi/backend/apps/cms/models.py#L1064-L1102).
- **Current Scope**: Only stores index records for CMS content (`article`, `blog`, `page`, `tutorial`, `faq`).
- **Storage Strategy**: Local SQLite indexes mapping to canonical URL paths.

### B. Current Search Logic
- **Search Logic (`SearchService`)**: Defined in [services.py:L782-830](file:///c:/Users/USER/Downloads/bramhavi/backend/apps/cms/services.py#L782-L830).
- **Mechanism**:
  - Uses multi-field case-insensitive substring search (`icontains`).
  - Implements relevance-aware ordering using custom annotations (giving higher weight to matches in titles than in excerpt or body).
  - Integrates with Celery async re-indexing task runners.

---

## 2. Reusable Components & Architecture Upgrades

### A. Reusable Indexing Framework
- Celery's `index_single_content_task` task structure in `tasks.py` can be extended to listen to post-save signals across LMS courses, Marketplace listings, and User resumes.

### B. Missing Search Scopes
- **LMS**: Courses, Lessons, and Assignments.
- **DAM**: Image tags, PDF text extraction, and video metadata.
- **Marketplace**: Books, assets, and service listings.
- **Resume/Jobs**: Profile tags, titles, and job requirements.

---

## 3. Storage, Ranking & AI Opportunities

### A. Scaling Database Indexes
- **PostgreSQL Upgrade**: Target using PostgreSQL `GIN` vector indexes (`SearchVector`, `SearchQuery`, `SearchRank`) to enable lexical scoring natively on database servers.

### B. Security & Scope Gating
- Gating indexes to enforce RBAC permissions (e.g. users should not see private course contents, draft articles, or restricted files in global search).

### C. Future AI Search Opportunities
- **Vector Embeddings**: Generate text embeddings for titles and bodies using Gemini API embeddings (`text-embedding-004`).
- **Semantic Search**: Store vector vectors inside a vector-compatible DB adapter (e.g. pgvector) to enable semantic matching bypassing exact keyword matching.
