# SCOF Master Operational Demonstration Guide

## Complete End-to-End Walkthrough, System Topology, and Feature-by-Feature Verification Manual

---

### Document Information
- **System**: Supply Chain Cognitive Orchestration Framework (SCOF)
- **Domain**: High-Tech Electronics & Semiconductor Manufacturing (Peninsular India Corridor)
- **Document Purpose**: Comprehensive operational guide and step-by-step demonstration script covering the full stack from container initialization to multi-agent consensus verification.
- **Reference Codebase**: `SCOF_V1`

---

## 1. System Architecture & Topology Overview

The Supply Chain Cognitive Orchestration Framework (SCOF) is an enterprise multi-agent autonomous control system designed to arbitrate cross-tier supply disruptions, simulate counterfactual interventions, and provide human-in-the-loop (HITL) auditability for high-tech manufacturing networks.

### 1.1 Microservices Fleet Architecture

```
                             [ SCOF Desktop Operations Console ]
                             (React 19 + TypeScript + Vite Shell)
                                       │
                      REST API (:8000) │ WebSocket Live Channels (:8000)
                                       ▼
                       ┌───────────────────────────────┐
                       │     API Gateway (FastAPI)     │
                       │         Port: 8000            │
                       └───────────────┬───────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
┌───────────────┐              ┌───────────────┐              ┌───────────────┐
│  Coordinator  │              │ Redis Caching │              │  PostgreSQL   │
│  LangGraph    │              │ & Pub/Sub     │              │  & pgvector   │
│  Port: 8010   │              │ Port: 6379    │              │  Port: 5432   │
└───────┬───────┘              └───────────────┘              └───────────────┘
        │
        │ Kafka Event Bus (:9092)
        ├────────────────────────────────┬────────────────────────────┐
        ▼                                ▼                            ▼
┌─────────────────┐            ┌──────────────────┐         ┌─────────────────┐
│ Demand & Inventory│          │Supplier & Transit│         │   Consensus     │
│ Specialists     │            │Specialists       │         │   Engine (CD2F) │
│ Ports: 8011/8012│            │Ports: 8013/8014  │         │   Port: 8020    │
└─────────────────┘            └──────────────────┘         └─────────────────┘
        │                                                             │
        └──────────────────────────────┬──────────────────────────────┘
                                       ▼
                       ┌───────────────────────────────┐
                       │ Observability & Audit Service │
                       │          Port: 8030           │
                       └───────────────────────────────┘
```

### 1.2 Enterprise Domain Scope: Peninsular India Electronics Network

The primary demonstration environment operates on the `mvp-electronics` domain profile, modeling 25 realistic supply disruption scenarios across the South Indian semiconductor corridor:
- **Tier-1 Semiconductor & Component Suppliers**:
  - `sup-01`: SPEL Semiconductor (Maraimalai Nagar, Chennai, Tamil Nadu)
  - `sup-02`: Continental Device India - CDIL (Electronic City, Bengaluru, Karnataka)
  - `sup-03`: Kaynes Technology India (Koorgalli Industrial Area, Mysuru, Karnataka)
  - `sup-04`: Syrma SGS Technology (Bargur Industrial Estate, Tamil Nadu)
  - `sup-05`: Centum Electronics (Yelahanka, Bengaluru, Karnataka)
  - `sup-06`: Vinyas Innovative Technologies (Hebbal Industrial Area, Mysuru, Karnataka)
  - `sup-07`: SFO Technologies NeST (Kakkanad, Kochi, Kerala)
  - `sup-08`: Sahasra Electronic Solutions (Hyderabad, Telangana)
- **Central Assembly Hub**:
  - `mfg-01`: Sriperumbudur High-Tech Assembly Plant (Sriperumbudur, Tamil Nadu)
- **Strategic Buffer Warehouses**:
  - `wh-01`: Hosur Logistics Buffer Warehouse (Hosur, Tamil Nadu)
  - `wh-02`: Whitefield Inland Container Depot (Bengaluru, Karnataka)
  - `wh-03`: Oragadam JIT Supplier Warehouse (Oragadam, Tamil Nadu)
  - `wh-04`: Sri City FTWZ Logistics Center (Sri City, Andhra Pradesh)
