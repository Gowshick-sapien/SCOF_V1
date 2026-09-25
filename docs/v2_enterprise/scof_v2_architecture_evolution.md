# SCOF Architecture Evolution: From V1 MVP to V2 Enterprise Cognitive Twin

## 1. Executive Summary & Purpose

This document formally records the architectural evolution of the **Supply Chain Cognitive Orchestration Framework (SCOF)** from its initial V1 MVP specification to its V2 Enterprise Cognitive Twin architecture. 

The original V1 documents and deliverables remain preserved as the foundational baseline. This document establishes the authoritative blueprint for how each deliverable (D1 through D11) transforms to leverage the 30-domain, 96-table, 3.73M-node enterprise dataset, establishing strict operational boundaries, data isolation, and query governance.

---

## 2. Core Architectural Shifts (V1 vs. V2)

| Dimension | V1 MVP Architecture | V2 Enterprise Cognitive Twin Architecture |
| :--- | :--- | :--- |
| **Enterprise Scale** | 1 manufacturer, 5 suppliers, 2 warehouses, 1 DC, 3–5 products. | 200 suppliers, 21 facilities (5 DCs, 16 stores), 49,616 SKUs, 346,238 assortments, 18M demand rows. |
| **Role of D1** | Monolithic generator creating toy synthetic profiles. | **Enterprise World & Simulation Foundation**: Dataset provenance, versioned manifests, baseline state, and isolated scenario injection. |
| **Role of D2** | Basic ETL pipeline loading PostgreSQL, Neo4j, and pgvector. | **Enterprise Knowledge & Data Fabric**: Clear separation of concerns (PostgreSQL = System of Record, Neo4j = Materialized Topology Projection, pgvector = Semantic Projection). |
| **Domain Profiles** | Procedural script inputs ("generate 5 suppliers and 2 warehouses"). | **Declarative Operational Bindings**: "This SCOF deployment operates over this specific enterprise dataset and active operational subset." |
| **Graph Model Role** | Second operational database storing state and facts. | **Materialized Topology & Traversal Engine**: Bounded graph traversals for structural dependencies; transactions and facts remain in PostgreSQL. |
| **State Mutation** | In-place state modification during simulations. | **Strict Tripartite Isolation**: Layer 1 (Frozen Ground Truth) $\to$ Layer 2 (Baseline State) $\to$ Layer 3 (Isolated Scenario Snapshots). |
| **Domain Identity** | Mixed terminology (retail mart, shopping mall, multi-billion conglomerate). | **SCOF Retail Enterprise Reference World**: Single unified enterprise ontology with hierarchical operational tiers. |
| **Domain vs. Agent Mapping** | Implied 1:1 coupling (e.g., Finance domain implies Finance agent). | **Many-to-Many Decoupling**: 30 business domains form the data ontology; 4–5 federated specialist agents consume multiple domains. |

---

## 3. Critical Analysis & Technical Stakes

### 3.1 The 3.73M-Node Neo4j Graph: Bounded Query Contracts
The Neo4j property graph contains **3,728,199 nodes and 2,104,514 edges** across 59 schema constraints. While this provides unprecedented topological richness, treating it as an unconstrained operational database presents severe failure modes:
1. **Unconstrained Cypher Traversal Hazard:** If autonomous LLM agents (D3/D4) issue raw Cypher queries with unbounded depth (e.g., `MATCH (s:Store)-[*1..5]-(x) RETURN x`), query latency will exceed the sub-second SLA ($< 500\text{ ms}$) and exhaust server memory.
2. **Dual-Master Consistency Drift:** If agents write operational state directly to Neo4j while PostgreSQL records transactions, the relational and graph states will inevitably diverge.

#### Architectural Stake:
* **Neo4j is Strictly a Materialized Projection:** PostgreSQL is the single source of transactional truth. Neo4j is populated via unidirectional synchronization from PostgreSQL.
* **Agent-Facing Bounded APIs (MCP):** Agents are **never** permitted to execute arbitrary, unconstrained Cypher queries. Instead, the Knowledge Fabric (D2) exposes parameterized, bounded graph traversal tools via Model Context Protocol (MCP), such as:
  * `get_upstream_supply_path(sku_id, store_id, max_depth=3)`
  * `get_affected_downstream_facilities(disrupted_facility_id, max_hops=2)`
  * `find_alternate_carrier_routes(origin_id, dest_id, max_transit_days=5)`

