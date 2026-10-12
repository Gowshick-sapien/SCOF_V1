# Unified SCOF Workspace Plan: Implementation-Ready Specification

## 1. Executive Summary & Review Resolutions

This specification details the structural transformation of the SCOF desktop console from a static, three-panel dashboard into a cohesive, task-driven operational workspace. It incorporates all requirements from the architectural review, establishing deterministic state contracts, container-responsive layout behaviors, safe form lifecycle management, truthful connection integrity, and a hardened multi-tier verification gate.

### 1.1 Architectural Resolutions Matrix

| Review Finding | Classification | Architectural Resolution in This Specification |
| :--- | :--- | :--- |
| **Deterministic Connection Precedence** | P0 | Model API REST health, WebSocket stream health, reconnection activity, polling fallback state, and data freshness as separate underlying signals. Derive displayed status using a deterministic, mutually exclusive precedence hierarchy: `OFFLINE_CACHED` > `RECONNECTING` > `DEGRADED` > `CONNECTED`. Display `POLLING FALLBACK ACTIVE` only if an active polling loop is verified and returning data. |
| **Unambiguous Scenario Dispatch** | P0 | Classify dispatch outcomes into four explicit categories: `ACCEPTED` (HTTP 200 from API with `event_id` and `trace_id`), `REJECTED` (HTTP 4xx validation or business rejection), `FAILED` (confirmed server 5xx with no dispatch), and `UNKNOWN` (network drop or client timeout). Block non-idempotent retries on `UNKNOWN` and provide a dedicated reconciliation path via the Decision Center queue. Clarify that identifiers are generated and returned by `scof-api`, not direct broker receipts. |
| **Standardized Drawer Modes & Draft Lifetime** | P1 | Standardize drawer modes to `docked` and `overlay`. Eliminate `full-detail` as a drawer mode; treat deep inspection (e.g., full reasoning traces) as standard workspace navigation. Scope draft form preservation explicitly to in-session memory (`scenarioDrafts: Record<string, DraftConfig>`), documenting that drafts do not persist across application restarts. |
| **Container-Responsive Workspace Layout** | P1 | Replace the rigid 1440px window threshold with container-responsive thresholds based on available workspace content width. Account for navigation rail width (68px or 208px), window chrome, content padding, and docked inspector width (360px). Transition between side-by-side (65/35) and vertical stacked workflows at 960px available workspace width. Retain 1600px and 1280px as verification targets, including intermediate transitions. |
| **Decision Lifecycle Schema Mapping** | P1 | Map displayed decision statuses strictly to verified fields in `DecisionRecord` (`escalation_tier`, `decision_confidence`, `weighted_consensus_stability`, `final_recommendation`). Derive presentation statuses (`FAST-PATH RECOMMENDATION`, `DELIBERATED CONSENSUS`, `HUMAN ESCALATION REQUIRED`) without introducing unsupported backend states (`APPROVED`, `AUTHORIZED`, `EXECUTING`, `COMPLETED`). Frame execution integration as an external system boundary (ERP/WMS/TMS unlinked). |
| **Precisely Scoped Zero-Emoji Validation** | P2 | Define prohibited Unicode code-point ranges covering emoji, pictographs, and decorative dingbats (`0x1F300-0x1FAFF`, `0x2600-0x27BF`, `0xFE00-0xFE0F`, etc.). Scope automated scanning to files modified by this deliverable, with explicit exclusions for currency symbols (INR `0x20B9`), ASCII box-drawing characters (`0x2500-0x257F`), and standard punctuation. |
| **Frozen Backend Invariants** | P0 | Guarantee zero modifications to backend files (`services/api/`, `services/coordinator/`, `services/evaluator/`, PostgreSQL, Kafka, Redis, Neo4j). API route contracts, WebSocket channel schemas, and authorization semantics remain 100% frozen. |

---

### 1.2 Strict UI/UX Scope Boundary & Backend Freezing Policy

This refinement deliverable is strictly limited to user interface (UI) and user experience (UX) enhancements within the desktop client. To protect system integrity and prevent regressions across running services, the following scope boundaries are absolute:

1. **Strictly Frontend-Exclusive Scope**:
   - All code modifications, component additions, interaction handlers, and CSS styles are confined strictly to `desktop/src/` and project documentation in `docs/`.
   - The architectural focus is entirely on operational layout composition, compact navigation rail interactions, container-responsive workspace scaling, truthful connection indicators, and on-demand contextual drawers.

