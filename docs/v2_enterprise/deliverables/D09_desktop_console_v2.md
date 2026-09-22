# Deliverable D09 (V2): Tauri v2 Desktop Operations Console

## 1. Overview & Objectives

Deliverable D09 transforms the prototype preview of V1 into an enterprise-grade **Desktop Operations Console** built with Tauri v2. The console serves as the primary visual command center for supply chain operators, logistics planners, and executive stakeholders, providing real-time situational awareness, live agent deliberation tracking, and interactive scenario simulation across the SCOF Retail Enterprise Reference World.

---

## 2. The Seven Primary Operational Views

The console is structured around seven specialized operational views:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SCOF OPERATIONS CONSOLE                         │
├─────────────┬─────────────┬─────────────┬──────────────────────────────┤
│ 1. Topology │ 2. War Room │ 3. Lab      │ 4. Inventory & Assets        │
│ 5. Consensus│ 6. What-If  │ 7. Auditing │ Status: CONNECTED (Port 8000)│
└─────────────┴─────────────┴─────────────┴──────────────────────────────┘
```

| View ID | View Name | Core Functionality | Primary Visual Component |
| :--- | :--- | :--- | :--- |
| **V1** | **Network Topology Visualizer** | Displays the physical network (5 Regional DCs, 16 Stores, 35 Corridors) with live inventory levels and status indicators. | Interactive multi-layer canvas / WebGL graph |
| **V2** | **Agent Deliberation War Room** | Live feed of multi-agent debate (Demand, Inventory, Supplier, Transport) streaming via WebSockets. | Multi-column conversation stream with claim cards |
| **V3** | **Disruption Injection Lab** | Interactive control panel allowing operators to inject localized disruptions (asset failure, lead-time shock, corridor closure). | Parameter form with immediate blast-radius preview |
| **V4** | **Inventory & Asset Health** | Real-time monitoring of SKU buffer health, stockout risks, and cold-chain asset telemetry (`AST-xxxx`). | Heatmap matrix and equipment telemetry gauges |
| **V5** | **Consensus Decision Matrix** | Real-time CD²F arbitration view displaying agent weights, conflict metrics, and the Human-in-the-Loop approval modal. | Multi-factor radar chart and action approval card |
| **V6** | **What-If Simulation Sandbox** | Interactive parameter sliders allowing side-by-side comparison of alternative mitigation policies against the Day-0 baseline. | Dual-axis metric comparison graphs |
| **V7** | **Audit & Lineage Explorer** | Searchable repository of 8-stage decision traces, contrastive explanations, and pgvector precedent lookups. | Collapsible DAG viewer and audit log table |

---

## 3. Human-in-the-Loop (HITL) Workflow

When the CD²F engine gates an incident to **Tier 3 (Human Escalation)**, the console surfaces a high-priority action modal:
1. **Disruption Summary:** Type, affected facilities, and estimated financial exposure.
2. **Specialist Recommendations:** Tabular comparison of competing claims from Demand, Inventory, Supplier, and Transport agents.
3. **Contrastive Rationale:** Highlights why automated consensus was deferred (e.g., severe conflict score or financial exposure $> \$100,000$).
4. **Action Options:** The operator can `Approve Leading Proposal`, `Select Alternate Agent Claim`, or `Submit Custom Directive`.

---

## 4. Technical Stack & Performance Architecture

* **Desktop Shell:** Tauri v2 with Rust backend providing native window management and local caching.
* **Frontend Core:** Fast, modern reactive UI communicating via high-speed WebSockets and typed REST clients.
* **Graph Rendering:** Hardware-accelerated canvas for fluid rendering of facilities, transport lanes, and freight flows.
* **Resource Envelope:** Target memory footprint $\le 120\text{ MB}$, launch time $\le 1.5\text{ s}$.

---

## 5. Acceptance Criteria & Verification Evidence

1. **Rendering Performance Gate:** Sustained 60 FPS during pan/zoom operations across the 21-facility network topology.
2. **WebSocket Latency Gate:** Agent deliberation tokens and state transitions render in the War Room within $\le 45\text{ ms}$ of arrival.
3. **HITL Interactivity Gate:** Tier-3 human intervention immediately unblocks the D05 Orchestration Kernel upon submission.
4. **State Integrity Gate:** What-If sandbox simulations run strictly in isolated Layer 3 contexts with zero mutation of baseline state.
