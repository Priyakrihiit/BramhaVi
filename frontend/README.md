# Frontend Application - BrahmaVidya Galaxy

This directory houses the presentation layer SPA for **BrahmaVidya Galaxy**, built using React, Vite, Tailwind CSS, Lucide icons, and Framer Motion.

## Directory Structure & Purpose

- **`public/`**: Serves static media assets, global icons, vector backgrounds, and verification template images.
- **`src/assets/`**: Uncompiled frontend media variables, fonts, stylesheet extensions.
- **`src/components/`**: Modular, atomic, and state-agnostic UI widgets (e.g., custom buttons, interactive cards, dynamic icons).
- **`src/context/`**: State coordinate clusters orchestrating session values (`AuthContext`), navigation paths (`CMSContext`), and course trackers (`LMSContext`).
- **`src/hooks/`**: Custom functional wrappers binding interactive utility behaviors (e.g., real-time SEO counters, AI query controllers).
- **`src/services/`**: API brokers mapping visual events to transactional backend REST calls.
- **`src/types/`**: Enforces strict TypeScript models matching API JSON schemas.

---

## Architectural Principles
1. **Zero Static Content**: Front-end components read layout nodes, active courses, user permissions, and custom elements dynamically from the backend APIs.
2. **Accessible Execution**: Designs strictly enforce contrast ratios and fully support standard key-navigation indices.
