# Digital Twin Service Architecture

## 1. Executive Summary & Conceptual Grounding

The **Digital Twin Service** in SCOF V2 is not an analytical query wrapper, not a procedural data generator, and not an autonomous multi-agent coordinator. It is the **Authoritative Cyber-Physical State & Simulation Substrate** for the enterprise.

Architecturally, SCOF V2 formally anchors the Twin as **a Distinct Operational World and Simulation Layer Sitting Above D1 (Enterprise World Foundation) and D2 (Enterprise Knowledge Fabric)**:

```text
+-------------------------------------------------------------------------------+
|                       LANGGRAPH ORCHESTRATION KERNEL                          |
|   Specialist Cognitive Agents: Demand, Inventory, Supplier, Transportation    |
+---------------------------------------+---------------------------------------+
                                        | Operational Queries & Claims
                                        v
+-------------------------------------------------------------------------------+
|                   DIGITAL TWIN SERVICE (OPERATIONAL SIMULATION SUBSTRATE)                   |
|   State Authority  |  DES Simulation Kernel  |  Causal Engine  |  Sandbox     |
+---------------------------------------+---------------------------------------+
                                        | Authoritative State & Projections
                                        v
+-------------------------------------------------------------------------------+
|                      ENTERPRISE KNOWLEDGE FABRIC (D2)                         |
|   PostgreSQL (System of Record)  |  Neo4j (Topology)  |  pgvector (Memory)    |
+-------------------------------------------------------------------------------+
                                        ^
                                        | Ingestion & Schema Contracts
+-------------------------------------------------------------------------------+
|                   ENTERPRISE WORLD FOUNDATION (D1)                            |
|   30 Domains, 96 Tables, 49.6K SKUs, Deterministic DAG, SHA-256 Provenance    |
+-------------------------------------------------------------------------------+
```

### The Foundational Separation of Responsibilities:
* **D1 (World Foundation) asks:** *"What is the enterprise world, its historical facts, and its baseline seed structure?"*
* **D2 (Knowledge Fabric) asks:** *"What does the current enterprise data say across relational records, topology, and vector embeddings?"*
* **Twin (Simulation Substrate) asks:** *"What is the current operational reality, how does physical reality propagate forward over time, and what happens to the enterprise when specific disruptions or interventions occur?"*
* **Agents (Cognitive Reasoners) ask:** *"Given this operational reality and forward projections, what strategic trade-offs exist and what actions should we propose?"*
* **CD2F (Consensus Engine) asks:** *"Which cross-domain proposal maximizes conglomerate utility and reconciles specialist conflicts?"*

---

## 2. Evaluation of Architectural Design Alternatives

During V2 design evaluation, three competing structural paradigms were analyzed:

| Architectural Option | Structural Description | Critical Evaluation & Failure Modes | Architectural Verdict |
| :--- | :--- | :--- | :--- |
| **Alternative 1: Coupling Twin Inside D1 Generation Engine** | The Twin is coupled directly inside D1, running inside the synthetic data generation pipeline. | Conflates static world generation with dynamic operational state. Forces agents to interact with a synthetic generator rather than enterprise data systems. Does not scale to real-world ingested datasets. | **REJECTED** |
| **Alternative 2: Twin as Monolithic Shared Data Gateway** | The Twin acts as a unified data gateway wrapping both D1 generation and D2 databases, routing all queries. | Anti-pattern: turns the Twin into an expensive, monolithic database proxy. Unnecessary overhead for read-only relational queries. Creates a single point of failure and bottleneck for concurrent agent execution. | **REJECTED** |
| **Adopted Architecture: Decoupled Operational State & Simulation Substrate Above D1/D2** | The Twin is an independent cyber-physical state and simulation authority positioned above the data fabric. | Establishes clean separation of concerns. Read-only queries route directly to D2; only scenario mutations, forward propagation, and counterfactual simulations invoke the Twin. Enforces physical invariants without mutating ground truth. | **ACCEPTED & LOCKED** |

---

## 3. The Five Core Pillars of the Digital Twin

The Digital Twin substrate is built upon five foundational pillars, refined to maintain strict architectural boundaries:

```text
+-------------------------------------------------------------------------------+
|                     PILLAR 1: MULTI-LAYER STATE ISOLATION                     |
|   Layer 1: Frozen Ground Truth (SHA-256)                                      |
|   Layer 2: Baseline Day-0 State (PostgreSQL & Immutable Neo4j)                |
|   Layer 3: Ephemeral Scenario Sandboxes (In-Memory / Scenario Delta Schemas)  |
+-------------------------------------------------------------------------------+
                                        |
+-------------------------------------------------------------------------------+
|                     PILLAR 2: PHYSICAL & CAUSAL INVARIANTS                    |
|   Conservation of Mass  |  Lead-Time Physics  |  Asset Capacities  |  Ledger  |
+-------------------------------------------------------------------------------+
                                        |
+-------------------------------------------------------------------------------+
|                  PILLAR 3: DETERMINISTIC FORWARD PROPAGATION                  |
|   Event-Stepped DES Kernel  |  Timeline Queue  |  Causal Network Traversal    |
+-------------------------------------------------------------------------------+
                                        |
+-------------------------------------------------------------------------------+
|                 PILLAR 4: COUNTERFACTUAL BRANCHING ENGINE                     |
|   Branch Scenarios (A vs B vs C)  |  Intervention Sandbox  |  State Diffing   |
+-------------------------------------------------------------------------------+
                                        |
+-------------------------------------------------------------------------------+
|                 PILLAR 5: APPROVED ACTION EXECUTION BOUNDARY                  |
|   Sandbox Actuation (Simulated)  |  CD2F Gating  |  HITL  |  ERP Adapters     |
+-------------------------------------------------------------------------------+
```

