# Implementation Plan: Desktop Console UI/UX Refinement (Calm Enterprise Operations)

## 1. Executive Summary & Design Vision

### 1.1 Context & Problem Statement
The current desktop console layout implemented macOS window controls and dark theme styling, but retains residual visual artifacts often associated with decorative "AI/sci-fi" dashboards:
- Heavy frosted glass blur (`backdrop-filter: blur(24px)` to `blur(28px) saturate(190%)`).
- Saturated neon glowing filters and drop shadows (`#glow`, `#hubGlow`, heavy cyan/blue text glows).
- Inconsistent corner radii with excessive pill-shaped buttons and tags (`border-radius: 9999px`).
- Decorative card layouts in the Agent Command center rather than structured operational tables.
- Stylized node maps with pulsing circles rather than precise, high-contrast schematic diagrams.

### 1.2 Core Design Direction (Per `docs/desktop_console_ui_update.md`)
The revised design language establishes a composed, credible, analytical, and dependable enterprise operations console:
- **Brand Essence**: "Complexity, connected. Decisions, coordinated." Intelligence is conveyed through information hierarchy, evidence presentation, and operational comparison tools, rather than decorative visual effects.
- **Brand Palette**:
  - `brand.navy`: `#0B2545` (Primary identity, selected navigation emphasis, headings in brand moments)
  - `brand.blue`: `#0E82D6` (Interactive accent, focus, links, selection, primary actions)
  - `brand.teal`: `#16A67E` (Positive resolution, resilience, successful outcomes)
  - `brand.slate`: `#CBD5E1` (Neutral supporting detail, dividers, inactive visual structure)
- **Materials**: Opaque or lightly-tinted neutral surfaces (`surface.canvas: #11161D`, `surface.panel: #1B232E`, `surface.sidebar: #171D26`), thin solid boundaries (`border.default: #303B49`), and restrained elevation.
- **Typography & Layout**: System font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`), tabular numerals for aligned metrics, strict 8px base spacing grid, disciplined radius scale (`6px` controls, `9px` cards, `12px` panels), and zero emojis across the entire project.

---

## 2. Phased Implementation Roadmap (U1 through U6)

```
[ Phase U1: Shared Design Tokens & Core Materials ]
                     │
                     ▼
[ Phase U2: Global Shell, Navigation & Settings ]
                     │
                     ├─────────────────────────────────────┐
                     ▼                                     ▼
[ Phase U3: Operations Overview & Clean Topology ]    [ Phase U4: Decision Center & Scenario Launcher ]
                     │                                     │
                     └──────────────────┬──────────────────┘
                                        ▼
           [ Phase U5: Agent Command, What-If Lab, Traces & Evaluation ]
                                        │
                                        ▼
           [ Phase U6: Quality Gate, Accessibility, Build Verification ]
```

### 2.1 Non-Functional Boundaries & Functional Preservation Policy
To ensure zero disruption to core system mechanics, the following architectural invariants are strictly enforced:
1. **Zero Backend Alterations**:
   - No modifications to any backend microservice (`services/coordinator`, `services/api`, `services/specialists`, `services/simulation`, `services/evaluation`).
   - No changes to Docker configurations, PostgreSQL tables (`scof.*`), Neo4j graph schemas, Redis caches, or Kafka topic event buses.
2. **API Client & Hook Contract Preservation**:
   - All `ApiClient` endpoint signatures, payload types, and error handling contracts remain 100% frozen.
   - Custom state hooks (`useDecisions`, `useAgentActivity`, `useConnection`, `useDashboardState`) retain identical WebSocket and polling logic.
3. **Execution & Navigation Invariance**:
   - Scenario triggering continues to publish events to Kafka with unique `event_id` and `trace_id`.
   - What-If counterfactual computations execute the verified mathematical matrix with INR currency formatting.
   - Keyboard hotkeys (`Ctrl+1` to `Ctrl+7`, `Shift+?`, `Esc`) remain functionally bound to view navigation.

### 2.2 Three-Tier Verification Check Framework
Every UI refinement phase must pass three automated verification gates:
- **Tier 1 (API & Services Health)**: `curl.exe -s http://localhost:8000/health` confirming HTTP 200 and operational availability.
- **Tier 2 (Multi-Agent E2E Verification)**: `python scripts/verify_scenario_suite.py` validating 25-scenario catalog integrity, predictive matrix computation, and disruption dispatch.
- **Tier 3 (Frontend Compilation)**: `npm run build` in `desktop/` validating 0 TypeScript errors and clean Vite production bundling.