2. **Absolute Backend Freezing Policy**:
   - **`services/api/` (API Gateway, Port 8000)**: 100% Frozen. Zero changes to FastAPI routes (`/health`, `/scenarios`, `/scenarios/trigger`, `/whatif/run`, `/decisions`, `/agents`), Pydantic models, query parameters, or WebSocket streaming endpoints (`/ws/dashboard/state`, `/ws/decisions/live`, `/ws/agents/activity`).
   - **`services/coordinator/` (Orchestration Kernel, Port 8010)**: 100% Frozen. Zero changes to the LangGraph multi-agent kernel, CD2F arbitration engine, deliberation state machines, or agent scheduling loops.
   - **`services/specialists/` (Specialist Agents)**: 100% Frozen. Specialist agent logic, tools, prompt templates, and local execution paths remain untouched.
   - **`services/simulation/` & `services/evaluator/`**: 100% Frozen. Discrete-event simulation engines, baseline datasets, and evaluation metrics remain untouched.
   - **Data Stores & Event Infrastructure**: Zero changes to PostgreSQL schemas (`scof.*`), Neo4j graph nodes and edges, Redis caches, Kafka topics (`disruptions.triggered`, `decisions.published`), or consumer groups.
   - **Deployment & Containers**: `docker-compose.yml`, Dockerfiles, environment variables, network bridges, and exposed service ports remain completely unchanged.

3. **Client-Side Adaptation Rule**:
   - If any UI interaction reveals a discrepancy or missing state in backend endpoints, the desktop client must gracefully adapt its presentation (e.g., derive presentation states from existing fields or display clear disabled notices with tooltips). Under no circumstances will backend code or contracts be modified to accommodate the UI.

---

## 2. Core Interaction & State Contracts

### 2.1 Deterministic Connection Precedence & Data-Freshness Contract
The console shell and all constituent views consume a synchronized connection state managed in `desktop/src/state/connection.tsx`. To eliminate state overlap, the client separates underlying transport signals from the derived presentation status.

```
                    ┌─────────────────────────┐
                    │    REST API (:8000)     │
                    │      GET /health        │
                    └────────────┬────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Global Connection State Manager                      │
│                                                                        │
│  Underlying Transport Signals:                                         │
│  - apiHealth: "nominal" | "down" | "checking"                          │
│  - streamsConnected: number (0 to 3)                                   │
│    * dashboardWs (/ws/dashboard/state)                                 │
│    * decisionsWs (/ws/decisions/live)                                  │
│    * agentsWs    (/ws/agents/activity)                                 │
│  - isReconnecting: boolean (active transport retry in progress)        │
│  - pollingFallbackActive: boolean (verified HTTP poll returning data) │
│  - lastSuccessfulSync: ISO-8601 Timestamp | null                       │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
        Deterministic Precedence Hierarchy Evaluation (Top to Bottom)
                                 │
   1. apiHealth === "down" ──────────────────────────────► [ OFFLINE_CACHED ]
                                 │
   2. isReconnecting && apiHealth === "nominal" ────────► [ RECONNECTING ]
                                 │
   3. streamsConnected < 3 && apiHealth === "nominal" ──► [ DEGRADED ]
                                 │
   4. streamsConnected === 3 && apiHealth === "nominal" ─► [ CONNECTED ]
```

#### Deterministic Precedence Hierarchy:

1. **`OFFLINE_CACHED`** (Precedence 1 — Highest):
   - **Trigger Condition**: `apiHealth === "down"` OR (`apiHealth === "checking"` AND `streamsConnected === 0` AND `lastSuccessfulSync === null`).
   - **Rationale**: If the REST API gateway is unreachable, data fetching and dispatch fail completely. Reconnection attempts on WebSockets cannot compensate for a down gateway.
   - **TopBar / Rail Badge**: Red indicator (`#F0747E`), label `OFFLINE (CACHED)`.
   - **Prominent Banner**: `[CACHED DATA - Last synced: {HH:MM:SS UTC}]`.
   - **Footer Indicator**: `A2A GATEWAY UNREACHABLE`.
   - **Data Rendering Guard**: All operational cards, topology nodes, and decision lists render a `CACHED` badge. The UI must never claim `A2A Protocol Live` or `Nominal` when running on offline cache.

2. **`RECONNECTING`** (Precedence 2):
   - **Trigger Condition**: `apiHealth === "nominal"` AND `isReconnecting === true` AND `streamsConnected < 3`.
   - **Rationale**: The API gateway is healthy, but WebSocket transport was interrupted and active backoff reconnection loops are in flight.
   - **TopBar / Rail Badge**: Amber pulsing indicator (`#E9B45C`), label `RECONNECTING...`.
   - **Footer Indicator**: `RECONNECTING EVENT STREAMS ({streamsConnected}/3 CONNECTED)`.
   - **Staleness Notice**: Displays timestamp of last received live event.