- **Multi-Modal Gateways & Transit Corridors**:
  - `dc-01`: Chennai Port Container Terminal
  - `dc-02`: Cochin Port Vallarpadam ICTT
  - `dc-03`: Hyderabad Aerotropolis Air Cargo Gateway
  - Arterial freight lanes along NH44, NH48, and NH544

---

## 2. Phase 0: System Initialization & Pre-Flight Verification

Before launching the desktop operations console, initialize the supporting container fleet and verify all health probes.

### Step 0.1: Container Infrastructure Startup

Open a terminal at the repository root and start the complete microservices stack:

```bash
docker compose up -d
```

#### What This Step Does
1. Spawns the underlying message bus (`zookeeper`, `kafka`), operational database (`postgres` with `pgvector`), cache layer (`redis`), and knowledge graph (`neo4j`).
2. Bootstraps the backend microservices fleet (`scof-api`, `scof-coordinator`, `scof-demand-agent`, `scof-inventory-agent`, `scof-supplier-agent`, `scof-transport-agent`, `scof-consensus`, `scof-observability`, `scof-simulation`).
3. Executes database migrations, populates the `scof` schema, and seeds baseline supply chain topology tables.

#### How to Verify Step 0.1
Run the container status check:

```bash
docker compose ps
```

**Expected Verification Output**:
All primary services must report `healthy` or `running` state.
- `postgres`: running on port `5432`
- `kafka`: running on port `9092`
- `redis`: running on port `6379`
- `neo4j`: running on port `7474`, `7687`
- `scof-api`: running on port `8000`
- `scof-coordinator`: running on port `8010`

Query the API Gateway health probe via HTTP:

```bash
curl http://localhost:8000/health
```

**Expected HTTP Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "kafka": "connected"
}
```

---

### Step 0.2: Desktop Console Launch

Open a second terminal window, navigate to the `desktop/` directory, and launch the Vite development server:

```bash
cd desktop
npm run dev
```

#### What This Step Does
1. Starts the Vite bundler compiling the React 19 application.
2. Serves the application locally (typically at `http://localhost:5173`).
3. Initializes the global connection state manager (`desktop/src/state/connection.tsx`), establishing REST polling and WebSocket connections to `ws://localhost:8000/ws/dashboard/state`, `ws://localhost:8000/ws/decisions/live`, and `ws://localhost:8000/ws/agents/activity`.

#### How to Verify Step 0.2
1. The terminal displays `VITE v7.x.x ready in ... ms` with Local URL `http://localhost:5173/`.
2. Open `http://localhost:5173/` in your browser or desktop container window.
3. Observe the top bar of the application window.

---

### Step 0.3: Global Header Bar & Connectivity Check

Inspect the **TopBar** component (`desktop/src/components/layout/TopBar.tsx`).

#### Visual Elements to Verify:
1. **Window Identity & Controls**: Simulated native window controls (red, yellow, green window action buttons) displayed on the left.
2. **Current View Title**: Defaults to `Operations Overview`.
3. **Active Domain Profile**: Displays `MVP-ELECTRONICS` in a high-contrast mono badge.
4. **Connection State Pill**: Displays a green dot with label `CONNECTED`.
   - *Technical Note*: The console enforces a deterministic precedence hierarchy:
     `OFFLINE_CACHED` > `RECONNECTING` > `DEGRADED` > `CONNECTED`.
     Seeing `CONNECTED` confirms both HTTP `/health` and WebSocket event streams are operational.
5. **Real-time UTC Clock**: Synchronized tabular clock displaying live UTC time.
6. **Shortcuts HUD (`?`) Button**: Opens keyboard shortcuts mapping.
7. **Intelligence Assistant (`Ctrl + K`) Button**: Opens the Copilot drawer.

---

## 3. Phase 1: Global Navigation & Common Utilities

Demonstrate the global application framework, navigation mechanisms, and contextual overlays before diving into specific workspaces.

### Step 1.1: Navigation Rail Expansion & Hotkey Switching

The left sidebar (`desktop/src/components/layout/Sidebar.tsx`) provides access to the 7 canonical platform workspaces.

