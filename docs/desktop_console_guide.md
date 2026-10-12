# SCOF Desktop Operations Console — Master Operational Guide

This document provides a comprehensive operational reference for the Supply Chain Cognitive Orchestration Framework (SCOF) Desktop Operations Console. It details the architecture, page layouts, functional controls, testing procedures, and the end-to-end operational workflow for running full disruption scenarios.

---

## 1. System Overview & Console Architecture

The SCOF Desktop Operations Console serves as the centralized human-in-the-loop (HITL) control room for multi-agent autonomous supply chain orchestration. It interfaces with the backend microservices fleet via REST APIs and real-time WebSocket channels managed by the FastAPI Gateway.

### Core Architecture Components

- **Frontend Runtime**: React 19, TypeScript, Vite, and Tauri v2 desktop shell.
- **Backend API Gateway**: FastAPI running on port 8000 (`services/api`).
- **Orchestration Kernel**: LangGraph Coordinator running on port 8010 (`services/coordinator`).
- **Autonomous Specialist Fleet**:
  - Demand Forecasting Agent (`services/agents/demand`, port 8011)
  - Inventory Risk Agent (`services/agents/inventory`, port 8012)
  - Supplier Intelligence Agent (`services/agents/supplier`, port 8013)
  - Transportation Logistics Agent (`services/agents/transport`, port 8014)
- **Consensus Engine**: CD2F Consensus Arbitration Service running on port 8020 (`services/consensus`).
- **Observability & Storage**: PostgreSQL with pgvector semantic memory and Kafka event streaming bus running on port 8030 (`services/observability`).

---

## 2. Global Shell & Navigation Framework

The application window is designed around an ultra-minimal dark mode aesthetic adhering to Apple Human Interface Guidelines (HIG), featuring frosted acrylic vibrancy, high-contrast typography, and native desktop controls.

### 2.1 Window Controls & Header Bar

- **Native Window Controls (Sidebar Top-Left)**:
  - **Red Button (Close)**: Closes the desktop window via Tauri window API (`appWindow.close()`) or browser close.
  - **Yellow Button (Minimize)**: Minimizes the application window to the taskbar.
  - **Green Button (Zoom / Maximize)**: Toggles window maximization or full-screen mode.
- **TopBar Toolbar (`desktop/src/components/layout/TopBar.tsx`)**:
  - **View Title**: Displays the human-readable label of the active screen.
  - **Profile Badge**: Indicates the active domain profile (`MVP-ELECTRONICS`).
  - **System Connection Status Pill**: Displays real-time operational status:
    - `CONNECTED` (Green): Backend API Gateway and all 3 WebSocket channels active.
    - `RECONNECTING` (Amber): Network or container blip; WebSocket auto-reconnect in progress.
    - `DISCONNECTED` (Red): API Gateway unreachable; operating in offline fallback mode.
  - **UTC Clock**: Real-time Greenwich Mean Time reference clock.
  - **Shortcuts HUD Button (`?`)**: Opens the modal listing all hotkeys (`Shift + ?`).
  - **Intelligence Assistant Button (`Ctrl + K` / `Cmd + K`)**: Toggles the slide-over AI chat panel.

### 2.2 Global Hotkeys & Shortcuts

| Hotkey | Target Destination / Action | Reference Component |
| :--- | :--- | :--- |
| **Ctrl + 1** | Operations Overview | `desktop/src/views/Operations/OperationsView.tsx` |
| **Ctrl + 2** | Decision Center & Meeting Log | `desktop/src/views/DecisionCenter/DecisionCenterView.tsx` |
| **Ctrl + 3** | Scenario Launcher & Disruptions | `desktop/src/views/Scenarios/ScenariosView.tsx` |
| **Ctrl + 4** | Agent Command Center | `desktop/src/views/AgentCommand/AgentCommandView.tsx` |
| **Ctrl + 5** | What-If Simulation Lab | `desktop/src/views/WhatIfLab/WhatIfLabView.tsx` |
| **Ctrl + 6** | Reasoning Trace Explorer | `desktop/src/views/ReasoningTrace/ReasoningTraceView.tsx` |
| **Ctrl + 7** | Evaluation & Benchmarks | `desktop/src/views/Evaluation/EvaluationView.tsx` |
| **Ctrl + K** | Toggle AI Operational Assistant Drawer | `desktop/src/components/chat/AIChatDrawer.tsx` |
| **Shift + ?** | Toggle Keyboard Shortcuts HUD Modal | `desktop/src/components/modals/ShortcutsModal.tsx` |
| **Esc** | Dismiss Open Modal or Drawer | Global window handler |

