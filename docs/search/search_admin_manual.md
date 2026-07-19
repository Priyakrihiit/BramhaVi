# Administrator Manual: Unified Enterprise Search Platform

This manual guides search platform administrators on managing search configurations, synonyms, document boosts, and monitoring click metrics.

---

## 1. Entering the Admin Panel

If your user account has administrator privileges (is marked staff), you will see an **Admin Panel** toggle button at the top right of the `/search` page.
Click this button to open the **Search Control Center**.

---

## 2. Search Performance & CTR Analytics

The **Analytics** tab displays cards summarizing key telemetry metrics:
* **Total Queries logged:** The aggregate number of query operations.
* **Average Click CTR:** Click-through-rate percentage calculated from clicked results.
* **Avg Result Dwell:** Average time (in seconds) users spend looking at clicked results.
* **Query Performance Report:** A table listing each search term, total searches, returned results, and CTR percentages. Use this to identify queries with low CTR that could benefit from synonym mappings or ranking boosts.

---

## 3. Configuration Management

### 1. Active Rankings overrides (Pins & Boosts)
Modify search result placement for specific queries:
* **Pin result:** Force a document to appear at the very top of search results.
* **Boost score factor:** Multiply a document's relevance score by a boost factor (e.g. `2.5`) to move it higher in search results.
* Enter the **Document UUID** (from search result items), target **Trigger Query Term**, select **is_pinned** or boost factor, and click **Add Override**.

### 2. Synonym Mappings
Map equivalent terms to expand search coverage:
* **Primary Term:** The base search keyword (e.g. `exam`).
* **Equivalent terms:** Comma-separated synonyms (e.g. `test, quiz, assessment`).
* Click **Add Synonym Set** to register.

### 3. Dynamic Facets configuration
Register metadata keys that should be aggregated:
* **Display label:** Visual header (e.g. `Difficulty Level`).
* **Field Key:** Metadata JSON path key (e.g. `level`).