### Pillar 1: Multi-Layer State Isolation
The Twin enforces a strict three-layer state boundary (see [ADR ADR 002](file:///d:/projects/SCOF_V1/SCOF/docs/adr/002_tripartite_state_isolation_for_benchmark_integrity.md)):
1. **Layer 1 (Frozen Ground Truth):** Immutable physical data files in `datasets/` verified by SHA-256 digests.
2. **Layer 2 (Baseline Operational State):** Authoritative Day-0 relational state in PostgreSQL and topological projection in Neo4j.
3. **Layer 3 (Scenario Runtime State):** Isolated, ephemeral scenario sandboxes (`scenario_id`, `sim_run_id`). All scenario perturbations, asset downtime injections, and simulated order rerouting execute exclusively within Layer 3. Layer 1 and Layer 2 are never mutated.

### Pillar 2: Physical & Causal Invariants
The Twin enforces hard real-world operational invariants that cannot be violated by agent hallucinations or flawed heuristics:
* **Conservation of Inventory & Mass:** At every facility $f$ and SKU $s$ across time step $t$:
  $$I_{f,s,t} = I_{f,s,t-1} + \sum \text{Receipts}_{f,s,t} - \sum \text{Shipments}_{f,s,t} - \sum \text{Sales}_{f,s,t} - \sum \text{Spoilage}_{f,s,t}$$
  Inventory cannot become negative. Damaged or spoiled goods cannot satisfy customer orders.
* **Lead-Time Physical Causality:** Goods in transit cannot arrive before transit time expires ($t_{\text{arrival}} \ge t_{\text{dispatch}} + \tau_{\text{lane}}$). An order cannot be shipped if inventory has not been received or cross-docked.
* **Asset & Capacity Constraints:** Facility throughput cannot exceed maximum operational capacity:
  $$\sum_s \text{Volume}_{f,s,t} \le \text{Capacity}_{\text{max}}(f)$$
  Cold-chain chiller breakdown ($T > 4^\circ\text{C}$) triggers deterministic spoilage calculation for temperature-sensitive merchandise.
* **Double-Entry Financial Ledger Invariants:** Any simulated inventory purchase, write-off, or expedited freight charge must balance across general ledger debits and credits:
  $$\Delta \text{Assets} = \Delta \text{Liabilities} + \Delta \text{Equity}$$

### Pillar 3: Deterministic Forward Propagation
When a disruption is injected (e.g., Tier-1 supplier failure, port strike, or refrigeration chiller outage), the Twin's **Causal Cascade Engine** deterministically traces and projects the downstream impact across the multi-tier supply chain:
1. Upstream delay injected into Purchase Orders $\text{PO}_{1..k}$.
2. Lead-time delta propagated to Distribution Center receiving docks.
3. Safety stock buffer depleted over time horizon $t \in [t_0, t_0 + \Delta t]$.
4. Secondary store stockouts projected based on weekly demand distributions.
5. Service-level degradation (OTIF drop) and lost revenue quantified.
6. Evidence pack assembled and timestamped for agent consumption.

### Pillar 4: Counterfactual Branching Engine
Agents exploring candidate interventions can fork an active scenario into isolated counterfactual branches:
* **Baseline Branch:** Disruption continues without intervention (Run 0: Unmitigated decay).
* **Branch A (Expedited Air Freight):** Carrier reallocated to air corridor; transit time reduced from 5 days to 1 day; freight cost increased by $3.2\times$.
* **Branch B (Alternate Supplier Sourcing):** Secondary vendor engaged; unit cost $+12\%$; lead time 3 days; minimum order quantity enforced.
* **Branch C (Cross-Facility Rebalancing):** Inter-DC transfer executed; fleet assets reallocated; regional DC stock balanced.
The Twin executes each branch in an isolated sandbox, computes the state delta, and outputs a comparative delta matrix for CD2F deliberation.

### Pillar 5: Approved Action Execution Boundary
A critical architectural boundary: **The Twin executes simulated interventions inside its Layer 3 sandbox. It does NOT directly execute real-world ERP actions.**
* When an agent proposes an action, the Twin evaluates its counterfactual impact.
* When the CD2F consensus engine reaches approved consensus ($WCS \ge 0.70$), the approved action is committed to the scenario runtime state.
* If the system operates in real-world deployment, physical ERP actuation (placing real POs, reallocating real trucks) requires Human-in-the-Loop (HITL) authorization and execution via external ERP Adapters. The Twin never possesses unconstrained external write access.

---

## 4. Subsystem Architecture & Internal Components

The Digital Twin Service is organized into six cohesive internal engines:

```text
+-------------------------------------------------------------------------------+
|                             TWIN SERVICE CORE                                 |
|                                                                               |
|  +---------------------------+       +-------------------------------------+  |
|  | Scenario Context Manager  |       | Timeline & Event Queue (DES Kernel) |  |
|  | - Scenario lifecycle      |       | - Deterministic event scheduling    |  |
|  | - Fork & branch overlays  |       | - Event-stepped clock advance       |  |
|  | - Layer 3 sandbox state   |       | - Causal event ordering             |  |
|  +-------------+-------------+       +------------------+------------------+  |
|                |                                        |                     |
|                +-------------------+--------------------+                     |
|                                    |                                          |
|                                    v                                          |
|  +---------------------------------+---------------------------------------+  |
|  | Physical Rules & Invariants Engine                                      |  |
|  | - Conservation of inventory & mass                                      |  |
|  | - Lead-time causality & transportation physics                         |  |
|  | - Facility capacity & cold-chain thermal thresholds                     |  |
|  | - Double-entry financial ledger validation                             |  |
|  +---------------------------------+---------------------------------------+  |
|                                    |                                          |
|                +-------------------+--------------------+                     |
|                |                                        |                     |
|                v                                        v                     |
|  +-------------+-------------+       +------------------+------------------+  |
|  | Causal Cascade Engine     |       | Counterfactual Sandbox Engine       |  |
|  | - Upstream-downstream     |       | - Branch diffing & delta metrics    |  |
|  |   dependency propagation  |       | - Candidate intervention evaluation |  |
|  | - OTIF & stockout compute |       | - Scenario comparison matrices      |  |
|  +---------------------------+       +-------------------------------------+  |
|                                                                               |
|  +-------------------------------------------------------------------------+  |
|  | Evidence Pack & Provenance Generator                                    |  |
|  | - Cryptographic SHA-256 state hashing                                  |  |
|  | - Structured Claim evidence binding                                     |  |
|  | - Verifiable audit trail for D07 observability                          |  |
|  +-------------------------------------------------------------------------+  |
+-------------------------------------------------------------------------------+
```

---

## 5. Event-Stepped Discrete-Event Simulation (DES) Kernel

Rather than maintaining an expensive, continuous real-time tick daemon (which introduces synchronization drift and idle CPU consumption), the Twin operates an **Event-Stepped Discrete-Event Simulation (DES) Kernel**:

1. **Discrete Simulation Clock ($t_{\text{sim}}$):** Time advances deterministically from the current event timestamp to the exact timestamp of the next scheduled event in the priority event queue.
2. **Deterministic Event Queue:** Events are ordered by `(event_timestamp, event_priority, event_id)`.
3. **Execution Steps:**
   - Pop next event $E_k$ at time $t_k$.
   - Advance $t_{\text{sim}} \leftarrow t_k$.
   - Evaluate event pre-conditions against current Layer 3 scenario state.
   - Execute physical state transition function:
     $$S_{t_k} = f(S_{t_{k-1}}, E_k)$$
   - Enforce physical invariants; revert transaction if any invariant is violated.
   - Schedule resultant downstream causal events $E_{k+1..m}$ into the queue.
   - Record state delta in scenario transaction log.

---

## 6. Formal Digital Twin API Contracts

The Twin exposes a bounded, cohesive API surface rather than hundreds of manual query endpoints:

### 6.1 Scenario Lifecycle Management
```python
def create_scenario(
    baseline_id: str,
    scenario_type: str,
    parameters: dict[str, Any],
    seed: int = 42
) -> ScenarioContext:
    """Creates an isolated Layer 3 execution sandbox with clean Day-0 baseline reference."""

def fork_scenario(
    parent_scenario_id: str,
    branch_name: str
) -> ScenarioContext:
    """Forks an active scenario into an isolated counterfactual sandbox branch."""

def close_scenario(scenario_id: str) -> bool:
    """Tears down ephemeral Layer 3 sandbox state and archives execution run logs."""
```

### 6.2 Simulation & Stepping
```python
def simulate(
    scenario_id: str,
    horizon_steps: int,
    disruptions: list[DisruptionEvent]
) -> SimulationResult:
    """Executes deterministic forward propagation across the specified time horizon."""

def advance(
    scenario_id: str,
    step_delta: int = 1
) -> StepResult:
    """Advances the discrete-event simulation clock by step_delta events."""

def evaluate_counterfactual(
    scenario_id: str,
    interventions: list[InterventionAction]
) -> CounterfactualDelta:
    """Applies candidate interventions in a sandbox branch and computes state deltas."""
```

### 6.3 Operational State & Impact Queries
```python
def get_operational_state(
    scenario_id: str,
    entity_type: str,
    entity_id: str
) -> EntityOperationalState:
    """Retrieves authoritative runtime state for an entity within the scenario sandbox."""

def get_impact(
    scenario_id: str,
    dimension: str  # 'inventory', 'financial', 'service_level', 'transport'
) -> ImpactAssessment:
    """Quantifies aggregated disruption impact across specified operational dimension."""
```

### 6.4 Intervention & Evidence
```python
def apply_scenario_action(
    scenario_id: str,
    action: ApprovedAction
) -> ActionExecutionReceipt:
    """Applies an arbitrated, CD2F-approved intervention to the scenario runtime state."""

def get_evidence_pack(
    scenario_id: str,
    claim_id: str
) -> DeterministicEvidencePack:
    """Generates a cryptographically verified evidence pack supporting an agent claim."""
```

---

## 7. Six-Phase Implementation Roadmap (Phases T1 to T6)

The development of the Digital Twin Service follows a phased, verified roadmap:

| Phase | Milestone Name | Key Capabilities Delivered | Verification Gate |
| :--- | :--- | :--- | :--- |
| **Phase T1** | **Scenario State Foundation** | `ScenarioContext`, Layer 1-3 state isolation, SHA-256 provenance hashing, deterministic scenario initialization. | 0 mutation of Layer 1/2 files; reproducible scenario context creation. |
| **Phase T2** | **Deterministic Simulation Kernel** | Event-stepped DES priority queue, state transition dispatcher, discrete clock advancement. | Replay of 100 identical event queues yields identical state digests. |
| **Phase T3** | **Physical & Causal Models** | Conservation of mass, lead-time causality, warehouse/chiller capacity rules, double-entry financial ledger checks. | Unit tests catch negative inventory, instant travel, and unbalanced ledger attempts. |
| **Phase T4** | **Counterfactual Engine** | Scenario forking (`fork_scenario`), parallel branch isolation, state diffing, comparative delta matrices. | Side-by-side execution of 3 candidate branches without cross-branch state leakage. |
| **Phase T5** | **Cognitive Integration** | Integration with Cognitive Query Router, Dynamic Capability Registry, LangGraph claim synthesis, and CD2F action application. | End-to-end deliberation cycle from disruption injection to consensus execution. |
| **Phase T6** | **Benchmark & Evaluation** | Reproducible benchmark harness for D10, empirical validation under 100+ disruption runs, SLA and latency profiling. | Sub-second simulation execution SLA ($< 500\text{ ms}$) validated on benchmark suite. |

---

## 8. Explicitly Rejected Architectural Anti-Patterns

To prevent scope creep and maintain architectural purity, the following patterns are **explicitly rejected**:

1. **Continuous Real-Time Tick Daemon:** Supply chain disruptions are discrete events, not millisecond physical control loops. Continuous ticking wastes CPU and introduces clock drift.
2. **Direct Graph Mutations in Production Neo4j:** Runtime scenario perturbations must never write dirty edges or properties into the 3.73M-node Neo4j graph. Scenario topology perturbations are stored as in-memory overlays.
3. **Twin-as-Omnipresent-Orchestrator:** The Twin does not coordinate agent communications, manage agent prompts, or arbitrate claims. LangGraph coordinates workflows; CD2F arbitrates decisions.
4. **Giant Manually Enumerated Tool API:** Building individual `get_X()`, `get_Y()` tools for every enterprise query creates brittle coupling. Queries are resolved dynamically via the Capability Registry and Tri-Zone Router.
5. **Direct Real-World ERP Actuation:** The Twin sandbox modifies scenario state only. External ERP write-back is governed strictly by CD2F consensus, HITL authorization, and isolated ERP adapters.