#### Action
1. Move the mouse over the compact navigation rail (68px width) or click the toggle icon to expand to the full 208px labeled sidebar.
2. Demonstrate global hotkeys to switch between workspaces:
   - `Ctrl + 1` -> Operations Overview
   - `Ctrl + 2` -> Decision Center
   - `Ctrl + 3` -> Scenario Launcher
   - `Ctrl + 4` -> Agent Command
   - `Ctrl + 5` -> What-If Simulation Lab
   - `Ctrl + 6` -> Reasoning Traces
   - `Ctrl + 7` -> Evaluation Matrix

#### How to Verify
- Pressing `Ctrl + 5` instantly switches the active workspace to What-If Simulation Lab.
- Pressing `Ctrl + 1` returns to Operations Overview.
- Active workspace tab displays high-contrast brand selection styling (`--brand-navy` background and `--brand-blue` accent).

---

### Step 1.2: Shortcuts HUD Modal

Press `Shift + ?` on the keyboard, or click the `?` button on the TopBar.

#### What This Step Does
Triggers `desktop/src/components/modals/ShortcutsModal.tsx`, rendering an accessible modal dialog listing all keyboard accelerators.

#### How to Verify
- The modal appears centered with backdrop blur.
- Press `Esc` or click the dismiss button to close the modal.

---

### Step 1.3: Copilot Intelligence Drawer (RAG Vector Search)

Press `Ctrl + K` or click the Copilot button on the TopBar.

#### What This Step Does
Slides open `desktop/src/components/chat/AIChatDrawer.tsx` from the right edge of the workspace. This tool queries the FastAPI `/chat/query` endpoint, which performs cosine similarity retrieval over PostgreSQL `pgvector` semantic embeddings of past decisions.

#### Demo Interaction:
In the query input box, enter:
```
What mitigation strategy was selected for the SPEL Semiconductor supplier delay?
```
Click **Submit Query**.

#### How to Verify
- A response is returned citing historical decisions (e.g., dual-sourcing failover to Continental Device India `sup-02` and wafer release from Hosur Warehouse `wh-01`).
- Cited Decision IDs are rendered as clickable references.
- Press `Esc` to close the Copilot drawer.

---

## 4. Phase 2: Operations Overview (`Ctrl + 1`)

**Primary Role**: Tactical situational awareness, real-time KPI metrics, South Indian electronics topology visualization, and active disruption monitoring.

### Step 2.1: Key Performance Indicator (KPI) Metric Cards

Examine the 4 headline metric tiles at the top of the workspace:
1. **Supply Chain Reliability**: Displays network reliability index (nominal benchmark: 96.4%, with target variance indicator `+1.2%`).
2. **Inventory Stock Coverage**: Shows aggregate buffer inventory across all warehouses (e.g., 18.4 days vs safety threshold of 14.0 days).
3. **Active Disruption Risk**: Displays `NOMINAL` badge during steady state, switching to `ELEVATED` or `CRITICAL` when disruptions are in flight.
4. **Specialist Agents Online**: Fleet status displaying `4 / 4` with active multi-agent discovery confirmation.

---

### Step 2.2: Interactive Supply Network Topology Map

Inspect the central vector graphic visualizer (`desktop/src/views/Operations/OperationsView.tsx`).

#### Visual Elements:
- **Supplier Cluster**: Displays tier-1 suppliers across Chennai (`sup-01`), Bengaluru (`sup-02`, `sup-05`), Mysuru (`sup-03`, `sup-06`), Bargur (`sup-04`), Kochi (`sup-07`), and Hyderabad (`sup-08`).
- **Assembly Hub**: Central node `mfg-01` representing the Sriperumbudur manufacturing campus.
- **Logistics Nodes**: Buffer warehouses (`wh-01` to `wh-04`) and multimodal container ports (`dc-01`, `dc-02`, `dc-03`).
- **Corridor Vectors**: Freight lanes connecting nodes with directional arrows and state glow.

#### Demo Interaction:
1. Hover the cursor over node `sup-01 (SPEL Semiconductor)`.
2. Notice the interactive hover tooltip displaying entity details: facility name, cluster location, nominal lead time, and base risk score.
3. Click on node `sup-01`.

