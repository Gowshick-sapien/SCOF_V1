# SCOF Desktop Console & Architecture Deep-Dive

This document provides a detailed technical analysis of the SCOF Desktop Operations Console and the underlying orchestration engine. It covers the metrics, topology visualization, escalation tiers, deterministic arbitration behavior, benchmarking engine, and semantic intelligence retrieval.

---

## 1. Top Metric Cards (Operations Overview)

### 1.1 Metrics Breakdown & Implementation Status

| Metric Card | Displayed Value | Meaning & Objective | Dynamic vs Hardcoded Status |
| :--- | :--- | :--- | :--- |
| **Supply Chain Reliability** | `96.4%` (`+1.2% vs target`) | Represents the macro network operational index (percentage of orders and freight delivered without delay or stockout). | **Partially Dynamic Template**: The value toggles between `96.4%` and `95.8%` depending on whether `dashboardState.system_health` returns nominal or degraded from `GET /dashboard/state`. The numeric target variance `+1.2%` is currently a template constant. |
| **Inventory Stock Coverage** | `18.4 d` (`Safety threshold: 14d`) | Represents the aggregate days of inventory on hand across warehouses before stockout risk occurs. | **Template Constant**: Currently rendered as static UI telemetry (`18.4 d`) in `desktop/src/views/Operations/OperationsView.tsx`. In production, this binds to aggregated warehouse inventory levels from `scof.inventory_levels`. |
| **Active Disruption Risk** | `NOMINAL` or `ELEVATED` | Indicates whether the supply network is experiencing active disruptions and consensus arbitrations. | **Fully Dynamic**: Directly bound to `recentDecisions.length`. When decisions are active or recently arbitrated, it renders `ELEVATED` with warning styling; when no decisions exist, it renders `NOMINAL` ("All nodes stable"). |
| **Specialist Agents Online** | `4 / 4` (`A2A Discovery OK`) | Indicates the health and discovery status of the 4 autonomous specialist agents on the A2A network. | **Static Summary**: Hardcoded to `4 / 4` in the Overview card, but dynamically verified and monitored in the **Agent Command Center** (`desktop/src/views/AgentCommand/AgentCommandView.tsx`), where live status pills track real agent heartbeats. |

### 1.2 What Causes Them to Change?
- **Active Disruption Risk** changes dynamically as disruptions are injected via `POST /scenarios/trigger` and completed decisions are written to PostgreSQL (`scof.decision_records`).
- **Telemetry Integration**: The values for inventory stock coverage and reliability are designed to be hooked into continuous rollups over `scof.inventory_levels` and `scof.shipments` once real-time ERP event streams are connected.

---

## 2. Global Supply Network Topology Visualization

### 2.1 What the Diagram Represents
The vector diagram in `desktop/src/views/Operations/OperationsView.tsx` visualizes the canonical supply chain topology defined in `profiles/mvp-electronics/topology.yaml`:
- **Central Node (`MFG-01`)**: The Shenzhen Assembly Plant where components are assembled into finished consumer electronics.
- **Supplier Nodes (`sup-01`, `sup-02`, `sup-03`)**:
  - `sup-01` (Global Silicon): Secondary Tier-1 semiconductor vendor.
  - `sup-02` (Pacific Semi): Primary contracted Tier-1 component supplier.
  - `sup-03` (Apex Microdevices): Certified alternate/backup supplier for dual-sourcing.
- **Distribution Nodes (`wh-01`, `dc-02`)**:
  - `wh-01` (Frankfurt Regional Distribution Center).
  - `dc-02` (Amsterdam Central Distribution Hub).

### 2.2 Why Specific Lines are Colored vs Dotted
- **Solid Glowing Blue Line (`sup-02` to `MFG-01`)**: Represents the **active primary freight procurement lane**. In normal baseline operations, volume flows through Pacific Semi (`sup-02`).
- **Dotted Grey Lines (`sup-01` and `sup-03` to `MFG-01`)**: Represent **standby / secondary corridors**. These contracts exist but do not carry active procurement volume unless an arbitration decision reroutes volume to them.
- **Solid Green Lines (`MFG-01` to `wh-01` and `dc-02`)**: Represent **nominal outbound finished-goods transit corridors** to regional distribution hubs.

### 2.3 Does the Diagram Change Dynamically?
In the current MVP release, the SVG paths and lane colors are rendered using declarative baseline SVG elements. The topology layout accurately depicts the static network structure. Dynamic lane pulse animation upon active disruption is on the post-MVP roadmap to visually highlight rerouted volume in real time.

---

## 3. Fast-Path, Slow-Path, and Human Escalation (In Detail)

The CD2F Consensus Arbitration Engine (`services/consensus/src/escalation.py`) evaluates every disruption through a three-tier risk-gating model:

```
[ Specialist Agent Claims & Evidence ]
                  │
                  ▼
[ Dynamic Weighting & WCS Calculation ]
                  │
        ┌─────────┴─────────┐
        │                   │
  WCS >= 0.85 &       WCS < 0.70 OR
  Unanimous Agreement High/Critical Impact
        │                   │
        ▼                   ▼
   [ FAST_PATH ]     [ HUMAN_ESCALATION ]
Autonomous Execution    Operator Review
    (< 500ms SLA)          Required
        │                   │
        └─────────┬─────────┘
                  │
           Intermediate WCS
                  │
                  ▼
            [ SLOW_PATH ]
      Simulation / What-If Run
```

### 3.1 Fast-Path Autonomous Execution
- **Criteria**:
  1. **Unanimous Agreement**: All participating agents agree on the same core recommendation (`num_distinct_recs == 1`).
  2. **High Agent Confidence**: Minimum stated confidence across all agents exceeds the threshold (`min_stated_confidence >= 0.85`).
  3. **Low/Moderate Impact**: Maximum operational impact does not exceed `MEDIUM`.