### 2.3 Global Banner & Notification System

- **Connection Banner (`desktop/src/components/common/ConnectionBanner.tsx`)**:
  - Automatically slides down across the top of the interface if connectivity to `http://localhost:8000` is lost.
  - Informs the operator when operating in offline/cached fallback mode and displays reconnection attempts.
- **Decision Notification Toast (`desktop/src/components/common/NotificationToast.tsx`)**:
  - Listens to incoming decision completion events on `/ws/decisions/live`.
  - Displays a floating notification in the bottom-right corner when an arbitration completes.
  - Shows Scenario ID, Escalation Tier (`FAST_PATH` or `HUMAN_ESCALATION`), final recommendation snippet, and WCS confidence percentage.
  - Features an **Inspect Decision ->** button that immediately navigates to the Decision Center with the completed record selected.

---

## 3. Comprehensive Page-by-Page Specifications

### Page 1: Operations Overview (`desktop/src/views/Operations/OperationsView.tsx`)

#### Purpose
Provides executive and tactical situational awareness over the global supply chain network, real-time key performance indicators (KPIs), active disruption alerts, and recent consensus arbitrations.

#### What It Displays
1. **Top Metric Cards**:
   - **Supply Chain Reliability**: Current network reliability index (e.g., 96.4%) with target variance (+1.2% vs target).
   - **Inventory Stock Coverage**: Aggregate inventory buffer (18.4 days) against the safety threshold (14.0 days).
   - **Active Disruption Risk**: State badge showing `NOMINAL` (when all nodes are stable) or `ELEVATED` (when active arbitrations or disruptions are in flight).
   - **Specialist Agents Online**: Autonomous fleet availability counter (4 / 4) with A2A discovery confirmation.
2. **Global Supply Network Topology Map**:
   - Declarative SVG visualizer representing the `mvp-electronics` domain network:
     - Tier-1 Suppliers: `sup-01` (Global Silicon), `sup-02` (Pacific Semi), `sup-03` (Apex Micro).
     - Central Assembly Hub: `mfg-01` (Shenzhen Plant).
     - Regional Distribution Centers: `wh-01` (Frankfurt Regional DC), `dc-02` (Amsterdam DC).
     - Shipping corridors and freight lanes with dynamic route glow filters.
3. **Operational Alerts Panel**:
   - Real-time alert card showing active scenario disruptions, or "ALL SYSTEMS NORMAL - NOMINAL" when idle.
4. **Recent Decisions Stream**:
   - Card listing the 4 most recent decisions fetched from the database ledger.
   - Shows scenario tags, escalation tier badges, recommendation text, confidence scores, and arbitration methods (`CD2F`).

#### Intended Actions & Options
- **Decision Inspection**: Clicking any row in the Recent Decisions list navigates directly to the **Decision Center** with that record loaded.

---

### Page 2: Decision Center & Meeting Log (`desktop/src/views/DecisionCenter/DecisionCenterView.tsx`)

#### Purpose
Serves as the explainability and audit center for multi-agent deliberations. It provides a readable transcript of agent debate and shows the mathematical resolution of conflicting domain claims.

#### What It Displays
1. **Left Column (Decisions Stream)**:
   - Chronological list of all persisted decisions merged with live real-time completions.
   - Total count badge of recorded decisions.
   - Cards display Scenario ID, Weighted Consensus Stability (WCS) percentage, recommendation preview, escalation tier, and timestamp.
2. **Right Column (Selected Decision Inspection)**:
   - **Header & Trace Action**: Scenario name, Decision ID, and an **"Explore Reasoning Trace"** button that jumps to the trace pipeline view.
   - **Metadata Grid**:
     - Escalation Tier: `FAST_PATH` (automated execution) vs `HUMAN_ESCALATION` (operator sign-off required).
     - Consensus Stability: WCS stability percentage.
     - Decision Method: Arbitration engine used (`CD2F`).
     - Profile Scope: Active configuration profile (`mvp-electronics`).
   - **Winning Recommendation Callout**: Prominent banner presenting the arbitrated mitigation action.
   - **AI Meeting Log Timeline**:
     - Chronological conversational transcript capturing statements made during arbitration.
     - Details speaker (`Demand Agent`, `Inventory Agent`, `Supplier Agent`, `Transport Agent`, `CD2F Engine`), statement type (`CLAIM`, `WEIGHT_REPORT`, `TALLY`, `ESCALATION`, `DECISION`), timestamp, and verbatim domain reasoning.

