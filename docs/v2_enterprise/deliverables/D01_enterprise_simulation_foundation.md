# Deliverable D01 (V2): Enterprise World & Simulation Foundation

## 1. Overview & Objectives

Deliverable D01 in SCOF V2 elevates the simulation foundation from a toy generator creating 5 suppliers and 2 warehouses into the **Enterprise World & Simulation Foundation** governing the 30-domain, 49,616-SKU retail ecosystem.

Its primary responsibilities are:
1. **Authoritative Dataset Provenance:** Immutable tracking of the 96 relational tables via SHA-256 cryptographic hashes and `run_manifest.json`.
2. **Simulation Lifecycle Engine:** Managing stateful execution contexts (`scenario`, `simulation_run`, and `validation_result`).
3. **Deterministic Disruption Injection:** Supporting multi-dimensional disruptions (supplier lead time blowouts, asset breakdowns, transport corridor closures, and festival demand shocks).
4. **Reproducibility Guarantee:** Ensuring any scenario can be deterministically replayed using `scenario_id`, `dataset_version`, `random_seed`, and initial state parameters.

---

## 2. Technical Architecture & Invariants

### 2.1 The Tripartite State Architecture (ADR 015)
D01 strictly enforces the three-layer state model:
* **Layer 1 (Frozen Ground Truth):** The physical datasets in `datasets/` (`scof_relational.db`, Parquet files, CSV masters) are immutable.
* **Layer 2 (Baseline Operational State):** Clean Day-0 operational reference state.
* **Layer 3 (Scenario Runtime State):** Ephemeral copy-on-write execution context tagged with `sim_run_id`.

### 2.2 Core Invariant
No simulation run may mutate Layer 1 or Layer 2. All perturbations occur in isolated Layer 3 contexts, guaranteeing that subsequent simulation or evaluation runs in D10 are never contaminated.

---

## 3. Disruption Injection Specifications

| Disruption Type | Target Entity | Injected Parameters | Physical Propagation |
| :--- | :--- | :--- | :--- |
| **Supplier Delay** | Supplier Profile (`SUP-xxxx`) | Lead time delta ($+\Delta t$ days), affected POs | Delays goods receipts $\to$ warehouse buffer depletion $\to$ store stockouts |
| **Asset Downtime** | Physical Asset (`AST-xxxx`) | Downtime hours ($t_{down}$), capacity drop % | Chiller failure $\to$ perishable SKU spoilage $\to$ inventory write-off $\to$ lost sales |
| **Route Closure** | Transport Lane (`TL-xxxx`) | Transit delay multiplier ($k_{delay}$), freight cost surge | Carrier delay $\to$ shipment backlog $\to$ alternate corridor rerouting |
| **Demand Shock** | Event + Zone (`EV-xxxx`, Zone) | Lift multiplier ($k_{lift}$), duration weeks | Customer transaction surge $\to$ shelf-facing depletion $\to$ emergency replenishment |

---

## 4. Acceptance Criteria & Verification Evidence

1. **Integrity Gate:** All 96 tables and Parquet files verified with 0 schema violations.
2. **Provenance Gate:** `generation_manifest.json` and `run_manifest.json` match file hashes.
3. **Simulation Lifecycle Gate:** `twin_service.py` successfully creates scenarios, launches runs, records validation results, and marks runs completed.
4. **Reproducibility Gate:** Re-running the disruption simulation with identical parameters produces identical capacity drops and financial exposure numbers.
