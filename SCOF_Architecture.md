# **SCOF — System Architecture Document**

## **Supply Chain Cognitive Orchestration Framework**

### **Powered by CD²F (Consensus-Driven Collaborative Decision Framework)**

**Document Version:** 1.0 **Status:** Draft **Prepared for:** SCOF MVP Development (Docker-Simulation Phase)

**Source Documents:** SCOF Ideation Document (Sections 1–23), Software Requirements Specification (SRS), Implementation Plan (D1–D11), Domain Binding Strategy

---

## **1\. System Overview**

### **1.1 What SCOF Is**

SCOF is a **profile-driven, multi-agent cognitive platform** that monitors, predicts, and recommends mitigation decisions for supply chain disruptions. Multiple specialized autonomous agents each own a domain, produce independent predictions, and negotiate a consensus recommendation through the CD²F mechanism — the system's core research contribution.

The platform is **domain-agnostic by design**: its engine (agent orchestration, consensus, observability, API, dashboard) operates independently of any particular supply chain context. The specific supply chain environment — its topology, entities, disruption types, escalation thresholds, and evaluation criteria — is provided through a declarative configuration artifact called a **Domain Profile**. Deploying SCOF to a new supply chain context means writing a new profile, not modifying platform code.

### **1.2 Architectural Principles**

| Principle | Description |
| ----- | ----- |
| **Profile-Driven Configuration** | The supply chain context (topology, agents, disruptions, thresholds, evaluation) is captured in a declarative Domain Profile — not hardcoded into the platform. Changing the deployment context is a configuration change, not a code change. |
| **Distributed Intelligence** | No single model reasons over everything. Each agent owns a domain and produces an independent structured claim before collaboration begins. |
| **Protocol-First Interoperability** | Agents reach their data/tools via **MCP** and reach each other via **A2A** — open, standardized protocols, not hardcoded function calls. |
| **Explainability by Design** | Every decision ships with a reasoning trail, confidence scores, evidence, and an auditable "AI Meeting Log." Traces are persisted and replayable. |
| **Incremental Isolation** | Each deliverable (D1–D10) is independently runnable and testable before being wired into the next stage. |
| **Extensibility without Rearchitecture** | The A2A/MCP protocol layer and profile-driven configuration ensure new agents, data sources, and even new supply chain contexts are additive — not architectural rewrites. |

---

## **2\. Domain Profile Architecture**

### **2.1 The Core Design Decision**

SCOF cannot reason about a supply chain in the abstract — it needs concrete entities, relationships, disruption types, and evaluation criteria. But the platform should not be rebuilt for each deployment. The solution is to treat the operating environment as a **configurable input**:

```
SCOF Platform (unchanged)  +  Domain Profile (per deployment)  =  Running System
```

### **2.2 What a Domain Profile Contains**

A Domain Profile is a directory of declarative YAML configuration files that captures everything SCOF needs to know about a specific supply chain context:

| Profile Component | File | What It Defines |
| ----- | ----- | ----- |
| **Topology** | `topology.yaml` | Entities (manufacturers, suppliers, warehouses, DCs, routes, products) and their relationships, locations, and operational parameters |
| **Agent Roster** | `agents.yaml` | Which agents are active, their model configurations, MCP tool bindings, confidence thresholds, and historical accuracy windows |
| **Disruption Catalog** | `disruptions.yaml` | What disruption types are relevant (with parameters, severity scales, propagation rules, and which agents they trigger) |
| **Consensus Tuning** | `consensus.yaml` | CD²F escalation thresholds, impact scale definitions, fast-path/slow-path/human-escalation criteria, and calibration settings |
| **Data Bindings** | `data_bindings.yaml` | MCP server configurations, database connection mappings, ETL source/target specifications |
| **Evaluation Criteria** | `evaluation.yaml` | Which metrics define "good," which baselines to benchmark against, and which scenario sets to use |
| **Dashboard Configuration** | `dashboard.yaml` | Which views are active, map bounds/coordinates, entity display names, heatmap dimensions and scales |

### **2.3 Profile Directory Structure**