- **Operational Action**:
  - The decision is executed **autonomously in sub-second latency** (< 500ms SLA).
  - No human approval is required. The system issues procurement POs or reroutes shipments automatically.

### 3.2 Human Escalation (HITL)
- **Criteria**:
  1. **Low Consensus Stability**: Weighted Consensus Stability falls below safety minimum (`WCS < 0.70`), indicating sharp disagreement between specialist domains.
  2. **High/Critical Impact**: Disruption impact is rated `HIGH` or `CRITICAL` (e.g., severe lead-time blowout threatening complete factory stoppage).
  3. **Low Decision Confidence**: Winning recommendation confidence falls below safe execution thresholds (`decision_confidence < 0.60`).
  4. **Unresolvable Tie**: Specialist agents propose diametrically opposed actions with identical weights.
- **Operational Action**:
  - The mitigation is **gated**. It is highlighted in red in the Desktop Console.
  - An operator must review the meeting log in the **Decision Center** and manually approve the mitigation.

### 3.3 Slow-Path Simulation
- **Criteria**:
  - The decision does not meet the strict unanimity requirements of Fast-Path, but does not trigger the severe risk thresholds of Human Escalation (`0.70 <= WCS < 0.85`).
- **Operational Action**:
  - The proposed action is routed through the **What-If Simulation Lab** to run counterfactual impact projections before committing physical inventory.

---

## 4. Scenario Determinism & Repeatability: Why It Is an Engineering Feature

### 4.1 Why Triggering Scenario 2 Multiple Times Gives the Same Decision
If you trigger `scen-02` multiple times with default parameters, the system outputs the identical winning recommendation:
1. **Underlying Database Grounding**: The underlying historical records in PostgreSQL (e.g., supplier on-time delivery percentages, lead-time variance) and Neo4j graph relationships are fixed historical snapshots for that scenario context.
2. **Deterministic Model Inference**: Machine learning models (XGBoost, Prophet, Scikit-learn) in each specialist agent evaluate fixed feature vectors under fixed random seeds.
3. **Deterministic Consensus Formulations**: The CD2F arbitration engine uses closed-form mathematical equations:
   $$W_i = w_i \times c_i$$
   Given identical inputs, the mathematics produce identical output weights.

### 4.2 Why This Is Mandatory in Enterprise Operations
In mission-critical enterprise environments (defense, aerospace, semiconductors):
- **Stochastic Hallucination is Unacceptable**: An autonomous AI system that recommends rerouting to Supplier B on Monday, but recommends shutting down the factory when presented with the exact same data on Tuesday, cannot be trusted in production.
- **Auditability & Regulatory Compliance**: Operations directors must be able to reproduce decisions during post-mortem audits.

### 4.3 How to Observe Different Outcomes
To see different outputs and emergent behavior:
- **Adjust Parameters in the Scenario Launcher (`Ctrl + 3`)**:
  - Change the **Severity Slider** from `4` to `1` (low severity changes escalation from `HUMAN_ESCALATION` to `FAST_PATH`).
  - Change the **Target Node** from `sup-01` to `wh-01` (involves the Inventory and Transport agents rather than the Supplier agent).
  - Change the **Disruption Type** to `demand_spike` or `adverse_weather`.
- **Counterfactual Exploration in What-If Lab (`Ctrl + 5`)**:
  - Override lead times and observe how the winning recommendation switches dynamically between buffer absorption and dual-sourcing contracts.

---

## 5. Evaluation & Benchmarking Engine Explained

The **Evaluation & Benchmarks** screen (`desktop/src/views/Evaluation/EvaluationView.tsx`) validates system performance across research questions RQ1 through RQ4 using 20 benchmark scenarios.

### 5.1 Calibration KPI Cards
- **Inter-Agent Agreement Kappa (`1.000` / `>= 0.85`)**:
  - Measures inter-annotator consistency using Cohen's Kappa.
  - Demonstrates that specialist agents consistently align on disruption root causes rather than producing conflicting assessments.
- **Fast-Path Resolution P90 (`330ms` / `< 500ms`)**:
  - 90th percentile round-trip latency from disruption ingestion to arbitrated consensus decision.
  - Confirms compliance with sub-second operational SLAs.
- **Stockout Risk Reduction (`42.0%`)**:
  - Measures the percentage reduction in stockout probability achieved by CD2F mitigations compared to unmitigated operations.

### 5.2 Arbitration Methods Comparative Matrix
Directly compares CD2F against baseline industry heuristics:
1. **CD2F (Consensus-Driven Collaborative Decision Framework)**:
   - Uses multi-factor confidence and domain competence weighting ($W_i = w_i \times c_i$).
   - Achieves highest accuracy (~90%) with lowest human escalation rate (~10%).
2. **Single-Agent (Demand Only)**:
   - Models traditional single-agent AI systems. Lacks supplier and transportation operational awareness, resulting in localized bias and high stockout errors.
3. **Naive Majority Voting**:
   - Models unweighted majority voting common in multi-agent frameworks. Suffers from deadlocks during ties and fails to account for historical agent accuracy.

### 5.3 Categorical Breakdown Table (20 Scenarios)
Breaks down accuracy, latency, and conflict intensity across the 4 core disruption categories:
- `supplier_delay`: Supplier lead-time blowouts.
- `demand_spike`: Rapid customer order surges.
- `transport_failure`: Freight corridor closures and customs bottlenecks.
- `adverse_weather`: Severe regional weather events impacting logistics.

---

## 6. AI Operational Assistant (Intelligence Drawer) & Semantic Search

### 6.1 What Is the Intelligence Drawer Targeting?
The AI Operational Assistant (`desktop/src/components/chat/AIChatDrawer.tsx`) is a **Retrieval-Augmented Generation (RAG) semantic lookup engine** connected to `scof.decision_records` and `scof.embeddings` in PostgreSQL via `pgvector`.

