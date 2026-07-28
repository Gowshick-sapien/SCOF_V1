# **SCOF — Implementation Plan (Docker-Simulation MVP)**

*Deliverable-based build plan. Each deliverable is independently runnable and testable in isolation (own inputs, own outputs, own pass/fail check) before being wired into the next. Consolidating D1→D10 is the MVP defined in Section 21 of the ideation doc. D11 is explicitly out of MVP scope. The MVP scope is expressed as a Domain Profile from D1 onward, validating the profile-driven architecture as part of the build itself.*

---

## **Dependency Graph**

D1 (Sim Data) ──► D2 (Knowledge Layer) ──► D3 (Demand+Inventory Agents)  
                                        ├─► D4 (Supplier+Transport Agents)  
                                          
D3 \+ D4 ──► D5 (Orchestration: LangGraph \+ MCP \+ A2A) ──► D6 (CD²F Consensus Engine)  
                                                                    │  
D6 ──► D7 (Observability/Explainability) ──► D8 (Backend API \+ Realtime)  
                                                                    │  
D8 ──► D9 (Frontend Dashboard)   
D8 \+ D9 ──► D10 (End-to-End Integration \+ Evaluation Harness) \= MVP COMPLETE

D10 ──► D11 (Post-MVP stubs — not built, only interfaced)

---

## **D1 — Simulation Environment & Synthetic Data Foundation**

**Objective:** Produce a self-contained, reproducible synthetic supply chain world before any AI touches it, driven by the active Domain Profile.

**Builds:**

* **MVP Domain Profile:** the declarative configuration directory (`topology.yaml`, `disruptions.yaml`, `agents.yaml`, `consensus.yaml`, `evaluation.yaml`, `dashboard.yaml`, `data_bindings.yaml`) expressing the MVP scope — 1 manufacturer, 3–5 products, 5 suppliers, 2 warehouses, 1 DC, multi-route transport network, and 4 disruption types  
* Docker Compose skeleton: Postgres, Redis, Kafka/RabbitMQ, Neo4j (containers only, no app logic yet)  
* Synthetic data generator: reads `topology.yaml` to generate entities and relationships matching the profile, rather than from hardcoded values  
* Disruption event generator: reads `disruptions.yaml` to produce parameterized events — supplier delay, transport failure, demand spike, adverse weather — each with severity, duration, timing from the profile

**Standalone test of "done":** Run docker compose up, trigger the generator, and query Postgres directly to confirm realistic order/inventory/shipment histories and injectable disruption events exist — no agents or APIs involved yet. Changing the profile's topology (e.g., adding a 6th supplier) and re-running the generator should produce a correspondingly different dataset.

**Maps to:** Section 17 (Dataset Strategy), Section 21 (Scope), Domain Binding Strategy

---

## **D2 — Knowledge & Data Layer**

**Objective:** Give agents somewhere to read from and write to, independent of the agents themselves.

**Builds:**

* Neo4j schema: supplier/product/warehouse/route nodes and relationships, derived from the profile's `topology.yaml`  
* pgvector schema in Postgres: tables for decision records, evidence snippets, embeddings  
* ETL scripts: reads `data_bindings.yaml` to load D1's synthetic data into Neo4j + Postgres, idempotent and re-runnable

**Standalone test of "done":** Run a handful of Cypher queries against Neo4j (e.g., "shortest path between Supplier 3 and Warehouse 1") and a vector similarity query against pgvector on seeded dummy decision text — both return sane results without any agent code existing.

**Maps to:** Section 15 (Neo4j, pgvector), Section 16 (Architecture)

---

## **D3 — Forecasting Agent Slice: Demand \+ Inventory**

**Objective:** Build the two data-heaviest agents first, as standalone callable services.

**Builds:**

* Demand Agent: XGBoost/Prophet baseline ensembled with a time-series foundation model (e.g., Chronos-2), exposed as an MCP-tool-connected service. Model configuration and MCP tool bindings read from the profile's `agents.yaml`  
* Inventory Agent: same ensembling approach, reasoning over D1/D2 inventory data, configured via `agents.yaml`  
* Each agent returns a structured claim (recommendation, confidence, evidence) per Section 13.1 — but in isolation, not yet talking to anything else

**Standalone test of "done":** Call each agent's endpoint directly with a synthetic scenario ID and get back a structured claim with a forecast, confidence score, and evidence references — verifiable against D1's ground truth without the Coordinator existing.