---

## 3. Detailed Work Breakdown Structure

### Phase U1: Shared Design Tokens, Reset & Material Foundation (COMPLETED)
- **Status**: Completed & Verified
- **Target File**: `desktop/src/index.css`
- **Scope & Objectives**:
  1. Replaced Apple frosted-blur variables with canonical tokens from Section 3.2 and 3.3 of `docs/desktop_console_ui_update.md`:
     - Surfaces: `--surface-canvas` (`#11161D`), `--surface-sidebar` (`#171D26`), `--surface-panel` (`#1B232E`), `--surface-raised` (`#222C39`), `--surface-subtle` (`#252F3C`).
     - Text: `--text-primary` (`#F2F5F8`), `--text-secondary` (`#AAB6C4`), `--text-muted` (`#8492A3`).
     - Borders: `--border-default` (`#303B49`), `--border-strong` (`#455264`).
     - Interactive: `--interactive-primary` (`#45A9F3`), `--interactive-hover` (`#1B354A`).
     - Status: `--status-success` (`#48C69A`), `--status-warning` (`#E9B45C`), `--status-critical` (`#F0747E`), `--status-info` (`#45A9F3`).
     - Brand accents: `--brand-navy` (`#0B2545`), `--brand-blue` (`#0E82D6`), `--brand-teal` (`#16A67E`), `--brand-slate` (`#CBD5E1`).
  2. Normalized geometric corner radii:
     - `--radius-sm`: `6px` (small controls, input fields, badges)
     - `--radius-md`: `9px` (standard cards, metric tiles)
     - `--radius-lg`: `12px` (inspector sheets, modal windows)
     - Removed `--radius-full: 9999px` to prevent pill-shaped overuse.
  3. Enforced 8px grid spacing scale: `--space-1` (`4px`), `--space-2` (`8px`), `--space-3` (`12px`), `--space-4` (`16px`), `--space-6` (`24px`), `--space-8` (`32px`), `--space-12` (`48px`).
  4. Standardized typography:
     - Set `font-variant-numeric: tabular-nums` across tables, metrics, and timestamps.
     - Eliminated heavy letter-spacing and all-caps styling on general headings.
  5. Removed decorative blur filters and continuous animations.
  6. Provided backward-compatible transitional aliases to maintain visual stability across all views.

---

### Phase U2: Global Desktop Shell, Clean Sidebar, TopBar & Settings Dialog (COMPLETED)
- **Status**: Completed & Verified
- **Target Files**:
  - `desktop/src/components/layout/Sidebar.tsx` & `Sidebar.module.css`
  - `desktop/src/components/layout/TopBar.tsx` & `TopBar.module.css`
  - `desktop/src/components/modals/SettingsModal.tsx` & `SettingsModal.module.css`
  - `desktop/src/components/modals/ShortcutsModal.tsx` & `ShortcutsModal.module.css`
  - `desktop/src/App.tsx` & `App.css`