#### How to Verify:
A contextual drawer (`desktop/src/components/common/ContextualDrawer.tsx`) opens on the right, displaying:
- Node Identifier: `sup-01`
- Facility Type: Semiconductor Wafer Packaging Fab
- Location: Maraimalai Nagar, Chennai, TN
- Nominal Buffer: 12 days safety stock
- Direct Outbound Freight Lane: `route-sup-01-mfg-01` to Sriperumbudur

Click the drawer close icon to dismiss the inspector.

---

### Step 2.3: Operational Alerts Banner & Recent Consensus Stream

Examine the lower section of the Operations workspace:
1. **Active Disruption Alerts**: In nominal state, displays `ALL SYSTEMS NOMINAL - NO ACTIVE DISRUPTIONS`.
2. **Recent Decisions Stream**: Displays cards summarizing the latest consensus arbitrations from PostgreSQL (`scof.decisions`), showing Scenario ID, Escalation Tier (`FAST_PATH` or `HUMAN_ESCALATION`), final recommendation snippet, and consensus confidence percentage.

---

## 5. Phase 3: Scenario Launcher (`Ctrl + 3`)

**Primary Role**: Catalog browsing, custom parameter formulation, and two-stage idempotent dispatch of disruption shocks into the live Kafka message bus.

### Step 3.1: Scenario Catalog Browsing & Filtering

Navigate to Scenario Launcher using `Ctrl + 3` or the navigation rail.

#### Visual Elements:
- **Scenario Table**: Displays the complete catalog of 25 pre-configured South Indian disruption scenarios.
- **Category Filter Tabs**:
  - `All (25)`: Complete scenario catalog.
  - `Supplier (11)`: Lead time delays, wafer stockouts, and packaging halt events.
  - `Demand (4)`: Automotive surges, IoT meter rollouts, and EV retrofit spikes.
  - `Transport (8)`: Highway blockades, port silting, and rail container shortages.
  - `Weather (2)`: Cyclonic inundation and regional monsoon emergencies.
- **Search Filter Input**: Instant real-time filtering by scenario ID, facility name, or keywords.

#### Demo Interaction:
1. Click the `Supplier` tab. Observe the table filter down to the 11 supplier-specific scenarios.
2. In the search box, type `SPEL`. Observe the table immediately isolate `scen-02` (Tier-1 Semiconductor Packaging Delay).
3. Clear the search box and switch back to the `All (25)` tab.
4. Scroll through the table. Verify that sticky headers remain fixed and all 25 rows are accessible.

---

### Step 3.2: Configuration Drawer & In-Session Draft Form

#### Demo Interaction:
1. Click on row `scen-02` (`Tier-1 Semiconductor Packaging Delay - SPEL Chennai`).
2. A contextual drawer opens on the right showing the **Scenario Configuration Form**.

#### What to Verify in the Form:
- **Base Scenario Title**: `[scen-02] Tier-1 Semiconductor Packaging Delay`
- **Target Topology Node**: Pre-populated with `sup-01 (SPEL Semiconductor - Maraimalai Nagar, Chennai)`.
- **Disruption Type**: Pre-populated with `supplier_delay`.
- **Severity Level**: Pre-populated with `Level 4: Acute localized disruption requiring CD2F arbitration`.
- **Draft Dirty State**:
  - Change Severity from Level 4 to **Level 3**.
  - Notice the `DRAFT MODIFIED` badge appears on the drawer header, indicating in-session modified state.
  - Click **Reset to Baseline**. Observe the severity restore to Level 4.

---

### Step 3.3: Two-Stage Dispatch & 4-Outcome State Machine

Now trigger the disruption into the live backend orchestration stack.

#### Demo Action:
Click the primary action button: **Dispatch Scenario Disruption**.

#### What Happens Behind the Scenes:
1. The desktop client posts a JSON payload to `http://localhost:8000/api/scenarios/trigger`:
   ```json
   {
     "scenario_id": "scen-02",
     "disruption_type": "supplier_delay",
     "target_entity_id": "sup-01",
     "severity": 4
   }
   ```
2. The FastAPI Gateway creates an event envelope (`event_type: "disruption.triggered"`).
3. The event is published to the Kafka broker topic `scof.disruptions.triggered`.
4. The LangGraph Orchestrator (`scof-coordinator`) consumes the event and initiates autonomous agent deliberation.