```
profiles/
└── <profile-name>/
    ├── profile.yaml              # Top-level metadata (name, version, description)
    ├── topology.yaml             # Entities and relationships
    ├── agents.yaml               # Active agents and their configurations
    ├── disruptions.yaml          # Disruption catalog
    ├── consensus.yaml            # CD²F thresholds and escalation rules
    ├── data_bindings.yaml        # MCP server configs, DB connection mappings
    ├── evaluation.yaml           # Metrics, baselines, scenario sets
    ├── dashboard.yaml            # View configuration, map bounds, labels
    └── scenarios/
        ├── calibration_set.json  # Hand-labeled scenarios for judge calibration
        └── evaluation_set.json   # Scenarios for benchmark evaluation
```

### **2.4 How Layers Consume the Profile**

| SCOF Layer | What It Reads from the Profile |
| ----- | ----- |
| **D1 — Simulation** | `topology.yaml` → generates entities and relationships matching the profile |
| **D2 — Knowledge Layer** | `topology.yaml` + `data_bindings.yaml` → builds Neo4j graph and pgvector schemas from profile |
| **D3/D4 — Agents** | `agents.yaml` → model selection, thresholds, MCP tool bindings per agent |
| **D5 — Orchestration** | `agents.yaml` → Coordinator discovers active agents via A2A at startup |
| **D6 — CD²F** | `consensus.yaml` → escalation thresholds, impact scales, calibration settings |
| **D7 — Observability** | Agent IDs from profile → traces keyed by profile-defined agent identifiers |
| **D8 — API** | Profile metadata → validates scenario triggers and parameterizes responses |
| **D9 — Dashboard** | `dashboard.yaml` → map bounds, entity labels, active views, heatmap scales |
| **D10 — Evaluation** | `evaluation.yaml` → metrics, baselines, scenario sets |

### **2.5 Deployment Patterns**

**Pattern 1 — Single-Profile (MVP):** One SCOF instance, one Domain Profile. The MVP uses this pattern, with the current scope (1 manufacturer, 5 suppliers, 2 warehouses, etc.) expressed as the profile rather than as hardcoded values.

**Pattern 2 — Multi-Profile Switchable:** One SCOF instance loads different profiles at startup or runtime. Useful for organizations with multiple supply chain contexts (e.g., different product lines, different regions).

**Pattern 3 — Multi-Tenant:** Multiple SCOF instances, each with its own profile and isolated data stores, sharing core platform containers. The path toward SCOF-as-a-service.

### **2.6 What Is Already Domain-Agnostic (No Profile Needed)**

These platform components work identically across all profiles:

* The **Structured Claim Contract** — universal agent output format
* The **A2A protocol** — agents self-describe via Agent Cards regardless of domain
* The **MCP protocol** — tool/data access abstraction
* The **LangGraph orchestration engine** — state graph structure is domain-independent
* The **CD²F arbitration algorithm** — confidence-weighted voting works on any claim bundle of any size
* The **Observability layer** — traces are keyed by agent ID and decision ID, not by domain
* The **API endpoint structure** — parameterized by IDs, not by entity types
* The **Dashboard component library** — different components are *activated* per profile, but the same library exists

---

