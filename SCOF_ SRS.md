# **Software Requirements Specification (SRS)**

## **SCOF — Supply Chain Cognitive Orchestration Framework**

### **Powered by CD²F (Consensus-Driven Collaborative Decision Framework)**

**Document Version:** 1.0 **Status:** Draft **Prepared for:** SCOF MVP Development (Docker-Simulation Phase)

---

## **1\. Introduction**

### **1.1 Purpose**

This Software Requirements Specification (SRS) defines the functional and non-functional requirements for SCOF, a multi-agent cognitive platform that monitors, predicts, and recommends mitigation decisions for supply chain disruptions. The document translates the project's vision and research goals into requirements that guide the design, implementation, and evaluation of the MVP, structured according to the deliverable-based implementation plan (D1–D11).

### **1.2 Scope**

SCOF is an AI-powered decision-support system in which multiple specialized autonomous agents (Supplier, Inventory, Transportation, Demand, Coordinator, and post-MVP: Risk, Finance, Sustainability, Weather) observe supply chain data, generate individual predictions, and negotiate a consensus recommendation through the CD²F mechanism. The system exposes this reasoning process to human operators through a dashboard, including an auditable "AI Meeting Log," confidence/disagreement views, and what-if simulation tools.

The MVP is built and validated entirely within a **Docker-based simulation environment** using synthetic data — no live ERP/IoT integration is in scope for this phase.

### **1.3 Intended Audience**

* Development team (backend, ML/agent engineers, frontend engineers)  
* Research supervisors / academic reviewers  
* Project stakeholders evaluating feasibility and novelty  
* Future contributors extending the system post-MVP

### **1.4 Definitions, Acronyms, Abbreviations**

| Term | Definition |
| ----- | ----- |
| SCOF | Supply Chain Cognitive Orchestration Framework |
| CD²F | Consensus-Driven Collaborative Decision Framework |
| MCP | Model Context Protocol — standardized tool/data access for agents |
| A2A | Agent-to-Agent protocol — agent discovery and delegation |
| Agent Card | A published descriptor of an agent's capabilities used for A2A discovery |
| Claim | A structured output from an agent: recommendation, confidence, priority, impact, evidence |
| Meeting Log | A stored, human-readable transcript of inter-agent discussion for a given decision |
| Fast/Slow Path | Escalation tiers in CD²F based on confidence and impact thresholds |
| MVP | Minimum Viable Product (Deliverables D1–D10) |

### **1.5 References**

* SCOF Ideation Document (Project Themes, Vision, Objectives, Architecture, Section 1–23)  
* SCOF Implementation Plan — Docker-Simulation MVP (Deliverables D1–D11)

---

## **2\. Overall Description**

### **2.1 Product Perspective**

SCOF is a new, standalone system (not an extension of an existing ERP). It is conceptually modeled as "NASA Mission Control for Supply Chains": specialized agents each own a domain, and a Coordinator Agent reconciles their input into a single, auditable decision — analogous to a flight director reconciling propulsion, life support, navigation, and comms specialists.

### **2.2 Product Functions (Summary)**

* Real-time monitoring of a simulated supply chain (orders, inventory, suppliers, shipments)  
* Injection and detection of disruption events (supplier delay, transport failure, demand spike, adverse weather)  
* Per-domain prediction by specialized agents, each returning a structured claim  
* Inter-agent negotiation and consensus decision-making via CD²F  
* Human-auditable explanation of every recommendation (reasoning trail, confidence, evidence)  
* What-if scenario simulation and comparison  
* Dashboard visualization: map, risk heatmap, meeting log, recommendation timeline  
* Evaluation harness benchmarking CD²F against single-agent and naive-majority-voting baselines

### **2.3 Product Scope (MVP Boundary)**

As defined in Section 21 of the ideation document, the MVP models a **bounded system**:

* 1 manufacturer producing 3–5 products  
* 5 suppliers with varying reliability profiles  
* 2 warehouses and 1 distribution center  
* A transportation network with multiple route options  
* 5 agents: Supplier, Inventory, Transportation, Demand, Coordinator (Risk, Finance, Sustainability, Weather are deferred to post-MVP)  
* Simulated disruptions only: supplier delays, transport failures, demand spikes, adverse weather  
* Dashboard with live state, agent reasoning ("meeting log"), recommendations, and what-if analysis

All MVP work is validated in a Docker-based simulation with synthetic data before any consideration of real ERP/IoT integration.

### **2.4 User Classes and Characteristics**

