# Deliverable D01 (V2): Enterprise World & Simulation Foundation

## 1. Overview & Objectives

Deliverable D01 in SCOF V2 elevates the simulation foundation from a toy generator creating 5 suppliers and 2 warehouses into the **Enterprise World & Simulation Foundation** governing the 30-domain, 49,616-SKU retail ecosystem.

Its primary responsibilities are:
1. **Authoritative Dataset Provenance:** Immutable tracking of the 96 relational tables via SHA-256 cryptographic hashes and `run_manifest.json`.
2. **Operational Digital Twin Substrate:** Serving as the authoritative cyber-physical state and discrete-event simulation engine ([ADR 019](file:///d:/projects/SCOF_V1/SCOF/docs/adr/019_operational_digital_twin_substrate_layer.md)).
3. **Event-Stepped DES Simulation Kernel:** Deterministic timeline advancement advancing state from event to event without idle CPU ticking ([ADR 023](file:///d:/projects/SCOF_V1/SCOF/docs/adr/023_event_stepped_simulation_kernel_over_fixed_tick_daemon.md)).
4. **Physical & Causal Invariant Enforcement:** Non-negotiable physical laws (conservation of mass/inventory, lead-time causality, asset capacity limits, double-entry financial ledger validation).
5. **Counterfactual Scenario Branching:** Isolated Layer 3 sandboxes enabling agents and CD²F to evaluate candidate operational interventions side by side.
6. **Minimalist Concurrency Control:** 4-tier Priority Queue (P0-P3) backed by a Bounded Worker Pool with FIFO dispatching ([ADR 022](file:///d:/projects/SCOF_V1/SCOF/docs/adr/022_minimalist_bounded_worker_concurrency.md)).

---

## 2. Technical Architecture & State Isolation

### 2.1 The Tripartite State Architecture (ADR 015)
D01 strictly enforces the three-layer state model:
* **Layer 1 (Frozen Ground Truth):** The physical datasets in [`datasets/`](file:///d:/projects/SCOF_V1/SCOF/datasets/) (`scof_relational.db`, Parquet files, CSV masters) are immutable and sealed by cryptographic SHA-256 hashes.
* **Layer 2 (Baseline Operational State):** Clean Day-0 operational reference state residing in PostgreSQL and materialized read-only Neo4j graph.
* **Layer 3 (Scenario Runtime State):** Ephemeral copy-on-write execution context tagged with `scenario_id` and `sim_run_id`. All perturbations and counterfactual branches exist exclusively within Layer 3.

### 2.2 Core Invariant
No simulation run may mutate Layer 1 or Layer 2. All perturbations occur in isolated Layer 3 contexts, guaranteeing that subsequent simulation or evaluation runs in D10 are never contaminated.

---

## 3. Physical Invariants & Causal Propagation

The simulation kernel deterministically enforces four core physical invariants:

1. **Conservation of Inventory & Mass:**
   $$I_{f,s,t} = I_{f,s,t-1} + \text{Receipts}_{f,s,t} - \text{Shipments}_{f,s,t} - \text{Sales}_{f,s,t} - \text{Spoilage}_{f,s,t}$$
   Inventory quantities cannot become negative. Damaged, spoiled, or expired SKUs are immediately written off and cannot satisfy customer demand.
2. **Lead-Time Physical Causality:**
   $$t_{\text{arrival}} \ge t_{\text{dispatch}} + \tau_{\text{lane}}$$
   Goods cannot arrive before transit time elapses. Shipments cannot be dispatched if stock has not been received or cross-docked.
3. **Asset & Capacity Constraints:**
   $$\sum_s \text{Volume}_{f,s,t} \le \text{Capacity}_{\text{max}}(f)$$
   Warehouse throughput and shelf-facing capacity are hard upper bounds. Cold-chain thermal failure ($T > 4^\circ\text{C}$) triggers deterministic spoilage functions.
4. **Double-Entry Financial Ledger Invariants:**
   Every simulated transaction, write-off, or expedited freight fee must balance across assets, liabilities, and equity in the simulated general ledger.

---

## 4. Disruption Injection Specifications

| Disruption Type | Target Entity | Injected Parameters | Physical Propagation |
| :--- | :--- | :--- | :--- |
| **Supplier Delay** | Supplier Profile (`SUP-xxxx`) | Lead time delta ($+\Delta t$ days), affected POs | Delays goods receipts $\to$ warehouse buffer depletion $\to$ store stockouts |
| **Asset Downtime** | Physical Asset (`AST-xxxx`) | Downtime hours ($t_{down}$), capacity drop % | Chiller failure $\to$ perishable SKU spoilage $\to$ inventory write-off $\to$ lost sales |
| **Route Closure** | Transport Lane (`TL-xxxx`) | Transit delay multiplier ($k_{delay}$), freight cost surge | Carrier delay $\to$ shipment backlog $\to$ alternate corridor rerouting |
| **Demand Shock** | Event + Zone (`EV-xxxx`, Zone) | Lift multiplier ($k_{lift}$), duration weeks | Customer transaction surge $\to$ shelf-facing depletion $\to$ emergency replenishment |

---

## 5. Six-Phase Implementation Roadmap (T1 to T6)

Development follows a verified six-phase roadmap:
* **Phase T1 — Scenario State Foundation:** `ScenarioContext` lifecycle, Layer 1-3 isolation, SHA-256 state hashing, deterministic scenario creation.
* **Phase T2 — Deterministic Simulation Kernel:** Event-stepped DES priority queue, state transition dispatcher, discrete clock advancement.
* **Phase T3 — Physical & Causal Models:** Conservation of mass, lead-time causality, capacity constraints, double-entry financial checks.
* **Phase T4 — Counterfactual Engine:** Scenario forking (`fork_scenario`), parallel branch isolation, state diffing, comparative delta matrices.
* **Phase T5 — Cognitive Integration:** Integration with Cognitive Query Router, Dynamic Capability Registry, and LangGraph/CD²F contracts.
* **Phase T6 — Benchmark & Evaluation:** Reproducible benchmark harness for D10, empirical validation under 100+ disruption runs, SLA and latency profiling.

---

## 6. Formal Contracts & Verification Evidence

* **API Specification:** [`twin_service_api_spec.md`](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/contracts/twin_service_api_spec.md)
* **Architecture Specification:** [Digital Twin Service Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/01_digital_twin_service_architecture.md)
* **Unit Test Suite:** [`tests/test_twin_service.py`](file:///d:/projects/SCOF_V1/SCOF/tests/test_twin_service.py) (5/5 unit tests verifying lineage, demand shock, asset disruption, 3-way match, and financial ledger).
* **Integrity Gate:** All 96 tables and Parquet files verified with 0 schema violations.
* **Provenance Gate:** `generation_manifest.json` and `run_manifest.json` match file hashes.