#### How to Verify Step 3.3:
The drawer displays an immediate **Accepted Outcome Banner**:
- Status: `ACCEPTED` (Green border)
- Event ID: `evt-...`
- Trace ID: `trace-...`
- Notification: `Disruption accepted by API Gateway. Awaiting multi-agent deliberation on Kafka bus.`

*Note on Idempotency Protection*: While a scenario submission is in flight or if a timeout occurs (`UNKNOWN` outcome), duplicate submission buttons are disabled to prevent duplicate shock waves from hitting the Kafka cluster.

---

## 6. Phase 4: Agent Command Center (`Ctrl + 4`)

**Primary Role**: Live monitoring of autonomous specialist fleet activity, task execution states, and emitted claims.

### Step 4.1: Specialist Fleet Telemetry Table

Navigate to Agent Command Center using `Ctrl + 4`.

#### Visual Elements:
- **Specialist Agent Fleet Cards**:
  1. **Demand Forecasting Specialist** (`scof-demand-agent`, port 8011)
  2. **Inventory Risk Specialist** (`scof-inventory-agent`, port 8012)
  3. **Supplier Intelligence Specialist** (`scof-supplier-agent`, port 8013)
  4. **Logistics & Transit Specialist** (`scof-transport-agent`, port 8014)
- **Status Indicators**: Each specialist displays operational state (`IDLE`, `ANALYZING`, `CLAIM_EMITTED`, or `COMPLETED`).
- **Telemetry Metrics**: Heartbeat timestamp, latency (ms), and active correlation trace ID.

---

### Step 4.2: Real-time Claims & Activity Inspection

Click on the **Supplier Intelligence Specialist** row or card.

#### How to Verify:
A detail drawer opens on the right displaying the specialist's recent deliberation payload:
- **Emitted Claim**: `Supplier lead time at SPEL Semiconductor increased by +5.4 days due to wafer-level packaging hold.`
- **Confidence Score**: `0.88`
- **Utility Bid**: Proposed failover sourcing score.
- **Evidence References**: Cites local inventory buffers at Hosur (`wh-01`) and alternative production capacity at Continental Device India (`sup-02`).

---

## 7. Phase 5: Reasoning Trace Explorer (`Ctrl + 6`)

**Primary Role**: End-to-end auditability and execution lineage showing how the system progressed from shock observation to consensus decision.

### Step 5.1: 8-Phase Architectural Execution Pipeline

Navigate to Reasoning Traces using `Ctrl + 6`.

#### Core Concept to Explain to Audience:
SCOF does not use unstructured LLM chatter. It enforces an immutable, deterministic 8-phase reasoning pipeline:
1. `OBSERVE`: Ingest raw disruption event from Kafka.
2. `SCOPE`: Identify affected supply network nodes and inventory buffers.
3. `RETRIEVE`: Query Neo4j knowledge graph and PostgreSQL semantic memory for constraints and supplier alternatives.
4. `ANALYZE`: Specialists calculate risk, cost, and schedule impacts.
5. `CHECK`: Validate proposals against operational hard constraints (e.g., minimum safety stock).
6. `PROPOSE`: Specialists submit candidate actions and utility bids.
7. `VALIDATE`: CD²F consensus engine checks for cross-agent conflicts.
8. `EMIT`: Publish the final consensus decision record.

---

### Step 5.2: Trace Event Chronology & Stage Filters

#### Demo Interaction:
1. Locate the trace corresponding to the disruption triggered in Phase 3 (matches the `trace_id` returned during dispatch).
2. Use the **Stage Filter** dropdown at the top to filter events (e.g., select `CHECK` or `VALIDATE`).
3. Click on the `VALIDATE` stage event.
4. Expand the event details card:
   - **Executive Summary**: Plain-English explanation of the consensus validation.
   - **Structured Payload**: Expandable JSON viewer showing exact utility scores, weights, and mathematical arbitration matrices.

#### How to Verify:
All 8 pipeline stages are chronologically represented with millisecond-precision timestamps and verified component signatures.

---

## 8. Phase 6: Decision Center (`Ctrl + 2`)

**Primary Role**: Human-in-the-loop governance, consensus meeting minutes audit, trade-off inspection, and decision authorization.

### Step 6.1: Decision Queue & Master-Detail Inspection