---

### 3.2 Runtime State Isolation: The Three-Layer Invariant
In simulation and evaluation, mutating the baseline dataset directly corrupts subsequent runs. For example, in Deliverable D10 (Evaluation & Benchmarks), if Scenario A (Supplier Delay) mutates warehouse stock levels, Scenario B (Transit Route Closure) running immediately afterward will observe degraded inventory, rendering the evaluation invalid and non-reproducible.

#### Architectural Stake:
SCOF enforces a **Strict Tripartite State Architecture**:

```
+==========================================================================+
| LAYER 1: FROZEN GROUND TRUTH (Immutable)                                 |
| - Parquet files, canonical CSVs, frozen SQLite/PostgreSQL seed           |
| - Immutable cryptographic hash (SHA-256) recorded in run_manifest.json   |
+==========================================================================+
                                     │
                                     ▼
+==========================================================================+
| LAYER 2: BASELINE OPERATIONAL STATE (Queryable, Reset Target)            |
| - Operational database populated to Day 0 baseline state                |
| - Materialized Neo4j topology and pgvector embeddings                    |
| - Read-only reference for all baseline agent queries                     |
+==========================================================================+
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
+==================================+   +==================================+
| LAYER 3A: SCENARIO A RUNTIME     |   | LAYER 3B: SCENARIO B RUNTIME     |
| - Ephemeral copy-on-write state  |   | - Ephemeral copy-on-write state  |
| - Asset downtime, disrupted POs  |   | - Route closure, delayed freight |
| - Destroyed/reset on completion  |   | - Destroyed/reset on completion  |
+==================================+   +==================================+
```