#### Intended Actions & Options
- **Record Selection**: Clicking any decision in the left stream updates the right panel with its full meeting log and audit metadata.
- **Trace Deep-Dive**: Clicking **"Explore Reasoning Trace"** opens `ReasoningTraceView` pre-filtered to the active decision.

---

### Page 3: Scenario Launcher & Disruptions (`desktop/src/views/Scenarios/ScenariosView.tsx`)

#### Purpose
Allows supply chain operators to trigger, configure, and inject canonical or customized disruption scenarios directly into the Kafka event bus to test autonomous multi-agent arbitration.

#### What It Displays
1. **Left Column (Scenario Library Catalog)**:
   - Tabular library of standard benchmark scenarios:
     - `scen-01`: Baseline Nominal Operations (`none`, target: `global`, severity: 1/5)
     - `scen-02`: Tier-1 Semiconductor Supplier Delay (`supplier_delay`, target: `sup-01`, severity: 4/5)
     - `scen-03`: Consumer Electronics Demand Spike (`demand_spike`, target: `wh-01`, severity: 3/5)
     - `scen-04`: Cross-Border Route Failure (`transport_failure`, target: `route-sup-01-wh-01`, severity: 5/5)
   - Columns: Scenario ID, Title, Disruption Type, Target Node, Severity, and Action button (`ACTIVE` / `Select`).
2. **Right Column (Disruption Trigger Launcher Form)**:
   - **Active Scenario Selector**: Dropdown to select existing scenario templates.
   - **Disruption Type Selector**: Dropdown offering:
     - `supplier_delay`: Component lead-time delay.
     - `demand_spike`: Regional consumption surge.
     - `transport_failure`: Freight lane or customs blockage.
     - `adverse_weather`: Severe weather bottleneck.
     - `none`: Nominal baseline.
   - **Target Node Selector**: Dropdown selecting target entities (`sup-01`, `sup-02`, `sup-03`, `mfg-01`, `wh-01`, `route-sup-01-wh-01`, `global`).
   - **Severity Level Slider**: Range input adjusting impact intensity from 1 to 5.
   - **Trigger Button**: Interactive button showing target scenario name and loading progress.
   - **Dispatch Result Card**: Appears upon trigger, displaying returned `event_id`, `trace_id`, and status (`TRIGGERED`).

#### Intended Actions & Options
- **Select Scenario**: Clicking `Select` in the library populates the configuration launcher with that scenario's parameters.
- **Parameter Customization**: Adjusting the type, target node, or severity modifies the payload sent to the API.
- **Trigger Disruption**: Clicking **Trigger Disruption** dispatches `POST /scenarios/trigger` to inject the event into the Kafka bus and start the orchestration loop.

---

### Page 4: Agent Command Center (`desktop/src/views/AgentCommand/AgentCommandView.tsx`)

#### Purpose
Monitors the real-time operational health, MCP tool registries, and execution activity of the autonomous specialist agent fleet across the Agent-to-Agent (A2A) network.

#### What It Displays
1. **Specialist Agents Grid (4 Cards)**:
   - **Demand Forecasting Specialist** (`demand-agent`, `:8011`): Time-series forecasting (Prophet + XGBoost), anomaly detection. Skills: `forecast_demand`, `detect_anomalies`.
   - **Inventory Risk Specialist** (`inventory-agent`, `:8012`): Multi-echelon safety stock optimization, stockout hazard modeling. Skills: `evaluate_stockouts`, `reorder_safety_stock`.
   - **Supplier Intelligence Specialist** (`supplier-agent`, `:8013`): Lead-time variance, supplier reliability scoring, alternate sourcing. Skills: `analyze_lead_times`, `alternate_routing`.
   - **Transportation Logistics Specialist** (`transport-agent`, `:8014`): Dynamic lane rerouting, carrier capacity optimization. Skills: `reroute_lanes`, `estimate_transit_delays`.
   - Each card displays agent status pills (`IDLE`, `DISPATCHED`, `RUNNING`, `COMPLETED`), endpoint port, and execution latency.
2. **Live Activity Event Feed**:
   - Real-time event log streamed over `/ws/agents/activity`.
   - Records every state transition, dispatched scenario, execution latency in milliseconds, and timestamp.