3. **`DEGRADED`** (Precedence 3):
   - **Trigger Condition**: `apiHealth === "nominal"` AND `streamsConnected < 3` AND `isReconnecting === false`.
   - **Rationale**: The API is reachable, but one or more event streams are dropped without an active reconnection loop.
   - **TopBar / Rail Badge**: Amber indicator (`#E9B45C`), label `STREAMS DEGRADED ({streamsConnected}/3)`.
   - **Footer Indicator & Polling Truthfulness Rule**:
     - IF and ONLY IF a dedicated HTTP polling fallback loop is actively running and returning HTTP 200 data: render `POLLING FALLBACK ACTIVE`.
     - IF no polling fallback loop is operating: render `WEBSOCKET DISCONNECTED - REST NOMINAL`.
     - **Negative Invariant**: A disconnected WebSocket does not by itself establish that polling fallback is active. The UI must never display `POLLING FALLBACK ACTIVE` without a verified running poll cycle.

4. **`CONNECTED`** (Precedence 4 — Nominal Baseline):
   - **Trigger Condition**: `apiHealth === "nominal"` AND `streamsConnected === 3` AND `isReconnecting === false`.
   - **TopBar / Rail Badge**: Solid green indicator (`#48C69A`), label `CONNECTED`.
   - **Footer Indicator**: `A2A PROTOCOL LIVE`.
   - **Metrics**: Standard live telemetry rendering without warning badges.

---

### 2.2 Reusable Contextual Drawer Contract (`ContextualDrawer.tsx`)

The contextual drawer provides on-demand detail inspection and parameter configuration without permanent workspace partitioning.

#### 1. Presentation Modes:
The component interface standardizes strictly on two presentation modes:
- **`docked`**:
  - Inspector sits adjacent to the main workspace, occupying a dedicated grid column (`width: 360px`).
  - Active on wide viewports with sufficient content width. Underlying maps, tables, and workflows remain visible and interactive.
- **`overlay`**:
  - Inspector slides in from the right edge (`width: 360px`, `z-index: 500`) over a semi-transparent backdrop (`rgba(0, 0, 0, 0.4)`).
  - Active on compact viewports or when temporary modal inspection is required.

> [!IMPORTANT]
> Deep drill-down (such as viewing the complete multi-agent reasoning trace from a decision summary) is implemented as standard route navigation to `traces` via the application router, NOT as an oversized drawer mode. The drawer is strictly an inspection and input panel.

#### 2. Component Interface Specification:
```typescript
export interface ContextualDrawerProps {
  isOpen: boolean;
  title: string;
  badge?: string;
  mode: "docked" | "overlay";
  isDirty?: boolean;
  onClose: () => void;
  onDiscard?: () => void;
  children: React.ReactNode;
}
```

#### 3. Draft Lifetime & Memory Scope Contract:
- **Draft Persistence Scope**: Unsaved form state in configuration drawers (e.g., scenario severity, target node selection, parameter overrides) is preserved strictly in **in-session client memory** (`scenarioDrafts: Record<string, DraftConfig>` in React state/context).
- **Session Boundary**: Drafts survive navigating between console views within the active browser/desktop session.
- **Restart Boundary**: Drafts do NOT survive application reloads, tab closures, or desktop process restarts. The application does not claim durable cross-restart draft persistence because no durable client storage schema is approved or configured.
- **Dirty Form Dismissal**:
  - Read-only inspector (`isDirty: false`): Dismisses immediately on `Escape` key, backdrop click, or close button (`x`).
  - Editable form drawer (`isDirty: true`): Closing retains draft state in memory and prompts: `"Draft saved in session. Discard changes or keep draft?"`.

#### 4. Focus & Accessibility Management:
- **Overlay Mode**: On open, keyboard focus programmatically shifts to the drawer container or first interactive element. Tab cycling is trapped within the drawer.
- **On Close**: Focus programmatically restores to the invoking element (the table row, topology node, or button that triggered the drawer).
- **Dismiss Control**: Plain character `'x'` with `aria-label="Close Inspector"`.

---

### 2.3 Scenario Launcher State Machine & Dispatch Contract

The two-stage Scenario Launcher (`desktop/src/views/Scenarios/ScenariosView.tsx`) transitions between catalog browsing and parameter dispatch according to an explicit 6-state finite state machine.

