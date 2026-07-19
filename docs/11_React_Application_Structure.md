# React Application Structure - BrahmaVidya Galaxy

## 1. Front-End Core Canvas Architecture
BrahmaVidya Galaxy's frontend is engineered as a metadata-driven shell. The React engine loads structural instructions from API responses and binds those properties dynamically.

```
       +-------------------------------------------------------+
       |                  React Entrypoint                     |
       |                     (main.tsx)                        |
       +-------------------------------------------------------+
                                  ||
                                  \/
       +-------------------------------------------------------+
       |                     App Shell                         |
       |                     (App.tsx)                         |
       +-------------------------------------------------------+
                                  ||
         +------------------------+------------------------+
         ||                                                ||
         \/                                                \/
+------------------+                              +------------------+
| Context Managers |                              |  Router Core     |
| - AuthContext    |                              |  (React Router)  |
| - CMSContext     |                              +------------------+
| - LMSContext     |                                       ||
+------------------+                                       \/
                                                  +------------------+
                                                  |  Dynamic Pages   |
                                                  |  - Public Canvas |
                                                  |  - Admin Control |
                                                  |  - LMS Portals   |
                                                  +------------------+
```

---

## 2. Dynamic Block Page Renderer
Our custom core layout engine maps backend layout blocks dynamically to specialized visual components:

```typescript
// Example dynamic mapping engine in /src/components/PageRenderer.tsx
import React from 'react';
import { LayoutBlock } from '../types';
import HeroBlock from './blocks/HeroBlock';
import StatsGridBlock from './blocks/StatsGridBlock';
import FeaturesGridBlock from './blocks/FeaturesGridBlock';

interface RendererProps {
  blocks: LayoutBlock[];
}

export const PageRenderer: React.FC<RendererProps> = ({ blocks }) => {
  return (
    <div className="space-y-12">
      {blocks.map((block) => {
        switch (block.type) {
          case 'HERO':
            return <HeroBlock key={block.id} data={block.properties} />;
          case 'STATS_GRID':
            return <StatsGridBlock key={block.id} data={block.properties} />;
          case 'FEATURES_GRID':
            return <FeaturesGridBlock key={block.id} data={block.properties} />;
          default:
            return (
              <div className="p-4 rounded border border-rose-500/30 bg-rose-950/20 text-rose-300 text-xs">
                Unknown content block type: {block.type}
              </div>
            );
        }
      })}
    </div>
  );
};
```

---

## 3. Strict Frontend Rules

### 3.1 State Isolation Policy
- React state must only represent client UI settings (e.g., toggle states, editing forms, input properties).
- Core metadata parameters (e.g., available courses, active menu options, security settings) must be sourced from context states and refreshed when actions complete.

### 3.2 Dynamic Component Imports
- Large dashboard components (such as `ControlCenter`) or intensive modules (such as `CertificateVerifier` or code editors) must be loaded dynamically using React's lazy loading engine to ensure optimal page speed for our students:
```typescript
const ControlCenter = React.lazy(() => import('./components/ControlCenter'));
```

### 3.3 Visual Identity and Transitions
- Page route switches and layout changes must utilize standard `motion` transitions (imported from `motion/react`) to elevate the user experience. 
- All dynamic elements must include appropriate exit transitions to guarantee fluid visuals.