#### Intended Actions & Options
- Real-time observability: Observe status pills turn to `RUNNING` and `COMPLETED` as disruption events are processed across the fleet.

---

### Page 5: What-If Simulation Lab (`desktop/src/views/WhatIfLab/WhatIfLabView.tsx`)

#### Purpose
Provides counterfactual simulation tools for supply chain analysts. Operators can model alternative disruption conditions, test "what-if" hypotheses, and project financial and stockout risks before physical decisions are executed.

#### What It Displays
1. **Left Column (Counterfactual Parameters Form)**:
   - **Base Scenario Dropdown**: Selects reference scenario (`scen-01` through `scen-04`).
   - **Disruption Type Override Dropdown**: Changes the simulated shock (`supplier_delay`, `demand_spike`, `transport_failure`, `adverse_weather`).
   - **Target Node Override Dropdown**: Changes affected node (`sup-01`, `sup-02`, `sup-03`, `mfg-01`, `wh-01`).
   - **Severity Slider**: Modifies simulated severity from 1 to 5.
   - **Simulation Trigger Button**: "Execute What-If Simulation".
2. **Right Column (Comparative Outcome Analysis)**:
   - Displays simulation run ID (`whatif_id`).
   - **Delta Impact Metrics**:
     - Stockout Risk Delta (e.g., `+38.5%` vs baseline).
     - Lead Time Variance (e.g., `+5.0 days` delivery delay).
     - Estimated Cost Delta (e.g., `+$42,000` freight/expediting expense).
     - Consensus Status (`RESOLVED` multi-agent agreement).
   - **Counterfactual Consensus Action Callout**: Displays recommended mitigation strategy derived under the simulated parameters.

#### Intended Actions & Options
- **Run Simulation**: Submits parameters to `POST /whatif/run` to generate comparative metrics and evaluate risk buffers.

---

### Page 6: Reasoning Trace Explorer (`desktop/src/views/ReasoningTrace/ReasoningTraceView.tsx`)

#### Purpose
Provides white-box mathematical transparency into CD2F consensus arbitration. Operators can verify raw specialist claims, competence weights, and escalation routing.

#### What It Displays
1. **Header & Decision Selector**:
   - Trace ID indicator.
   - Dropdown to select any recorded decision from the database for step-by-step provenance inspection.
2. **4-Phase Vertical Provenance Pipeline**:
   - **Phase 1: Disruption Context & Targeting**: Ingestion details from Kafka event, including scenario context and resolved specialist agents.
   - **Phase 2: Specialist Evidence & Claims**: Grid showing raw claims submitted by each agent, including proposed recommendations, stated confidence percentages, and perceived operational impact (`HIGH`, `MEDIUM`, `LOW`).
   - **Phase 3: Weighted Consensus Arbitration (CD2F)**: Detailed log of dynamic weight calculations ($W_i = w_i \times c_i$), error penalties, and recommendation tallies.
   - **Phase 4: Policy Evaluation & Escalation**: Escalation tier outcome badge (`FAST_PATH` vs `HUMAN_ESCALATION`), selected winning recommendation, and escalation rationale.

#### Intended Actions & Options
- **Inspect Alternate Traces**: Select any decision from the dropdown to immediately render its complete provenance pipeline.

---

### Page 7: Evaluation & Benchmarks (`desktop/src/views/Evaluation/EvaluationView.tsx`)

#### Purpose
Displays empirical performance benchmarks validating the SCOF architecture against standard baselines across accuracy, consensus stability, latency, and human escalation frequency.

#### What It Displays
1. **Top Header & Status**:
   - Dataset reference (`benchmark_suite.json`), validation status badge (`VALIDATED`), evaluation run ID, and timestamp.
   - Action Button: **"Re-run Evaluation"**.
2. **Calibration KPI Cards**:
   - **Inter-Agent Agreement Kappa**: Cohen's Kappa metric (e.g., `1.000` vs target `>= 0.85`).
   - **Fast-Path Resolution P90**: Sub-second 90th percentile latency (e.g., `330ms` against `< 500ms` SLA).
   - **Stockout Risk Reduction**: Empirical risk reduction percentage (e.g., `42.0%`).
3. **Arbitration Methods Comparative Matrix Table**:
   - Directly compares `CD2F (Consensus-Driven)` against baseline methods:
     - `Single-Agent (Demand Only)`
     - `Naive Majority Voting`
   - Metrics compared: Recommendation Accuracy, Weighted Consensus Stability (WCS), Median Latency, and Human Escalation Rate.
