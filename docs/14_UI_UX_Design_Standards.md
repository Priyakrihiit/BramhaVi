# UI/UX Design Standards - BrahmaVidya Galaxy

## 1. Visual Identity and "Cosmic Slate" Styling Theme
BrahmaVidya Galaxy incorporates a custom, professional, high-integrity "Cosmic Slate" aesthetic. No default generic UI gradients are allowed. 

### 1.1 Palette Specifications
The application uses a high-contrast dark palette with rich accents for administrative controls, while dynamic public elements adapt dynamically to clean corporate configurations:
- **Primary Background**: Deep Navy/Charcoal Slate (`bg-slate-950`).
- **Surface Panels**: Styled Slate (`bg-slate-900`, `border-slate-850`).
- **Interactive Accents**: Elegant Indigo (`text-indigo-400`, `bg-indigo-600`) and Warm Amber warnings.
- **Academic Highlights**: Gold/Amber typography matching intellectual excellence.

---

## 2. Typography Hierarchy
The application loads polished typefaces to communicate intellectual authority and clarity:
- **Primary Typography**: **Inter** (sans-serif) for general UI options, cards, and input values.
- **Display Headings**: **Space Grotesk** or **Outfit** for system titles, headers, and dashboard metrics.
- **Technical Elements**: **JetBrains Mono** or **Fira Code** for system telemetry, code values, certification codes, and metadata indicators.

| Element | Typeface | Tailwind Utility | Purpose |
| :--- | :--- | :--- | :--- |
| **System Headings** | Space Grotesk | `font-sans font-bold tracking-tight text-slate-100` | Major headers, Page Titles |
| **Section Labels** | Inter | `font-sans font-semibold text-slate-300 text-sm` | Card headers, sidebar options |
| **Standard Body** | Inter | `font-sans text-slate-400 text-xs leading-relaxed`| General content, reading texts |
| **Metadata Labels**| JetBrains Mono | `font-mono text-[10px] text-slate-500 uppercase` | Identifiers, dates, logs |

---

## 3. Visual Density & Sizing Guidelines
- **Touch and Click Targets**: Interactive elements (buttons, links, checklist options) must preserve a minimum area of `44px x 44px` on mobile platforms.
- **Outer Margins**: General site panels and cards must contain spacious margins:
  - Mobile profiles: `p-4` or `p-5` spacing bounds.
  - Large desktops: `p-8` spacing bounds.
- **Aesthetic Pairings over Margin Clutter**: To prevent visual noise, marginal layouts must remain clean. Status indicators (e.g., "Online") must be small and subtle, avoiding large banners or terminal logging widgets.

---

## 4. Animation and Micro-interactions
To guide learner focus, visual transitions must be purposeful:
- **Page Entrances**: Fade-in transitions with subtle vertical drift:
  - Framer Motion: `initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}`.
- **Interactive States**: Smooth interactive hover adjustments:
  - Tailwind: `transition-all duration-300 hover:scale-[1.01]`.
- **Exit Transitions**: Always specify structural exits to prevent visual jumps. Grids and list rows must slide smoothly upon deletions or changes.