```
        ┌────────────────────────┐
        │   1. CATALOG_BROWSE    │  (25 scenarios, category filter tabs)
        └───────────┬────────────┘
                    │ Operator selects scenario row
                    ▼
        ┌────────────────────────┐
        │       2. DRAFT         │  (In-session memory: severity, target node)
        └───────────┬────────────┘
                    │ Pre-flight validation passes
                    ▼
        ┌────────────────────────┐
        │      3. VALIDATED      │  (Summary: Scenario ID, target node, topic)
        └───────────┬────────────┘
                    │ Operator clicks "Trigger Disruption"
                    ▼
        ┌────────────────────────┐
        │     4. SUBMITTING      │  (In-flight debounce lock active)
        └───────────┬────────────┘
                    │
      ┌─────────────┼───────────────────────────┬──────────────────────┐
      │             │                           │                      │
  HTTP 200      HTTP 4xx                    HTTP 5xx               Timeout /
  from API      from API                    from API               Network Drop
      │             │                           │                      │
      ▼             ▼                           ▼                      ▼
┌───────────┐ ┌───────────┐               ┌───────────┐          ┌───────────┐
│5. ACCEPTED│ │6. REJECTED│               │ 7. FAILED │          │8. UNKNOWN │
└───────────┘ └───────────┘               └───────────┘          └───────────┘
```

#### Dispatch Outcome Specifications:

1. **`ACCEPTED`**:
   - **Contract**: `POST /scenarios/trigger` returns HTTP 200 with `{ event_id, trace_id, status: "TRIGGERED", scenario_id }`.
   - **Semantics**: The API gateway (`scof-api`) accepted the request, generated `event_id` and `trace_id`, cached the envelope in Redis, and dispatched the event to the Kafka bus.
   - **UI Assertion**: The UI displays `DISPATCH ACCEPTED (Awaiting Multi-Agent Deliberation)`.
   - **Critical Rule**: The UI must NOT claim "Scenario Completed" or "Consensus Reached" upon trigger acceptance. The trigger only initiates the orchestration loop.

2. **`REJECTED`**:
   - **Contract**: API returns HTTP 4xx (e.g., 404 Scenario Not Found, 422 Validation Error).
   - **Semantics**: The backend explicitly rejected the request. No disruption event was published to Kafka.
   - **UI Behavior**: Retains draft inputs; displays backend error details. Safe for the operator to modify parameters and re-submit.

3. **`FAILED`**:
   - **Contract**: Confirmed server error (HTTP 5xx before publish or database connectivity failure) with guaranteed non-dispatch.
   - **Semantics**: The request failed prior to event bus publication.
   - **UI Behavior**: Displays server error description; retains draft parameters; enables explicit retry button.

4. **`UNKNOWN`** (`TIMEOUT_UNKNOWN`):
   - **Trigger**: Client network drop, TCP socket disconnect, or request timeout (> 10s) while awaiting API response.
   - **Semantics**: The client cannot verify whether the request reached `scof-api` and was published to Kafka.
   - **Non-Idempotent Retry Guard**: The UI must NOT offer an unrestricted "Retry Trigger" button. Retrying blind risks injecting duplicate disruptions into the running simulation.
   - **Reconciliation Path**:
     - The UI transitions to `STATUS UNKNOWN (DISPATCH IN TRANSIT)`.
     - Renders an explicit reconciliation banner with two actions:
       1. **Inspect Decisions Queue**: Direct shortcut to `DecisionCenterView` to check whether a deliberation was initiated for this scenario ID.
       2. **Check API Health**: Re-checks `GET /health` to confirm gateway availability before allowing any manual override.

---

### 2.4 Decision Lifecycle Display Model & Backend Schema Mapping

The Decision Center (`desktop/src/views/DecisionCenter/DecisionCenterView.tsx`) visualizes arbitration outputs from the cognitive twin. The UI derives presentation statuses directly from supported fields in `DecisionRecord` without inventing unsupported backend execution lifecycles.

#### Real Backend Schema Mapping (`desktop/src/api/types.ts` & `scof.decision_records`):

```typescript
export interface DecisionRecord {
  decision_id: string;
  scenario_id: string;
  trace_id?: string;
  consensus_bundle_id: string;
  source_bundle_id: string;
  decision_method: "CD2F" | "SINGLE_AGENT" | "NAIVE_MAJORITY" | string;
  final_recommendation?: string;
  decision_confidence: number;              // float 0.0 to 1.0
  weighted_consensus_stability: number;     // float 0.0 to 1.0
  escalation_tier: "FAST_PATH" | "SLOW_PATH" | "HUMAN_ESCALATION";
  escalation_rationale: string;
  agent_weights: Record<string, AgentWeightBreakdown>;
  recommendation_tallies: Record<string, number>;
  reasoning_trail: ReasoningStep[];
  meeting_log_entries: MeetingLogEntry[];
  timestamp: string;
}
```

#### Display Status Derivation Table:

| Displayed Status | Derivation Rule from Backend Fields | Operational Meaning | Action Available to Operator |
| :--- | :--- | :--- | :--- |
| **`FAST-PATH RECOMMENDATION`** | `escalation_tier === "FAST_PATH"` AND `decision_confidence >= 0.8` | High-confidence candidate action generated autonomously under tight latency SLA. | Review claims in drawer; open full reasoning trace. |
| **`DELIBERATED CONSENSUS`** | `escalation_tier === "SLOW_PATH"` AND `weighted_consensus_stability >= 0.7` | Multi-agent consensus achieved through multi-round arbitration (CD2F). | Review specialist concessions and weight breakdown. |
| **`HUMAN ESCALATION REQUIRED`** | `escalation_tier === "HUMAN_ESCALATION"` OR `decision_confidence < 0.8` | Policy boundary breach, unresolved agent dispute, or low stability requiring human judgment. | Acknowledge escalation; review dissenting claims. |
| **`OPERATOR ACKNOWLEDGED`** | Client session state: operator clicked "Acknowledge Recommendation" in UI. | In-session operator review acknowledgment. Strictly a client-side tracking state. | Badge displayed: `ACKNOWLEDGED (CLIENT SESSION)`. |

#### Physical Execution Boundary Rule:
The SCOF backend provides multi-agent cognitive deliberation and recommendations. It does not contain an integrated ERP/WMS/TMS order-execution pipeline in the current release.
- **Rule**: The UI will NOT display mock `EXECUTING` or `COMPLETED` lifecycle states.
- **Labeling**: Downstream execution actions are explicitly flagged as `EXTERNAL SYSTEM INTEGRATION (ERP UNLINKED)`. Execution trigger buttons remain disabled with informative tooltips, preserving the truthfulness of the advisory twin boundary.

---

### 2.5 Container-Responsive Workspace Sizing (Operations Overview)

The Operations Overview (`desktop/src/views/Operations/OperationsView.tsx`) transitions between a side-by-side arrangement and a vertical workflow based on **available workspace content width**, not raw window width.

#### Available Content Width Calculation:
```
Available Workspace Content Width = 
  Window Width 
  - Navigation Rail Width (68px collapsed, 208px expanded)
  - Docked Inspector Width (360px when active, 0px when closed)
  - Workspace Content Padding (48px total)
  - Window Chrome & Scrollbars (~16px)
```

#### Responsive Thresholds:

```
                      Available Workspace Content Width
   0px ───────────────────────────── 960px ────────────────────────────►
   ◄────── Vertical Stacked ────────►◄────── Balanced Side-by-Side ─────►
   Full-width Topology schematic     65% Topology Schematic
   Stacked Attention Queue beneath   35% Attention Queue
```

#### Layout Behavior by Operational Configuration:

| Desktop Window Width | Rail State | Docked Inspector | Usable Workspace Width | Active Layout Mode | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1600px** | Expanded (208px) | Docked (360px) | ~968px | **Side-by-Side (65/35)** | Exceeds 960px threshold; topology and queue render comfortably side-by-side. |
| **1600px** | Collapsed (68px) | Closed (0px) | ~1468px | **Side-by-Side (65/35)** | Expansive canvas; schematic expands while retaining clean 35% queue column. |
| **1440px** | Collapsed (68px) | Closed (0px) | ~1308px | **Side-by-Side (65/35)** | Nominal standard desktop view. |
| **1440px** | Expanded (208px) | Docked (360px) | ~808px | **Vertical Stacked (100/100)** | Content width drops below 960px. Layout automatically collapses to vertical stack to prevent cramped, truncated columns. |
| **1280px** | Collapsed (68px) | Closed (0px) | ~1148px | **Side-by-Side (65/35)** | Without inspector, side-by-side fits cleanly. |
| **1280px** | Collapsed (68px) | Active Inspector | ~788px | **Overlay Drawer Mode** | At 1280px, opening the inspector automatically defaults to `overlay` mode rather than docking, preserving 100% workspace width behind. |

---

## 3. Work Breakdown Structure (Phases W1 to W5)

```
[ Phase W1: Compact Navigation Rail & Truthful State Integrity ]
                                │
                                ▼
[ Phase W2: Contextual Drawer System & Operations Overview ]
                                │
                                ▼
[ Phase W3: Decision Center & Two-Stage Scenario Launcher ]
                                │
                                ▼
[ Phase W4: Agent Command, What-If Lab, Traces & Evaluation ]
                                │
                                ▼
[ Phase W5: Hardened Acceptance Verification Gate ]
```

---

### Phase W1: Compact Navigation Rail & Truthful State Integrity
- **Target Files**:
  - `desktop/src/components/layout/Sidebar.tsx` & `Sidebar.module.css`
  - `desktop/src/components/layout/TopBar.tsx` & `TopBar.module.css`
  - `desktop/src/state/connection.tsx`
  - `desktop/src/components/common/ConnectionBanner.tsx` & `ConnectionBanner.module.css`
  - `desktop/src/App.tsx` & `App.css`