Navigate to Decision Center using `Ctrl + 2`.

#### Visual Elements:
- **Decision Queue (Left Column / Master Table)**: Displays all arbitrated decisions stored in PostgreSQL (`scof.decisions`).
- **Escalation Tier Badges**:
  - `FAST-PATH RECOMMENDATION`: Unanimous agreement among specialists; low risk; automated execution permissible.
  - `DELIBERATED CONSENSUS`: Multi-agent utility conflict resolved through CD²F mathematical arbitration.
  - `HUMAN ESCALATION REQUIRED`: High-severity shock exceeding autonomous policy limits (e.g., Cyclone Michaung storm landfall or regional blackout), requiring mandatory human sign-off.

#### Demo Interaction:
Select the decision generated from `scen-02` (Tier-1 Semiconductor Packaging Delay).

---

### Step 6.2: Winning Recommendation Callout & Consensus Meeting Log

Inspect the central detail pane:

1. **Winning Recommendation Banner**:
   - High-contrast callout summarizing the finalized operational policy:
     ```
     Execute dual-sourcing failover to Continental Device India (sup-02, Electronic City)
     and draw 4-day wafer buffer from Hosur Logistics Buffer (wh-01).
     ```
   - **Financial Impact**: Projected cost variance in Indian Rupees (`+₹14,400`).
   - **Schedule Impact**: Lead-time delay restricted to `+1.8 days` (vs 5.4 days unmitigated).
   - **Confidence Score**: Weighted Consensus Stability (WCS) score: `92.4%`.

2. **Consensus Meeting Minutes Log**:
   - Scroll down to review the step-by-step consensus meeting records:
     - **Round 1 (Initial Bids)**: Inventory Specialist advocated holding buffers; Supplier Specialist advocated full commercial re-order.
     - **Round 2 (Arbitration)**: CD²F consensus algorithm calculated joint utility Pareto frontier.
     - **Round 3 (Consensus Settlement)**: Final compromise reached with zero unhandled vetoes.

---

### Step 6.3: External Execution Integration Boundary

At the bottom of the decision panel, notice the authorization control buttons:
- **Approve & Authorize Execution**
- **Reject Recommendation**
- **Request Secondary Deliberation**

#### What to Explain to Audience:
Point out the system boundary note:
*External execution integration boundary: Once approved by an operator, the decision payload is formatted for downstream ERP (SAP S/4HANA), WMS (Manhattan Associates), and TMS freight dispatch APIs. The console maintains a clean boundary to prevent unverified mock executions.*

---

## 9. Phase 7: What-If Simulation Lab (`Ctrl + 5`)

**Primary Role**: Analytical sandbox for counterfactual exploration and Monte-Carlo projections without injecting live disruptions into the running event bus.

### Step 7.1: Parameters Configuration Workspace

Navigate to What-If Simulation Lab using `Ctrl + 5`.

#### Visual Layout & Verification:
- Notice the two-column responsive layout:
  - Left Card: **Counterfactual Parameters** (380px width, clean 20px padding `--space-5`).
  - Right Card: **Comparative Outcome Analysis** (flexible width canvas).
- Top Right Toggle: Click **Hide Assumptions** / **Show Assumptions** to demonstrate collapsible sidebar capabilities.

#### Demo Interaction:
In the Counterfactual Parameters card, configure an alternative hypothetical scenario:
1. **Base Scenario**: Select `[scen-02] Tier-1 Semiconductor Packaging Delay (SPEL Chennai)`.
2. **Disruption Type Override**: Select `Facility Extreme Weather / Cyclone`.
3. **Target Topology Node**: Select `sup-01 (SPEL Semiconductor - Maraimalai Nagar, Chennai)`.
4. **Severity Override**: Click the segmented button `Level 5`.

---

### Step 7.2: Counterfactual Simulation Execution

Click the primary action button: **Execute What-If Simulation**.

#### What Happens Behind the Scenes:
1. Calls backend API `http://localhost:8000/api/whatif/run`.
2. Computes Monte-Carlo predictive outcome deltas using specialized domain multiplier matrices.
3. Caches computed results in Redis under key `whatif:{whatif_id}`.
4. *Crucial Distinction*: Unlike Scenario Launcher, this does **NOT** publish to `scof.disruptions.triggered` and does **NOT** wake up the live agent coordinator. The production environment remains completely unaffected.