| User Class | Description |
| ----- | ----- |
| Supply Chain Operator / Decision-Maker | Reviews recommendations, approves/rejects decisions, runs what-if scenarios |
| Research Evaluator | Reviews evaluation metrics, benchmark comparisons, calibration reports |
| System Administrator | Manages Docker environment, data generation, service health |
| Developer / Extender | Adds new agents or extends orchestration per D11 interface contracts |

### **2.5 Operating Environment**

* Containerized via Docker Compose (local or cloud: AWS/Azure)  
* Backend: Python, FastAPI  
* Frontend: React, TypeScript, Next.js, Tailwind CSS, D3.js/Recharts, Leaflet  
* Data stores: PostgreSQL (+ pgvector), Redis, Neo4j  
* Messaging: Apache Kafka or RabbitMQ  
* Real-time: WebSockets  
* Agent orchestration: LangGraph, with MCP for tool/data access and A2A for agent discovery/delegation

### **2.6 Design and Implementation Constraints**

* MVP must run fully offline against synthetic/simulated data — no external live data feeds or hardware integration  
* Agent orchestration framework choice (LangGraph vs. CrewAI vs. AutoGen vs. Semantic Kernel) must be evaluated and finalized before D5; this SRS assumes LangGraph per the implementation plan  
* Consensus algorithm specifics (confidence-weighted arbitration, learned meta-policy, or rule-based arbitration with escalation) are a design task resolved during D6, but must conform to the structured claim input/output contract defined in Section 3.4  
* All decision traces must be persisted and replayable (non-negotiable, since explainability is a core research contribution)

### **2.7 Assumptions and Dependencies**