- **Scope & Objectives**:
  1. **Sidebar Navigation**:
     - Replaced saturated active state with calm surface highlight: `var(--surface-raised)` with thin `var(--brand-blue)` indicator bar and primary text weight.
     - Implemented 7 canonical navigation items with keyboard hotkey chips (`Ctrl 1` to `Ctrl 7`).
     - Replaced non-standard window traffic symbols with clean ASCII characters (`x`, `-`, `+`).
     - Added clean operations footer with A2A protocol live indicator, `MVP-ELECTRONICS` domain badge, and Settings button.
  2. **TopBar Header**:
     - Removed frosted blur filter (`backdrop-filter: blur(20px)`), replacing with solid `--surface-canvas` and `--border-default`.
     - Integrated dynamic view titles, active domain profile badge (`MVP-ELECTRONICS`), real health check connection status, and tabular numerals UTC clock.
     - Retained shortcuts HUD trigger (`?`).
  3. **Settings Dialog**:
     - Created `SettingsModal.tsx` with tabs: Diagnostics (gateway, ports, brokers), Active Profile (Peninsular India electronics corridor specifications), Shortcuts, and Platform About.
     - Wired up dialog state in `App.tsx` with `Esc` dismiss and backdrop click handler.
  4. **Verification Gates Passed**:
     - Tier 1: Health check OK (`http://localhost:8000/health`).
     - Tier 2: Scenario Suite Verification (`scripts/verify_scenario_suite.py`) passed 100%.
     - Tier 3: TypeScript and Vite build passed in 871ms with 0 errors.
     - Zero-emoji scan: 0 flagged characters.

---

### Phase U3: Operations Overview & High-Tech Topology Schematic
- **Target Files**:
  - `desktop/src/views/Operations/OperationsView.tsx` & `Operations.module.css`
- **Scope & Objectives**:
  1. **Operational KPI Tiles**:
     - Restructure into 4 disciplined cards: Supply Chain Reliability, Inventory Stock Coverage, At-Risk Demand Value, Active Disruptions.
     - Clear numeric values with tabular numerals and comparison benchmarks (e.g. `18.4 d` vs `14.0 d safety threshold`).
     - Remove decorative gradient backgrounds.
  2. **Active Alert & Disruption Queue**:
     - Replace stylized cards with a clean operational alert table (ID, Severity, Target Facility, Disruption Type, Est. Impact, Action Status).
  3. **Peninsular India Supply Topology Schematic**:
     - Remove SVG neon glow filters (`#glow`, `#hubGlow`) and pulsating outer rings.
     - Replace corridor paths with clean, crisp lines:
       - NH48 Freight Spine: Solid 2.5px `var(--brand-blue)`.
       - FTWZ Bonded Connector: Solid 2px `var(--brand-navy)` / deep slate violet.
       - Finished Goods Export Lanes: Clean 2px `var(--brand-teal)`.
       - Feeder Lanes: 1.5px dashed `var(--border-strong)` with 4px dash spacing.
     - Replace nodes with sharp, unblurred geometric shapes:
       - Assembly Hub (`mfg-01`): Clean rounded square (amber accent border, dark solid fill).
       - Suppliers (`sup-01` to `sup-08`): Clean circular nodes with solid core.
       - Buffer Warehouses (`wh-01` to `wh-04`): Clean rounded rectangles.
       - Multimodal Gateways (`dc-01` to `dc-03`): Crisp double-ring bullseye.
     - Right-side contextual Entity Inspector: When a node is selected, show an inspector panel displaying capacity, lead time, coordinates, and active dependencies without obscuring the map.

---

### Phase U4: Decision Center & Scenario Launcher
- **Target Files**:
  - `desktop/src/views/DecisionCenter/DecisionCenterView.tsx` & `DecisionCenter.module.css`
  - `desktop/src/views/Scenarios/ScenariosView.tsx` & `Scenarios.module.css`
- **Scope & Objectives**:
  1. **Decision Center Refinement**:
     - Queue List: Display priority, scenario ID, confidence score (WCS), lifecycle status, and elapsed age.
     - Implement explicit lifecycle status badges: `Proposed`, `Under review`, `Approved`, `Authorized`, `Executing`, `Completed`, `Rejected`, `Blocked`, `Failed`.
     - Decision Inspector Pane:
       - Operational Issue Summary.
       - Recommended Action & Quantified Trade-Offs (Cost variance in INR, lead time impact).
       - Specialist Agreement & Deliberation Claims (CD2F consensus breakdown).
       - Policy Constraints & Trace Audit Links.
  2. **Scenario Launcher Modernization**:
     - Maintain the full 25-scenario catalog with categorized segment filters (`All`, `Supplier`, `Demand`, `Transport`, `Weather & Systemic`).
     - Replace slider gimmicks with precise numeric input fields and bounded unit steppers.
     - Summary review card detailing affected topology node, shock parameters, and duration before dispatching.