---

### Step 7.3: Aligned Comparative Outcome Analysis

Inspect the results rendered on the right card:

#### Visual Elements to Verify:
1. **Side-by-Side Comparison Tiles**:
   - **Baseline Nominal Tile**: Nominal lead time `1.35d`, nominal risk `8.6%`, nominal cost `₹9,600`.
   - **Counterfactual Projected Tile**: High-severity cyclonic storm projection showing elevated risk and delay.
2. **Delta Variance Grid**:
   - **Stockout Risk Delta**: Highlighted in red/amber (e.g., `+20.4%`).
   - **Lead-Time Impact**: Highlighted in days (e.g., `+4.5 days`).
   - **Cost Variance**: Formatted in Indian Rupees (e.g., `+₹42,500`).
3. **Consensus Status & Action Recommendation Banner**:
   - Status Badge: `ESCALATED_TO_HUMAN` (due to Level 5 category storm severity).
   - Recommended Policy:
     ```
     Emergency Disaster Protocol: Shift all wafer packaging to CDIL Bengaluru (sup-02),
     reroute export logistics through Cochin Vallarpadam Port (dc-02), and alert executive operations.
     ```

---

## 10. Phase 8: Evaluation & Benchmark Matrix (`Ctrl + 7`)

**Primary Role**: Empirical scientific evaluation proving that the multi-agent consensus system outperforms baseline heuristics.

### Step 8.1: Benchmark Calibration Profile Metadata

Navigate to Evaluation Matrix using `Ctrl + 7`.

#### Headline Metadata:
- **Dataset Profile**: `mvp-electronics-calibration-v1`
- **Total Calibration Runs**: 250 Monte-Carlo test iterations across all 25 scenarios.
- **Evaluation Baseline Models**:
  1. `CD2F Multi-Agent Consensus` (SCOF Proposed Framework)
  2. `Independent Specialist LLMs` (No arbitration / uncoordinated agents)
  3. `Static Rule-Based Engine` (Traditional ERP re-order heuristic)
  4. `Single Monolithic LLM` (Prompt-only GPT-4 baseline)

---

### Step 8.2: Comparative Benchmark Metric Cards

Inspect the 4 comparative benchmark cards:
1. **Decision Quality & Accuracy**:
   - SCOF CD²F: **94.2%** vs Static Rules: **68.5%** vs Monolithic LLM: **74.1%**.
2. **Stockout Risk Reduction**:
   - SCOF CD²F achieves **-38.6%** lower average stockout risk during acute disruptions.
3. **Cost Variance Optimization**:
   - SCOF CD²F delivers an average savings of **₹28,400 per disruption event** compared to uncoordinated reactive purchasing.
4. **Arbitration Latency Profile**:
   - Fast-Path consensus: **142 ms**.
   - Multi-round Slow-Path consensus: **860 ms** (well within the 2.5-second operational SLA).

---

### Step 8.3: Scenario-Level Benchmark Drill-Down Table

Scroll down to review the scenario-by-scenario benchmark table:
- Demonstrates performance across all 25 scenarios.
- Shows side-by-side win/loss rates, consensus stability indices, and human escalation precision.

---

## 11. Phase 9: Resilience & Edge-Case Demonstration

To prove the robustness of the platform to clients and evaluators, demonstrate the system's graceful degradation under network fault conditions.

### Step 11.1: Simulating Backend Failure & Offline Caching Fallback

In a terminal, temporarily pause the API Gateway service:

```bash
docker compose pause api
```
*(Alternatively, using the container name: `docker pause scof-api`)*

#### What This Step Demonstrates:
1. Within 3 seconds, the desktop console detects the failed health probe.
2. The TopBar connection status indicator changes from `CONNECTED` to `OFFLINE_CACHED`.
3. The global **Connection Banner** (`desktop/src/components/common/ConnectionBanner.tsx`) slides down across the top of the interface:
   - Message: `Operating in offline cached mode. Displaying latest synchronized snapshot.`
4. Navigate through views (`Operations`, `Scenarios`, `What-If`). Notice that the interface does **not** crash; it gracefully renders cached data from in-memory state and localStorage.