1. **Layer 1 (Frozen Ground Truth):** The physical datasets in [`datasets/`](file:///d:/projects/SCOF_V1/SCOF/datasets/) are immutable. No service, agent, or simulation may write to or modify these files.
2. **Layer 2 (Baseline Operational State):** The relational database and Neo4j graph initialized to Day 0. It serves as the clean reference state for baseline operations.
3. **Layer 3 (Scenario Runtime State):** When a scenario is injected, the system creates an isolated, ephemeral runtime context identified by `scenario_id` and `sim_run_id`. All state mutations (inventory deductions, delayed shipments, cancelled orders) are isolated to this execution run. Once the run or evaluation completes, the ephemeral state is archived or discarded, leaving Layer 2 completely untouched.

---

### 3.3 Domain Identity: "SCOF Retail Enterprise Reference World"
To eliminate ambiguity between "retail mart," "shopping complex," and "multi-billion conglomerate," the enterprise is formally defined as:

**SCOF Retail Enterprise Reference World**
A multi-tier retail conglomerate operating across 30 unified business domains:
* **Corporate & Legal Structure:** 1 Enterprise complex, 2 Legal Entities, 2 Business Units (`governance/`).
* **Network Infrastructure:** 5 Regional Distribution Centers, 16 Multi-Format Retail Stores (21 facilities total), 35 Transport Lanes (`network/`).
* **Merchandise Hierarchy:** 12 Departments, 67 Categories, 200 Subcategories, 1,453 Product Families, 3,458 Products, 49,616 SKUs (`masters/`).
* **Supply Ecosystem:** 200 Tier-1 Suppliers, 25 Logistics Carriers, 225 Commercial Contracts (`sourcing/`).
* **Operational Volumes:** 15,000 Purchase Orders, 18,000 Shipments, 15,000 Goods Receipts, 65,000 Invoices, 65,000 Payments, 50,000 Point-of-Sale Transactions, 18M Weekly Demand Observations.

---

### 3.4 Domain Ontology vs. Agent Roster: 30 Domains != 30 Agents
A critical principle for V2 is that the **30 business domains represent the enterprise data model and ontology, NOT the agent roster.**

* An agent is an **autonomous decision specialist**, not a database table wrapper.
* In SCOF V2, the core multi-agent federation remains focused on **4 primary operational specialists** coordinated by an orchestration kernel:
  1. **Demand Agent:** Consumes Commerce, Sales Transactions, Promotions, Calendar Events, Weather, and Macroeconomic signals.
  2. **Inventory Agent:** Consumes Inventory Positions, Goods Receipts, Assortments, Replenishment Policies, and Physical Assets.
  3. **Supplier Agent:** Consumes Supplier Profiles, Commercial Contracts, Purchase Orders, Supplier Invoices, and Three-Way Match records.
  4. **Transportation Agent:** Consumes Transport Lanes, Shipments, Carrier Profiles, Fleet Assets, and Disruptions.
* **Timing & Roadmap:** 
  * This architectural principle is **locked now** to prevent scope creep.
  * The actual implementation and MCP tool bindings for these 4 agents will be delivered during the planned refinement of **D3 and D4**, requiring zero premature rework today.

---

### 3.5 Digital Twin Architecture: Cyber-Physical State Authority
A foundational decision established during V2 evolution is positioning the Digital Twin Service as an **Operational World and Simulation Layer Above D1 and D2** ([ADR 019](file:///d:/projects/SCOF_V1/SCOF/docs/adr/019_operational_digital_twin_substrate_layer.md)):

* **D1 (World Foundation)** owns the enterprise dataset, schema manifests, and generation provenance.
* **D2 (Knowledge Fabric)** owns authoritative enterprise storage (PostgreSQL System of Record, Neo4j Topology, pgvector Semantic Memory).
* **The Twin** turns data into an operationally meaningful, scenario-aware cyber-physical world. It executes forward propagation along event timelines, enforces physical invariants (conservation of mass, capacity, lead-time causality), and forks isolated counterfactual branches.
* **Subsystem Boundaries:** The Twin owns simulation state and physics; it does **NOT** own agent orchestration (owned by LangGraph) or consensus arbitration (owned by CD²F).
* **Event-Stepped DES Kernel:** Rather than running an expensive continuous fixed-tick clock, the Twin advances state deterministically from event to event along discrete event timelines ([ADR 023](file:///d:/projects/SCOF_V1/SCOF/docs/adr/023_event_stepped_simulation_kernel_over_fixed_tick_daemon.md)).

Detailed Specification: [Digital Twin Service Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/01_digital_twin_service_architecture.md).

---

### 3.6 Tri-Zone Cognitive Query Routing & Dynamic Capability Registry
To prevent the Twin from becoming a congested query bottleneck, operations are segregated into three distinct classes ([ADR 020](file:///d:/projects/SCOF_V1/SCOF/docs/adr/020_tri_zone_query_routing_and_deeper_resolver.md)):
1. **Class A (Direct Read-Only Facts):** Direct queries against PostgreSQL and Neo4j via bounded MCP tools ($< 50\text{ ms}$). Bypasses the Twin completely.
2. **Class B (Derived Analytics & Forecasts):** Statistical ensembling and ML forecasting ($< 250\text{ ms}$).
3. **Class C (Counterfactual Simulation):** State forward propagation, asset disruption testing, and intervention delta evaluation in the Twin ($< 500\text{ ms}$).

The **Tri-Zone Cognitive Router** governs execution:
* **Zone 1 (Fast-Path Router):** High-confidence ($c \ge 0.85$) deterministic signature matching executing in $< 10\text{ ms}$.
* **Zone 2 (Ambiguous-Path Deeper Resolver):** Triggered when $0.50 \le c < 0.85$ to disambiguate intent, resolve entity bindings, and synthesize parameters.
* **Zone 3 (Fallback Handler):** Triggered when $c < 0.50$ to emit structured clarification requests and log routing anomalies.

**Dynamic Capability Registry ([ADR 021](file:///d:/projects/SCOF_V1/SCOF/docs/adr/021_dynamic_capability_registry_over_static_mcp_endpoints.md)):** Replaces brittle manual tool enumeration. Service providers register declarative Capability Cards. The registry dynamically mounts only the 3–5 most relevant bounded tools into each agent prompt, reducing prompt tokens by $91\%$.

Detailed Specifications: [Cognitive Query Routing](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/02_cognitive_query_routing_and_resolution_pipeline.md) and [Dynamic Capability Registry](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/03_dynamic_capability_registry.md).

---

### 3.7 Minimalist Concurrency Model: Priority Queue & Bounded Worker Pool
To handle concurrent multi-agent simulation inquiries without over-engineering complex scheduling machinery, SCOF adopts a minimalist concurrency architecture ([ADR 022](file:///d:/projects/SCOF_V1/SCOF/docs/adr/022_minimalist_bounded_worker_concurrency.md)):
* **4-Tier Priority Queue:**
  * **P0 (Emergency):** System telemetry threshold alerts and critical asset breakdown interrupts.
  * **P1 (Consensus Deliberation):** CD²F arbitration queries evaluating final trade-offs.
  * **P2 (Agent Deliberation):** Routine specialist agent what-if explorations.
  * **P3 (Background Evaluation):** Batch benchmark runs and long-horizon risk heatmaps.
* **Bounded Worker Pool:** Fixed concurrency ($W = 4..8$ workers) processing tasks FIFO within each tier, guaranteeing complete resource containment.
* **In-Memory Scenario Overlays:** Non-blocking Day-0 baseline reads with branch-local copy-on-write overlays ensuring zero lock contention.

Detailed Specification: [Minimalist Concurrency & Worker Pool Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/04_minimalist_concurrency_and_worker_pool.md).

---

### 3.8 Five-Tier State Hierarchy & Actuation Boundaries
SCOF eliminates ambiguity across facts, baselines, simulations, claims, and decisions by enforcing a five-tier state hierarchy ([ADR 025](file:///d:/projects/SCOF_V1/SCOF/docs/adr/025_five_tier_state_hierarchy_and_actuation_boundaries.md)):
1. **Tier 1 (Historical Fact):** Frozen ground truth sealed with SHA-256 digests.
2. **Tier 2 (Baseline Current State):** Active Day-0 relational state and immutable Neo4j topology.
3. **Tier 3 (Scenario Projection):** Simulated Layer 3 sandbox state overlays.
4. **Tier 4 (Agent Recommendation):** Structured claims emitted by specialist agents.
5. **Tier 5 (CD²F Decision):** Approved cross-domain consensus outcome.

**Actuation Boundary:** Applying an approved decision to Tier 3 modifies simulation sandbox state only. Real-world actuation (ERP PO creation, EDI freight booking) requires Human-in-the-Loop authorization via the Tauri v2 Desktop Operations Console (D09) and execution via isolated Execution Adapters.

Detailed Specification: [State Isolation & Evidence Fabric Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/05_state_isolation_and_evidence_fabric.md).

---

### 3.9 Explicitly Rejected Architectural Anti-Patterns
To preserve engineering discipline and prevent architectural drift, the following patterns are explicitly rejected:
1. **Continuous Real-Time Tick Daemon:** Supply chains operate via discrete events; continuous ticking introduces idle CPU burn and clock drift ([ADR 023](file:///d:/projects/SCOF_V1/SCOF/docs/adr/023_event_stepped_simulation_kernel_over_fixed_tick_daemon.md)).
2. **Direct Graph Mutations in Production Neo4j:** Runtime scenario perturbations must never write dirty edges or properties to Neo4j. Overlays are held in memory ([ADR 024](file:///d:/projects/SCOF_V1/SCOF/docs/adr/024_immutable_neo4j_topology_with_in_memory_scenario_overlays.md)).
3. **Twin-as-Monolithic-Gateway:** Routing all queries through the Twin causes severe latency degradation and bottlenecks ([ADR 019](file:///d:/projects/SCOF_V1/SCOF/docs/adr/019_operational_digital_twin_substrate_layer.md), [ADR 020](file:///d:/projects/SCOF_V1/SCOF/docs/adr/020_tri_zone_query_routing_and_deeper_resolver.md)).
4. **Static Tool Signature Sprawl:** Hardcoding 50+ domain-specific MCP endpoints dilutes prompt context and causes tool call errors ([ADR 021](file:///d:/projects/SCOF_V1/SCOF/docs/adr/021_dynamic_capability_registry_over_static_mcp_endpoints.md)).
5. **Direct Automated ERP Actuation:** Autonomous un-gated physical writes to production ERP systems violate enterprise risk boundaries ([ADR 025](file:///d:/projects/SCOF_V1/SCOF/docs/adr/025_five_tier_state_hierarchy_and_actuation_boundaries.md)).

---

## 4. Deliverable-by-Deliverable Transformation Matrix (D1 to D11)

### Deliverable D1: Enterprise World & Simulation Foundation
* **V1 Concept:** Procedural synthetic data generator producing a toy supply chain.
* **V2 Concept:** The foundational bedrock providing:
  1. **Dataset Provenance & Integrity:** Cryptographic verification of the 96 tables, manifests, and generation DAG.
  2. **Simulation Lifecycle Engine:** Management of `scenario`, `simulation_run`, and `validation_result` entities.
  3. **Deterministic Scenario Injection:** Parameterized disruption injection (supplier delay, asset downtime, route closure, demand surge).
  4. **Reproducibility Contract:** Exact replayability using `scenario_id`, `dataset_version`, `random_seed`, and initial state vectors.

### Deliverable D2: Enterprise Knowledge & Data Fabric
* **V1 Concept:** Basic ETL scripts moving CSV data into PostgreSQL, Neo4j, and pgvector.
* **V2 Concept:** Unified Enterprise Knowledge Fabric establishing:
  1. **System of Record (PostgreSQL):** Authoritative storage for transactional facts, orders, inventory levels, and financial ledgers.
  2. **Topological Knowledge Projection (Neo4j):** Materialized property graph serving bounded structural traversals.
  3. **Semantic Memory Projection (pgvector):** 384-dimensional vector store indexing historical decisions, meeting logs, and evidence snippets.
  4. **Contractual Identity & Lineage:** Strict primary/foreign key mappings and cross-tier lineage tracing.

### Deliverable D3: Demand & Inventory Specialist Agents
* **V1 Concept:** Single-model predictors (basic XGBoost) running over small synthetic CSVs.
* **V2 Concept:** Cross-domain cognitive specialists:
  1. **Demand Agent:** Multi-horizon ensemble (XGBoost, Prophet, Chronos-2) incorporating 554 regional events, price elasticities, and promotions across 49,616 SKUs.
  2. **Inventory Agent:** Multi-echelon stock optimization enforcing safety stock thresholds, perishability/shelf-life rules, and storage conditions.
  3. **MCP Tool Integration:** Agents interface with D2 via bounded tools (`get_inventory_position`, `evaluate_demand_shock`).

### Deliverable D4: Supplier & Transportation Specialist Agents
* **V1 Concept:** Simple rule-based delay predictors.
* **V2 Concept:** Structural network specialists:
  1. **Supplier Agent:** Dynamic vendor reliability scoring ($0.0 - 1.0$), contract compliance tracking, and alternate vendor capacity discovery.
  2. **Transportation Agent:** Multi-modal transit delay estimation, carrier capacity constraints, and dynamic freight re-routing logic.
  3. **Graph-Native Reasoning:** Leverages Neo4j bounded traversals to evaluate multi-tier supply chain paths.

### Deliverable D5: Agent Orchestration & Protocol Kernel
* **V1 Concept:** Basic sequential LangGraph state machine.
* **V2 Concept:** Resilient, asynchronous multi-agent coordination kernel:
  1. **A2A Protocol & Agent Cards:** Dynamic discovery and capability self-description of active specialist agents.
  2. **Structured Claim Contract:** Universal claim format specifying proposed action, situational confidence ($c_i$), cost impact, and evidence references.
  3. **Parallel Fan-Out / Fan-In:** Concurrent agent deliberation with sub-second execution budgets.

### Deliverable D6: CD²F Dynamic Consensus Engine
* **V1 Concept:** Static weighted average of agent claims.
* **V2 Concept:** Dynamic, multi-factor consensus arbitration engine:
  1. **Continuous Multi-Factor Weighting:** $W_i = w_i \times c_i$ (historical domain competence $\times$ real-time confidence).
  2. **Greedy Bias & Error Override:** Algorithmic detection and overruling of isolated, overconfident specialist claims.
  3. **Tri-Tier Escalation Gating:**
     * *Fast-Path Autonomous Execution:* $WCS \ge 0.70$ and low risk ($< 335\text{ ms}$).
     * *Slow-Path Extended Deliberation:* Moderate consensus requiring secondary trade-off analysis.
     * *Human-in-the-Loop (HITL) Escalation:* Critical severity or low consensus ($WCS < 0.70$).

### Deliverable D7: Observability & Explainability Backend
* **V1 Concept:** Basic logging of decisions to PostgreSQL.
* **V2 Concept:** Comprehensive enterprise audit and explainability infrastructure:
  1. **Verbatim Meeting Log:** Full multi-agent conversational transcripts capturing claims, counter-arguments, and compromises.
  2. **8-Stage Reasoning Trace:** Step-by-step decision audit trail from disruption ingestion to consensus execution.
  3. **pgvector Semantic Search:** Sub-50ms natural language query retrieval over historical decisions and precedent cases.

### Deliverable D8: Real-Time API Gateway & Event Bus
* **V1 Concept:** Simple FastAPI endpoints for triggering scenarios.
* **V2 Concept:** Enterprise event streaming and communication gateway:
  1. **FastAPI Gateway:** Parameterized REST endpoints for scenario management, what-if simulations, and decision replay.
  2. **Apache Kafka Event Bus:** High-throughput event streaming decoupling disruption producers, orchestrators, and consumers.
  3. **WebSocket Live Push:** Real-time state broadcasting to desktop control rooms and external dashboards.

### Deliverable D9: Desktop Operations Console (Tauri v2)
* **V1 Concept:** Web dashboard preview.
* **V2 Concept:** Native, high-performance desktop control room (Apple HIG dark-mode aesthetic):
  1. **7 Specialized Views:** Operations Overview (`Ctrl+1`), Decision Center (`Ctrl+2`), Scenario Launcher (`Ctrl+3`), Agent Command (`Ctrl+4`), What-If Simulation Lab (`Ctrl+5`), Reasoning Traces (`Ctrl+6`), Evaluation Matrix (`Ctrl+7`).
  2. **Interactive What-If Simulation Lab:** Real-time sliders allowing operators to adjust disruption severity, evaluate alternate routes, and observe projected fill-rate preservation.
  3. **Zero-Latency State Synchronization:** Instant UI updates driven by WebSocket event streams.

### Deliverable D10: Integration, Benchmarking & Empirical Evaluation
* **V1 Concept:** Basic test scripts running a few scenario assertions.
* **V2 Concept:** Rigorous scientific evaluation framework:
  1. **Isolated Benchmark Harness:** Guarantees zero cross-scenario state contamination across all evaluation runs.
  2. **Comparative Baselines:** Benchmarks CD²F against Single-Agent, Naive Unweighted Voting, and Static Priority Heuristics.
  3. **Formal Research Questions (RQ1–RQ4):** Quantitative proofs of decision accuracy, consensus stability, latency distribution, and fill-rate preservation.

### Deliverable D11: Post-MVP Extension Points
* **V1 Concept:** Placeholder notes for future work.
* **V2 Concept:** Architectural plug-in interfaces:
  1. **Specialized Extension Agents:** Risk & Resilience Agent, Sustainability/ESG Agent, Macro-Finance Agent.
  2. **Cross-Enterprise A2A Handoff:** Protocol extensions allowing SCOF to negotiate with external supplier and carrier agent twins.
  3. **Digital Twin Continuous Replay:** Live synchronization with real-world ERP/WMS feeds.

---

## 5. Conclusion & Governance

By anchoring SCOF V2 in this architecture evolution blueprint:
1. All V1 documents remain intact as historical and structural baselines.
2. The system gains a clear, unambiguous domain identity: **SCOF Retail Enterprise Reference World**.
3. D1 and D2 are elevated to enterprise-grade foundations (Simulation Foundation and Knowledge Fabric).
4. The 3.73M-node graph is safely governed by bounded query contracts.
5. Evaluation in D10 is protected by strict tripartite data isolation.
6. The 30 business domains are cleanly decoupled from the 4-agent operational roster.