It is **not** a general conversational chatbot (like a conversational assistant designed to say "Hello, how can I help you?"). Its purpose is:
- To allow human supply chain operators to query past historical arbitrations and mitigations using natural language.
- To retrieve past consensus decisions and display exact source citations.

### 6.2 Critical Root-Cause Analysis: The Three Subsystem Flaws

A rigorous audit of the codebase reveals why the chatbot returned inaccurate and unexpected answers for operational questions:

#### Flaw 1: Pseudo-Random SHA-256 Hashes Rather than Neural Embeddings
In `services/observability/src/embedding_client.py`:
```python
def generate_embedding(self, text: str) -> List[float]:
    hash_digest = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(hash_digest[:4], "big")
    rng = np.random.RandomState(seed)
    raw_vector = rng.randn(self.dimension)
    norm = float(np.linalg.norm(raw_vector))
    ...
```
- The embedding client does not use a trained neural transformer model (such as `MiniLM` or OpenAI/Gemini embeddings).
- Instead, it hashes the text using SHA-256 and takes the first 4 bytes as a random seed to sample 384 Gaussian random numbers.
- Cryptographic hash functions have an **avalanche effect**: changing even a single word completely alters the hash and generates an unrelated random vector. Natural language semantic relationships are completely destroyed.
- Therefore, cosine similarity (`<=>`) in PostgreSQL does not measure linguistic meaning; it measures random geometric proximity on a 384-dimensional sphere.

#### Flaw 2: The Vector Database Only Contains Recommendation Strings
In `services/observability/src/decision_repo.py`:
- Only `decision.final_recommendation` is vectorized and stored in `scof.embeddings`.
- Vendor names ("Pacific Semi"), corridor identifiers ("primary freight route"), scenario IDs, and specialist debate logs are never embedded.
- Furthermore, an audit of `scof.embeddings` reveals that among 37 stored embeddings, **30 contain the exact identical string**: `"Issue expedited purchase reorder and reroute safety stock from alternate warehouse."` The database lacked the domain metadata to differentiate specific vendors or corridors.

#### Flaw 3: Absence of an LLM Reasoning Engine (Fixed 1-Shot Nearest Neighbor Template)
In `services/api/src/routers/chat.py`:
- The system is not an LLM conversational agent that reads documents, synthesizes answers, or handles conversational greetings.
- It takes the single nearest vector match (`matches[0]`) from PostgreSQL without a similarity cutoff threshold and plugs it into a static text template:
  `"Retrieved mitigation from CD2F consensus record:\n\n{rec}..."`
- It cannot aggregate records ("Which decisions..."), filter by conditions, or explain operational trade-offs.

---

### 6.3 Post-Mortem of User Test Queries

| User Prompt | Expected Outcome | Actual Returned Output | Root Cause |
| :--- | :--- | :--- | :--- |
| **"How did we resolve the Pacific Semi supplier delay?"** | Mitigation regarding Pacific Semi (`sup-02`). | Mitigation for `sup-01` (`dec-00001`). | Pacific Semi is `sup-02`. Because "Pacific Semi" was never embedded, the random Gaussian vector generated from SHA-256 had an arbitrary mathematical proximity to `dec-00001` (`sup-01`). |
| **"What action was taken when the primary freight lane was blocked?"** | Logistics reroute along freight lane `route-sup-01-wh-01`. | Demand spike mitigation on `prod-101` (`dec-00003`). | "Primary freight lane" was never vectorized. The random query vector matched with `dec-00003` purely by chance. |
| **"Which decisions resulted in human escalation?"** | A list or summary of decisions requiring human approval. | A single decision record (`7156a59a...`) with confidence 54.0%. | The query asks for an aggregation ("Which decisions..."). The endpoint only executes a `LIMIT 1` vector nearest-neighbor lookup without SQL aggregation. |

---

### 6.4 What Questions the Assistant Can and Cannot Solve in Its Current State

#### What It CAN Solve:
It can reliably match queries that closely or verbatim mirror the exact recommendation strings stored in PostgreSQL:
1. Exact recommendation retrieval: *"Issue expedited purchase reorder and reroute safety stock from alternate warehouse"* (Returns 1.000 cosine similarity match).
2. Supplier delay synthetic signal: *"Reroute shipments from sup-01 due to severe supplier_delay event"* (Matches `dec-00001`).
3. Transport failure synthetic signal: *"Reroute shipments from route-sup-01-wh-01 due to severe transport_failure event"* (Matches `dec-00002`).
4. Demand surge synthetic signal: *"Reroute shipments from prod-101 due to severe demand_spike event"* (Matches `dec-00003`).
5. Weather disruption synthetic signal: *"Reroute shipments from route-sup-01-wh-01 due to severe adverse_weather event"* (Matches `dec-00004`).

#### What It CANNOT Solve:
1. **Conversational greetings**: Inputs like "hi" or "hello" are converted into pseudo-vectors and force-matched against the nearest mitigation record.
2. **Aggregations & analytics**: Queries like "List all decisions from today" or "Which suppliers failed the most?"
3. **Natural language synonyms**: Queries using everyday phrasing ("delayed microchips", "customs bottleneck") because SHA-256 does not preserve linguistic synonyms.
4. **Deliberation audit queries**: Inquiries into why agents disagreed, because meeting logs are not indexed into vector storage.

---

### 6.5 Production Architectural Roadmap for True AI Intelligence

1. **Replace SHA-256 with Real Transformer Embeddings**:
   - Use `fastembed` or `sentence-transformers/all-MiniLM-L6-v2` (runs in CPU Docker in < 25ms).
   - This ensures "chip delay" and "supplier lead time blowout" occupy proximate coordinates in vector space.
2. **Vectorize Comprehensive Context Cards**:
   - Embed full metadata: Scenario ID, disruption type, affected entities, vendor names, winning recommendation, and summary of specialist arguments.