4. **Disruption Domain Categorical Performance Breakdown (20 Scenarios Table)**:
   - Performance breakdown across all 4 canonical disruption domains:
     - `supplier_delay`
     - `demand_spike`
     - `transport_failure`
     - `adverse_weather`
   - Metrics: Scenario Count, Accuracy, WCS Stability, Median Latency (P50), Fast-Path %, and Conflict Intensity.

#### Intended Actions & Options
- **Re-run Evaluation**: Triggers `POST /evaluation/run` to re-execute the automated evaluation suite and refresh metrics.

---

### Global Drawer: AI Operational Assistant (`desktop/src/components/chat/AIChatDrawer.tsx`)

#### Purpose
Slide-over RAG (Retrieval-Augmented Generation) assistant allowing operators to query past decisions, supplier lead-time trends, and historical mitigations using natural language.

#### What It Displays
- Conversational chat thread with user prompts and assistant answers.
- Source citation tags linking responses to database records (e.g., `scof.decision_records`, `pgvector`).
- Search status indicator ("Searching vector embeddings and reasoning trails...").
- Query input field with Send button.

#### Intended Actions & Options
- Open with `Ctrl + K` or the **Intelligence** button in the TopBar.
- Type queries such as *"What was the mitigation for scen-02?"* to retrieve historical mitigations via pgvector cosine similarity search.
- Close via the `X` button, `Ctrl + K`, or `Esc`.

---

## 4. How to Test Each Feature and Component

### 4.1 Frontend TypeScript & Build Verification
To ensure all frontend components, types, and stylesheets compile without errors:
```bash
cd desktop
npm run build
```
Expected result: Exit code 0, zero compilation errors, assets output to `desktop/dist`.

### 4.2 Offline Fallback & Connection Banner Test
1. Start the desktop console without starting Docker services.
2. Verify that the TopBar status pill displays `DISCONNECTED` in red.
3. Verify that the amber/red `ConnectionBanner` ribbon slides down at the top of the interface.
4. Navigate to **What-If Lab** (`Ctrl + 5`) and click **Execute What-If Simulation**; verify that local fallback simulations execute gracefully.

### 4.3 Automated Verification Scripts
Run the automated verification suite from the project root:
```bash
# Verify complete autonomous 8-stage loop
python scripts/verify_full_loop.py

# Verify observability persistence and traces
python scripts/verify_d7.py

# Run complete evaluation benchmark suite
python -m pytest services/evaluation/tests/ -v
```

---

## 5. End-to-End Test Run: Running the Project Using the Desktop Console

Follow this step-by-step procedure to execute an end-to-end autonomous multi-agent disruption scenario directly through the Desktop Operations Console:

### Step 1: Start Background Infrastructure & Microservices
Ensure Docker Desktop is running, then launch the complete microservices fleet from the project root:
```bash
docker compose up -d
```
Verify that all 8 microservices and infrastructure containers are healthy:
```bash
docker compose ps
```
Required healthy containers:
- `scof-api` (:8000)
- `scof-coordinator` (:8010)
- `scof-consensus` (:8020)
- `scof-observability` (:8030)
- `scof-agent-demand` (:8011)
- `scof-agent-inventory` (:8012)
- `scof-agent-supplier` (:8013)
- `scof-agent-transport` (:8014)
- PostgreSQL (with pgvector), Redis, Kafka, and Neo4j

### Step 2: Launch the Desktop Operations Console
Navigate to the desktop directory and launch the application:

**Option A — Native Desktop Shell (Tauri v2)**:
```bash
cd desktop
npm run tauri dev
```

**Option B — Modern Browser Preview**:
```bash
cd desktop
npm run dev
```
Open your browser at `http://localhost:1420`.

### Step 3: Verify Initial System Connectivity
1. Check the TopBar:
   - Ensure the status pill displays `CONNECTED` with a green indicator.
   - Confirm the profile badge displays `MVP-ELECTRONICS`.
2. Inspect the **Operations Overview** (`Ctrl + 1`):
   - Confirm the 4 KPI cards render nominal metrics.
   - Verify that the vector topology map renders without visual defects.

