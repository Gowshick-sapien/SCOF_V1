# D09 -- SCOF Desktop Operations Console

## Complete Implementation Plan

**Document Version:** 1.0
**Status:** Final Draft
**Deliverable:** D09
**Predecessor:** D08 -- Backend API and Real-Time Layer
**Successor:** D10 -- Evaluation and Benchmarking

---

## 1. Executive Summary

D09 replaces the originally planned Next.js web-based dashboard with a **Tauri v2 + React + TypeScript desktop application** -- a native, installable SCOF Operations Console that consumes the D08 REST and WebSocket contracts without backend modification.

SCOF is an operational intelligence / control-room application. The operator sits in front of a persistent dashboard monitoring supply-chain state, disruptions, agent activity, consensus decisions, confidence, reasoning traces, what-if simulations, and system health. A desktop application delivers a dedicated, always-present operational workspace rather than a browser tab competing with other browser activity.

### Architectural Boundary

```
+----------------------------------------------+
|             SCOF Desktop Console             |
|                                              |
|  React + TypeScript                          |
|  +-- Views                                   |
|  +-- Components                              |
|  +-- Stores (Zustand)                        |
|  +-- REST client                             |
|  +-- WebSocket manager                       |
|                                              |
|  Tauri / Rust (thin native layer)            |
|  +-- System tray                             |
|  +-- Native notifications                    |
|  +-- Window management                       |
+----------------------+-----------------------+
                       |
                 REST + WebSocket
                       |
                       v
              +------------------+
              |       D08        |
              |   FastAPI :8000  |
              +--------+---------+
                       |
         +-------------+-------------+
         v             v             v
        D05           D07          Kafka
```

**Governing principle:** The Tauri/Rust layer contains no SCOF business logic and no D08 transport/orchestration logic. All communication with D08 -- REST requests, WebSocket connections, reconnection, heartbeat, backoff -- lives in the React/TypeScript layer. The Rust layer handles only genuinely native OS functionality: system tray, desktop notifications, and window management.

---

## 2. Impact Analysis on D01 through D08

### 2.1 D01 through D07 -- No Changes Required

These deliverables define the simulation data, knowledge layer, agents, orchestration, consensus engine, and observability backend. None of them reference the frontend technology or delivery medium. They remain entirely untouched.

### 2.2 D08 -- No Source Code Changes

The D08 API Gateway was explicitly designed as a frontend-agnostic service layer. Its CORS configuration is already environment-driven:

**Current state** ([config.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/config.py), line 23):

```python
CORS_ORIGINS: List[str] = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))
```

The `CORS_ORIGINS` environment variable controls which origins are permitted. The default value (`http://localhost:3000`) was set for the original Next.js plan, but the mechanism is already configurable through `.env` or Docker Compose environment without touching D08 source code.

**D09 approach to CORS:**

During D09 Phase 1, after scaffolding the Tauri v2 project:

1. Launch the desktop application against a running D08 instance.
2. Inspect the actual `Origin` header sent by the Tauri webview (varies by Tauri version and OS -- typically `tauri://localhost` or `https://tauri.localhost`).
3. Add the verified origin to the `CORS_ORIGINS` environment variable in `.env`.
4. Verify both REST and WebSocket connectivity.

No guessed Tauri origins are baked into D08 source code. This preserves the environment-driven configuration principle established in D08.

### 2.3 D10 -- Minor Wording Update

D10's acceptance criterion references "run a disruption scenario from the dashboard." The word "dashboard" remains accurate -- it is now a desktop dashboard. The full-loop wiring changes from:

```
D1 disruption -> D5 agents -> D6 CD2F -> D7 trace -> D8 API -> D9 desktop console
```

No evaluation harness code changes. The benchmark methodology, metrics computation, and RQ mapping operate against D08's API, not the frontend.

### 2.4 Docker Compose -- No Change

The desktop application runs natively on the host OS, outside Docker. It connects to D08 at `localhost:8000` (or a configured remote address). There is no need for a frontend container. The original plan's Next.js `Dockerfile` and container are eliminated entirely.

---

## 3. D08 Contract Surface (Complete Reference)

D09 consumes the full D08 API surface. This section serves as the authoritative contract reference for the desktop client implementation.

### 3.1 REST Endpoints