**Maps to:** Section 10.2, 10.4, Section 15 (ML stack)

---

## **D4 — Reliability Agent Slice: Supplier \+ Transportation**

**Objective:** Build the two network/reliability-focused agents, same standalone pattern as D3.

**Builds:**

* Supplier Agent: reliability scoring and failure prediction from D2's Neo4j graph + historical delivery data, configured via `agents.yaml`  
* Transportation Agent: delay prediction and rerouting-option generation over the route network, configured via `agents.yaml`  
* Same structured-claim output contract as D3, MCP-connected

**Standalone test of "done":** Inject a D1 disruption event (e.g., supplier delay) directly into these two agents' inputs and confirm each produces a sensible structured claim — again with no Coordinator or consensus logic involved yet.

**Maps to:** Section 10.1, 10.3

---

## **D5 — Agent Orchestration & Protocol Layer**

**Objective:** Wire the four independent agents (D3+D4) together under a real orchestrator, using standardized protocols rather than direct function calls — but without consensus logic yet.

**Builds:**

* LangGraph state graph connecting the specialist agents to a minimal Coordinator node  
* MCP servers formalized for each agent's existing tool/data access (already built in D3/D4, now protocol-wrapped)  
* A2A layer: each agent publishes an Agent Card; Coordinator discovers and delegates via A2A instead of hardcoded calls  
* Coordinator reads the active agent set from `agents.yaml` and discovers them via A2A at startup — adding or removing agents is a profile change, not a code change  
* Coordinator at this stage only *collects* claims — no arbitration yet

**Standalone test of "done":** Trigger one D1 disruption scenario end-to-end and confirm the Coordinator receives all four agents' structured claims via A2A/MCP, with the full call graph visible — output is a raw claim bundle, not yet a decision.

**Maps to:** Section 10.8, Section 15 (MCP/A2A), Section 16

---

## **D6 — CD²F Consensus Engine**

**Objective:** Build the actual research core in isolation, against fixture data first, so it can be validated before being trusted on live agent output.

**Builds:**