- **Scope**:
  1. **Compact Navigation Rail**:
     - Default width: 68px (icon-only mode with tooltips, SVG outline icons, shortcut indicators `Ctrl 1` to `Ctrl 7`).
     - Deliberate expand toggle to 208px. Hover preview does not shift workspace layout.
     - Active indicator: 3px solid `var(--brand-blue)` accent bar.
     - Footer region: Dedicated Settings button, Profile badge (`MVP-ELECTRONICS`), and truthful connection status badge.
  2. **Deterministic Connection Precedence**:
     - Implement the 4-level precedence hierarchy in `connection.tsx` (`OFFLINE_CACHED` > `RECONNECTING` > `DEGRADED` > `CONNECTED`).
     - Display `POLLING FALLBACK ACTIVE` strictly when a live polling fallback cycle is verified.
     - When status is `OFFLINE_CACHED`, render `[CACHED DATA - Last synced: {timestamp}]` across TopBar and ConnectionBanner.
  3. **Fluid Layout Grid**:
     - Reset `App.css` to fluid layout: `[Navigation Rail (68px / 208px)] + [Fluid Workspace (1fr)]`.

---

### Phase W2: Contextual Drawer System & Operations Overview
- **Target Files**:
  - `desktop/src/components/common/ContextualDrawer.tsx` & `ContextualDrawer.module.css` (New Reusable Component)
  - `desktop/src/views/Operations/OperationsView.tsx` & `Operations.module.css`
- **Scope**:
  1. **Reusable `ContextualDrawer`**:
     - Standardize modes strictly to `docked` and `overlay`.
     - In-session memory draft management (`scenarioDrafts`).
     - Focus trap for overlay mode; restores focus to invoking DOM element on close.
     - `Escape` key dismisses read-only inspectors immediately; guards dirty form drawers.
  2. **Operations Overview Container-Responsive Recomposition**:
     - Top: 4 operational KPI summary cards.
     - Center Workspace: Container-responsive layout (65/35 grid when content width >= 960px; vertical stacked workflow when < 960px).
     - On-demand facility inspector drawer: Clicking topology nodes opens `ContextualDrawer` in docked or overlay mode without resetting map zoom.
     - Bottom: Recent deliberated decisions and audit log table.

---

### Phase W3: Decision Center & Two-Stage Scenario Launcher
- **Target Files**:
  - `desktop/src/views/DecisionCenter/DecisionCenterView.tsx` & `DecisionCenter.module.css`
  - `desktop/src/views/Scenarios/ScenariosView.tsx` & `Scenarios.module.css`
- **Scope**:
  1. **Decision Center Schema Alignment**:
     - Map displayed statuses directly to `DecisionRecord` fields (`FAST-PATH RECOMMENDATION`, `DELIBERATED CONSENSUS`, `HUMAN ESCALATION REQUIRED`).
     - Contextual drawer displays deliberation claims and statement chips (`CLAIM`, `WEIGHT_REPORT`, `TALLY`, `ESCALATION`, `DECISION`).
     - "Open Reasoning Trace" action navigates directly to `traces` view via router, rather than opening an oversized drawer.
     - Explicit labeling of downstream ERP execution as unlinked external boundary.
  2. **Two-Stage Scenario Launcher**:
     - Stage 1: Full-width 25-scenario catalog table with category tabs.
     - Stage 2: Slide-over configuration drawer (380px) with 5-level severity stepper and target node selector.
     - Implement 4-outcome dispatch contract (`ACCEPTED`, `REJECTED`, `FAILED`, `UNKNOWN`).
     - Debounce lock on dispatch button preventing duplicate triggers.
     - Dedicated reconciliation path for `UNKNOWN` outcomes guiding operators to verify the Decision Center queue.

---

### Phase W4: Agent Command, What-If Lab, Traces & Evaluation
- **Target Files**:
  - `desktop/src/views/AgentCommand/AgentCommandView.tsx` & `AgentCommand.module.css`
  - `desktop/src/views/WhatIfLab/WhatIfLabView.tsx` & `WhatIfLab.module.css`
  - `desktop/src/views/ReasoningTrace/ReasoningTraceView.tsx` & `ReasoningTrace.module.css`
  - `desktop/src/views/Evaluation/EvaluationView.tsx` & `Evaluation.module.css`