---

### Step 11.2: Automatic Reconnection Recovery

Resume the API Gateway service:

```bash
docker compose unpause api
```
*(Alternatively, using the container name: `docker unpause scof-api`)*

#### What to Verify:
1. The TopBar transition state briefly shows `RECONNECTING` (amber dot).
2. Within 2 seconds, all three WebSocket channels reconnect.
3. The status restores to `CONNECTED` (green dot).
4. The offline banner automatically slides back up and disappears.

---

## 12. Phase 10: Orderly System Teardown

Conclude the demonstration session by cleanly shutting down services.

### Step 12.1: Stopping the Desktop Console
In the desktop terminal, press `Ctrl + C` to stop the Vite development server.

### Step 12.2: Stopping Docker Microservices
In the root terminal, run:

```bash
docker compose down
```

*Note*: If you wish to preserve the database records, Kafka topics, and Neo4j graph data for the next demonstration session, run `docker compose stop` instead of `docker compose down`.

---

## 13. High-Impact Screenshot & Presentation Checklist

When preparing presentation decks, video recordings, or evaluation reports, capture the following 10 canonical screenshots:

| # | Screenshot Target View | Action State / Configuration | Key Visual Focal Point | Suggested Filename |
| :---: | :--- | :--- | :--- | :--- |
| **1** | TopBar Header Bar | Steady state (`CONNECTED`) | Green connection pill, UTC clock, profile badge | `01_topbar_connection_header.png` |
| **2** | Operations Overview | Steady state | 4 KPI tiles, South Indian topology map | `02_operations_topology_overview.png` |
| **3** | Operations Overview | Node inspector drawer open | Contextual drawer showing `sup-01` metadata | `03_operations_node_drawer.png` |
| **4** | Scenario Launcher | Filtered by `Supplier (11)` | Scenario catalog table, sticky headers | `04_scenarios_catalog_filter.png` |
| **5** | Scenario Launcher | Drawer open, Dispatched | Accepted outcome banner (`event_id`, `trace_id`) | `05_scenarios_dispatch_accepted.png` |
| **6** | Agent Command | During active deliberation | Fleet telemetry cards, claims drawer | `06_agent_command_fleet_claims.png` |
| **7** | Reasoning Traces | `scen-02` trace expanded | 8-phase pipeline (`OBSERVE` -> `EMIT`) | `07_reasoning_trace_pipeline.png` |
| **8** | Decision Center | Consensus meeting log open | Winning recommendation banner, INR cost | `08_decision_center_cd2f_meeting.png` |
| **9** | What-If Simulation Lab | Simulation executed | Side-by-side comparison tiles, delta grid | `09_whatif_counterfactual_comparison.png` |
| **10** | Evaluation Matrix | Benchmark results | CD²F vs Baselines comparison cards | `10_evaluation_benchmark_matrix.png` |

---

## 14. Quick Reference: Troubleshooting & Common FAQs

### Q1: The TopBar status shows `DISCONNECTED` immediately on launch.
- **Cause**: The API Gateway (`scof-api`) is not running on port `8000` or Docker is still booting.
- **Resolution**: Check container logs with `docker compose logs scof-api`. Verify port 8000 is open with `curl http://localhost:8000/health`.

### Q2: Why did `scof-kafka-setup` container exit with code 0?
- **Cause**: This is normal and expected. `scof-kafka-setup` is a one-time utility container that creates Kafka topics (`scof.disruptions.triggered`, `scof.decisions.published`, etc.) and exits upon completion.

### Q3: What is the difference between Scenario Launcher and What-If Lab?
- **Scenario Launcher**: Dispatches real disruption events to Kafka (`scof.disruptions.triggered`), executing live multi-agent deliberation across the coordinator and updating the operational ledger.
- **What-If Simulation Lab**: Runs offline counterfactual Monte-Carlo calculations, providing instantaneous side-by-side comparisons without injecting shocks into the running platform.

### Q4: Are keyboard shortcuts supported on all operating systems?
- **Resolution**: Yes. Global hotkeys support `Ctrl+1` through `Ctrl+7` on Windows/Linux, and automatically map to `Cmd+1` through `Cmd+7` on macOS.
