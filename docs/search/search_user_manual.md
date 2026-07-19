# User Manual: Unified Enterprise Search Platform

This manual guides standard platform users on executing searches, filtering results, and managing their history.

---

## 1. Finding Content

Access the search interface by navigating to `/search` in the application header menu.

### Running a Query
* Type keywords into the query bar (e.g. `python`).
* The system displays matching typeahead completions under the input bar. Click a completion to run the query immediately.
* Press `Enter` or click **Search** to run a query.

### Spelling Suggestions
If a keyword is misspelled (e.g. `pythn`), the system will display a helpful message:
`Did you mean: python?`
Click the suggested term to run a search for it.

---

## 2. Refining Results

### 1. Sidebar Filters (Facets)
After running a query, the sidebar displays filters dynamically populated based on metadata keys (e.g. categories, tags). Check options to filter results dynamically without hitting the database again.

### 2. Target Index (Scope Limiters)
Under **Advanced Options**, you can scope search to specific modules:
* LMS Courses
* CMS Articles / Blogs
* Bookstore / Textbooks
* Portfolios / Resumes / Jobs
* AI conversations / Prompt templates

---

## 3. History Management

Under **Recent Searches**, you will see a list of your recent search terms.
* Click a term to re-run the search.
* Hover over a term and click the **Trash** icon to delete it from your search history.