- **Scope**:
  1. **Agent Command**:
     - Full-width operations data table listing dynamically registered specialists from API (`agent_id`, `role`, `status`, `endpoint`, `latency_ms`).
     - Selecting an agent opens `ContextualDrawer` with endpoint metadata and tool capabilities.
  2. **What-If Simulation Lab**:
     - Comparison-first workspace: side-by-side tiles (Baseline vs. Counterfactual) with INR cost variance (`+₹...`), lead-time impact, and stockout delta.
     - Collapsible assumptions column maximizing comparison table width.
     - Clear attribution tag: `Simulated Counterfactual Projection (Isolated Run)`.
  3. **Reasoning Traces & Evaluation Matrix**:
     - Traces: Chronological 4-phase pipeline with expandable raw JSON payloads, accessible via direct workspace navigation.
     - Evaluation: Benchmark summary cards and comparative matrix tables with tabular numerals.

---

### Phase W5: Hardened Acceptance Verification Gate
- **Target Files**:
  - `scripts/verify_scenario_suite.py`
  - All modified TSX, CSS, and Markdown files across `desktop/src` and `docs/`
- **Verification Gates**:

| Gate Identifier | Gate Name | Required Evidence & Verification Criteria |
| :--- | :--- | :--- |
| **G1** | **Build & Compilation** | Execute `npm run build` in `desktop/`. Must produce 0 TypeScript errors and a clean Vite production bundle. |
| **G2** | **Multi-Agent E2E Suite** | Execute `python scripts/verify_scenario_suite.py` against `:8000`. Must validate all 25 scenarios, What-If predictive matrix with INR formatting, and live Kafka disruption dispatch. |
| **G3** | **Backend Port Verification** | Validate HTTP 200 on `http://localhost:8000/health` (`scof-api`) and confirm coordinator availability on `http://localhost:8010` (`scof-coordinator`). |
| **G4** | **Navigation & Rail** | All 7 canonical routes accessible via rail clicks and keyboard hotkeys (`Ctrl+1` to `Ctrl+7`). Rail expands/collapses cleanly via toggle button without unpinned layout jitter. |
| **G5** | **Contextual Drawer Behavior** | Test drawer in both `docked` and `overlay` modes. Verify focus movement on open, focus restoration on close, `Escape` key dismissal, and dirty form draft preservation in session memory. |
| **G6** | **Truthful State Integrity** | Verify deterministic connection precedence: simulating offline gateway state transitions the UI to `OFFLINE (CACHED)`, displays `[CACHED DATA]` notice, and renders `POLLING FALLBACK ACTIVE` strictly when verified. |
| **G7** | **Scenario Launch & Debounce** | Verify parameter validation, duplicate-click blocking during in-flight dispatch, proper display of `DISPATCH ACCEPTED`, and reconciliation guidance on simulated timeout. |
| **G8** | **Container-Responsive Layout Check** | Verify clean transitions at 1600px, 1440px, and 1280px window widths. Confirm layout transitions cleanly between side-by-side (>= 960px usable width) and vertical stacked (< 960px usable width) without horizontal overflow. |
| **G9** | **Zero Backend Modifications Gate** | Execute `git status --porcelain services/` and `git diff --stat services/`. Must return zero output (0 files modified). All backend microservices, route contracts, database schemas, Kafka topics, and Docker configs remain 100% frozen. |
| **G10** | **Precisely Scoped Zero-Emoji Enforcement** | Execute automated Unicode codepoint scanner across all deliverable files. Strictly 0 emoji or dingbat characters allowed within prohibited ranges (`0x1F300-0x1FAFF`, `0x2600-0x27BF`, `0xFE00-0xFE0F`). Documented exclusions (INR `₹`, ASCII box characters) verified. |

---

## 4. File Modification Matrix

