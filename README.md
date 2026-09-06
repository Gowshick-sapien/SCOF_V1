# SCOF — Supply Chain Cognitive Orchestration Framework

**Powered by CD²F (Consensus-Driven Collaborative Decision Framework)**

An autonomous, multi-agent cognitive operations platform that monitors, predicts, and recommends mitigation decisions for complex enterprise supply chain disruptions in real time.

---

## What is SCOF?

Modern enterprise supply chains face sudden, compounding disruptions: supplier lead-time blowouts, transit route closures, sudden demand surges, and severe weather bottlenecks. Traditional centralized heuristics are rigid, while single-agent generative AI models suffer from localized bias, ungrounded hallucinations, and lack cross-domain operational awareness.

**SCOF** solves this by deploying a collaborative federation of specialized cognitive agents (Demand, Inventory, Supplier, and Logistics) coordinated by an autonomous orchestration kernel. Rather than relying on a single opaque model or unweighted voting, SCOF introduces **CD²F (Consensus-Driven Collaborative Decision Framework)** to arbitrate conflicting specialist claims using continuous confidence and reliability weighting. The result is a sub-second, explainable, and risk-gated mitigation engine designed for mission-critical supply networks.

---

## Key System Capabilities

### 1. Collaborative Multi-Agent Intelligence
Four autonomous domain specialists continuously assess disruption signals in parallel:
* **Demand Agent**: Analyzes consumption velocity, sales surges, and stockout projections.
* **Inventory Agent**: Evaluates warehouse buffer depletion, safety stock thresholds, and holding costs.
* **Supplier Agent**: Monitors component lead times, supplier reliability ratings, and alternate vendor capacities.
* **Transportation Agent**: Assesses transit corridors, carrier delays, expedited freight options, and rerouting feasibility.

### 2. CD²F Dynamic Consensus Arbitration
* **Continuous Multi-Factor Weighting**: Weights specialist recommendations by historical domain competence ($w_i$) and real-time situational confidence ($c_i$), completely eliminating the deadlocks common in traditional voting.
* **Greedy Bias & Error Override**: Automatically identifies and overrules isolated, overconfident specialist claims when cross-functional evidence indicates systemic risk.

### 3. Dual-Path Autonomous Risk Gating
* **Fast-Path Autonomous Execution**: Routine, high-consensus disruptions resolve autonomously in under **335 milliseconds** ($< 500\text{ ms}$ SLA) without human intervention.
* **Slow-Path & Human-in-the-Loop (HITL) Escalation**: Complex, high-severity anomalies ($WCS < 0.70$ or severity $\ge 0.60$) are automatically routed to simulation or human operator review.

### 4. Transparent Explainability & Immutable Audit Trail
* **The "Meeting Log"**: Live, readable conversational transcripts capturing verbatim specialist claims, counter-arguments, and trade-off deliberations.
* **8-Stage Reasoning Trace**: Step-by-step decision trail persisted to PostgreSQL (`scof.decision_records`).
* **Semantic Memory (pgvector)**: 384-dimension vector embeddings enabling natural-language similarity search over historical disruptions.

### 5. Native Desktop Control Room (Apple HIG)
A native desktop operations console built with **Tauri v2 + React 19 + TypeScript**, styled with an ultra-clean, high-contrast dark mode aesthetic, native window controls, and keyboard navigation.

### 6. What-If Counterfactual Simulation Lab
Interactive simulation tools allowing supply chain operators to adjust severity parameters, compare proposed actions side-by-side, and project fill rate preservation prior to physical execution.

---

## System Architecture Flow

```
[ Multimodal Disruption Signal ]
   (Supplier Delay | Transit Failure | Demand Spike | Weather)
                 |
                 v
+-------------------------------------------------------------+
|              FastAPI Real-Time Gateway (:8000)              |
+-------------------------------------------------------------+
                 |
                 v
+-------------------------------------------------------------+
|        LangGraph Coordinator & A2A Orchestration (:8010)    |
|   - Dispatches disruption context to specialist agents      |
+-------------------------------------------------------------+
        |                 |                 |                 |
        v                 v                 v                 v
  +-----------+     +-----------+     +-----------+     +-----------+
  |  Demand   |     | Inventory |     | Supplier  |     | Transport |
  |   Agent   |     |   Agent   |     |   Agent   |     |   Agent   |
  |  (:8011)  |     |  (:8012)  |     |  (:8013)  |     |  (:8014)  |
  +-----------+     +-----------+     +-----------+     +-----------+
        |                 |                 |                 |
        +-----------------+-----------------+-----------------+
                                  |
                                  v
+-------------------------------------------------------------+
|              CD²F Consensus Arbitration Engine (:8020)      |
|   - Multi-factor weighting (W_i = w_i * c_i)                |
|   - Weighted Consensus Stability (WCS) computation          |
|   - Escalation Tier Gating (Fast-Path / Slow-Path / HITL)   |
+-------------------------------------------------------------+
                                  |
        +-------------------------+-------------------------+
        |                                                   |
        v                                                   v
+-----------------------------------+   +-----------------------------------+
|     Observability Backend (:8030) |   |   Desktop Operations Console      |
|   - PostgreSQL decision ledger    |   |   - Live Supply Chain Topology    |
|   - pgvector semantic memory      |   |   - Agent Meeting Log Inspector   |
|   - Kafka event streaming bus     |   |   - Evaluation & Benchmarking     |
+-----------------------------------+   +-----------------------------------+
```