### Step 4: Inject a Disruption Scenario
1. Press `Ctrl + 3` to navigate to the **Scenario Launcher**.
2. Select scenario `scen-02` (Tier-1 Semiconductor Supplier Delay) from the table.
3. Review the launcher parameters:
   - Active Scenario: `scen-02`
   - Disruption Type: `supplier_delay`
   - Target Node: `sup-01`
   - Severity Level: `4 / 5`
4. Click the button: **Trigger Disruption: [SCEN-02] Tier-1 Semiconductor Supplier Delay**.
5. Observe the **Dispatch Result Card** appearing with assigned `event_id` and `trace_id`.

### Step 5: Observe Fleet Activity in Real Time
1. Press `Ctrl + 4` to navigate to the **Agent Command Center**.
2. Observe the status pills for `inventory-agent` and `supplier-agent` transition from `IDLE` to `RUNNING`, then to `COMPLETED`.
3. Verify that the execution latency (typically 180ms to 350ms) and timestamps appear in the Live Activity Feed.

### Step 6: Review Decision Completion Toast
1. Within sub-second latency, a floating **Notification Toast** will appear in the bottom-right corner.
2. The toast displays:
   - Scenario tag: `SCEN-02`
   - Escalation Tier: `FAST_PATH` (or `HUMAN_ESCALATION` if high severity)
   - Recommendation summary
   - Weighted Consensus Stability score (WCS)
3. Click **Inspect Decision ->** on the toast (or press `Ctrl + 2`).

### Step 7: Inspect Meeting Log & Deliberation in Decision Center
1. In the **Decision Center** (`Ctrl + 2`), locate the new decision at the top of the left feed.
2. Review the right inspection panel:
   - Confirm the winning recommendation banner (e.g., dual-sourcing allocation or inventory buffer reorder).
   - Scroll through the **AI Meeting Log Timeline** to read verbatim arguments presented by the specialist agents.

### Step 8: Deep-Dive into Mathematical Provenance
1. Click the **Explore Reasoning Trace** button at the top of the Decision Center (or press `Ctrl + 6`).
2. Review the 4-phase reasoning pipeline:
   - **Phase 1**: Ingest context and target node.
   - **Phase 2**: Compare stated claims, confidences, and impact ratings between `inventory-agent` and `supplier-agent`.
   - **Phase 3**: Inspect the computed competence weights and score tallies under CD2F arbitration.
   - **Phase 4**: Review the final escalation decision rule.

### Step 9: Test Counterfactual Simulation in What-If Lab
1. Press `Ctrl + 5` to navigate to the **What-If Lab**.
2. Set Base Scenario to `scen-02`, Disruption Type to `supplier_delay`, Target Node to `sup-01`, and Severity to `5`.
3. Click **Execute What-If Simulation**.
4. Observe the Comparative Outcome Analysis card populate with stockout risk delta (+38.5%), lead time impact (+5.0 days), and cost delta (+$42,000).

### Step 10: Test Natural-Language RAG Query
1. Press `Ctrl + K` to open the **AI Operational Assistant Drawer**.
2. In the input box, type:
   `What was the mitigation for scen-02?`
3. Press Enter or click Send.
4. Verify that the assistant queries pgvector semantic memory and returns the exact arbitrated mitigation with database citations.
5. Press `Esc` to close the drawer.

### Step 11: Inspect System Benchmarks
1. Press `Ctrl + 7` to navigate to **Evaluation & Benchmarks**.
2. Review the Arbitration Methods Comparative Matrix table to verify that CD2F achieves superior accuracy and lower human escalation rates than Single-Agent and Naive Majority Voting baselines.
3. Click **Re-run Evaluation** to verify dynamic benchmark execution.

---

## 6. Troubleshooting & Operational Tips

- **TopBar Displays DISCONNECTED**:
  - Verify that the Docker stack is active: `docker compose ps`.
  - Check that port 8000 is listening: `curl http://localhost:8000/health`.
  - Check API Gateway container logs: `docker compose logs -f scof-api`.
- **WebSocket Reconnection Loop**:
  - If the TopBar displays `RECONNECTING`, check for CORS or port proxy conflicts on `ws://localhost:8000/ws/*`.
- **Agent Command Center Cards Remain Idle**:
  - Specialist agents only transition to `RUNNING` when a scenario is actively dispatched. Once triggered, status is updated in real time via Kafka event streaming.
- **Port Conflicts**:
  - Default ports: 8000 (API), 8010 (Coordinator), 8011–8014 (Agents), 8020 (Consensus), 8030 (Observability), 1420 (Desktop UI). Ensure these ports are not in use by other local applications.