## **3\. High-Level Architecture**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              USER LAYER                                      │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                    Frontend Dashboard (D9)                           │   │
│   │  React · Next.js · TypeScript · Tailwind CSS · D3/Recharts · Leaflet │   │
│   │                                                                      │   │
│   │  ┌─────────────┐ ┌──────────────┐ ┌─────────────┐ ┌──────────────┐  │   │
│   │  │ Operational  │ │ Supply Chain │ │  AI Meeting │ │  What-If     │  │   │
│   │  │ Dashboard    │ │ Map (Leaflet)│ │  Log View   │ │  Simulation  │  │   │
│   │  └─────────────┘ └──────────────┘ └─────────────┘ └──────────────┘  │   │
│   │  ┌─────────────┐ ┌──────────────┐ ┌─────────────┐ ┌──────────────┐  │   │
│   │  │ Confidence & │ │  Decision    │ │  Risk       │ │  Scenario    │  │   │
│   │  │ Disagreement │ │  Replay UI   │ │  Heatmap    │ │  Library     │  │   │
│   │  └─────────────┘ └──────────────┘ └─────────────┘ └──────────────┘  │   │
│   │  ┌─────────────┐ ┌──────────────┐                                    │   │
│   │  │ Recommend.   │ │  AI Chat     │                                    │   │
│   │  │ Timeline     │ │  (NL Q&A)    │                                    │   │
│   │  └─────────────┘ └──────────────┘                                    │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                               │ HTTP/REST + WebSocket                        │
└───────────────────────────────┼──────────────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           API & REAL-TIME LAYER (D8)                         │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                      FastAPI Backend Service                         │   │
│   │                                                                      │   │
│   │  /scenarios/trigger   /whatif/run   /dashboard/state                  │   │
│   │  /decisions/{id}/log  /decisions/{id}/trace  /decisions/{id}/replay   │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│          │                          │                          │              │
│    ┌─────┴─────┐             ┌──────┴──────┐          ┌───────┴───────┐     │
│    │ WebSocket │             │ Event Bus   │          │ REST          │     │
│    │ (Live     │             │ (Kafka /    │          │ Endpoints     │     │
│    │  Push)    │             │  RabbitMQ)  │          │               │     │
│    └───────────┘             └─────────────┘          └───────────────┘     │
└──────────────────────────────────────────────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     OBSERVABILITY & EXPLAINABILITY LAYER (D7)                 │
│                                                                              │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│   │ LangSmith /      │  │ Decision Trace   │  │ Judge Calibration        │  │
│   │ Langfuse Tracing │  │ Persistence      │  │ Metrics Logger           │  │
│   │ (per-agent turn, │  │ (Postgres/       │  │ (Cohen's kappa over      │  │
│   │  token cost,     │  │  pgvector, keyed │  │  time, queryable)        │  │
│   │  latency)        │  │  per decision)   │  │                          │  │
│   └──────────────────┘  └──────────────────┘  └──────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         CD²F CONSENSUS ENGINE (D6)                           │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────┐         │
│   │                  Arbitration Pipeline                           │         │
│   │                                                                │         │
│   │  Structured Claims ──► Confidence-Weighted Voting ──► Decision │         │
│   │   (from all agents)    (stated confidence × rolling            │         │
│   │                         historical accuracy)                   │         │
│   └────────────────────────────────────────────────────────────────┘         │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                Escalation Tiering (profile-configurable)              │   │
│   │                                                                      │   │
│   │   FAST PATH              SLOW PATH              HUMAN ESCALATION     │   │
│   │   ┌──────────────┐      ┌──────────────┐       ┌──────────────┐     │   │
│   │   │ Single agent │      │ Full CD²F    │       │ Low consensus│     │   │
│   │   │ High conf.   │──►   │ multi-agent  │──►    │ or high      │     │   │
│   │   │ Low impact   │      │ discussion   │       │ impact       │     │   │
│   │   └──────────────┘      └──────────────┘       └──────────────┘     │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Thresholds, impact scales, and escalation criteria read from               │
│   consensus.yaml in the active Domain Profile.                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                  AGENT ORCHESTRATION & PROTOCOL LAYER (D5)                    │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                      LangGraph State Graph                           │   │
│   │                                                                      │   │
│   │                    ┌─────────────────────┐                           │   │
│   │                    │  COORDINATOR AGENT  │                           │   │
│   │                    │  Discovers agents   │                           │   │
│   │                    │  via A2A Agent Cards│                           │   │
│   │                    │  (roster from       │                           │   │
│   │                    │   agents.yaml)      │                           │   │
│   │                    └────────┬────────────┘                           │   │
│   │           ┌────────────────┼────────────────┐                       │   │
│   │           │ A2A            │ A2A            │ A2A                    │   │
│   │           ▼                ▼                ▼                        │   │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│   │  │  DEMAND    │  │ INVENTORY  │  │  SUPPLIER  │  │ TRANSPORT  │    │   │
│   │  │  AGENT     │  │  AGENT     │  │  AGENT     │  │  AGENT     │    │   │
│   │  │  (D3)      │  │  (D3)      │  │  (D4)      │  │  (D4)      │    │   │
│   │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘    │   │
│   │        │ MCP           │ MCP           │ MCP           │ MCP        │   │
│   │        ▼               ▼               ▼               ▼            │   │
│   │   Tools & Data    Tools & Data    Tools & Data    Tools & Data      │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Agent set is determined by agents.yaml — adding/removing an agent is       │
│   a profile configuration change, not a code change.                         │
└──────────────────────────────────────────────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    DATA & KNOWLEDGE LAYER (D1 + D2)                          │
│                                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │  PostgreSQL  │  │  pgvector    │  │    Neo4j     │  │    Redis     │   │
│   │  (Operational│  │  (Decision   │  │  (Knowledge  │  │  (Cache,     │   │
│   │   DB: orders,│  │   records,   │  │   Graph:     │  │   session,   │   │
│   │   inventory, │  │   evidence   │  │   supplier → │  │   ephemeral  │   │
│   │   suppliers, │  │   embeddings,│  │   product →  │  │   state)     │   │
│   │   shipments) │  │   AI Chat    │  │   warehouse  │  │              │   │
│   │              │  │   retrieval) │  │   → route)   │  │              │   │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │          Synthetic Data & Disruption Generator (D1)                   │   │
│   │  Reads topology.yaml and disruptions.yaml from the active profile    │   │
│   │  to generate entities, relationships, and disruption events.         │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                      ETL Pipeline (D2)                                │   │
│   │  Reads data_bindings.yaml to load D1 data into Neo4j + Postgres.     │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                   DOMAIN PROFILE (active)                             │   │
│   │  profiles/<profile-name>/                                             │   │
│   │  topology.yaml · agents.yaml · disruptions.yaml · consensus.yaml     │   │
│   │  data_bindings.yaml · evaluation.yaml · dashboard.yaml               │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## **4\. Layer-by-Layer Architecture**