3. **Dual-Route Architecture in `chat.py`**:
   - **Similarity Cutoff**: If similarity is below `0.65`, return: *"No matching historical decision found."*
   - **Analytical Query Routing**: Route questions containing words like "which", "how many", "list all" to SQL queries over `scof.decision_records`.
   - **Generative Synthesis**: Feed top-3 retrieved context cards into an LLM (such as Gemini) to formulate natural, accurate answers with citations.

---

## 7. Increasing the Number of Scenarios: Architectural Scalability Analysis

### 7.1 Can the Number of Scenarios Be Increased?
**Yes, absolutely.** You can scale the system from 4 scenarios to 50, 100, or 1,000+ scenarios.

### 7.2 Does Adding Scenarios Require Changing the Core System Architecture?
**No. It is an easy, configuration-driven task.** 

The SCOF architecture was explicitly designed to be **domain-agnostic and profile-driven**:
- **Coordinator Orchestration Engine (`services/coordinator/src/agent_discovery.py`)**:
  Does not hardcode scenario IDs. It resolves specialist agents dynamically based on the disruption context:
  ```python
  matched_cards = registry.find_by_context(disruption_type)
  if not matched_cards:
      matched_cards = registry.get_healthy_cards()
  ```
- **Consensus Engine (`services/consensus/src/arbitration.py`)**:
  Calculates dynamic multi-factor weighting ($W_i = w_i \times c_i$) and Weighted Consensus Stability (WCS) strictly from normalized claim bundles. It is completely decoupled from scenario identifiers.
- **Observability Ledger (`services/observability/src/decision_repo.py`)**:
  Stores decision records, reasoning trails, and meeting logs keyed by UUIDs and scenario context without fixed schema constraints.
- **Desktop Operations Console (`desktop/src/views/Scenarios/ScenariosView.tsx`)**:
  Dynamically fetches scenarios from the backend via `GET /scenarios`.

---

### 7.3 How Scenarios Are Framed and the Two Scaling Modes

#### Mode 1: Creating New Scenarios with Existing Disruption Types (Very Simple, Zero Code Changes)
If you are framing scenarios using existing disruption types (`supplier_delay`, `demand_spike`, `transport_failure`, `adverse_weather`), no code changes are required anywhere in the microservice fleet.

To add a new scenario (for example, `scen-05: Shenzhen Assembly Power Outage`):
1. **Insert Metadata into PostgreSQL**:
   ```sql
   INSERT INTO scof.scenarios (scenario_id, run_id, name, description, random_seed)
   VALUES ('scen-05', 'run-20260814-001', 'Shenzhen Assembly Power Outage', 'Regional power bottleneck halting assembly at MFG-01', 501);

   INSERT INTO scof.disruption_events (id, run_id, scenario_id, disruption_type, target_entity_type, target_entity_id, severity, start_date, end_date, status)
   VALUES ('disrupt-00007', 'run-20260814-001', 'scen-05', 'adverse_weather', 'manufacturer', 'mfg-01', 4, '2026-06-01', '2026-06-08', 'ACTIVE');
   ```
2. **Verify in Desktop Console**:
   Refresh the **Scenario Launcher (`Ctrl + 3`)**. `scen-05` will appear in the library table. Triggering it immediately dispatches the event, invokes the agents, arbitrates consensus, and logs the decision.

#### Mode 2: Introducing a Brand-New Disruption Category (Simple Profile Configuration)
If you want to frame a completely new disruption category (for example, `cyber_attack`, `quality_defect`, or `geopolitical_embargo`):
1. **Declare in Domain Profile (`profiles/mvp-electronics/disruptions.yaml`)**:
   ```yaml
   disruption_types:
     - id: "quality_defect"
       name: "Component Batch Quality Contamination"
       severity_range: [1, 5]
       default_duration_days: 10
       target_entity: "supplier"
   ```
2. **Map Agent Capability Context (`profiles/mvp-electronics/agents.yaml`)**:
   Add `quality_defect` to the `supported_contexts` of the relevant specialist agents (e.g., Supplier Agent and Inventory Agent).
3. **Agent Inference Logic**:
   In `services/agents/supplier/src/agent.py`, add a rule or model feature mapping `quality_defect` to supplier reliability degradation.
4. **No Kernel Changes**:
   The API Gateway, Kafka bus, LangGraph Coordinator, CD2F Consensus Engine, Observability backend, and Desktop Console handle the new disruption category automatically without architectural modifications.

---

## 8. Summary of Console Operational Workflow

- **Operations Overview (`Ctrl + 1`)**: Provides macro situational awareness; displays live risk state and recent decisions.
- **Decision Center (`Ctrl + 2`)**: The audit room; inspects verbatim specialist claims, confidence scores, and meeting logs.
- **Scenario Launcher (`Ctrl + 3`)**: The simulation trigger; injects disruptions into the Kafka event bus with custom severities and target nodes.
- **Agent Command (`Ctrl + 4`)**: Fleet monitor; observes live A2A execution status and latency in real time.
- **What-If Lab (`Ctrl + 5`)**: The counterfactual lab; models simulated disruptions and evaluates cost/risk deltas before execution.
- **Reasoning Traces (`Ctrl + 6`)**: Mathematical transparency; inspects the 4-phase weighting pipeline per decision.
- **Evaluation (`Ctrl + 7`)**: Empirical benchmark engine; proves CD2F superiority over single-agent and naive voting baselines.
- **Intelligence Drawer (`Ctrl + K`)**: Semantic memory; retrieves historical mitigations and source citations via pgvector cosine search.

---

## 9. Enterprise Network Expansion & South Indian Localization (Topology & Entity Scaling)

### 9.1 Core Architectural Assessment: Is It Possible Easily? Does It Require Core Changes?

