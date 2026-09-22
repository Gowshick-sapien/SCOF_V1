# ADR 019: Operational Digital Twin Substrate Layer Above D1 and D2

* **Status**: Accepted

---

## 1. Context and Problem Statement

With the transition from a toy synthetic generator (V1) to the 30-domain, 96-table, 49,616-SKU SCOF Retail Enterprise Reference World (V2), the role and placement of the Digital Twin Service required formal re-anchoring.

In earlier conceptualizations, the boundary between synthetic data generation (D1), data fabric storage (D2), and dynamic operational simulation was blurred. An architecture was needed that allows cognitive agents to reason over dynamic scenarios, evaluate counterfactual interventions, and enforce physical invariants without polluting immutable enterprise master data or turning the simulation engine into an expensive bottleneck.

---

## 2. Decision Drivers

* **Separation of Concerns:** Clear demarcation between historical data generation/seed (D1), authoritative data fabric storage (D2), and dynamic simulation state.
* **Latency & Performance:** Preventing non-simulation read queries from suffering simulation engine overhead.
* **Data Integrity:** Absolute guarantee that hypothetical scenario simulations never mutate frozen ground truth or Day-0 baseline records.
* **Counterfactual Agility:** Enabling fast, isolated scenario branching to compare candidate agent interventions side by side.

---

## 3. Considered Options

* **Alternative 1 — Twin Coupled Inside D1 Generation Engine:** Embed the Twin directly within Deliverable D1, making the synthetic data generator double as the operational simulation engine.
* **Alternative 2 — Twin as D1/D2 Shared Facade Gateway:** Position the Twin as a mandatory facade and unified gateway wrapping all D1 generation and D2 database queries.
* **Alternative 3 — Operational Digital Twin Substrate Above D1 and D2:** Establish the Twin as an authoritative, independent cyber-physical state and simulation substrate residing above D1 and D2. D2 provides authoritative relational and graph facts; the Twin manages isolated scenario states, enforces physical invariants, executes forward propagation, and evaluates counterfactual branches.

---

## 4. Decision Outcome

**Chosen Option**: **Operational Digital Twin Substrate Above D1 and D2**

### Rationale:
The adopted decoupled architecture cleanly separates enterprise data custody from dynamic operational reasoning:
1. **D1** owns the enterprise world definition, historical facts, and deterministic generation provenance.
2. **D2** owns the enterprise data fabric (PostgreSQL as system of record, Neo4j as materialized topology, pgvector as semantic memory).
3. **The Twin** turns enterprise data into an operationally meaningful, scenario-aware cyber-physical world. It executes forward propagation along event timelines, enforces physical invariants (conservation of mass, capacity, lead-time causality), and forks isolated counterfactual branches.
4. Agents query D2 directly for read-only enterprise facts (Class A), invoking the Twin exclusively when scenario forward projection or counterfactual intervention analysis is required (Class C).

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Read-only relational and graph queries bypass the simulation engine, achieving $< 50\text{ ms}$ response times.
* The Twin is freed from routine database proxy duties, focusing compute resources on discrete-event forward propagation.
* Layer 1 (Frozen Ground Truth) and Layer 2 (Day-0 Baseline) are structurally protected from scenario state mutation.
* Supports clean counterfactual forking (`fork_scenario`), enabling side-by-side comparative trade-off analysis during CD²F arbitration.

### Negative Consequences / Trade-offs:
* Requires maintaining explicit state synchronization between D2 Day-0 snapshots and the Twin's Layer 3 sandbox overlays.
* Calling agents must distinguish between querying historical/current facts (D2) versus forward projections (Twin), managed via the Cognitive Query Router.

---

## 6. Implementation & Compliance Notes

* Implemented in [`src/simulation/twin_service.py`](file:///d:/projects/SCOF_V1/SCOF/src/simulation/twin_service.py) and detailed in [Digital Twin Service Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/01_digital_twin_service_architecture.md).
* Verified by automated test suite in [`tests/test_twin_service.py`](file:///d:/projects/SCOF_V1/SCOF/tests/test_twin_service.py).
* State isolation verified by SHA-256 digests in `run_manifest.json`.

---

## 7. Related Decisions & Artifacts

* [ADR 015: Tripartite State Isolation for Benchmark Integrity](file:///d:/projects/SCOF_V1/SCOF/docs/adr/015_tripartite_state_isolation_for_benchmark_integrity.md)
* [ADR 018: Cognitive Twin Service Substrate](file:///d:/projects/SCOF_V1/SCOF/docs/adr/018_cognitive_twin_service_substrate.md)
* [ADR 020: Tri-Zone Query Routing and Deeper Resolver](file:///d:/projects/SCOF_V1/SCOF/docs/adr/020_tri_zone_query_routing_and_deeper_resolver.md)
* [ADR 023: Event-Stepped Simulation Kernel Over Fixed-Tick Daemon](file:///d:/projects/SCOF_V1/SCOF/docs/adr/023_event_stepped_simulation_kernel_over_fixed_tick_daemon.md)
* [Digital Twin Service Architecture Specification](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/01_digital_twin_service_architecture.md)
