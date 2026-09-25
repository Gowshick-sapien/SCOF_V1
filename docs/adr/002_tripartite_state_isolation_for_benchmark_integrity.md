ADR 002: Tripartite State Isolation for Benchmark and Simulation Integrity

* **Status**: Accepted

---


## 1. Context and Problem Statement

In supply chain simulation and evaluation, counterfactual experiments perturb operational states (e.g., deducting inventory due to spoilage, modifying purchase order delivery dates, or closing transport lanes). 

If these mutations occur directly against the shared operational database, subsequent simulations or benchmarks will inherit contaminated states. Specifically, in Deliverable D10 (Integration & Empirical Evaluation), if Scenario A (Supplier Delay) permanently alters warehouse stock, Scenario B (Transit Route Closure) running immediately afterward will evaluate against degraded inventory, invalidating scientific benchmarks and preventing exact reproducibility.

---

## 2. Decision Drivers

* **Zero Cross-Scenario Contamination:** Ensure that any simulation run executes against a guaranteed clean baseline.
* **Exact Reproducibility:** Ensure any scenario run can be deterministically replayed with identical outputs given the same seed and parameters.
* **Scientific Validity for D10:** Protect empirical research questions (RQ1-RQ4) from state pollution.
* **Ground-Truth Immutability:** Guarantee that the source dataset is never modified by runtime execution.

---

## 3. Considered Options

* **Option 1 (In-Place Mutation with Database Teardown):** Mutate tables directly in PostgreSQL and drop/re-seed the entire database between scenario runs.
* **Option 2 (Application-Level Rollback Scripts):** Run compensation scripts (e.g., "re-add 280 units of milk") after each run.
* **Option 3 (Tripartite State Architecture with Copy-on-Write Snapshots):** Establish a strict three-layer state model separating Frozen Ground Truth, Baseline Operational State, and Ephemeral Scenario Runtime State.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3: Tripartite State Architecture with Copy-on-Write Snapshots**

### Architecture:

```
LAYER 1: FROZEN GROUND TRUTH (Immutable)
├── Canonical Parquet files & CSV master tables
└── Verified via SHA-256 hashes in run_manifest.json
         │
         ▼
LAYER 2: BASELINE OPERATIONAL STATE (Read-Only Operational Reference)
├── Populated to clean Day-0 baseline state
└── Serves as the immutable reference point for baseline queries
         │
         ├───► Scenario Run A (sim_run_id: SIM-01) ──► Ephemeral Delta Table
         ├───► Scenario Run B (sim_run_id: SIM-02) ──► Ephemeral Delta Table
         └───► Scenario Run C (sim_run_id: SIM-03) ──► Ephemeral Delta Table
```

### Rationale:
1. **Layer 1 (Frozen Ground Truth):** The physical files in `datasets/` are strictly read-only.
2. **Layer 2 (Baseline Operational State):** The relational database and Neo4j graph initialized to Day 0. It serves as the baseline reference point.
3. **Layer 3 (Scenario Runtime State):** When a scenario is triggered, a dedicated `scenario_id` and `sim_run_id` are created. Mutations (e.g., spoilage deductions, expedited shipments) are recorded either in run-tagged delta records or ephemeral memory stores. Once the simulation run completes, the runtime state is archived, leaving Layer 2 completely untouched.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Completely guarantees zero cross-scenario contamination across evaluation runs in D10.
* Replayability is guaranteed: any run can be re-executed from clean baseline state.
* Eliminates the heavy operational overhead of dropping and re-seeding 585 MB databases between test runs.

### Negative Consequences / Trade-offs:
* Query logic must account for active scenario run IDs when checking operational deltas.
* Requires lifecycle tracking via `scenario` and `simulation_run` tables (already implemented in `twin_service.py`).

---

## 6. Implementation & Compliance Notes

* **Lifecycle Management:** Implemented in `services/twin_service.py` via `create_scenario()` and `start_simulation_run()`.
* **State Isolation Tables:** Managed in SQLite / PostgreSQL schemas (`scenario`, `simulation_run`, `validation_result`).
* **Evaluation Enforcement:** Enforced in D10 benchmark harnesses (`services/evaluation/`).