**Answer**:
1. **Is it possible easily?**: **Yes, exceptionally easy.** The entire SCOF platform was designed around declarative domain profiles and normalized relational/graph models.
2. **Does it require core architecture changes?**: **No. Zero core architectural changes are required.**

The microservice kernel, message broker pipelines, consensus mathematical formulation, and multi-agent discovery layers are 100% decoupled from entity counts and geographic names:
- **API Gateway (`services/api/`)**: Dispatches scenario events without entity validation hardcodes; accepts any valid entity identifier present in the operational tables.
- **LangGraph Coordinator (`services/coordinator/`)**: Queries agent cards and resolves participants dynamically using context metadata rather than hardcoded topology dictionaries.
- **CD2F Consensus Engine (`services/consensus/`)**: Solves weighted arbitrations using closed-form mathematical equations ($W_i = w_i \times c_i$). The number of nodes in the graph has zero impact on consensus kernel stability.
- **A2A Protocol & Specialist Agents (`services/agents/`)**: Specialized agents query PostgreSQL tables (`scof.suppliers`, `scof.warehouses`, `scof.routes`, `scof.shipments`, `scof.inventory_levels`) and Neo4j graph relationships (`MATCH (alt:Supplier)-[:ALTERNATE_FOR]->(s:Supplier)`) using parameterized entity IDs.
- **Synthetic Simulation & ETL Pipeline (`services/simulation/` & `services/etl/`)**: The `EntityGenerator` dynamically reads whatever entities are defined in `profiles/mvp-electronics/topology.yaml`, automatically calculates Haversine geographic distances between latitude/longitude pairs, assigns transport modes, generates multi-sourcing ties, and loads nodes/edges into Neo4j and PostgreSQL using bulk Cypher `UNWIND` queries.

---

### 9.2 Enterprise South Indian Electronics Manufacturing Topology Blueprint

To transition from the initial 4-5 node sandbox to an enterprise-grade industrial network, the topology can be mapped directly to the premier electronics and semiconductor manufacturing corridors of South India (Tamil Nadu, Karnataka, Andhra Pradesh, Kerala, Telangana).

```
                      [ dc-03: Hyderabad Air Cargo (TS) ]
                                      ^
                                      | (Road / Air Express)
[ sup-02: Bengaluru CDIL ] ---+       |
[ sup-05: Bengaluru Centum ] -+---> [ wh-02: Whitefield Inbound Hub (KA) ]
                              |       |
                              |       v
[ sup-03: Mysuru Kaynes ] ----+---> [ wh-01: Hosur Industrial Buffer (TN/KA) ]
[ sup-06: Mysuru Vinyas ] ----+       |
                                      v
                      [ mfg-01: Sriperumbudur Assembly Hub (TN) ] <--- [ wh-03: Oragadam JIT Hub (TN) ]
                                      |                                ^
                                      +--------------------------------+
                                      v                                v
                      [ mfg-02: Sri City Cluster (AP/TN) ] <--- [ wh-04: Sri City FTWZ Buffer (AP) ]
                                      |                                ^
                                      +--------------------------------+
                                      |                                |
[ sup-01: Chennai SPEL Semi ] --------+                                |
[ sup-04: Bargur Syrma SGS ] ------------------------------------------+
                                      |
              +-----------------------+-----------------------+
              v                                               v
[ dc-01: Chennai / Ennore Port Gateway (TN) ]    [ dc-02: Kochi International Port (KL) ]
```

#### Node Inventory Breakdown (18 Enterprise Nodes)

1. **Manufacturing Assembly Plants (2 Central Nodes)**:
   - `mfg-01`: **Sriperumbudur High-Tech Assembly Plant** (Tamil Nadu; Lat: 12.9716, Lon: 79.9416)
     - Core industrial hub for consumer electronics, telematics, and smartphone assembly (Foxconn/Pegatron industrial corridor).
   - `mfg-02`: **Sri City Electronics Manufacturing Hub** (Andhra Pradesh / TN Border; Lat: 13.5284, Lon: 80.0315)
     - Secondary/overflow facility supporting multi-facility production balancing and failover.

2. **Tier-1 and Tier-2 Specialist Suppliers (8 Nodes)**:
   - `sup-01`: **SPEL Semiconductor** (Maraimalai Nagar, Chennai, TN; Lat: 12.7937, Lon: 80.0242)
     - IC packaging, leaded/non-leaded semiconductor test and assembly. (Reliability: `high`, Lead time: 5 days)
   - `sup-02`: **Continental Device India - CDIL** (Electronic City, Bengaluru, KA; Lat: 12.8452, Lon: 77.6602)
     - Discrete semiconductor components, transistors, rectifiers. (Reliability: `high`, Lead time: 6 days)
   - `sup-03`: **Kaynes Technology India** (Koorgalli, Mysuru, KA; Lat: 12.3382, Lon: 76.5824)
     - High-density multi-layer printed circuit board (PCB) assembly and box-build EMS. (Reliability: `medium`, Lead time: 8 days)
   - `sup-04`: **Syrma SGS Technology** (Bargur Industrial Estate, TN; Lat: 12.5442, Lon: 78.3614)
     - Custom magnetic components, RFID coils, micro-electronic assemblies. (Reliability: `high`, Lead time: 7 days)
   - `sup-05`: **Centum Electronics** (Yelahanka, Bengaluru, KA; Lat: 13.1007, Lon: 77.5963)
     - High-reliability power modules, frequency control products. (Reliability: `medium`, Lead time: 9 days)
   - `sup-06`: **Vinyas Innovative Technologies** (Hebbal Industrial Area, Mysuru, KA; Lat: 12.3551, Lon: 76.6110)
     - Precision cable assemblies, interconnect harnesses, sensory modules. (Reliability: `volatile`, Lead time: 12 days)
   - `sup-07`: **SFO Technologies / NeST Group** (Kakkanad / Infopark, Kochi, KL; Lat: 9.9982, Lon: 76.3570)
     - Optoelectronics, fiber-optic transceivers, and ruggedized housing. (Reliability: `high`, Lead time: 7 days)
   - `sup-08`: **Sahasra Electronic Solutions** (Expansion Hub, Hyderabad, TS; Lat: 17.3850, Lon: 78.4867)
     - Memory module packaging and storage subsystems. (Reliability: `medium`, Lead time: 10 days)