| Method | Endpoint | Purpose | Router Source |
|---|---|---|---|
| `GET` | `/health` | Service health check | [main.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/main.py#L125-L127) |
| `GET` | `/dashboard/state` | Aggregated operational snapshot (cached in Redis, 5s TTL) | [dashboard.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/dashboard.py) |
| `GET` | `/scenarios` | List available scenarios | [scenarios.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/scenarios.py#L25-L28) |
| `POST` | `/scenarios/trigger` | Trigger a disruption scenario (async via Kafka) | [scenarios.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/scenarios.py#L30-L65) |
| `POST` | `/scenarios/replay` | Replay a past event with new trace/event IDs | [scenarios.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/scenarios.py#L67-L100) |
| `POST` | `/whatif/run` | Submit a what-if simulation (async, returns `whatif_id`) | [whatif.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/whatif.py#L22-L61) |
| `GET` | `/whatif/{whatif_id}/result` | Poll what-if simulation status/result | [whatif.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/whatif.py#L63-L69) |
| `GET` | `/decisions` | List all decisions | [decisions.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/decisions.py#L7-L19) |
| `GET` | `/decisions/{id}/log` | Meeting log entries for a decision | [decisions.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/decisions.py#L21-L34) |
| `GET` | `/decisions/{id}/confidence` | Confidence breakdown, weights, stability | [decisions.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/decisions.py#L36-L53) |
| `GET` | `/decisions/{id}/trace` | Full reasoning trail | [decisions.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/decisions.py#L55-L68) |
| `GET` | `/evaluation/benchmark` | Benchmark results | [evaluation.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/evaluation.py#L6-L9) |
| `GET` | `/evaluation/calibration` | Calibration run history | [evaluation.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/evaluation.py#L11-L14) |
| `POST` | `/chat/query` | AI chat / semantic retrieval | [chat.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/chat.py#L10-L21) |
| `GET` | `/profile/active` | Active Domain Profile metadata | [profile.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/routers/profile.py#L8-L25) |

### 3.2 WebSocket Channels

| Channel | Path | Direction | Purpose | Source |
|---|---|---|---|---|
| Dashboard State | `ws://*/ws/dashboard/state` | Server -> Client | Live operational state push. Sends initialization payload on connect, then broadcasts on Kafka-triggered cache invalidation. | [channels.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/websocket/channels.py#L27-L38) |
| Decisions Live | `ws://*/ws/decisions/live` | Server -> Client | Live decision completion feed. Pushed when `scof.decisions.completed` Kafka events arrive. | [channels.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/websocket/channels.py#L8-L16) |
| Agents Activity | `ws://*/ws/agents/activity` | Server -> Client | Real-time agent lifecycle stream (`DISPATCHED`, `RUNNING`, `COMPLETED`, `FAILED`). Fed from `scof.agents.activity` Kafka topic. | [channels.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/websocket/channels.py#L18-L25) |

### 3.3 Kafka Topics (Internal -- Not Directly Consumed by D09)

D09 does not connect to Kafka directly. These topics are listed for context -- they drive the WebSocket events that D09 receives:

| Topic | Producer | Consumer |
|---|---|---|
| `scof.disruptions.triggered` | D08 API (scenario trigger) | D08 handler -> Coordinator |
| `scof.whatif.requested` | D08 API (what-if run) | D08 handler -> Coordinator |
| `scof.decisions.completed` | D05 Coordinator | D08 handler -> WebSocket broadcast |
| `scof.agents.activity` | D05 Coordinator | D08 handler -> WebSocket broadcast |
| `scof.orchestration.failed` | D05 Coordinator | D08 handler -> WebSocket broadcast |

---

## 4. Technology Stack (Finalized)

| Layer | Technology | Rationale |
|---|---|---|
| Desktop shell | **Tauri v2** | Lightweight native wrapper (Rust-based), approximately 10MB bundle vs 200MB+ Electron. Uses the OS native webview, no bundled Chromium. Cross-platform: Windows, macOS, Linux. Tauri v2 chosen for its stable API surface and improved permission model. |
| UI framework | **React 18+** | Component model, ecosystem maturity, identical development experience to a browser React app. |
| Language | **TypeScript (strict mode)** | Type safety across the entire frontend codebase. |
| Build tool | **Vite** | Default bundler for Tauri projects. Fast HMR, ESM-native, minimal configuration. |
| State management | **Zustand** | Lightweight, sufficient for dashboard state. Cross-view state requires stores beyond what React Context handles cleanly: `connectionStore`, `dashboardStore`, `decisionStore`, `agentStore`, `scenarioStore`. React Context remains available for truly local UI concerns (modal state, form state). |
| Styling | **CSS Modules + CSS custom properties** | Consistent with project rules (vanilla CSS). Custom property design token system for the control-room aesthetic. No Tailwind dependency. |
| Charting | **Recharts + D3.js** | Same libraries originally planned. Recharts for standard charts. D3 for custom visualizations (heatmaps, network graphs, agent contribution bars). |
| Mapping | **Leaflet + react-leaflet** | Supply chain map visualization. Same library originally planned. |
| WebSocket client | **Native WebSocket API** | Direct connection to D08 WebSocket channels. Reconnection, heartbeat, and backoff logic implemented in TypeScript, not in the Tauri/Rust layer. |
| Type generation | **OpenAPI -> TypeScript** | D08 Pydantic schemas exported as OpenAPI spec. TypeScript types generated (not manually mirrored) to prevent contract drift. |

---

## 5. Type Contract Strategy

### 5.1 The Problem with Manual Type Mirroring

D09 consumes a large API surface: dashboard state, scenarios, decisions, confidence, traces, evaluation, chat, profile, health, and three WebSocket channels. Manually maintaining TypeScript types that mirror D08's Pydantic schemas will inevitably drift as the backend evolves.

### 5.2 The Solution: Generated Types

```
D08 Pydantic schemas (source of truth)
        |
        v
FastAPI /openapi.json (auto-generated by FastAPI)
        |
        v
OpenAPI TypeScript codegen (build-time step)
        |
        v
desktop/src/api/generated/types.ts (consumed by D09)
```

**Implementation:**

1. D08 already exposes `/openapi.json` via FastAPI's built-in OpenAPI generation.
2. During D09 build, run a codegen tool (e.g., `openapi-typescript` or `openapi-typescript-codegen`) against `http://localhost:8000/openapi.json`.
3. Output goes to `desktop/src/api/generated/types.ts`.
4. The `api/client.ts` REST wrapper and `api/websocket.ts` manager import from the generated types.
5. A `package.json` script (`npm run generate:types`) automates this step.

### 5.3 WebSocket Event Types

WebSocket payloads are not covered by the OpenAPI spec (OpenAPI describes REST endpoints, not WebSocket frames). For the three WebSocket channels, define explicit TypeScript interfaces in `desktop/src/api/ws-types.ts`:

```
DashboardStatePayload      -- mirrors the dashboard state structure
DecisionCompletedPayload   -- mirrors the decision completed event envelope
AgentActivityPayload       -- mirrors the agent lifecycle event envelope
```

These types are defined once, based on the Kafka event envelope structure established in D08's [handlers.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/events/handlers.py). They should be reviewed whenever D08's event schemas change.

---

## 6. Application Architecture

### 6.1 UX Architecture: Operations as the Persistent Shell

The desktop application is not eight independent pages inside a window. **Operations is the persistent control-room shell.** The sidebar navigates between views that render in the main content area. Detail views (reasoning trace for a specific decision, what-if comparison results, decision detail panels) open as secondary panels or overlay windows, making the application feel genuinely desktop-native rather than a website packaged as an executable.

```
+--------------------------------------------------------------+
| SCOF     [*] CONNECTED              Profile: MVP-ELECTRONICS |
+----------+---------------------------------------------------+
|          |                                                   |
| Overview |              Operations                           |
| Scenarios|                                                   |
| Decisions|     Metrics + Map + Active Alerts                 |
| Agents   |                                                   |
| What-If  |                                                   |
| Traces   |                                                   |
| Eval     |                                                   |
|          |                                                   |
|          |                                                   |
| Settings |                                                   |
+----------+---------------------------------------------------+
```

Secondary panels (opened from within views):

- **Reasoning Trace** -- opens from Decision Center when inspecting a specific decision
- **What-If Comparison** -- opens from What-If Lab after simulation completes
- **Decision Detail** -- opens from the live decision feed or decision list

These panels can be:
- Inline expanded panels within the main content area
- Slide-over panels from the right edge
- Detachable windows (Tauri supports multi-window) for multi-monitor setups (nice-to-have)

### 6.2 Directory Structure

```
desktop/                              # D09 -- SCOF Desktop Operations Console
|
+-- src-tauri/                        # Tauri native layer (Rust, kept thin)
|   +-- Cargo.toml
|   +-- tauri.conf.json               # Window config, app metadata, permissions
|   +-- icons/                        # Application icons (all platforms)
|   +-- src/
|       +-- main.rs                   # Tauri entry point
|       +-- tray.rs                   # System tray setup and menu
|       +-- notifications.rs          # Desktop notification dispatch
|       +-- window.rs                 # Window state persistence (position, size)
|
+-- src/                              # React + TypeScript UI
|   +-- main.tsx                      # React entry point
|   +-- App.tsx                       # Root layout: sidebar + content area + top bar
|   +-- App.module.css                # Root layout styles
|   +-- index.css                     # Design system tokens (CSS custom properties) + resets
|   |
|   +-- api/                          # D08 communication layer
|   |   +-- client.ts                 # REST client (typed fetch wrapper)
|   |   +-- client.test.ts            # REST client tests (timeout, non-2xx, retry)
|   |   +-- websocket.ts              # WebSocket connection manager
|   |   |                             #   connect, disconnect, exponential backoff,
|   |   |                             #   heartbeat/timeout detection, reconnect,
|   |   |                             #   connection state, duplicate event filtering
|   |   +-- websocket.test.ts         # WebSocket tests (connect, reconnect, backoff,
|   |   |                             #   duplicate events, malformed payloads,
|   |   |                             #   disconnect -> reconnect -> state refresh)
|   |   +-- generated/                # Auto-generated from D08 OpenAPI
|   |   |   +-- types.ts              # TypeScript types from Pydantic schemas
|   |   +-- ws-types.ts               # WebSocket event payload types (manual, reviewed)
|   |
|   +-- stores/                       # Zustand state management
|   |   +-- connectionStore.ts        # D08 connection state (REST health, WS status)
|   |   +-- connectionStore.test.ts
|   |   +-- dashboardStore.ts         # Dashboard operational state
|   |   +-- decisionStore.ts          # Decision list and detail cache
|   |   +-- agentStore.ts             # Agent activity and status
|   |   +-- scenarioStore.ts          # Scenario library and active scenario state
|   |
|   +-- hooks/                        # Custom React hooks
|   |   +-- useDashboardState.ts      # Subscribe to dashboard state (REST + WS)
|   |   +-- useDecisions.ts           # Fetch and subscribe to decisions
|   |   +-- useAgentActivity.ts       # Subscribe to agent activity stream
|   |   +-- useWebSocket.ts           # Generic WebSocket subscription hook
|   |   +-- useProfile.ts             # Fetch active Domain Profile
|   |   +-- usePolling.ts             # Generic polling hook (for what-if result polling)
|   |
|   +-- views/                        # Top-level view components (one per sidebar entry)
|   |   +-- Operations/
|   |   |   +-- Operations.tsx        # Main control room (persistent shell)
|   |   |   +-- Operations.module.css
|   |   +-- Scenarios/
|   |   |   +-- Scenarios.tsx         # Scenario launcher + library
|   |   |   +-- Scenarios.module.css
|   |   +-- DecisionCenter/
|   |   |   +-- DecisionCenter.tsx    # Decision feed + detail inspection
|   |   |   +-- DecisionCenter.module.css
|   |   +-- AgentCommand/
|   |   |   +-- AgentCommand.tsx      # Agent activity monitor
|   |   |   +-- AgentCommand.module.css
|   |   +-- WhatIfLab/
|   |   |   +-- WhatIfLab.tsx         # What-if simulation workstation
|   |   |   +-- WhatIfLab.module.css
|   |   +-- ReasoningTrace/
|   |   |   +-- ReasoningTrace.tsx    # Decision trace / reasoning explorer (secondary panel)
|   |   |   +-- ReasoningTrace.module.css
|   |   +-- Evaluation/
|   |   |   +-- Evaluation.tsx        # Benchmark and calibration views
|   |   |   +-- Evaluation.module.css
|   |   +-- Settings/
|   |       +-- Settings.tsx          # Connection config, preferences
|   |       +-- Settings.module.css
|   |
|   +-- components/                   # Reusable UI components
|   |   +-- layout/
|   |   |   +-- Sidebar.tsx
|   |   |   +-- Sidebar.module.css
|   |   |   +-- TopBar.tsx
|   |   |   +-- TopBar.module.css
|   |   |   +-- StatusIndicator.tsx
|   |   |   +-- StatusIndicator.module.css
|   |   |   +-- SecondaryPanel.tsx    # Slide-over / expandable detail panel
|   |   |   +-- SecondaryPanel.module.css
|   |   +-- cards/
|   |   |   +-- MetricCard.tsx
|   |   |   +-- MetricCard.module.css
|   |   |   +-- AgentStatusCard.tsx
|   |   |   +-- AgentStatusCard.module.css
|   |   |   +-- DecisionCard.tsx
|   |   |   +-- DecisionCard.module.css
|   |   |   +-- DisruptionAlert.tsx
|   |   |   +-- DisruptionAlert.module.css
|   |   +-- charts/
|   |   |   +-- ConfidenceChart.tsx
|   |   |   +-- AgentContributionBar.tsx
|   |   |   +-- RiskHeatmap.tsx
|   |   |   +-- DemandForecastChart.tsx
|   |   |   +-- InventoryLevelChart.tsx
|   |   +-- map/
|   |   |   +-- SupplyChainMap.tsx
|   |   |   +-- SupplierMarker.tsx
|   |   |   +-- WarehouseMarker.tsx
|   |   |   +-- RoutePolyline.tsx
|   |   +-- meeting-log/
|   |   |   +-- MeetingLogTimeline.tsx
|   |   |   +-- AgentClaimCard.tsx
|   |   |   +-- DecisionSummaryCard.tsx
|   |   +-- chat/
|   |       +-- ChatWindow.tsx
|   |       +-- ChatMessage.tsx
|   |       +-- ChatInput.tsx
|   |
|   +-- utils/                        # Utility functions
|       +-- formatters.ts             # Number, date, duration formatting
|       +-- constants.ts              # API base URL, WS paths, retry config
|
+-- package.json                      # Dependencies: react, zustand, recharts, d3, leaflet, etc.
+-- tsconfig.json                     # TypeScript strict mode configuration
+-- vite.config.ts                    # Vite bundler configuration (Tauri default)
+-- index.html                        # HTML entry point (Vite)
+-- .eslintrc.cjs                     # ESLint configuration
```

### 6.3 Documentation Structure

```
docs/deliverables/D09_desktop_operations_console/
    README.md                   # D09 overview, objectives, acceptance criteria
    implementation_plan.md      # This document
    component_design.md         # React component hierarchy, view specifications
    ui_ux_design.md             # Wireframes, interaction patterns, control-room layout
    desktop_integration.md      # Tauri native features: tray, notifications, window
    type_contract.md            # OpenAPI codegen strategy, WebSocket type definitions
    acceptance_evidence.md      # Test results proving "done"
```

---

## 7. View Specifications and D08 API Mapping

### 7.1 Operations (Main Control Room)

The persistent shell view. Always the default landing view on application launch. Displays real-time supply chain state, system health, active disruptions, and recent decisions at a glance.

| Data | D08 Source | Update Mechanism |
|---|---|---|
| Supply chain snapshot | `GET /dashboard/state` | Initial REST fetch, then `WS /ws/dashboard/state` for live push |
| Active disruptions count | Derived from dashboard state payload | Automatic via WS |
| System health | `GET /health` | Periodic polling (every 30s) |
| Active profile metadata | `GET /profile/active` | Single fetch on startup |
| Recent decisions (latest 5) | `GET /decisions` | REST fetch + `WS /ws/decisions/live` for new entries |

**Layout:**

```
+-----------------------------------------------------------+
|  System Health: Nominal    Active Disruptions: 2           |
+-----------------------------------------------------------+
|                                                           |
|  +----------+  +----------+  +----------+  +----------+  |
|  | Supply   |  | Inventory|  | Risk     |  | Agents   |  |
|  | Health   |  | Health   |  | Level    |  | Active   |  |
|  | [metric] |  | [metric] |  | [metric] |  | [4/4]    |  |
|  +----------+  +----------+  +----------+  +----------+  |
|                                                           |
|  +----------------------------------------------------+  |
|  |                                                    |  |
|  |            SUPPLY CHAIN MAP (Leaflet)              |  |
|  |                                                    |  |
|  +----------------------------------------------------+  |
|                                                           |
|  Latest Decisions                                         |
|  +----------------------------------------------------+  |
|  | DEC-1042  Supplier delay  Confidence: 87%  FAST    |  |
|  | DEC-1041  Demand spike    Confidence: 92%  FAST    |  |
|  +----------------------------------------------------+  |
+-----------------------------------------------------------+
```

### 7.2 Scenarios (Scenario Launcher + Library)

Scenario management: browse the library, trigger disruptions, replay past events, monitor results.

| Action | D08 Source |
|---|---|
| List available scenarios | `GET /scenarios` |
| Trigger a scenario | `POST /scenarios/trigger` |
| Replay a past event | `POST /scenarios/replay` |
| Monitor result | `WS /ws/dashboard/state` (state update after orchestration completes) |

**Controls:**

- Disruption type selector (supplier delay, transport failure, demand spike, adverse weather)
- Severity slider (1-5)
- Duration input
- Target entity picker (from profile topology)
- Trigger button (returns `event_id` and `trace_id` immediately)
- Replay button (for past events, by `event_id`)

**After trigger:** The view shows the returned `event_id` and `trace_id` and indicates "TRIGGERED -- awaiting orchestration." The result arrives asynchronously via the dashboard state WebSocket and the decisions live WebSocket.

### 7.3 Decision Center

Live decision feed and deep inspection. Combines the AI Meeting Log and Confidence/Disagreement views from the original FR-9.2.

| Data | D08 Source |
|---|---|
| Live decision stream | `WS /ws/decisions/live` |
| Decision list (historical) | `GET /decisions` |
| Meeting log (per decision) | `GET /decisions/{id}/log` |
| Confidence breakdown | `GET /decisions/{id}/confidence` |
| Reasoning trace | `GET /decisions/{id}/trace` |

**Layout:**

Left panel: scrollable decision feed (live + historical). Each entry shows decision ID, recommendation summary, confidence percentage, escalation tier badge (FAST / SLOW / ESCALATED), and consensus stability indicator.

Right panel (or secondary panel): selected decision detail, showing:

```
Decision #DEC-1042
--------------------
Recommendation: [action text]
Confidence: 87%
Escalation Tier: FAST PATH
Consensus Stability: STABLE

Agent Contributions
--------------------
Demand       ########  0.86
Inventory    ######### 0.91
Supplier     #######   0.78
Transport    ########  0.84

Agent Weights
--------------------
[weighted bar chart from /confidence endpoint]

Meeting Log
--------------------
[timeline from /log endpoint]
```

Clicking "View Full Trace" opens the Reasoning Trace Explorer as a secondary panel.

### 7.4 Agent Command Center

Real-time agent execution monitoring. The desktop approach is particularly effective here -- a persistent, always-visible agent activity panel fed directly from D08's Kafka-backed agent lifecycle stream.

| Data | D08 Source |
|---|---|
| Agent lifecycle events | `WS /ws/agents/activity` |

**Display:**

```
Agent Execution Monitor
-----------------------
Demand Agent       [*] COMPLETED    842ms
Inventory Agent    [*] COMPLETED    615ms
Supplier Agent     [*] COMPLETED    1.2s
Transportation     [>] RUNNING      438ms
```

Per-agent row: name, status indicator (color-coded), execution duration timer (live for RUNNING), status text. Historical runs visible as a scrollable timeline below the current execution.

Status states: `DISPATCHED` (queued), `RUNNING` (in progress), `COMPLETED` (success), `FAILED` (error with message).

### 7.5 What-If Lab

Simulation workstation. Modify parameters, run counterfactual analyses, compare outcomes against the baseline scenario.

| Action | D08 Source |
|---|---|
| Submit simulation | `POST /whatif/run` |
| Poll result | `GET /whatif/{id}/result` (polled until status != "RUNNING") |

**Layout:**

```
BASE SCENARIO                    WHAT-IF MODIFICATION
------------------               ------------------
Severity: 2                      Severity: [4]  (slider)
Scenario: scen-01                Scenario: scen-01
                                 Severity Override: [4]

                    [ RUN SIMULATION ]

Result (when complete):
-----------------------
Risk        +34%
Inventory   -18%
Lead time   +22%
Confidence  84%
```

Side-by-side comparison opens as a secondary panel when results arrive.

### 7.6 Reasoning Trace Explorer

Dedicated investigation view for a single decision's full reasoning chain. Opens as a secondary panel from the Decision Center, not as a standalone sidebar entry. (The "Traces" sidebar entry navigates to Decision Center with the trace panel pre-opened for the most recent decision.)

| Data | D08 Source |
|---|---|
| Decision metadata | `GET /decisions/{id}/log` |
| Confidence data | `GET /decisions/{id}/confidence` |
| Full trace | `GET /decisions/{id}/trace` |

**Display:** Vertical pipeline visualization:

```
Decision #DEC-1042

Scenario
+-- Supplier delay -- Supplier-03
         |
         v
Agent Evidence
+-- Demand Agent
|   +-- claim, confidence, evidence
+-- Inventory Agent
|   +-- claim, confidence, evidence
+-- Supplier Agent
|   +-- claim, confidence, evidence
+-- Transportation Agent
    +-- claim, confidence, evidence
         |
         v
Consensus
+-- recommendation tallies
+-- agent weights
+-- confidence
+-- stability
         |
         v
Final Decision
+-- recommendation
+-- escalation tier
+-- reasoning summary
```

Each node is expandable to show raw data and reasoning steps from the D07 stored traces.

### 7.7 Evaluation View

Benchmark and calibration results display. Primarily relevant for D10, but the view is built in D09 to consume D08's evaluation endpoints.

| Data | D08 Source |
|---|---|
| Benchmark results | `GET /evaluation/benchmark` |
| Calibration runs | `GET /evaluation/calibration` |

**Display:**

- CD2F vs. single-agent vs. majority-voting comparison table
- Accuracy, consensus quality, agreement rate metrics
- Calibration kappa trend over time (line chart)
- Response time distribution (fast-path vs. slow-path)

### 7.8 Settings

Connection configuration, local preferences, and system information.

| Feature | Implementation |
|---|---|
| D08 API URL | Persisted in Tauri app config (local storage or Tauri store plugin) |
| Connection status | Read from `connectionStore` (Zustand) |
| Theme selection | CSS custom property overrides (dark mode default, light mode option) |
| Notification preferences | Toggle desktop notifications on/off per event type |
| Profile display | Read-only display of `GET /profile/active` response |
| Application version | Tauri app metadata |

---

## 8. Desktop-Native Features

### 8.1 Responsibility Boundary

| Responsibility | Layer | Rationale |
|---|---|---|
| REST requests | TypeScript (`api/client.ts`) | All D08 communication in one place |
| WebSocket connections | TypeScript (`api/websocket.ts`) | All D08 communication in one place |
| WebSocket reconnection + backoff | TypeScript (`api/websocket.ts`) | Transport logic, not native OS functionality |
| Heartbeat / timeout detection | TypeScript (`api/websocket.ts`) | Transport logic |
| Connection state management | TypeScript (`stores/connectionStore.ts`) | Application state |
| System tray | Rust (`src-tauri/src/tray.rs`) | Genuinely native OS functionality |
| Desktop notifications | Rust (`src-tauri/src/notifications.rs`) | Genuinely native OS functionality |
| Window state persistence | Rust (`src-tauri/src/window.rs`) | Genuinely native OS functionality |

The TypeScript layer invokes Tauri commands (via `@tauri-apps/api`) to trigger native notifications and update tray state. The Rust layer never initiates D08 communication.

### 8.2 Feature Classification

**Must-have for D09:**

| Feature | Description |
|---|---|
| Native window | Dedicated application window outside the browser |
| Connection status | Top bar indicator showing live connection state to D08 (connected / reconnecting / disconnected) |
| WebSocket reconnect | Exponential backoff reconnection in TypeScript. On reconnect, re-fetch dashboard state to rehydrate. |
| System tray | Persistent tray icon. Tray color reflects connection status: green = connected, yellow = reconnecting, red = disconnected. |
| Critical notification | Desktop-native notification for escalation events and decision completions |
| Persistent window state | Remember window position and size across sessions |

**Nice-to-have (do not delay core dashboard for these):**

| Feature | Description |
|---|---|
| Multi-monitor optimization | Detachable secondary windows for trace/detail views |
| Sophisticated tray menu | Extended menu with recent decisions, quick scenario trigger |
| Advanced notification preferences | Per-event-type notification controls, quiet hours |
| Fullscreen control-room mode | Kiosk-style fullscreen toggle (F11) |

### 8.3 Window Lifecycle

| User Action | Application Behavior |
|---|---|
| Click minimize button | Minimize to taskbar (standard OS behavior) |
| Click close button (X) | Minimize to system tray, maintain WebSocket connections |
| Tray menu -> "Open Console" | Restore window from tray |
| Tray menu -> "Quit" | Gracefully close all WebSocket connections, terminate application |
| OS keyboard shortcut (Alt+F4 / Cmd+Q) | Same as "Quit" -- graceful shutdown |

**Tray menu structure:**

```
SCOF
----------------
Open Console
Connection: Connected
----------------
Quit
```

---

## 9. WebSocket Manager Specification

The WebSocket manager (`desktop/src/api/websocket.ts`) is the single module responsible for all real-time D08 communication. It handles:

### 9.1 Connection Lifecycle

```
connect(channel: string, onMessage: (data) => void)
disconnect(channel: string)
disconnectAll()
getState(channel: string): ConnectionState
```

`ConnectionState`: `CONNECTING` | `CONNECTED` | `DISCONNECTED` | `RECONNECTING`

### 9.2 Reconnection Strategy

- On disconnect: wait `initialDelay` (1 second), then reconnect.
- On repeated failure: exponential backoff with jitter. Delays: 1s, 2s, 4s, 8s, 16s, capped at 30s.
- On reconnect success: emit `CONNECTED` state, trigger state rehydration (re-fetch `GET /dashboard/state` for the dashboard channel).
- Max reconnect attempts: unlimited (the application should always attempt to reconnect).

### 9.3 Heartbeat / Timeout Detection

- If no message received on a channel for 60 seconds, consider the connection stale.
- Send a WebSocket ping frame (or application-level keepalive if the server does not support ping/pong).
- If no pong/response within 10 seconds, treat as disconnect and trigger reconnection.

### 9.4 Duplicate Event Filtering

D08's Kafka consumer uses Redis-based idempotency to prevent duplicate WebSocket broadcasts. However, reconnection edge cases can cause the client to receive events it has already processed. The WebSocket manager maintains a short-lived set of recent `event_id` values (last 100) and drops duplicates.

### 9.5 Error Handling

- Malformed JSON payload: log warning, do not crash. Skip the event.
- Non-JSON WebSocket frame: log warning, skip.
- Connection refused: enter reconnection loop.

---

## 10. REST Client Specification

The REST client (`desktop/src/api/client.ts`) wraps the `fetch` API with:

### 10.1 Configuration

```typescript
interface ApiClientConfig {
  baseUrl: string;       // e.g., "http://localhost:8000"
  timeout: number;       // Request timeout in ms (default: 10000)
  retries: number;       // Max retries for transient failures (default: 2)
  retryDelay: number;    // Base delay between retries in ms (default: 1000)
}
```

### 10.2 Typed Methods

All methods return typed responses using the generated OpenAPI types:

```typescript
getDashboardState(): Promise<DashboardState>
getScenarios(): Promise<ScenarioList>
triggerScenario(scenarioId: string): Promise<TriggerResponse>
replayScenario(eventId: string): Promise<ReplayResponse>
runWhatIf(request: WhatIfRequest): Promise<WhatIfResponse>
getWhatIfResult(whatifId: string): Promise<WhatIfResult>
getDecisions(): Promise<Decision[]>
getDecisionLog(decisionId: string): Promise<MeetingLog>
getDecisionConfidence(decisionId: string): Promise<ConfidenceBreakdown>
getDecisionTrace(decisionId: string): Promise<ReasoningTrail>
getBenchmark(): Promise<BenchmarkResult>
getCalibration(): Promise<CalibrationRuns>
chatQuery(query: string, limit?: number): Promise<ChatResult>
getActiveProfile(): Promise<ProfileMetadata>
healthCheck(): Promise<HealthStatus>
```

### 10.3 Error Handling

- Timeout: reject with a typed `ApiTimeoutError`.
- Non-2xx response: reject with `ApiError` containing status code, message, and response body.
- Network error (D08 unreachable): reject with `ApiNetworkError`. Update `connectionStore` state to `DISCONNECTED`.
- Retry logic: retry on 502, 503, 504 status codes with exponential backoff. Do not retry on 4xx errors.

---

## 11. Zustand Store Architecture

| Store | Responsibility | Updated By |
|---|---|---|
| `connectionStore` | D08 connection state for REST and each WS channel. Exposes `isConnected`, `wsStates`, `lastHealthCheck`. | REST health polling, WebSocket manager state changes |
| `dashboardStore` | Operational dashboard data: metrics, alerts, disruption count, system health. | REST initial fetch + WS `dashboard/state` push |
| `decisionStore` | Decision list, selected decision detail, meeting log, confidence, trace. | REST fetches + WS `decisions/live` push |
| `agentStore` | Agent activity log, current execution statuses per agent. | WS `agents/activity` push |
| `scenarioStore` | Scenario library, active trigger state, what-if parameters and results. | REST fetches |

Each store follows the pattern:

```typescript
interface DashboardStore {
  state: DashboardState | null;
  isLoading: boolean;
  error: string | null;
  fetchState: () => Promise<void>;
  updateFromWebSocket: (payload: DashboardStatePayload) => void;
}
```

---

## 12. Updated Requirements Mapping

### 12.1 Functional Requirements (Revised FR-9.x)

| ID | Requirement |
|---|---|
| FR-9.1 | The system shall provide an Operational Dashboard and interactive Supply Chain Map within the Tauri desktop application (React + TypeScript, Leaflet, D3/Recharts), reading map bounds and entity labels from the Domain Profile (`dashboard.yaml`). |
| FR-9.2 | The system shall provide an AI Meeting Log view and a Confidence and Disagreement View, accessible from the Decision Center. |
| FR-9.3 | The system shall provide a What-If Simulation Lab and a Scenario Library within the desktop console, supporting parameter modification and outcome comparison. |
| FR-9.4 | The system shall provide a Reasoning Trace Explorer allowing step-through of D07's stored traces, rendered as a vertical pipeline visualization. |
| FR-9.5 | The system shall provide a Recommendation Timeline and a basic Risk Heatmap within the Operations view. |
| FR-9.6 | The system shall provide an AI Chat panel for natural-language Q&A over operational data, integrated into the desktop console. |
| FR-9.7 | The system shall provide an Agent Command Center displaying real-time agent execution monitoring via the `WS /ws/agents/activity` channel. |
| FR-9.8 | The system shall provide desktop-native operational features: system tray with connection status, desktop notifications for critical events, persistent window state, and close-to-tray behavior with explicit quit action. |
| FR-9.9 | The system shall generate TypeScript types from D08's OpenAPI specification rather than manually maintaining duplicate type definitions. |

### 12.2 Acceptance Criteria

**Primary acceptance criterion (revised from original):**

A reviewer can launch the SCOF Desktop Operations Console, connect to a running D08 instance, trigger a what-if scenario, observe real-time agent activity and decision progression, and inspect the resulting meeting log, confidence breakdown, and reasoning trace -- all within the desktop application, without needing D01-D07 explained separately.

**Desktop-specific acceptance criteria:**

| Criterion | Verification |
|---|---|
| The application installs and launches as a native executable on Windows (`.msi` or `.exe`) | Build with `npm run tauri build`, install, launch |
| The system tray icon reflects live connection status to D08 | Verify green (connected), red (kill D08 -> red), yellow (restart D08 -> yellow -> green) |
| Closing the window (X button) minimizes to system tray and maintains WebSocket connections | Close window, verify tray icon persists, verify WS messages still update stores |
| Tray menu "Quit" terminates WebSocket connections and exits the application | Click Quit, verify process terminates, verify no orphaned connections |
| Desktop notifications fire for completed decisions | Trigger a scenario, wait for orchestration, verify OS notification appears |
| The application reconnects automatically after a transient D08 outage | Kill D08 container, wait 10s, restart container, verify reconnection and state rehydration |
| TypeScript types are generated from D08 OpenAPI spec | Run `npm run generate:types`, verify `generated/types.ts` matches current D08 schemas |

---

## 13. Implementation Phases

### Phase 1: Scaffold and Core Shell

**Objective:** Standalone Tauri + React application that connects to D08 and proves bidirectional communication.

**Tasks:**

1. Initialize Tauri v2 + React + TypeScript project in `desktop/` using `npm create tauri-app`
2. Configure Vite build, TypeScript strict mode, ESLint
3. Set up CSS design system: `index.css` with custom properties (color tokens, spacing, typography, dark theme)
4. Build the REST client (`api/client.ts`) with typed fetch wrapper, timeout, retry logic
5. Build the WebSocket manager (`api/websocket.ts`) with connect, disconnect, exponential backoff, heartbeat, reconnection, duplicate filtering
6. Set up OpenAPI type generation pipeline (`npm run generate:types`)
7. Define WebSocket event types (`api/ws-types.ts`)
8. Create Zustand stores: `connectionStore`, `dashboardStore`
9. Build root layout (`App.tsx`): sidebar navigation, top bar with connection status, main content area
10. **CORS verification:** Launch app, inspect Tauri webview `Origin` header, add to `.env` `CORS_ORIGINS`, verify REST and WebSocket connectivity

**Exit criteria:** The application launches as a native window, connects to D08, displays connection status in the top bar, and receives a dashboard state payload via WebSocket.

### Phase 2: Operations and Agent Views

**Objective:** The primary operational views are functional with live data.

**Tasks:**

1. Operations view: metric cards (supply health, inventory health, risk level, agent count), system health indicator
2. Supply Chain Map: Leaflet integration, supplier/warehouse/route markers from profile topology
3. Recent decisions panel: latest 5 decisions from `GET /decisions`
4. Agent Command Center: real-time agent status cards fed from `WS /ws/agents/activity`
5. Create Zustand stores: `agentStore`
6. Active disruption count and alert display

**Exit criteria:** Operations view displays live dashboard state with map. Agent Command Center shows real-time agent lifecycle events during a triggered scenario.

### Phase 3: Decision and Scenario Views

**Objective:** Full scenario lifecycle and decision inspection are functional.

**Tasks:**

1. Scenarios view: scenario library list, trigger form (type, severity, target), trigger button, replay button
2. Create Zustand stores: `scenarioStore`, `decisionStore`
3. Decision Center: scrollable decision feed (live via WS + historical via REST)
4. Decision detail secondary panel: meeting log timeline, confidence chart, agent contribution bars
5. What-If Lab: parameter modification form, simulation execution, result polling, comparison display

**Exit criteria:** A reviewer can trigger a scenario, see it appear in the decision feed, and inspect the full meeting log, confidence breakdown, and agent contributions for the resulting decision.

### Phase 4: Investigation and Analysis Views

**Objective:** Deep inspection and evaluation views are functional.

**Tasks:**

1. Reasoning Trace Explorer: vertical pipeline visualization (scenario -> agents -> consensus -> decision), expandable nodes
2. Evaluation view: benchmark results table, calibration kappa trend chart, CD2F vs. baseline comparison
3. AI Chat panel: chat input, message display, semantic retrieval results from `POST /chat/query`
4. Recommendation Timeline component (within Operations view)
5. Risk Heatmap component (within Operations view)

**Exit criteria:** The reasoning trace for a completed decision renders as a navigable pipeline. Evaluation view displays benchmark data. AI Chat returns search results.

### Phase 5: Desktop Integration and Polish

**Objective:** Desktop-native features are implemented. Application is build-ready.

**Tasks:**

1. System tray: Rust tray module, icon reflecting connection state, tray menu (Open Console / Connection status / Quit)
2. Close-to-tray behavior: X button minimizes to tray, Quit terminates
3. Desktop notifications: Rust notification module, triggered from TypeScript via Tauri commands for decision completions and critical disruptions
4. Window state persistence: save/restore position and size via Rust window module
5. Settings view: D08 API URL configuration, notification toggles, theme switch
6. Transport layer tests: `client.test.ts`, `websocket.test.ts`, `connectionStore.test.ts`
7. Cross-platform build verification (Windows primary target)
8. Polish: loading states, error states, empty states, transition animations

**Exit criteria:** All must-have desktop features functional. Transport tests pass. Windows `.msi` build installs and launches correctly. All acceptance criteria from Section 12.2 met.

---

## 14. Verification Plan

### 14.1 Automated Tests

| Command | Scope |
|---|---|
| `npm test` | React component unit tests + store tests + transport layer tests (Vitest) |
| `npm run type-check` | TypeScript strict mode compilation (zero errors) |
| `npm run lint` | ESLint code quality checks |
| `npm run generate:types` | OpenAPI type generation (verify no generation errors) |

### 14.2 Transport Layer Tests (Required)

Tests in `api/client.test.ts`:

| Test Case | Verifies |
|---|---|
| REST request succeeds with typed response | Happy path, type correctness |
| REST request times out | Timeout handling, `ApiTimeoutError` thrown |
| REST non-2xx response | Error handling, `ApiError` with status code |
| REST 502/503/504 triggers retry | Retry logic with backoff |
| REST 4xx does not retry | No retry on client errors |
| Network error updates connection store | `connectionStore` state transitions |

Tests in `api/websocket.test.ts`:

| Test Case | Verifies |
|---|---|
| WebSocket connects and receives message | Happy path |
| WebSocket reconnects after disconnect | Reconnection logic |
| Exponential backoff between reconnect attempts | Backoff timing (1s, 2s, 4s, ...) |
| Backoff caps at 30 seconds | Maximum delay enforcement |
| Duplicate event IDs are filtered | Idempotency at the client level |
| Malformed JSON payload does not crash | Graceful error handling |
| Disconnect -> reconnect -> state refresh | Rehydration after reconnection |
| Connection state transitions emit correctly | `CONNECTING` -> `CONNECTED` -> `DISCONNECTED` -> `RECONNECTING` -> `CONNECTED` |

Tests in `stores/connectionStore.test.ts`:

| Test Case | Verifies |
|---|---|
| Initial state is disconnected | Default state |
| Health check success updates state | `isConnected` = true |
| Health check failure updates state | `isConnected` = false |
| WebSocket state changes propagate | `wsStates` map updates |

### 14.3 Manual Verification

| Step | What to Verify |
|---|---|
| Launch desktop application and connect to running Docker Compose stack (D01-D08) | Application opens, connection indicator shows green, dashboard state loads |
| Trigger a scenario from Scenarios view | `POST /scenarios/trigger` returns event_id, status shows "TRIGGERED" |
| Observe real-time updates during orchestration | Agent Command Center shows agent lifecycle (DISPATCHED -> RUNNING -> COMPLETED). Dashboard state updates via WebSocket. Decision appears in Decision Center via `WS /ws/decisions/live`. |
| Inspect completed decision | Meeting log timeline renders agent claims. Confidence chart shows per-agent weights. Agent contribution bars display correctly. |
| Open Reasoning Trace Explorer for the decision | Vertical pipeline renders: scenario -> agent evidence (expandable) -> consensus -> final decision |
| Run a what-if simulation | Submit modified parameters, poll result, view comparison |
| Verify system tray behavior | Minimize to tray (X button). Tray icon is green. Open Console from tray menu restores window. |
| Kill D08 container | Connection indicator turns red. Tray icon turns red. Application enters reconnection loop. |
| Restart D08 container | Connection indicator turns yellow (reconnecting), then green (connected). Dashboard state rehydrates automatically. |
| Quit from tray menu | Application terminates. Process exits. No orphaned connections. |

---

## 15. Files to Modify in Existing Codebase

These changes are preparatory -- applied before D09 implementation begins.

### 15.1 Documentation Updates

| File | Change |
|---|---|
| [implementation_plan.md](file:///d:/projects/SCOF_V1/SCOF/docs/implementation_plan.md) | Update D09 entry: "Frontend Dashboard" -> "SCOF Desktop Operations Console." Update technology references. Update dependency graph and summary table. |
| [srs.md](file:///d:/projects/SCOF_V1/SCOF/docs/srs.md) | Update Section 3.9 (FR-9.x): revised requirements per Section 12.1 of this document. Update Section 4.1: "Desktop application (Tauri v2 + React + TypeScript)" instead of "Web dashboard (React/Next.js) accessible via browser." |
| [repository_structure.md](file:///d:/projects/SCOF_V1/SCOF/docs/repository_structure.md) | Replace `frontend/` directory tree with `desktop/` structure per Section 6.2. Update D09 deliverable docs path to `D09_desktop_operations_console/`. |

### 15.2 Directory Operations

| Operation | Path | Reason |
|---|---|---|
| Rename | `docs/deliverables/D09_frontend_dashboard/` -> `docs/deliverables/D09_desktop_operations_console/` | Reflects the architectural shift |
| Delete | `frontend/.gitkeep` | Directory will be replaced by `desktop/` during Phase 1 scaffold |
| Remove | `frontend/` directory | No longer used |

### 15.3 No D08 Source Code Changes

The CORS origin for the Tauri webview will be added to the `.env` file during Phase 1, not hardcoded into [config.py](file:///d:/projects/SCOF_V1/SCOF/services/api/src/config.py). The D08 source code remains untouched.

---

## 16. Updated Roadmap Summary

| Deliverable | Name | Status |
|---|---|---|
| D01 | Simulation Foundation | Complete |
| D02 | Knowledge and Data Layer | Complete |
| D03 | Forecasting Agents | Complete |
| D04 | Reliability Agents | Complete |
| D05 | Agent Orchestration | Complete |
| D06 | Consensus / Arbitration | Complete |
| D07 | Observability | Complete |
| D08 | Backend API and Real-Time Layer | Complete |
| **D09** | **SCOF Desktop Operations Console** | **Next** |
| D10 | Evaluation and Benchmarking | Pending |

---

## 17. Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Tauri v2 webview rendering inconsistencies across OS versions | UI may render differently on Windows WebView2 vs macOS WebKit vs Linux WebKitGTK | Primary target is Windows. Test on macOS/Linux during Phase 5 polish. Use standard CSS, avoid browser-specific features. |
| OpenAPI type generation produces incomplete types for complex nested schemas | Manual type corrections needed, defeating the purpose | Validate generated types against actual API responses during Phase 1. Supplement with manual types only where codegen falls short. |
| WebSocket reconnection edge cases cause stale state | Dashboard shows outdated data after reconnect | On reconnect, always re-fetch full state via REST before trusting WebSocket push. Clear stores on disconnect. |
| Tauri v2 CORS/origin behavior changes between versions | REST/WebSocket calls fail silently | Pin Tauri version in `Cargo.toml`. Verify CORS on every Tauri upgrade. Document the verified origin in `.env.example`. |
| Desktop packaging increases development cycle time | Slower iteration than browser-based development | Use `npm run tauri dev` for hot-reload during development. Only build native packages during Phase 5 and CI. |