* Synthetic data generation (D1) can produce realistic and sufficiently varied disruption scenarios for both training/evaluation and demo purposes  
* A small hand-labeled scenario set can be produced for consensus/judge calibration (Cohen's kappa)  
* LangSmith or Langfuse is available for tracing  
* Team has capacity to evaluate and select one agent-orchestration framework before D5 begins

---

## **3\. System Features and Functional Requirements**

Requirements are grouped by deliverable stage (D1–D11), matching the implementation plan's dependency graph. Each stage lists functional requirements (FR) and its own standalone acceptance/"done" criterion.

### **3.0 Deliverable Dependency Overview**

D1 (Sim Data) → D2 (Knowledge Layer) → D3 (Demand+Inventory Agents) ─┐  
                                      → D4 (Supplier+Transport Agents) ─┤  
                                                                        ▼  
                                D3 \+ D4 → D5 (Orchestration) → D6 (CD²F Consensus Engine)  
                                                                        │  
                                                D6 → D7 (Observability) → D8 (Backend API \+ Realtime)  
                                                                        │  
                                                        D8 → D9 (Frontend Dashboard)  
                                                        D8 \+ D9 → D10 (Integration \+ Evaluation) \= MVP COMPLETE  
                                                        D10 → D11 (Post-MVP interface stubs, not built)

---

### **3.1 D1 — Simulation Environment & Synthetic Data Foundation**

**Objective:** Produce a self-contained, reproducible synthetic supply chain world before any AI touches it.

| ID | Requirement |
| ----- | ----- |
| FR-1.1 | The system shall provide a Docker Compose configuration provisioning Postgres, Redis, Kafka/RabbitMQ, and Neo4j as standalone containers. |
| FR-1.2 | The system shall generate synthetic entities for 1 manufacturer, 3–5 products, 5 suppliers (with varying reliability profiles), 2 warehouses, 1 distribution center, and a multi-route transport network. |
| FR-1.3 | The system shall generate a disruption event generator supporting: supplier delay, transport failure, demand spike, and adverse weather, each parameterized by severity, duration, and timing. |
| FR-1.4 | The generated data shall be queryable directly from Postgres, independent of any agent or API code. |

**Acceptance Criterion (Standalone "Done"):** Running docker compose up, triggering the generator, and querying Postgres directly returns realistic order/inventory/shipment histories and injectable disruption events, with no agents or APIs involved.

---

### **3.2 D2 — Knowledge & Data Layer**

**Objective:** Give agents somewhere to read from and write to, independent of the agents themselves.

| ID | Requirement |
| ----- | ----- |
| FR-2.1 | The system shall define a Neo4j schema modeling supplier, product, warehouse, and route nodes and their relationships. |
| FR-2.2 | The system shall define a pgvector schema in Postgres with tables for decision records, evidence snippets, and embeddings. |
| FR-2.3 | The system shall provide idempotent, re-runnable ETL scripts loading D1's synthetic data into Neo4j and Postgres. |

**Acceptance Criterion:** Cypher queries (e.g., shortest path between a supplier and a warehouse) and a pgvector similarity query on seeded dummy decision text both return sane results, with no agent code present.

---

### **3.3 D3 — Forecasting Agent Slice: Demand \+ Inventory**

**Objective:** Build the two data-heaviest agents as standalone callable services.

| ID | Requirement |
| ----- | ----- |
| FR-3.1 | The system shall implement a Demand Agent using an XGBoost/Prophet baseline ensembled with a time-series foundation model, exposed as an MCP-tool-connected service. |
| FR-3.2 | The system shall implement an Inventory Agent using the same ensembling approach, reasoning over D1/D2 inventory data. |
| FR-3.3 | Each agent shall return a structured claim (recommendation, confidence, evidence) as defined in Section 3.4 (Structured Claim Contract), independent of other agents. |

**Acceptance Criterion:** Calling each agent's endpoint with a synthetic scenario ID returns a structured claim with forecast, confidence score, and evidence references, verifiable against D1 ground truth, without the Coordinator existing.

---

### **3.4 D4 — Reliability Agent Slice: Supplier \+ Transportation**

**Objective:** Build the two network/reliability-focused agents using the same standalone pattern as D3.

| ID | Requirement |
| ----- | ----- |
| FR-4.1 | The system shall implement a Supplier Agent producing reliability scores and failure predictions from Neo4j graph data and historical delivery data. |
| FR-4.2 | The system shall implement a Transportation Agent producing delay predictions and rerouting-option generation over the route network. |
| FR-4.3 | Both agents shall conform to the same structured-claim output contract as D3 and be MCP-connected. |

**Structured Claim Contract (applies to all agents, D3 onward):**

| Field | Description |
| ----- | ----- |
| Recommendation | Proposed action |
| Confidence | Calibrated certainty (0–100%) |
| Priority | Urgency relative to other open issues |
| Impact | Estimated magnitude of consequence if ignored |
| Evidence | Supporting data/signals |

**Acceptance Criterion:** Injecting a D1 disruption event (e.g., supplier delay) directly into these agents' inputs produces sensible structured claims, with no Coordinator or consensus logic involved.

---

### **3.5 D5 — Agent Orchestration & Protocol Layer**

**Objective:** Wire the four independent agents (D3+D4) together under a real orchestrator using standardized protocols, without consensus logic yet.

| ID | Requirement |
| ----- | ----- |
| FR-5.1 | The system shall implement a LangGraph state graph connecting the four specialist agents to a minimal Coordinator node. |
| FR-5.2 | The system shall formalize MCP servers for each agent's existing tool/data access, protocol-wrapping the D3/D4 implementations. |
| FR-5.3 | The system shall implement an A2A layer where each agent publishes an Agent Card, and the Coordinator discovers and delegates via A2A rather than hardcoded calls. |
| FR-5.4 | The Coordinator, at this stage, shall only collect claims from all agents — no arbitration logic is invoked. |

**Acceptance Criterion:** Triggering one D1 disruption scenario end-to-end results in the Coordinator receiving all four agents' structured claims via A2A/MCP, with the full call graph visible; output is a raw claim bundle, not a decision.

---

### **3.6 D6 — CD²F Consensus Engine**

**Objective:** Build the research core in isolation against fixture data, validating it before trusting it on live agent output.

| ID | Requirement |
| ----- | ----- |
| FR-6.1 | The system shall implement a structured-claim-to-arbitration pipeline using confidence-weighted voting that combines stated confidence with rolling historical accuracy. |
| FR-6.2 | The system shall implement escalation tiering logic (fast path / slow path / human-escalation) based on configurable confidence and impact thresholds. |
| FR-6.3 | The system shall support a judge/Coordinator calibration check against a hand-labeled scenario set, computing Cohen's kappa. |
| FR-6.4 | The system shall implement a naive-majority-voting baseline, used solely as an evaluation comparator (not in production decisions). |
| FR-6.5 | For every arbitration, the engine shall produce: a final decision, a reasoning trail, and an escalation tier. |

**Acceptance Criterion:** Feeding the engine a fixture set of mock agent claims (agreement, disagreement, conflicting-evidence cases) produces a final decision, reasoning trail, and escalation tier matching hand-worked expectations — independent of live D5 output.

---

### **3.7 D7 — Observability & Explainability Backend**

**Objective:** Make every agent turn and consensus decision inspectable before any UI is built.

| ID | Requirement |
| ----- | ----- |
| FR-7.1 | The system shall integrate LangSmith or Langfuse tracing into the D5 orchestration graph and D6 consensus engine. |
| FR-7.2 | The system shall persist a full agent-by-agent reasoning trail in Postgres/pgvector, keyed per decision, to support later replay. |
| FR-7.3 | The system shall log and make queryable judge calibration metrics produced in D6, over time. |

**Acceptance Criterion:** Re-running a D5+D6 scenario allows the complete trace — every agent call, every claim, the arbitration outcome, and escalation tier — to be pulled from storage/tooling alone, without a frontend.

---

### **3.8 D8 — Backend API & Real-Time Layer**

**Objective:** Expose everything built in D1–D7 as a coherent API a frontend (or Postman) can drive.

| ID | Requirement |
| ----- | ----- |
| FR-8.1 | The system shall expose a FastAPI service with endpoints to: trigger scenarios, run what-if simulations, fetch dashboard state, and fetch a decision's meeting log / confidence view / replay trace. |
| FR-8.2 | The system shall implement a Kafka or RabbitMQ event bus connecting disruption events (D1) to the agent trigger pipeline (D5), decoupling simulation from orchestration. |
| FR-8.3 | The system shall implement a WebSocket layer for pushing live state updates to clients. |

**Acceptance Criterion:** The full pipeline can be driven via API calls alone (e.g., Postman/curl) — trigger a disruption, poll or subscribe for the resulting decision, and fetch its trace — with zero frontend code written.

---

### **3.9 D9 — Frontend Dashboard**

**Objective:** Build the user-facing surface against the stable D8 API.

| ID | Requirement |
| ----- | ----- |
| FR-9.1 | The system shall provide an Operational Dashboard and interactive Supply Chain Map (React/Next.js, Leaflet, D3/Recharts). |
| FR-9.2 | The system shall provide an AI Meeting Log view and a Confidence & Disagreement View. |
| FR-9.3 | The system shall provide a What-If Simulation UI and a Scenario Library / Scenario Comparison view. |
| FR-9.4 | The system shall provide a Decision Replay UI allowing step-through of D7's stored traces. |
| FR-9.5 | The system shall provide a Recommendation Timeline and a basic Risk Heatmap. |
| FR-9.6 | The system shall provide an AI Chat interface for natural-language Q\&A over operational data (e.g., "Why is Warehouse 4 at risk?"). |

**Acceptance Criterion:** A reviewer can, via a fully clickable demo against D8's API alone, trigger a what-if scenario, watch it run, and inspect the resulting meeting log and confidence view, without needing D1–D7 explained separately.

---

### **3.10 D10 — End-to-End Integration & Evaluation Harness (MVP Consolidation)**

**Objective:** Prove the whole pipeline works as one system and produce research evidence.

| ID | Requirement |
| ----- | ----- |
| FR-10.1 | The system shall demonstrate full loop wiring: D1 disruption → D5 agents → D6 CD²F → D7 trace → D8 API → D9 dashboard, run back-to-back without manual intervention. |
| FR-10.2 | The system shall implement an evaluation harness computing: decision accuracy, consensus quality, agent agreement rate, judge calibration kappa, response time (fast-path vs. slow-path split), risk reduction, inventory cost, and fill rate. |
| FR-10.3 | The system shall benchmark CD²F against a single-agent baseline and the naive-majority-voting baseline (from D6), across the hand-labeled scenario set. |
| FR-10.4 | The system shall produce a results write-up mapping outcomes directly to Research Questions RQ1–RQ4. |

**Acceptance Criterion (MVP Complete):** A person can run a disruption scenario from the dashboard and see, end to end, a justified, explainable decision, plus a metrics report comparing CD²F against the two baselines.

---

### **3.11 D11 — Post-MVP Extension Points (Interface Only — Not Built)**

**Objective:** Confirm the D1–D10 architecture does not require rework to support future extensions, without building them now.

| ID | Requirement |
| ----- | ----- |
| FR-11.1 | The system design shall document where a Risk Agent (GNN over the D2 Neo4j graph) would plug into D5's orchestration graph. |
| FR-11.2 | The system design shall document where Finance, Sustainability, and Weather agents would attach as additional A2A-discoverable specialists. |
| FR-11.3 | The system design shall document where an external/cross-organization agent would attach via the same A2A layer used internally in D5 (Cross-Org Agent Handoff). |
| FR-11.4 | The system design shall document where Digital Twin playback would extend D7's trace storage into full network-propagation replay. |

**Acceptance Criterion:** A short interface/contract document confirms each extension point is additive to D5–D9, not a rearchitecture. No code is required for MVP sign-off.

---

## **4\. External Interface Requirements**

### **4.1 User Interfaces**

* Web dashboard (React/Next.js) accessible via browser, covering: Operational Dashboard, Supply Chain Map, AI Meeting Log, What-If Simulation, Scenario Comparison, Risk Heatmap, Recommendation Timeline, AI Chat.

### **4.2 Software Interfaces**

* **MCP** — standardized protocol for agent tool/data access (used from D3 onward)  
* **A2A** — agent discovery/delegation protocol via published Agent Cards (D5+)  
* **FastAPI REST endpoints** — scenario triggers, what-if simulation, dashboard state, meeting log/trace retrieval (D8)  
* **WebSocket** — live state push (D8)  
* **Kafka/RabbitMQ** — event bus between disruption generator and agent pipeline (D8)  
* **Neo4j (Cypher)** and **PostgreSQL/pgvector (SQL)** — knowledge and vector storage (D2)

### **4.3 Communication Interfaces**

* Internal service-to-service communication via the message broker and A2A/MCP protocols within the Docker network.

---

## **5\. Non-Functional Requirements**

| Category | Requirement |
| ----- | ----- |
| Explainability | Every recommendation shall ship with reason, confidence, and evidence (Section 14 of ideation doc), and be fully traceable/replayable per D7. |
| Auditability | All decision traces shall be persisted and queryable independent of the frontend. |
| Modularity | Each deliverable (D1–D10) shall be independently runnable and testable in isolation before being wired into the next stage. |
| Extensibility | The architecture shall support adding new agents (Risk, Finance, Sustainability, Weather, cross-org) without rearchitecture, per D11. |
| Reproducibility | Synthetic data generation and ETL processes shall be idempotent and re-runnable. |
| Environment Isolation | The MVP shall run fully within Docker containers against synthetic data, with no external hardware or live data feed dependency. |
| Response Time | The CD²F engine shall support a fast-path/slow-path split so that low-complexity decisions resolve with materially lower latency than escalated ones (measured in D10). |
| Evaluability | The system shall support benchmarking of decision quality against defined baselines (single-agent, naive-majority-voting) using the metrics in Section 20 of the ideation document. |

---

## **6\. Data Requirements**

| Data Category | Source | Used By |
| ----- | ----- | ----- |
| Historical orders, inventory, suppliers, shipments | Synthetic generator (D1) | D2, D3, D4 |
| External signals (weather, fuel prices, calendar effects) | Synthetic/external stub | Weather Agent (post-MVP, D11), Demand Agent |
| Synthetic disruption events | Synthetic generator (D1) | D5 trigger pipeline, D6 evaluation fixtures |
| Knowledge graph (supplier/product/warehouse/route) | Neo4j (D2) | Supplier Agent, Transportation Agent |
| Decision records, evidence embeddings | pgvector (D2, D7) | Consensus engine, observability, dashboard replay |
| Hand-labeled scenario set | Manually curated | D6 calibration, D10 benchmarking |

---

## **7\. Traceability: Requirements to Research Questions**

| Deliverable | Primary RQ(s) Supported |
| ----- | ----- |
| D6 (Consensus Engine) | RQ1 (decision quality vs. centralized baseline), RQ2 (reduction of false/low-confidence recommendations) |
| D7 (Observability) | RQ3 (trust via explainability) |
| D8–D9 (API \+ Dashboard) | RQ3 (trust), RQ4 (response time vs. human-only workflows) |
| D10 (Evaluation Harness) | RQ1–RQ4 (all, via benchmark results write-up) |

---

## **8\. Assumptions, Constraints, and Out-of-Scope Items**

**Out of scope for MVP:**

* Risk, Finance, Sustainability, and Weather agents (deferred to post-MVP, interfaced only in D11)  
* Live ERP/IoT data integration  
* Reinforcement learning, federated learning, GNNs, Digital Twin simulation, blockchain-backed provenance, carbon-aware optimization, and full LLM-based natural-language reasoning beyond the basic AI Chat feature (all listed as future research extensions)

**Constraints:**

* Orchestration framework must be selected (LangGraph assumed) prior to D5  
* Consensus algorithm mechanics finalized during D6 implementation, within the structured claim contract defined here