---

## How to Run SCOF

### Prerequisites
* **Docker & Docker Compose** (v24+ recommended)
* **Python 3.12+**
* **Node.js 20+** & **npm**
* **Rust & Cargo** (optional, required only for native Tauri desktop build; web preview available via browser)

---

### Step 1: Clone and Configure Environment

```bash
git clone https://github.com/Gowshick-sapien/SCOF_V1.git
cd SCOF_V1/SCOF

# Create local environment configuration from template
cp .env.example .env
```

---

### Step 2: Start Background Infrastructure & Microservices

Start the complete microservice fleet (PostgreSQL, Redis, Kafka, Neo4j, API Gateway, Coordinator, Consensus Engine, Observability, and Specialist Agents) via Docker Compose:

```bash
docker compose up -d
```

Verify that all service health checks pass:
```bash
docker compose ps
```

---

### Step 3: Launch the Desktop Operations Console

Navigate to the desktop directory and start the application:

#### Option A: Native Desktop Application (Tauri v2)
```bash
cd desktop
npm run tauri dev
```
*Compiles the native Rust desktop shell and opens the standalone 1440x900 control room window.*

#### Option B: Browser Web Interface
```bash
cd desktop
npm run dev
```
*Access the operations console directly in any modern browser at **`http://localhost:1420`**.*

---

### Step 4: Run an Autonomous Full-Loop Disruption Scenario

Inject a simulated disruption and observe the end-to-end multi-agent resolution in real time:

```bash
python scripts/verify_full_loop.py
```

This script:
1. Verifies health across all 8 microservices.
2. Injects a disruption event via the API Gateway.
3. Coordinates multi-agent claim gathering across Demand, Inventory, Supplier, and Logistics.
4. Arbitrates a consensus decision via CD²F.
5. Persists the reasoning trail to PostgreSQL and indexes the vector embedding in pgvector.
6. Displays the winning mitigation, consensus stability score, and round-trip execution latency.

---

## Navigating the Desktop Operations Console

The Operations Console provides 7 dedicated command views accessible via keyboard shortcuts:

| Shortcut | View Name | Primary Operational Capabilities |
| :--- | :--- | :--- |
| **`Ctrl + 1`** | **Operational Overview** | Global supply network topology visualizer, real-time KPI cards (Reliability, Stock Coverage, Disruption Risk), and live alert feed. |
| **`Ctrl + 2`** | **Decision Center** | Multi-agent debate inspector, verbatim meeting log statements, agent confidence scores, and historical decision ledger. |
| **`Ctrl + 3`** | **Scenario Launcher** | Scenario catalog library; trigger, replay, or simulate custom disruptions across suppliers, transport, and demand. |
| **`Ctrl + 4`** | **Agent Command Center** | Specialist agent fleet monitor; inspect agent health, MCP tool registries, and real-time A2A activity streams. |
| **`Ctrl + 5`** | **What-If Simulation Lab** | Counterfactual impact lab; adjust disruption severity sliders, evaluate alternate routing, and project fill rates. |
| **`Ctrl + 6`** | **Reasoning Trace Explorer**| Vertical 4-phase pipeline inspector; review raw specialist claims, computed weights, and consensus tallies per decision. |
| **`Ctrl + 7`** | **Evaluation & Benchmarks**| System benchmark suite; compare CD²F against baselines, inspect inter-agent agreement Kappa, and review domain breakdown tables. |

---

## Domain Profiles

SCOF is architected to be domain-agnostic. Supply chain topologies, products, facilities, disruptions, and agent policies are defined via declarative YAML Domain Profiles located in `profiles/`:

* **Default Profile**: [`profiles/mvp-electronics/`](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/)
  * Models a high-tech electronics supply chain: 5 products, 5 tier-1 suppliers, 2 distribution centers, and 10 regional transit corridors.
  * Includes declarative configurations for `topology.yaml`, `disruptions.yaml`, `agents.yaml`, `consensus.yaml`, and `dashboard.yaml`.

---

## System Verification & Testing

Execute the comprehensive automated test suite validating decision accuracy, consensus stability, latency distributions, and comparative baselines:

```bash
# Run complete evaluation test suite (40 / 40 tests)
python -m pytest services/evaluation/tests/ -v

# Run comparative baseline benchmark runner
python -m services.evaluation.src.benchmark_runner
```

---

## Documentation & Architecture Deep Dives

For detailed technical specifications, architectural diagrams, and empirical reports, explore the [`docs/`](file:///d:/projects/SCOF_V1/SCOF/docs/) directory:

* **[System Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/architecture.md)**: Deep dive into the LangGraph state machine, MCP tool architecture, and CD²F mathematical formulations.
* **[Software Requirements Specification (SRS)](file:///d:/projects/SCOF_V1/SCOF/docs/srs.md)**: Functional and non-functional requirements specification.
* **[Ideation & Vision](file:///d:/projects/SCOF_V1/SCOF/docs/ideation.md)**: Theoretical foundation, multi-agent collaboration rationale, and research questions.
* **[Evaluation & Research Results Report](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D10_integration_evaluation/results_report.md)**: Empirical validation answering Research Questions RQ1–RQ4 across 20 canonical disruption scenarios.
* **[Acceptance Evidence Document](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D10_integration_evaluation/acceptance_evidence.md)**: Detailed audit logs and verification matrices across all system capabilities.