3. **Regional Storage & Cross-Dock Warehouses (4 Nodes)**:
   - `wh-01`: **Hosur Logistics Buffer Warehouse** (Tamil Nadu / Karnataka Border; Lat: 12.7409, Lon: 77.8253)
     - Strategic cross-border staging warehouse buffering supplies from Bengaluru/Mysuru along NH44. Capacity: 75,000 units.
   - `wh-02`: **Whitefield Inland Container Depot** (Bengaluru, KA; Lat: 12.9698, Lon: 77.7500)
     - Inbound raw material consolidation depot serving Karnataka suppliers. Capacity: 50,000 units.
   - `wh-03`: **Oragadam JIT Supplier Warehouse** (Kanchipuram, TN; Lat: 12.8342, Lon: 79.9197)
     - Just-in-Time component buffer warehouse located 14 km from Sriperumbudur plant. Capacity: 60,000 units.
   - `wh-04`: **Sri City FTWZ Logistics Center** (Andhra Pradesh; Lat: 13.5410, Lon: 80.0210)
     - Free Trade and Warehousing Zone (FTWZ) bonded facility for duty-free intermediate inventory. Capacity: 40,000 units.

4. **Distribution Gateways & Seaports (3 Nodes)**:
   - `dc-01`: **Chennai Port / Ennore Logistics Gateway** (Chennai, TN; Lat: 13.0827, Lon: 80.2907)
     - Maritime container terminal for finished goods ocean freight export across Southeast Asia and Europe.
   - `dc-02`: **Cochin International Container Transshipment Terminal** (Vallarpadam, Kochi, KL; Lat: 9.9836, Lon: 76.2415)
     - Deep-water maritime gateway serving Western trade lanes and Gulf transshipment.
   - `dc-03`: **Shamshabad Aerotropolis Express Gateway** (RGIA, Hyderabad, TS; Lat: 17.2403, Lon: 78.4294)
     - Central air cargo transshipment terminal for express critical shipments across India and international hubs.

5. **Finished Goods Product Portfolio (3 SKUs)**:
   - `prod-101`: **Smart IoT Telematics Gateway** (`SKU-IOT-101`)
   - `prod-102`: **Industrial Automotive Sensor Hub** (`SKU-SNS-102`)
   - `prod-103`: **High-Efficiency Micro-Inverter Power Unit** (`SKU-PWR-103`)

---

### 9.3 Interconnections, Multi-Sourcing Dependencies, and Route Network

When expanding to this enterprise topology, the system models real-world interconnections and dependencies:

#### 1. Multi-Sourcing & Dual-Sourcing Sourcing Dependencies
In `Neo4j`, the `[:ALTERNATE_FOR]` graph relationships establish multi-sourcing contracts:
- `sup-02` (CDIL Bengaluru) acts as primary supplier for discrete semiconductors for `prod-101`; `sup-01` (SPEL Chennai) is the designated alternate with +12% cost premium and -2 days lead time.
- `sup-03` (Kaynes Mysuru) acts as primary PCB assembler for `prod-102`; `sup-06` (Vinyas Mysuru) and `sup-04` (Syrma Bargur) act as secondary dual-sourcing alternates.
- `sup-05` (Centum Bengaluru) acts as primary power electronics vendor for `prod-103`; `sup-07` (SFO Kochi) is certified backup.

If a severe disruption (e.g. `supplier_delay` on `sup-02`) is injected, the **Supplier Intelligence Agent** executes:
```cypher
MATCH (alt:Supplier)-[r:ALTERNATE_FOR]->(p:Supplier {id: 'sup-02'})
RETURN alt.id, alt.name, r.cost_delta_pct, r.lead_time_delta_days
```
and deterministically routes volume to `sup-01` (SPEL Chennai) without human intervention.

#### 2. Polymorphic Multi-Echelon Routes & True Road Distances
The simulation automatically computes Haversine distances between all declared coordinates:
- `route-sup-02-wh-01`: CDIL Electronic City -> Hosur Warehouse (approx. 22 km, NH44 road transit, 1 day SLA).
- `route-wh-01-mfg-01`: Hosur Buffer -> Sriperumbudur Assembly Hub (approx. 250 km, NH48 industrial freight corridor, 1 day SLA).
- `route-mfg-01-dc-01`: Sriperumbudur -> Chennai Port Gateway (approx. 45 km, Chennai Bypass road corridor, 1 day SLA).
- `route-wh-02-dc-03`: Whitefield Bengaluru -> Hyderabad Cargo Hub (approx. 560 km, NH44 interstate road corridor, 2 days SLA).
- `route-sup-07-dc-02`: Kochi NeST -> Vallarpadam Port (approx. 20 km, local road transit, 1 day SLA).

---

### 9.4 Concrete Migration Plan: What Needs to Be Touched

The table below outlines every component that needs to be updated. Notice that **no microservice source code, arbitration algorithms, or coordinator engines are altered**:

| Layer | File / Component | Work Required | Complexity |
| :--- | :--- | :--- | :--- |
| **Domain Configuration** | `profiles/mvp-electronics/topology.yaml` | Replace Shenzhen/Foreign entries with the 18 South Indian manufacturers, suppliers, warehouses, distribution centers, and geographic coordinates. | **5 minutes (Configuration edit)** |
| **PostgreSQL & Neo4j Ingestion** | `services/simulation/` & `services/etl/` | Execute synthetic generation and ETL ingestion commands to recompute routes, distances, and graph edges. | **1 command execution** |
| **Console SVG Topology** | `desktop/src/views/Operations/OperationsView.tsx` | Update SVG node coordinates and text labels from Shenzhen/Frankfurt to Sriperumbudur, Chennai, Bengaluru, Mysuru, Hosur, and Kochi. | **10 minutes (JSX styling)** |
| **Console Dropdown Options** | `desktop/src/views/Scenarios/ScenariosView.tsx`<br>`desktop/src/views/WhatIfLab/WhatIfLabView.tsx` | Update `TARGET_ENTITY_OPTIONS` array labels to display the South Indian supplier and warehouse names in the launcher UI. | **5 minutes (Config edit)** |
| **Scenario Seed Records** | PostgreSQL `scof.scenarios`<br>PostgreSQL `scof.disruption_events` | Ensure scenario descriptions reference the new entity names (e.g., SPEL Semiconductor delay instead of Pacific Semi). | **5 minutes (SQL insert/update)** |

---

### 9.5 Execution Commands to Deploy the South Indian Topology

#### Step 1: Update `profiles/mvp-electronics/topology.yaml`
Edit the YAML file with the South Indian entities and coordinates.

#### Step 2: Regenerate Synthetic Data and Seed PostgreSQL
Run the simulation engine to generate master data, routes, shipments, and baseline deliveries:
```bash
docker compose run --rm simulation python -m src.main
```

#### Step 3: Run the ETL Pipeline to Rebuild the Neo4j Knowledge Graph
Run the ETL service to populate Neo4j graph nodes, edges (`PRODUCES`, `SUPPLIES`, `STORED_IN`, `SHIPS_VIA`, `DELIVERS_TO`, `ALTERNATE_FOR`), and PostgreSQL vector embeddings:
```bash
docker compose run --rm etl python -m src.main
```

#### Step 4: Verify Graph Integrity in Neo4j
Open Neo4j Browser (`http://localhost:7474`) and verify the South Indian network topology:
```cypher
MATCH (m:Manufacturer)-[:PRODUCES]->(p:Product)<-[:SUPPLIES]-(s:Supplier)
RETURN m, p, s LIMIT 25;
```

#### Step 5: Update Frontend Console Labels & Launch
Update the node labels and coordinates in `desktop/src/views/Operations/OperationsView.tsx`, `desktop/src/views/Scenarios/ScenariosView.tsx`, and `desktop/src/views/WhatIfLab/WhatIfLabView.tsx`, then run:
```bash
cd desktop && npm run dev
```
The Desktop Operations Console will now visualize the South Indian electronics supply chain network, and all scenario triggers, agent consensus meetings, and What-If simulations will operate across the South Indian nodes.

---

## 10. Manual Scenario Creation: Structured Specification & Feasibility Analysis

### 10.1 Feasibility Assessment: Can Scenarios Be Manually Created Without NLP?

**Answer**: **Yes, 100% feasible.**

In enterprise supply chain digital twins and industrial simulation environments, **manual creation via strongly-typed, deterministic formats (JSON, YAML, UI forms, or SQL) is the standard and preferred industry practice**:
- **Why NLP is sub-optimal for scenario creation**: Natural language prompts ("Make a bad delay on the chip vendor") introduce ambiguity regarding exact entity IDs, temporal windows, and severity metrics. An automated simulation engine requires precise mathematical parameters (e.g., target entity ID `sup-01`, severity `4`, duration `7 days`).
- **Why deterministic formats excel**: Structured schemas guarantee reproducible execution, auditability, programmatic validation via Pydantic/JSON Schema, and seamless integration with external ERP systems (SAP, Oracle SCM).
- **Does it require core architecture changes?**: **No. Zero core architecture changes.** The SCOF platform already processes scenarios through a normalized `ScenarioContext` schema. The backend microservice fleet (Coordinator, Agents, Consensus Engine) does not differentiate whether a scenario was seeded during database initialization, imported via YAML, or posted via a REST API form.

---

### 10.2 Canonical Scenario Data Contract (The Specific Format)

A complete scenario in SCOF consists of two coupled records:
1. **Scenario Metadata** (`scof.scenarios`): High-level operational definition, audit identifier, and random seed.
2. **Disruption Event** (`scof.disruption_events`): Mathematical disruption parameters defining what breaks, where, for how long, and how severely.

#### Canonical JSON Format
```json
{
  "scenario_id": "scen-custom-01",
  "name": "Hosur Highway Freight Bottleneck",
  "description": "Severe monsoon flooding along the NH44 arterial logistics corridor blocking truck transit from Hosur Buffer Warehouse to Sriperumbudur Assembly Hub.",
  "random_seed": 742,
  "disruption": {
    "disruption_type": "adverse_weather",
    "target_entity_type": "route",
    "target_entity_id": "route-wh-01-mfg-01",
    "severity": 4,
    "duration_days": 8,
    "start_date": "2026-11-01",
    "end_date": "2026-11-09"
  }
}
```

#### Canonical YAML Format
```yaml
scenario:
  scenario_id: "scen-custom-02"
  name: "SPEL Semiconductor Cleanroom Contamination"
  description: "Particulate contamination in Maraimalai Nagar packaging fab halting micro-controller shipments."
  random_seed: 819
  disruption:
    disruption_type: "supplier_delay"
    target_entity_type: "supplier"
    target_entity_id: "sup-01"
    severity: 5
    duration_days: 12
    start_date: "2026-11-10"
    end_date: "2026-11-22"
```

#### Field Specification & Validation Rules