| Relative File Path | Phase | Architectural Scope |
| :--- | :--- | :--- |
| `desktop/src/state/connection.tsx` | Phase W1 | Implement deterministic 4-level precedence hierarchy; decouple API REST health from WebSocket status; truthful polling fallback detection. |
| `desktop/src/components/layout/Sidebar.tsx` | Phase W1 | Compact navigation rail (68px default, 208px toggle), tooltips, active indicator, state-aware footer. |
| `desktop/src/components/layout/Sidebar.module.css` | Phase W1 | Rail styling, transition animation, unpinned preview vs pinned expand. |
| `desktop/src/components/layout/TopBar.tsx` | Phase W1 | Lightweight workspace header, stale cache warning badge, truthful status indicator. |
| `desktop/src/components/layout/TopBar.module.css` | Phase W1 | Softened header styles consuming semantic canvas tokens. |
| `desktop/src/components/common/ConnectionBanner.tsx` | Phase W1 | Truthful cached data notice banner with last sync timestamp. |
| `desktop/src/App.tsx` & `App.css` | Phase W1 | Update layout grid to fluid rail + workspace model without rigid 3-column lock. |
| `desktop/src/components/common/ContextualDrawer.tsx` | Phase W2 | New reusable component supporting `docked` and `overlay` modes, focus traps, and in-session draft guards. |
| `desktop/src/components/common/ContextualDrawer.module.css` | Phase W2 | Clean drawer styling matching 12px panel standards and backdrop overlay. |
| `desktop/src/views/Operations/OperationsView.tsx` | Phase W2 | Container-responsive layout (65/35 wide, stacked narrow); on-demand facility inspector drawer. |
| `desktop/src/views/Operations/Operations.module.css` | Phase W2 | Container-responsive grid and restrained card styling. |
| `desktop/src/views/DecisionCenter/DecisionCenterView.tsx` | Phase W3 | Primary decision queue; deliberation claims drawer; display statuses mapped strictly to `DecisionRecord`. |
| `desktop/src/views/DecisionCenter/DecisionCenter.module.css` | Phase W3 | Split list-inspector styling with neutral panel surfaces. |
| `desktop/src/views/Scenarios/ScenariosView.tsx` | Phase W3 | Full-width 25-scenario catalog table; slide-over launch drawer with 4-outcome dispatch and reconciliation path. |
| `desktop/src/views/Scenarios/Scenarios.module.css` | Phase W3 | Catalog table and drawer parameter form styling. |
| `desktop/src/views/AgentCommand/AgentCommandView.tsx` | Phase W4 | Full-width operations data table; slide-over specialist telemetry inspector drawer. |
| `desktop/src/views/AgentCommand/AgentCommand.module.css` | Phase W4 | Clean table styling with muted hover states. |
| `desktop/src/views/WhatIfLab/WhatIfLabView.tsx` | Phase W4 | Comparison-first workspace with collapsible assumptions column and tabular deltas. |
| `desktop/src/views/WhatIfLab/WhatIfLab.module.css` | Phase W4 | Side-by-side comparison grid styling. |
| `desktop/src/views/ReasoningTrace/ReasoningTraceView.tsx` | Phase W4 | Chronological 4-phase trace pipeline with expandable raw JSON payloads; accessible via router navigation. |
| `desktop/src/views/ReasoningTrace/ReasoningTrace.module.css` | Phase W4 | Structured audit card styling. |
| `desktop/src/views/Evaluation/EvaluationView.tsx` | Phase W4 | Benchmark summary cards and data-dense comparative matrix tables. |
| `desktop/src/views/Evaluation/Evaluation.module.css` | Phase W4 | Data-dense table styling with tabular numerals. |

---

## 5. Acceptance Checklist

- [x] **W-A1: Rail Navigation**: 68px compact rail default with deliberate 208px toggle; all 7 canonical views accessible via mouse and `Ctrl 1` to `Ctrl 7`.
- [x] **W-A2: Deterministic State Precedence**: Strict hierarchy (`OFFLINE_CACHED` > `RECONNECTING` > `DEGRADED` > `CONNECTED`); stale data flagged with `[CACHED DATA]`; `POLLING FALLBACK ACTIVE` displayed strictly when verified.
- [x] **W-A3: Standardized Drawer System**: `ContextualDrawer` implements `docked` and `overlay` modes, keyboard focus traps, `Escape` key dismissal, and in-session draft retention.
- [x] **W-A4: Container-Responsive Operations Overview**: Balanced 65/35 grid on available width >= 960px; stacked vertical workflow on < 960px; on-demand facility drawer.
- [x] **W-A5: Unambiguous Scenario Dispatch**: Full catalog table; slide-over configuration drawer; 4-outcome dispatch contract (`ACCEPTED`, `REJECTED`, `FAILED`, `UNKNOWN`) with duplicate-click block and reconciliation path.
- [x] **W-A6: Truthful Decision Mapping**: Display statuses mapped strictly to real `DecisionRecord` schema fields (`escalation_tier`, `decision_confidence`); physical execution boundary explicitly labeled as external ERP unlinked.
- [ ] **W-A7: Observability Table & Comparison Lab**: Full-width agent operations table with telemetry drawer; comparison-first What-If simulation layout; direct navigation to Reasoning Traces.
- [ ] **W-A8: Zero Backend Modifications**: Coordinator kernel, LangGraph specialists, PostgreSQL, Redis, Neo4j, and Kafka remain 100% untouched.
- [ ] **W-A9: Scoped Zero-Emoji Validation**: Strictly 0 emoji or dingbat characters across all code, styling, and documentation within prohibited Unicode ranges.
- [ ] **W-A10: Build & Suite Verification**: Clean compilation via `npm run build` and 100% pass on `python scripts/verify_scenario_suite.py`.