### **4.1 Data & Knowledge Layer (D1 + D2)**

This is the foundation — all data exists and is queryable **before any agent code is written**. Entity structure and relationships are derived from the active Domain Profile's `topology.yaml`.

#### **4.1.1 Simulation Environment (D1)**

| Component | Technology | Role |
| ----- | ----- | ----- |
| **Synthetic Data Generator** | Python scripts | Reads `topology.yaml` to generate entities matching the profile's declared manufacturers, products, suppliers, warehouses, DCs, and routes |
| **Disruption Event Generator** | Python scripts | Reads `disruptions.yaml` to produce parameterized events matching the profile's declared disruption types, severity scales, and propagation rules |
| **Infrastructure Containers** | Docker Compose | Provisions PostgreSQL, Redis, Kafka/RabbitMQ, Neo4j as standalone containers — no application logic |

#### **4.1.2 Knowledge & Data Stores (D2)**

**Neo4j Schema** — models the supply chain as a graph, derived from `topology.yaml`:

```
(:Supplier)-[:SUPPLIES]->(:Product)
(:Product)-[:STORED_IN]->(:Warehouse)
(:Warehouse)-[:SHIPS_VIA]->(:Route)
(:Route)-[:DELIVERS_TO]->(:DistributionCenter)
(:Supplier)-[:ALTERNATE_FOR]->(:Supplier)
```

**pgvector Schema** — stores vectorized decision data for retrieval:

| Table | Purpose |
| ----- | ----- |
| `decision_records` | Final decisions with metadata, keyed per disruption event |
| `evidence_snippets` | Supporting data fragments referenced by agent claims |
| `embeddings` | Vector representations for similarity search (AI Chat retrieval) |

---

### **4.2 Specialist Agent Layer (D3 + D4)**

Each agent is a **standalone, independently testable service** that produces a **structured claim** conforming to the universal claim contract. Agent configuration (model selection, thresholds, MCP bindings) is read from the profile's `agents.yaml`.

#### **4.2.1 Structured Claim Contract**

Every agent, without exception, outputs this structure:

```json
{
  "recommendation": "Proposed action (string)",
  "confidence": 0.93,
  "priority": "HIGH | MEDIUM | LOW",
  "impact": "Estimated magnitude of consequence if ignored",
  "evidence": [
    {
      "type": "historical_data | model_output | graph_query | external_signal",
      "source": "reference to backing data",
      "summary": "human-readable evidence description"
    }
  ]
}
```

#### **4.2.2 Agent Specifications (MVP)**

| Agent | ML Stack | Data Sources (via MCP) | Output Focus |
| ----- | ----- | ----- | ----- |
| **Demand Agent** | XGBoost + Prophet + Chronos-2 ensemble | Historical sales, seasonality, promotions (PostgreSQL) | Future demand forecast |
| **Inventory Agent** | Same ensemble approach | Warehouse stock levels, safety stock, reorder points (PostgreSQL) | Stockout/overstock prediction |
| **Supplier Agent** | Reliability scoring model | Neo4j graph (supplier relationships) + historical delivery data | Supplier failure prediction, reliability score |
| **Transport Agent** | Delay prediction model | Route network (Neo4j) + shipment history (PostgreSQL) | Delay prediction, rerouting options |