---

### Phase U5: Agent Command, What-If Simulation Lab, Traces & Evaluation Matrix
- **Target Files**:
  - `desktop/src/views/AgentCommand/AgentCommandView.tsx` & `AgentCommand.module.css`
  - `desktop/src/views/WhatIfLab/WhatIfLabView.tsx` & `WhatIfLab.module.css`
  - `desktop/src/views/ReasoningTrace/ReasoningTraceView.tsx` & `ReasoningTrace.module.css`
  - `desktop/src/views/Evaluation/EvaluationView.tsx` & `Evaluation.module.css`
- **Scope & Objectives**:
  1. **Agent Command (Calm Operations Table)**:
     - Eliminate sci-fi card grid and pulsing status dots.
     - Implement a structured operations data table:
       - Columns: Specialist Component, Current Task, Operational Status, Scenario/Run Context, Execution Latency, Last Heartbeat.
     - Selecting an agent row opens a right-side Detail Inspector containing:
       - Registered capabilities, endpoint port, recent claims emitted, and execution trace correlation ID.
  2. **What-If Simulation Lab**:
     - Maintain counterfactual matrix across all 25 scenarios.
     - Replace flashy colored metric boxes with structured comparison cards showing baseline vs. counterfactual deltas (`+₹...`, `+X.X days`, `+X.X%`).
     - Provide unambiguous labeling: "Simulated Counterfactual Projection (Isolated Run)".
  3. **Reasoning Trace Explorer**:
     - Visual trace timeline mapping the 8 runtime stages: `OBSERVE` -> `SCOPE` -> `RETRIEVE` -> `ANALYZE` -> `CHECK` -> `PROPOSE` -> `VALIDATE` -> `EMIT`.
     - Render clean human-readable audit summaries first, with structured JSON payloads collapsible on demand.
  4. **Evaluation Matrix**:
     - Clean benchmark comparison tables comparing CD2F against Single-Agent LLM, Heuristic Greedy, and Static Rule Baselines.
     - Strict tabular alignment for P50/P90/P99 latency, WCS stability, and accuracy metrics.

---

### Phase U6: Acceptance Gate, Accessibility & Build Verification
- **Verification Targets**:
  1. **Color Contrast Compliance**: All text tokens must achieve WCAG AA contrast (>= 4.5:1 on background surfaces).
  2. **Zero-Emoji Enforcement**: Automated regex scan across all CSS, TSX, and Markdown files confirming 0 emojis.
  3. **Relative Paths**: Confirm all documentation and code links use valid relative paths.
  4. **Build & Bundle Verification**: Execute `npm run build` in `desktop/` to verify 0 TypeScript and 0 Vite build errors.

---

## 4. File Modification Matrix