| Field Name | Type | Valid Options / Constraints | Purpose & Downstream Impact |
| :--- | :--- | :--- | :--- |
| `scenario_id` | String | Unique string (e.g. `scen-05`, `scen-chennai-port-strike`) | Primary key for the scenario in PostgreSQL, Kafka event keys, and audit logs. |
| `name` | String | Max 255 chars | Human-readable title displayed in the Scenario Launcher table. |
| `description` | String | Text | Contextual summary displayed in decision cards and operator audit traces. |
| `disruption_type` | String | `supplier_delay`<br>`demand_spike`<br>`transport_failure`<br>`adverse_weather` | Governs which specialist agents are dynamically discovered via A2A cards. |
| `target_entity_type` | String | `supplier`<br>`warehouse`<br>`route`<br>`manufacturer`<br>`product` | Identifies the ontological layer in the Neo4j knowledge graph. |
| `target_entity_id` | String | Must match existing ID (e.g. `sup-01`, `wh-02`, `route-wh-01-mfg-01`) | The specific graph node or edge receiving the disruption shock. |
| `severity` | Integer | `1` to `5` | **Critical parameter**: Severities 1-2 allow Fast-Path resolution; severities 4-5 force Human Escalation gating. |
| `duration_days` | Integer | Positive integer (e.g. `3` to `30`) | Number of operational days the disruption persists in shipment delivery history. |

---

### 10.3 The Three Implementation Pathways for Users

#### Pathway 1: REST API Endpoint (`POST /scenarios`)
A clean, strongly-typed HTTP endpoint on the API Gateway:

```python
# Added to services/api/src/routers/scenarios.py
class DisruptionPayload(BaseModel):
    disruption_type: str
    target_entity_type: str
    target_entity_id: str
    severity: int
    duration_days: Optional[int] = 7
    start_date: Optional[datetime.date] = None

class CreateScenarioRequest(BaseModel):
    scenario_id: str
    name: str
    description: str
    disruption: DisruptionPayload
    random_seed: Optional[int] = 42

@router.post("", status_code=201)
async def create_scenario(req: CreateScenarioRequest):
    """Persist a user-defined scenario into PostgreSQL scof.scenarios and scof.disruption_events."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # 1. Check duplicate ID
            cur.execute("SELECT 1 FROM scof.scenarios WHERE scenario_id = %s", (req.scenario_id,))
            if cur.fetchone():
                raise HTTPException(status_code=409, detail=f"Scenario '{req.scenario_id}' already exists")
            
            # 2. Insert scenario metadata
            run_id = f"run-user-{uuid.uuid4().hex[:8]}"
            cur.execute(
                """
                INSERT INTO scof.scenarios (scenario_id, run_id, name, description, random_seed)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (req.scenario_id, run_id, req.name, req.description, req.random_seed),
            )
            
            # 3. Insert disruption event
            start_date = req.disruption.start_date or datetime.date.today()
            end_date = start_date + datetime.timedelta(days=req.disruption.duration_days)
            disrupt_id = f"disrupt-user-{uuid.uuid4().hex[:8]}"
            cur.execute(
                """
                INSERT INTO scof.disruption_events (
                    id, run_id, scenario_id, disruption_type,
                    target_entity_type, target_entity_id, severity,
                    start_date, end_date, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE')
                """,
                (
                    disrupt_id, run_id, req.scenario_id, req.disruption.disruption_type,
                    req.disruption.target_entity_type, req.disruption.target_entity_id,
                    req.disruption.severity, start_date, end_date
                ),
            )
    return {"status": "CREATED", "scenario_id": req.scenario_id}
```

Once created, the scenario immediately appears in `GET /scenarios`, is visible in the Desktop Console, and can be triggered via `POST /scenarios/trigger`.

#### Pathway 2: Desktop Console UI Modal ("Scenario Creator")
In `desktop/src/views/Scenarios/ScenariosView.tsx`, a **"+ New Scenario"** button opens a structured modal dialog containing:
1. **Scenario ID input**: (e.g. `scen-05`).
2. **Scenario Name input**: (e.g. `Mysuru Factory Power Interruption`).
3. **Disruption Category dropdown**: Select from `supplier_delay`, `demand_spike`, `transport_failure`, `adverse_weather`.
4. **Target Entity dropdown**: Select from live nodes (`sup-01: SPEL Semi`, `wh-01: Hosur Buffer`, `mfg-01: Sriperumbudur`, `route-sup-02-wh-01`).
5. **Severity slider**: Select from `1` (Minor) to `5` (Catastrophic).
6. **Save & Add to Catalog button**: Sends `POST /scenarios` and refreshes the table instantly.

#### Pathway 3: Batch YAML/JSON File Import
Users can place configuration files into a directory (e.g. `scenarios/custom_scenarios.yaml`), and an import command or startup hook reads the file and executes idempotent SQL inserts:
```bash
python -m scripts.import_scenarios --file profiles/mvp-electronics/scenarios/custom.yaml
```

---

### 10.4 Architectural Impact Matrix

| Subsystem | Impact of User-Created Scenarios | Architectural Changes Needed? |
| :--- | :--- | :--- |
| **PostgreSQL Database** | Receives standard rows in `scof.scenarios` and `scof.disruption_events`. | None (Schema already accommodates this). |
| **Kafka Event Bus** | Serializes the scenario payload into topic `scof.disruptions.triggered`. | None (Payload schema is dynamic). |
| **LangGraph Coordinator** | Resolves specialist agent cards matching `disruption_type`. | None (Context-driven discovery). |
| **Specialist Agents (4x)** | Evaluates entity history in DB and graph neighbors in Neo4j. | None (Parameterized queries). |
| **CD2F Consensus Engine** | Receives normalized claims and computes multi-factor weights. | None (Closed-form mathematical formulation). |
| **Desktop Console** | Renders new scenario in table and streams live decision metrics. | None (Pulls live from `GET /scenarios`). |

### 10.5 Conclusion
Manual scenario creation is **fully feasible, architecturally native, and immediately implementable**. It requires only adding a `POST /scenarios` endpoint on the API gateway and connecting a form modal in the Desktop Console.