#### **4.2.3 MCP Tool/Data Access Pattern**

Each agent accesses its tools and data through **MCP (Model Context Protocol)** servers — not direct database connections. The MCP server configurations are declared in the profile's `agents.yaml` and `data_bindings.yaml`:

```
┌─────────────┐      MCP Protocol       ┌──────────────────────┐
│  Agent       │ ◄──────────────────────► │  MCP Server          │
│  (reads its  │                          │  (tools declared in  │
│   config from│                          │   agents.yaml)       │
│   agents.yaml│                          │                      │
│  )           │                          │                      │
└─────────────┘                          └──────────┬───────────┘
                                                    │
                                         ┌──────────▼───────────┐
                                         │  Data Store           │
                                         │  (connection from     │
                                         │   data_bindings.yaml) │
                                         └──────────────────────┘
```

---

### **4.3 Agent Orchestration & Protocol Layer (D5)**

This layer wires agents into a coordinated system using **LangGraph** for state management and **A2A** for agent discovery/delegation. The active agent set is determined by the profile's `agents.yaml`.

#### **4.3.1 A2A Agent Card Schema**

Each agent publishes an **Agent Card** that the Coordinator uses for discovery:

```json
{
  "agent_id": "supplier-agent-v1",
  "name": "Supplier Intelligence Agent",
  "description": "Monitors supplier reliability and predicts failures",
  "capabilities": ["supplier_reliability_scoring", "failure_prediction", "alternate_supplier_lookup"],
  "input_schema": { "scenario_id": "string", "disruption_event": "object" },
  "output_schema": "StructuredClaim",
  "protocol": "A2A/1.0",
  "endpoint": "http://supplier-agent:8001/a2a"
}
```

The Coordinator **discovers** agents dynamically through the A2A registry. Adding a new agent means: (1) adding its block to `agents.yaml`, (2) deploying its container, (3) the Coordinator discovers it via A2A — no orchestration code changes.

#### **4.3.2 Why LangGraph**

| Criterion | LangGraph | CrewAI / AutoGen |
| ----- | ----- | ----- |
| State checkpointing | Explicit per-node | Implicit / session-based |
| Decision replay | Native (state graph snapshots) | Requires custom implementation |
| Per-node observability | Built-in with LangSmith | Requires additional wiring |
| Agent state model | Explicit graph — nodes and edges | Role-based / conversational |

---

### **4.4 CD²F Consensus Engine (D6)**

The research core. Operates on claim bundles of arbitrary size (not hardcoded to 4 agents). All thresholds and scales are read from the profile's `consensus.yaml`.

#### **4.4.1 Three Design Anchors**

| Design Choice | Mechanism | Rationale |
| ----- | ----- | ----- |
| **Vote Weighting** | `weight = stated_confidence × rolling_historical_accuracy` | Self-reported confidence alone is unreliable; pairing it with a track record makes agreement meaningful |
| **Error Correlation Control** | Vary underlying model/prompt families across agents | Homogeneous agents fail on the same inputs — consensus from identical models is illusory |
| **Escalation Tiering** | Fast path → Slow path → Human escalation | Keeps latency low for routine calls; reserves expensive discussion for cases that need it |

#### **4.4.2 Profile-Configurable Escalation**

The escalation thresholds are not hardcoded — they are read from `consensus.yaml`:

* **Fast path criteria:** minimum confidence, maximum impact level, single-agent sufficiency
* **Slow path criteria:** minimum confidence for full discussion, maximum impact before human escalation
* **Human escalation criteria:** consensus stability threshold, impact level floor
* **Impact scale:** domain-specific levels and thresholds (e.g., financial cost vs. patient safety)

This means a high-volume, low-stakes deployment (e.g., FMCG) can widen the fast-path for speed, while a safety-critical deployment (e.g., pharmaceuticals) can narrow it aggressively — without code changes.

#### **4.4.3 Judge Calibration**

* **Metric:** Cohen's kappa (inter-rater agreement vs. hand-labeled set)
* **Purpose:** Detect judge drift — Coordinator arbitration quality degrades silently without calibration checks
* **Configuration:** Check frequency and kappa threshold set in `consensus.yaml`

#### **4.4.4 Baselines for Evaluation**

