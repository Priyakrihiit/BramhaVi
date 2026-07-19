# Folder Structure Blueprint - BrahmaVidya Galaxy

## 1. Monorepo & Multi-App Directory Map
BrahmaVidya Galaxy organizes its code structure to enforce clean isolation between client rendering components, core API frameworks, database migrations, and testing tools.

```
/ (Project Root)
├── .env.example                # Blueprint for required system variables
├── package.json                # Project dependencies and script runner configurations
├── tsconfig.json               # Global TypeScript rules
├── server.ts                   # Core Express Application entrypoint
├── vite.config.ts              # Vite configurations for client bundling
├── metadata.json               # Applet definitions, permissions, and features
├── brahmavidya_db.json         # High-integrity local JSON DB state for development
│
├── /docs                       # Comprehensive Architectural and SRS Blueprints
│   ├── 01_SRS.md
│   ├── 02_BRD.md
│   ├── ...
│   └── 20_Milestone_Development_Plan.md
│
├── /src                        # Core Single Page Application Source
│   ├── main.tsx                # Client bundle mount point
│   ├── App.tsx                 # Core UI routing and master administrator dashboard
│   ├── types.ts                # Centralized TypeScript models and payload definitions
│   ├── index.css               # Global tailwind directive overrides
│   │
│   ├── /components             # Stateless and modular UI widgets
│   │   ├── DynamicIcon.tsx     # Maps dynamic Lucide keys to React components
│   │   ├── CertificateVerifier.tsx # Verifies dynamic signatures
│   │   ├── StudentPortal.tsx   # Learner workspace and lesson viewer
│   │   ├── ControlCenter.tsx   # Administrative dashboard
│   │   └── QuizPractice.tsx    # Interactive testing card
│   │
│   └── /lib                    # Helper libraries and utilities
│       └── utils.ts            # Common styling helpers
```

---

## 2. Directory Separation Rules

### 2.1 The `/src/components` Rule
- Components located in this folder must be modular and clean.
- They must not define custom state persistence layers. Instead, they consume data through React props or global Context providers.
- Components must implement standard `id` selectors on interactive elements to support proper styling and testing coverage.

### 2.2 The `/src/types.ts` Rule
- This file acts as the single source of truth for TypeScript types across the React platform.
- It defines enums (e.g., `CourseNodeType`) and interfaces (e.g., `LayoutBlock`) used by all modules.
- **Strict Separation**: Frontend components must import types from this shared directory rather than declaring inline overrides, preventing drift.

### 2.3 The `/docs` Rule
- The `/docs` directory is reserved solely for system blueprints, API contracts, deployment instructions, and user user-stories.
- Product documents must remain version-controlled and synchronized alongside respective codebase iterations to prevent drift.
