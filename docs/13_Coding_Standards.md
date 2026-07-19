# Coding Standards - BrahmaVidya Galaxy

## 1. Code Quality & Formatting Policies
- **Formatting Tools**: All files must conform to standard code spacing. ESLint and Prettier rules must be run prior to committing code.
- **Imports**: Place named imports grouped cleanly at the top of code files:
```typescript
import React, { useState, useEffect } from 'react';
import { Tag, BookOpen } from 'lucide-react';
```
- **File Modularity**: Single source code files must not exceed 500 lines of code. Large components must be extracted into modular sub-files within `/src/components/` to prevent maintenance drift and token bloat.

---

## 2. TypeScript and Strict Type Safety
BrahmaVidya Galaxy enforces rigid TypeScript policies to guarantee compiler-time safety:
- **No Implicit `any`**: Explicit types must be declared for all components, helpers, and handlers. Resorting to `any` is strictly prohibited.
- **Named Import Structure**: Named component imports must be preferred over full namespace or object destructuring imports:
```typescript
// Good Pattern
import { CheckCircle } from 'lucide-react';

// Bad Pattern
import * as LucideIcons from 'lucide-react';
```
- **Type Casting**: Safe type declarations (`as PageForm` or type guards) must be preferred over unsafe conversions.

---

## 3. React Development Principles
- **Functional Components**: All views and modular layout elements must be authored as React Functional Components (`React.FC<Props>`) using modern hooks. Class components are prohibited unless required by library constraints.
- **Static Hook Dependency Arrays**: dependency arrays in `useEffect` and `useMemo` hooks must be restricted to stable primitive parameters (e.g., strings, numbers, booleans) to prevent infinite render loops. Arrays and object structures must not be passed into hook dependency arrays.
- **No DOM Manipulation**: Manual selector modifications (e.g., `document.getElementById`) are forbidden. React state models or referenced elements (`useRef`) must be used exclusively.
- **Unique ID Seeding**: Meaningful interactive elements (cards, inputs, submit triggers) must include unique `id` properties to support standard visual styling and testing suites.

---

## 4. Documentation & Comments
- **Context Comments**: Every complex function or dynamic API client call must be preceded by explanatory JSDoc headers summarizing parameter types and return contracts.
- **Code Clarity Over Complicated Hacks**: Write clear, human-readable code. Over-engineering simple utilities to look "clever" is discouraged. Keep systems simple and robust.