| Baseline | Description | Purpose |
| ----- | ----- | ----- |
| **Single-Agent** | One agent makes the decision alone | Lower bound — does multi-agent collaboration add value? |
| **Naive Majority Voting** | Simple majority vote across agent recommendations | Known failure mode — amplifies shared errors. CD²F must outperform this. |

---

### **4.5 Observability & Explainability Layer (D7)**

Every agent turn and every consensus decision is **fully inspectable** before any UI is built. Traces are keyed by profile-defined agent IDs.

**What gets stored per decision:**

* Every agent call (input, output, latency, token cost)
* Every structured claim
* The arbitration outcome (final decision, reasoning trail, escalation tier)
* The confidence/disagreement breakdown
* Judge calibration metrics

---

### **4.6 API & Real-Time Layer (D8)**

#### **4.6.1 FastAPI Endpoint Map**

| Endpoint Group | Endpoints | Description |
| ----- | ----- | ----- |
| **Scenarios** | `POST /scenarios/trigger` | Trigger a disruption scenario |
| **What-If** | `POST /whatif/run`, `GET /whatif/{id}/result` | Run and retrieve what-if simulations |
| **Dashboard** | `GET /dashboard/state` | Current supply chain state |
| **Decisions** | `GET /decisions/{id}/log` | AI Meeting Log |
| | `GET /decisions/{id}/confidence` | Confidence & Disagreement View |
| | `GET /decisions/{id}/trace` | Full reasoning trail / replay data |
| **Evaluation** | `GET /evaluation/benchmark` | Benchmark results |
| **Chat** | `POST /chat/query` | AI Chat — NL Q&A over operational data |
| **Profile** | `GET /profile/active` | Active Domain Profile metadata |

#### **4.6.2 Event-Driven Architecture**

The event bus (Kafka / RabbitMQ) **decouples** the simulation (D1) from the orchestration (D5):

* Disruption events can be replayed without re-running the generator
* Multiple consumers can subscribe to the same event stream
* The same architecture supports both synthetic events (MVP) and real events (post-MVP)

#### **4.6.3 WebSocket Channels**

| Channel | Payload | Consumer |
| ----- | ----- | ----- |
| `ws://dashboard/state` | Live supply chain state updates | Operational Dashboard |
| `ws://decisions/live` | New decision notifications | Meeting Log, Recommendation Timeline |
| `ws://agents/activity` | Agent execution status | Supply Chain Map |

---

### **4.7 Frontend Dashboard Layer (D9)**

Built against the stable D8 API. All views are data-driven from the observability layer (D7). Active views and display configuration (map bounds, entity labels, heatmap scales) are read from the profile's `dashboard.yaml`.

#### **4.7.1 View Inventory**

| View Category | Views |
| ----- | ----- |
| **Primary** | Operational Dashboard, Supply Chain Map (Leaflet), AI Meeting Log, Confidence & Disagreement View |
| **Analysis** | What-If Simulation, Scenario Library, Scenario Comparison, Decision Replay |
| **Intelligence** | Recommendation Timeline, Risk Heatmap, AI Chat (NL Q&A grounded in pgvector retrieval) |

---

## **5\. End-to-End Data Flow**

The complete data flow from disruption injection to human-visible decision:

```
                        ┌──────────────┐
                        │ Domain       │
                        │ Profile      │ ◄── Loaded at startup
                        │ (active)     │
                        └──────┬───────┘
                               │ configures all layers
                               ▼
  ┌──────────┐    ┌──────────────┐    ┌──────────────┐
  │  D1:     │    │  Event Bus   │    │  D5:         │
  │  Simulate│───►│  (Kafka /    │───►│  Coordinator │
  │  Disrupt.│    │   RabbitMQ)  │    │  discovers   │
  └──────────┘    └──────────────┘    │  agents via  │
                                      │  A2A         │
                                      └──────┬───────┘
                               ┌─────────────┼─────────────┐
                               │ A2A         │ A2A         │ A2A
                               ▼             ▼             ▼
                          ┌────────┐   ┌────────┐   ┌────────┐
                          │ Agent  │   │ Agent  │   │ Agent  │  ...N agents
                          │  (MCP) │   │  (MCP) │   │  (MCP) │  (from profile)
                          └───┬────┘   └───┬────┘   └───┬────┘
                              │            │            │
                              └────────────┼────────────┘
                                           │ Structured Claims
                                           ▼
                                    ┌──────────────┐
                                    │  D6: CD²F    │
                                    │  Consensus   │ ◄── thresholds from
                                    │  Engine      │     consensus.yaml
                                    └──────┬───────┘
                                           │ Final Decision
                                           │ + Reasoning Trail
                                           │ + Escalation Tier
                                           ▼
                                    ┌──────────────┐
                                    │  D7:         │
                                    │  Persist     │
                                    │  Trace       │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  D8: API +   │
                                    │  WebSocket   │
                                    │  push        │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  D9:         │ ◄── views configured by
                                    │  Dashboard   │     dashboard.yaml
                                    └──────────────┘
```