* Structured claim → arbitration pipeline: confidence-weighted voting combining stated confidence + rolling historical accuracy (Section 13.2)  
* Escalation tiering logic: fast path / slow path / human-escalation — thresholds, impact scales, and criteria read from the profile's `consensus.yaml`, not hardcoded  
* Judge/Coordinator calibration check against a small hand-labeled scenario set (Cohen's kappa), with calibration frequency and kappa threshold from `consensus.yaml`  
* Naive-majority-voting baseline implementation, used later purely as an evaluation comparator (Section 19 RQ2)

**Standalone test of "done":** Feed the engine a fixture set of mock agent claims (not live D5 output) covering agreement, disagreement, and conflicting-evidence cases, and confirm it produces a final decision + reasoning trail + escalation tier that matches hand-worked expectations.

**Maps to:** Section 11–13 (CD²F), Section 19 (RQ1, RQ2)

---

## **D7 — Observability & Explainability Backend**

**Objective:** Make every agent turn and every consensus decision inspectable before building any UI on top of it.

**Builds:**

* LangSmith or Langfuse tracing wired into the D5 orchestration graph and D6 consensus engine  
* Decision trace persistence: full agent-by-agent reasoning trail stored in Postgres/pgvector (D2), keyed per decision, to support later replay  
* Judge calibration metrics (from D6) logged and queryable over time

**Standalone test of "done":** Re-run a D5+D6 scenario and pull the complete trace — every agent call, every claim, the arbitration outcome, and the escalation tier — from storage/tooling alone, without touching a frontend.

**Maps to:** Section 15 (Observability), Section 13.3, Section 14 (AI Meeting Log, Confidence & Disagreement View — backing data only)

---

## **D8 — Backend API & Real-Time Layer**

**Objective:** Expose everything built so far (D1–D7) as a coherent API a frontend (or Postman) can drive.

**Builds:**

* FastAPI service: endpoints for triggering scenarios, running what-if simulations, fetching dashboard state, fetching a decision's meeting log / confidence view / replay trace, and retrieving the active Domain Profile metadata  
* Kafka/RabbitMQ event bus: disruption events (D1) → agent trigger pipeline (D5), decoupling simulation from orchestration  
* WebSocket layer for pushing live state updates

**Standalone test of "done":** Drive the full pipeline via API calls alone (e.g., Postman/curl) — trigger a disruption, poll or subscribe for the resulting decision, fetch its trace — with zero frontend code written yet.

**Maps to:** Section 15 (Backend, Kafka, WebSockets), Section 16

---

## **D9 — Frontend Dashboard**

**Objective:** Build the user-facing surface against the now-stable D8 API.

**Builds:**

* Operational Dashboard + Supply Chain Map (React/Next.js, Leaflet, D3/Recharts) — map bounds, entity labels, and active views read from the profile's `dashboard.yaml`  
* AI Meeting Log view + Confidence & Disagreement View  
* What-If Simulation UI + Scenario Library  
* Decision Replay UI (step through D7's stored traces)  
* Recommendation Timeline, basic Risk Heatmap

**Standalone test of "done":** Full clickable demo against D8's API in isolation — a reviewer can trigger a what-if scenario, watch it run, and inspect the resulting meeting log and confidence view — without needing D1–D7 explained separately.

**Maps to:** Section 14 (Features), Section 15 (Frontend)

---

## **D10 — End-to-End Integration & Evaluation Harness (MVP Consolidation)**

**Objective:** Prove the whole pipeline works as one system and produce the actual research evidence.

**Builds:**

* Full loop wiring confirmation: D1 disruption → D5 agents → D6 CD²F → D7 trace → D8 API → D9 dashboard, run back-to-back without manual intervention between stages  
* Evaluation harness implementing Section 20's metrics: decision accuracy, consensus quality, agent agreement rate, judge calibration kappa, response time (fast-path vs. slow-path split), risk reduction, inventory cost, fill rate  
* Benchmark runs: CD²F vs. single-agent baseline vs. naive-majority-voting baseline (D6), across the hand-labeled scenario set  
* Results write-up mapped directly to RQ1–RQ4 (Section 19\)

**Standalone test of "done":** This is the MVP itself — a person can run a disruption scenario from the dashboard and see, end to end, a justified, explainable decision, plus a metrics report comparing CD²F against the two baselines.

**Maps to:** Section 19 (RQ1–RQ4), Section 20 (Evaluation Metrics), Section 21 (Scope) — completion of this deliverable **is** MVP completion.

---

## **D11 — Post-MVP Extension Points *(not built; interface only)***

**Objective:** Confirm D1–D10's architecture doesn't need to be reworked to support future extensions — without building them now.

**What gets defined, not built:**

* Where a Risk Agent (GNN over the D2 Neo4j graph) would plug into D5's orchestration graph — additive: add agent block to `agents.yaml`, deploy container  
* Where Finance, Sustainability, and Weather agents would attach as additional A2A-discoverable specialists — additive: add agent block to `agents.yaml`  
* Where an external/cross-org agent would attach via the same A2A layer already used internally in D5 (Cross-Org Agent Handoff) — additive: add external endpoint to `agents.yaml`  
* Where Digital Twin playback would extend D7's trace storage into full network-propagation replay  
* How a new supply chain context would be deployed — additive: write a new profile directory, no platform changes

**Standalone test of "done":** A short interface/contract doc confirming each extension point is additive to D5–D9, not a rearchitecture — including a demonstration that a new Domain Profile (different topology, different disruption types) can be loaded without code changes. No code required for MVP sign-off.

**Maps to:** Section 22 (Future Research Extensions), Section 23, Domain Binding Strategy

---

## **Summary Table**

| Deliverable | Independently testable output | Depends on | Profile Files Used |
| ----- | ----- | ----- | ----- |
| D1 | Queryable synthetic dataset + disruption events | — | `topology.yaml`, `disruptions.yaml` |
| D2 | Queryable graph + vector store | D1 | `topology.yaml`, `data_bindings.yaml` |
| D3 | Callable Demand + Inventory agent APIs | D1, D2 | `agents.yaml` |
| D4 | Callable Supplier + Transportation agent APIs | D1, D2 | `agents.yaml` |
| D5 | Full raw claim bundle via A2A/MCP orchestration | D3, D4 | `agents.yaml` |
| D6 | Validated consensus decisions on fixture data | (standalone, tested against fixtures) | `consensus.yaml` |
| D7 | Fully inspectable decision traces | D5, D6 | — |
| D8 | Fully API-drivable pipeline | D1–D7 | `profile.yaml` |
| D9 | Clickable dashboard demo | D8 | `dashboard.yaml` |
| D10 | **MVP**: full loop + benchmark results | D1–D9 | `evaluation.yaml` |
| D11 | Extension interface doc (no code) | D10 | — |


