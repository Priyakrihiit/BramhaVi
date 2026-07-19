# BrahmaVidya Search: Frontend Developer Reference

This document details the React components layout, services, and routing setup for the BrahmaVidya Galaxy Unified Search Platform in the frontend workspace.

---

## 1. File Structure

All frontend search components and client integrations reside in:

```
src/
├── services/
│   └── searchApi.ts            # Search API Client SDK (query, autocomplete, rankings, facets)
└── components/
    └── search/
        ├── Autocomplete.tsx    # Dropdown for typeahead selections
        ├── SearchBar.tsx       # Query input field with autocomplete hooks
        ├── SearchResults.tsx   # Polymorphic matched list (indexed items render styles)
        ├── SearchFilters.tsx   # Facet sidebar checkbox selectors
        ├── SuggestionPanel.tsx # Related phrase suggestions & spellcheck correction alerts
        ├── TrendingPanel.tsx   # List of popular terms queries
        ├── RecentSearches.tsx  # User search history manager
        ├── AdvancedSearch.tsx  # Query scope and meta parameter configs
        ├── SearchAnalytics.tsx # Admin search metrics (totals, CTRs, dwell stats)
        ├── SearchAdmin.tsx     # Admin panel (boost config, pinning, synonym mappings)
        ├── SearchDashboard.tsx # Root shell coordinating analytics and admin views
        └── GlobalSearchView.tsx# Main SearchPage coordinating user queries
```

---

## 2. API Integration Layer (`searchApi.ts`)

The client library handles calls to our Django backend versioned endpoints at `/api/v1/search/`:
* **`query(q, index, type, facets, page)`**: Queries search documents with filters.
* **`autocomplete(q)`**: Fetches prefix completions.
* **`suggestions(q)`**: Fetches related queries.
* **`logClick(historyId, documentId, position)`**: Logs search CTR click tracking metrics.
* **`getHistory()` / `deleteHistory(id)`**: Manages user history.
* **`getPopular()` / `getAnalytics()`**: Aggregates popular search terms.
* **`getRankings()` / `createRanking(data)` / `deleteRanking(id)`**: CRUD for admin boosts and pinning rules.
* **`getFacets()` / `createFacet(data)` / `deleteFacet(id)`**: Dynamic facets configurations.
* **`getSynonyms()` / `createSynonym(data)` / `deleteSynonym(id)`**: Synonym mappings.

---

## 3. UI Component Specifications

### 1. `GlobalSearchView` (SearchPage)
* **Route:** `/search` (registered inside `App.tsx` matching portal path router layout).
* **Role:** Coordinates all search components. Shows filters, results, spellchecks, advanced options, and triggers admin dashboards.

### 2. `SearchBar` & `Autocomplete`
* **Debounced input:** Input queries are debounced (150ms delay) to call the autocomplete API and display completion listings inside the floating dropdown.

### 3. `SearchResults`
* **Polymorphic Render:** Renders items with Lucide index indicators based on `index_name` mapping (LMS Courses, CMS Articles, DAM Media, Marketplace Books, Portfolio Resumes/Jobs).
* **Click Logging:** Result selection records click indexes to calculate CTR feedback loops.

### 4. `SearchFilters`
* **Faceted Counting:** Lists options dynamically calculated by the backend based on document metadata keys, showing the counts next to each selection.

### 5. `SearchDashboard` (Administrative)
* **Access Control:** Restricted via `useAuthStore` checks to staff/superuser roles. Exposes stats, total charts, and override settings.