---

## **6\. Deployment Architecture**

### **6.1 Docker Compose Service Map**

All services run within a **single Docker Compose** environment for the MVP.

| Service | Base Image | Persistent Volume | Exposed Port |
| ----- | ----- | ----- | ----- |
| PostgreSQL + pgvector | `pgvector/pgvector:pg16` | `pgdata:/var/lib/postgresql/data` | 5432 |
| Neo4j | `neo4j:5` | `neo4jdata:/data` | 7474, 7687 |
| Redis | `redis:7-alpine` | `redisdata:/data` | 6379 |
| Kafka | `confluentinc/cp-kafka:7` | `kafkadata:/var/lib/kafka/data` | 9092 |
| FastAPI Backend | `python:3.11-slim` | — | 8000 |
| Next.js Frontend | `node:20-alpine` | — | 3000 |
| Each Agent | `python:3.11-slim` | — | 8010–8014 |
| LangSmith/Langfuse | Vendor image | `tracedata:/data` | 4000 |

### **6.2 Profile Loading**

The active Domain Profile directory is mounted into the Docker Compose environment via a volume or environment variable:

```yaml
# docker-compose.yml (excerpt)
services:
  api:
    environment:
      - SCOF_PROFILE_PATH=/profiles/acme-electronics-southeast-asia
    volumes:
      - ./profiles:/profiles:ro
```

All services read their configuration from the profile path at startup.

---

## **7\. Technology Stack Summary**

| Layer | Technologies |
| ----- | ----- |
| **Frontend** | React, TypeScript, Next.js, Tailwind CSS, D3.js / Recharts, Leaflet |
| **Backend API** | Python, FastAPI |
| **Real-Time** | WebSockets (FastAPI) |
| **Agent Orchestration** | LangGraph (state graph model) |
| **Agent Protocols** | MCP (tool/data access), A2A (agent discovery/delegation) |
| **Agent Observability** | LangSmith or Langfuse |
| **ML / Forecasting** | PyTorch, Scikit-Learn, XGBoost, Prophet, LightGBM, Chronos-2 |
| **Graph Database** | Neo4j (Cypher queries) |
| **Vector Store** | pgvector on PostgreSQL |
| **Operational Database** | PostgreSQL |
| **Cache** | Redis |
| **Message Broker** | Apache Kafka or RabbitMQ |
| **Containerization** | Docker, Docker Compose |
| **Configuration** | Domain Profiles (YAML) |
| **Deployment** | AWS, Azure, or local Docker |

---

## **8\. Security & Isolation**

| Concern | MVP Approach |
| ----- | ----- |
| **Network Isolation** | All services communicate within the Docker Compose internal network. No services are exposed externally except the frontend (port 3000) and API (port 8000). |
| **Data Isolation** | MVP uses entirely synthetic data — no PII, no external data feeds, no live ERP connections. |
| **Agent Isolation** | Each agent runs in its own container with its own process boundary. MCP enforces tool-level access control. |
| **Trace Security** | Decision traces are persisted in PostgreSQL with access controlled at the API layer. |
| **Profile Isolation** | Domain Profiles are mounted read-only. In multi-tenant deployments, each tenant's data stores are isolated. |

---

## **9\. Evaluation Architecture (D10)**

### **9.1 Metrics Computed**

Metrics and baselines are read from the profile's `evaluation.yaml`:

| Category | Metrics |
| ----- | ----- |
| **Decision Quality** | Decision Accuracy, Consensus Quality, Agent Agreement Rate, Judge Calibration (Cohen's kappa) |
| **Prediction Quality** | Per-model Prediction Accuracy, Forecast Calibration (probabilistic outputs) |
| **Operational Impact** | Response Time (fast-path vs. slow-path breakdown), Risk Reduction, Inventory Cost, Fill Rate |

### **9.2 Benchmark Design**

CD²F is benchmarked against two baselines across a hand-labeled scenario set (from the profile's `scenarios/` directory):

* **Single-Agent Baseline** — best-performing single agent makes the decision alone
* **Naive Majority Voting Baseline** — simple majority vote across agent recommendations

Results map directly to Research Questions RQ1–RQ4.

---

## **10\. Post-MVP Extension Points (D11)**

These are **interface definitions only** — no code is built for MVP. The profile-driven architecture validates that these extensions are additive.

| Extension | Attachment Point | How Profile Enables It |
| ----- | ----- | ----- |
| **Risk Agent** (GNN over Neo4j) | New node in LangGraph state graph | Add agent block to `agents.yaml`, deploy container |
| **Finance Agent** | New A2A-discoverable specialist | Add agent block to `agents.yaml` |
| **Sustainability Agent** | New A2A-discoverable specialist | Add agent block to `agents.yaml` |
| **Weather Agent** | New A2A-discoverable specialist + external API | Add agent block to `agents.yaml` + MCP server in `data_bindings.yaml` |
| **Cross-Org Agent Handoff** | External agent via A2A | Add external endpoint to `agents.yaml` — same A2A protocol |
| **Digital Twin Playback** | Extension of D7 trace storage | Extend trace schema — profile adds propagation replay fields |
| **New Disruption Types** | Domain-specific events | Add entries to `disruptions.yaml` |
| **New Supply Chain Context** | Entirely new deployment scope | Write a new profile directory — no platform changes |

---

## **11\. Deliverable Dependency & Build Order**

| Deliverable | Independently Testable Output | Depends On | Profile Files Used |
| ----- | ----- | ----- | ----- |
| **D1** | Queryable synthetic dataset + disruption events | — | `topology.yaml`, `disruptions.yaml` |
| **D2** | Queryable graph + vector store | D1 | `topology.yaml`, `data_bindings.yaml` |
| **D3** | Callable Demand + Inventory agent APIs | D1, D2 | `agents.yaml` |
| **D4** | Callable Supplier + Transportation agent APIs | D1, D2 | `agents.yaml` |
| **D5** | Full raw claim bundle via A2A/MCP orchestration | D3, D4 | `agents.yaml` |
| **D6** | Validated consensus decisions on fixture data | (standalone fixtures) | `consensus.yaml` |
| **D7** | Fully inspectable decision traces | D5, D6 | — |
| **D8** | Fully API-drivable pipeline | D1–D7 | `profile.yaml` |
| **D9** | Clickable dashboard demo | D8 | `dashboard.yaml` |
| **D10** | **MVP**: full loop + benchmark results | D1–D9 | `evaluation.yaml` |
| **D11** | Extension interface doc (no code) | D10 | — |

**Note:** D6 is independently testable against fixture data — it does not require live D5 output for initial validation. This allows the consensus engine to be developed and validated in parallel with D5's protocol wiring.

---

## **12\. Cross-Cutting Concerns**

### **12.1 Explainability**

Every recommendation ships with: reason, confidence (0–100%), evidence (specific data/signals), meeting log (full inter-agent discussion transcript), and disagreement map (where agents diverged and how arbitration resolved it).

### **12.2 Reproducibility**

All synthetic data generation and ETL processes are idempotent and re-runnable. Decision traces are persisted and replayable from storage alone. Docker Compose ensures the entire environment is reproducible on any machine. Domain Profiles make the configuration itself reproducible and version-controllable.

### **12.3 Modularity**

Each deliverable is independently runnable and testable in isolation. Agents are standalone services. The Coordinator discovers agents via A2A registry, not hardcoded imports. The Domain Profile further decouples configuration from code.

### **12.4 Research Traceability**

| Deliverable | Research Questions Supported |
| ----- | ----- |
| D6 (Consensus Engine) | RQ1 (decision quality), RQ2 (false/low-confidence reduction) |
| D7 (Observability) | RQ3 (trust via explainability) |
| D8–D9 (API + Dashboard) | RQ3 (trust), RQ4 (response time) |
| D10 (Evaluation) | RQ1–RQ4 (all, via benchmarks) |
