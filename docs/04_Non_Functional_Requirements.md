# Non-Functional Requirements - BrahmaVidya Galaxy

## 1. Performance & Latency Budgets (NFR-PERF)
- **Interactive Response Time**: All interactive visual elements (button clicks, menu expansions, drawer toggles) must provide responsive feedback under 50 milliseconds.
- **Initial Page Load**: The dynamic rendering core must load and display above-the-fold content in under 1.5 seconds under standard broadband conditions.
- **API Throughput**: The core API endpoints (such as fetching layout JSONs) must achieve a mean latency of less than 200 milliseconds under a concurrent load of up to 10,000 active sessions.
- **Dynamic Content Caching**: Active menus and layouts must implement high-performance caching (such as standard memory stores or Redis layers) to bypass database roundtrips for un-modified configurations.

---

## 2. Security & Compliance (NFR-SEC)
- **Token-Based Sessions**: The authentication system must utilize dual JWT architectures (short-lived Access Tokens paired with HttpOnly, secure Refresh Cookies) to prevent token theft.
- **Cross-Site Scripting (XSS) Prevention**: All user-authored content, dynamic Markdown, and text blocks must be sanitized using robust libraries (e.g., `DOMPurify` or standard server-side sanitizers) before rendering.
- **Cross-Origin Resource Sharing (CORS)**: Backend APIs must enforce strict CORS policies allowing requests only from trusted, whitelisted frontend origins.
- **Cryptographic Signatures**: Certificate hashes must be calculated using robust SHA-256 algorithms salt-encrypted with platform secrets.

---

## 3. Reliability & High Availability (NFR-REL)
- **System SLA**: The platform must aim for an annual availability rate of 99.95%, excluding scheduled maintenance windows.
- **Graceful Degradation**: If external API integrations fail (such as the Vidya AI gateway), the application must degrade gracefully by displaying helpful diagnostic feedback while preserving core LMS and course navigation states.
- **Double-Entry Financial Integrity**: The financial ledger must operate in strict transaction-safe boundaries. Any database error must rollback pending wallet transfers, maintaining structural integrity.

---

## 4. Accessibility (NFR-ACC)
- **WCAG 2.1 Compliance**: The client user interface must conform to the Web Content Accessibility Guidelines (WCAG) 2.1 Level AA standards.
- **Color Contrast Guidelines**: Elements in both light and dark themes must uphold strict contrast limits (minimum of 4.5:1 for standard body text and 3:1 for large display headings).
- **Keyboard Navigation**: All administrative visual options and student learning portals must support complete keyboard interaction (such as standard Tab indexing and Escape drawer closings).

---

## 5. Portability & Responsive Fluidity (NFR-PORT)
- **Responsive Display Framework**: The interface must adapt cleanly across standard screen profiles including smartphones (min: 360px width), tablets, laptops, and ultra-wide desktops.
- **Browser Compatibility**: The application must remain compatible with modern evergreen web browsers (Chrome, Edge, Safari, and Firefox) running on mainstream platforms (Windows, macOS, iOS, Android).
- **Offline Resiliency**: In-progress curriculum tracking and quiz states should utilize safe `localStorage` or `IndexedDB` sync channels to preserve user progress during intermittent connectivity drops.
