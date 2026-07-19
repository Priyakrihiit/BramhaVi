# Functional Requirements - BrahmaVidya Galaxy

## 1. CMS Engine & Dynamic Page Builder (FR-CMS)

### FR-CMS-1: Dynamic Layout Grid
- The page rendering core must parse a JSON array of `LayoutBlock` components.
- Supported block schemas must include:
  - `HeroBlock`: Main banner with customizable titles, text, CTA buttons, background assets, and visual alignments.
  - `StatsGridBlock`: Numeric grid visualizing high-impact statistics with custom icons.
  - `FeaturesGridBlock`: Multicolumn layout highlighting system capabilities, cards, and transitions.
  - `CurriculumExplorerBlock`: Interactive, visual explorer of active curricular paths.
  - `CertVerifierBlock`: Interactive interface for scanning/pasting certificate verification codes.

### FR-CMS-2: Visual SEO Preview Utility
- The administrator page editor must render a real-time snippet simulation mimicking major search engines (e.g., Google).
- The snippet simulation must update instantly upon modifying:
  - Page URL / Slug
  - SEO Title override (or fallback to normal title)
  - SEO Meta Description
  - SEO Keywords
- The visual simulation must support device toggles (Desktop vs. Mobile widths) and color toggles (Light vs. Dark themes).
- The utility must provide diagnostic character counters for Titles (optimal: 50-60 chars) and Descriptions (optimal: 110-160 chars) with semantic progress bars and clear diagnostic notices.
- The utility must display a 'Keywords' count and a tag-based visual representation (Meta Keywords Ledger) of comma-separated SEO tags.

---

## 2. Dynamic Navigation System (FR-NAV)

### FR-NAV-1: Recursive Navigation Tree
- The navigation framework must dynamically fetch menu items from the `/api/menus` backend.
- It must support nested lists (menus and submenus) to arbitrary depths.
- Each navigation node must contain a title, link/URL, representative Lucide icon string, and displaying order.

### FR-NAV-2: Condition-Based Access
- The rendering engine must filter visible menu options based on the active user session.
- Menu items can require specific permission strings (e.g., `MENU_WRITE` or `FINANCE_READ`). Users missing these credentials must not see or access the menu node.

---

## 3. Dynamic Course & Content Engine (FR-LMS)

### FR-LMS-1: Six-Tier Curriculum Hierarchy
- The course structure must be modeled recursively to support a 6-tier educational ladder:
  1. **Programs**: Comprehensive organizational buckets (e.g., School of Engineering).
  2. **Degrees/Paths**: Career tracks or certification paths.
  3. **Courses**: Individual learning subjects.
  4. **Modules**: Sequential learning sections within a course.
  5. **Lessons**: Individual learning sessions containing educational pages.
  6. **Tasks/Quizzes**: Assessment nodes to test user knowledge.

### FR-LMS-2: Progress & State Synchronization
- The LMS must track student progress percentages in real time across all structure nodes.
- When a student completes a Task or Lesson, progress must cascade upwards to recalculate parent course and program completion metrics.

---

## 4. Cryptographic Certificate Engine (FR-CERT)

### FR-CERT-1: Custom Visual Templates
- System administrators must be able to visually customize certification parameters including recipient name margins, text sizing, border spacing, and background branding.

### FR-CERT-2: Cryptographic Hash and QR Code Ledger
- Upon programmatic course completion, the system must generate a unique cryptographic hash combining the `recipient_id`, `course_id`, and a secure signature.
- The system must render a dynamic, scannable QR code directing users to a high-integrity verification route (`/verify/:hash`).
- Anyone globally must be able to visit `/verify/:hash` to authenticate the credential against the ledger.

---

## 5. Vidya AI Gateway (FR-AI)

### FR-AI-1: Dynamic AI Course Architect
- In the Course Builder, entering a course topic and clicking "Generate Syllabus" must trigger a server-side API call to the Vidya AI gateway.
- The gateway must prompt the Gemini model (using `@google/genai` and `gemini-3.5-flash`) to generate structured JSON conforming exactly to the LMS curriculum schema.

### FR-AI-2: Interactive Assessment Generator
- Instructors can click "Generate Quiz" on any Lesson node.
- The AI must analyze the lesson metadata and output formatted quiz questions (multiple choice, explanation text) which can be inserted directly into the curriculum tree.

---

## 6. Financial Ledger & Wallet Engine (FR-FIN)

### FR-FIN-1: Wallet Tracking and Balance Logs
- The system must provide custom digital wallet states for Instructors, School Operators, and Students.
- Every monetary exchange (purchasing, commission routing, withdrawals) must be recorded in a double-entry ledger to prevent balancing issues.
- The platform must split course purchase fees instantly between the platform treasury and the corresponding teacher's wallet.