| File Path (Relative) | Primary Phase | Changes Description |
| :--- | :--- | :--- |
| `desktop/src/index.css` | Phase U1 | Replace Apple blur tokens with canonical SCOF brand and semantic palette; normalize radii and spacing. |
| `desktop/src/components/layout/Sidebar.tsx` | Phase U2 | Canonical 7-view navigation, subtle active state, profile label, settings trigger. |
| `desktop/src/components/layout/Sidebar.module.css` | Phase U2 | Clean sidebar styling, restrained item padding, no heavy blur. |
| `desktop/src/components/layout/TopBar.tsx` | Phase U3 | Calm header, title hierarchy, real health check status, UTC clock, shortcuts trigger. |
| `desktop/src/components/layout/TopBar.module.css` | Phase U2 | Header styles using `surface.canvas` and `border.default`. |
| `desktop/src/components/modals/SettingsModal.tsx` | Phase U2 | New utility modal for appearance, connection diagnostics, profile, and shortcuts. |
| `desktop/src/components/modals/SettingsModal.module.css` | Phase U2 | Clean modal styling matching desktop specifications. |
| `desktop/src/App.tsx` | Phase U2 | Integrate Settings modal state and canonical 7-view routing. |
| `desktop/src/views/Operations/OperationsView.tsx` | Phase U3 | Remove SVG glows; crisp topology diagram; right-side entity inspector; clean KPI cards. |
| `desktop/src/views/Operations/Operations.module.css` | Phase U3 | Restrained surface styling and structured grid layout. |
| `desktop/src/views/DecisionCenter/DecisionCenterView.tsx` | Phase U4 | Explicit lifecycle status tags, structured evidence inspector, tabular layout. |
| `desktop/src/views/DecisionCenter/DecisionCenter.module.css` | Phase U4 | Split list-inspector styling with neutral panel surfaces. |
| `desktop/src/views/Scenarios/ScenariosView.tsx` | Phase U4 | Clean catalog table, bounded input form, clear dispatch confirmation. |
| `desktop/src/views/Scenarios/Scenarios.module.css` | Phase U4 | Clean table and input controls matching 6px/9px radii. |
| `desktop/src/views/AgentCommand/AgentCommandView.tsx` | Phase U5 | Convert card grid to calm operations table; right-side inspector for specialist telemetry. |
| `desktop/src/views/AgentCommand/AgentCommand.module.css` | Phase U5 | Clean table styling with muted row hover states. |
| `desktop/src/views/WhatIfLab/WhatIfLabView.tsx` | Phase U5 | Clean baseline vs counterfactual comparison tiles; precise steppers. |
| `desktop/src/views/WhatIfLab/WhatIfLab.module.css` | Phase U5 | Neutral comparison grid without fluorescent highlights. |
| `desktop/src/views/ReasoningTrace/ReasoningTraceView.tsx` | Phase U5 | 8-stage chronological progression timeline with collapsible payloads. |
| `desktop/src/views/ReasoningTrace/ReasoningTrace.module.css` | Phase U5 | Structured audit card styling. |
| `desktop/src/views/Evaluation/EvaluationView.tsx` | Phase U5 | High-density benchmark comparison tables and latency distributions. |
| `desktop/src/views/Evaluation/Evaluation.module.css` | Phase U5 | Data-dense table styling with tabular numerals. |

---

## 5. Acceptance Criteria Checklist

- [ ] **A1: Token Compliance**: All CSS files consume shared tokens from `desktop/src/index.css`. No hardcoded ad-hoc hex colors.
- [ ] **A2: Elimination of "AI-ness"**: Zero neon glow filters, zero SVG blur filters (`feGaussianBlur`), zero decorative animated pulsing elements, and zero sci-fi agent avatars.
- [ ] **A3: Palette Discipline**: Primary surfaces use neutral slates/navies (`#11161D`, `#1B232E`, `#171D26`). Brand blue (`#0E82D6` / `#45A9F3`) and teal (`#16A67E` / `#48C69A`) used strictly as functional accents.
- [ ] **A4: Typography & Numerals**: Tabular numerals active for all operational KPIs, metrics, latency measurements, and timestamps.
- [ ] **A5: Corner Radii Hierarchy**: Radius scale strictly enforced (6px controls, 9px cards, 12px panels). No full-pill buttons.
- [ ] **A6: Navigation Integrity**: All 7 canonical views accessible via `Ctrl/Cmd + 1` through `Ctrl/Cmd + 7` and sidebar.
- [ ] **A7: Zero-Emoji Standard**: Zero emoji characters present across code and documentation.
- [ ] **A8: Build Verification**: Clean compilation via `npm run build` in `desktop/` with 0 errors.
