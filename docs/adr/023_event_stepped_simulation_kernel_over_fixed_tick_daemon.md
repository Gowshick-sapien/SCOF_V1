# ADR 023: Event-Stepped Simulation Kernel Over Fixed-Tick Daemon

* **Status**: Accepted

---

## 1. Context and Problem Statement

A core design requirement for the Digital Twin Service is simulating the temporal evolution of the supply chain when disruptions occur (e.g., supplier shipment delay cascading into warehouse inventory depletion, stockouts, and revenue loss).

Two competing temporal architectures were proposed:
1. **Continuous Fixed-Tick Daemon:** Running a continuous real-time background loop ticking at fixed intervals ($\Delta t = 1\text{ second}$ or $1\text{ hour}$), calculating delta equations at every tick.
2. **Event-Stepped DES Kernel:** Advancing the simulation clock directly to the timestamp of the next discrete event in an event queue.

The decision impacts compute efficiency, deterministic reproducibility, and integration latency.

---

## 2. Decision Drivers

* **Deterministic Reproducibility:** Replaying identical disruption vectors with identical seeds must produce bit-for-bit identical state histories.
* **Compute Efficiency:** Avoiding idle CPU cycles during periods where no physical state transitions occur.
* **Interactive Query Latency:** Ability to fast-forward a multi-week simulation horizon in $< 500\text{ ms}$ during agent what-if deliberation.
* **Scientific Validity:** Accurate modeling of discrete enterprise operations (purchase order placements, vessel arrivals, goods receipts, shift handovers).

---

## 3. Considered Options

* **Option 1 — Continuous Fixed-Tick Daemon:** Maintain an active background simulation service ticking at a fixed physical frequency, updating state incrementally.
* **Option 2 — Static Analytical Projection:** Reject simulation entirely in favor of static algebraic equations (e.g., calculating expected stockout day using average daily sales).
* **Option 3 — Event-Stepped Discrete-Event Simulation (DES) Kernel:** Model the world as an event-driven state machine. A priority event queue holds scheduled events; the simulation engine advances the simulation clock ($t_{\text{sim}}$) deterministically to the next event, executes the state transition, checks physical invariants, and schedules downstream events.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Event-Stepped Discrete-Event Simulation (DES) Kernel**

### Rationale:
1. **Supply Chain Discreteness:** Enterprise supply chains operate through discrete events (dispatching a truck, issuing an invoice, docking a container), not continuous fluid dynamics.
2. **Instant Fast-Forwarding:** An event-stepped engine can simulate 30 days of forward operational cascade across 21 facilities in $< 200\text{ ms}$, enabling real-time agent what-if evaluation. A fixed-tick daemon would require seconds or minutes to advance.
3. **100% Determinism:** Event execution order is strictly governed by `(timestamp, priority, event_id)`, eliminating timing races and clock synchronization drift.
4. **Zero Idle Overhead:** Consumes zero CPU when no scenarios are actively simulating.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Extremely fast execution suitable for synchronous multi-agent deliberation.
* Bit-for-bit reproducible results across benchmark and evaluation runs in D10.
* Clean integration with the Priority Queue and Bounded Worker Pool.
* Enables granular event-by-event causal explanation in D07 observability traces.

### Negative Consequences / Trade-offs:
* Continuous processes (e.g., temperature decay inside a damaged refrigerated truck) must be discretized into threshold-crossing events.
* Mitigated by scheduling discrete threshold events (e.g., scheduling a `ThermalSpoilageEvent` at calculated time $t_{\text{spoil}} = t_0 + \Delta t$).

---

## 6. Implementation & Compliance Notes

* Implemented in the simulation stepping functions in [`src/simulation/twin_service.py`](file:///d:/projects/SCOF_V1/SCOF/src/simulation/twin_service.py).
* Detailed in [Digital Twin Service Architecture Specification](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/01_digital_twin_service_architecture.md).
* Verified by deterministic replay unit tests in [`tests/test_twin_service.py`](file:///d:/projects/SCOF_V1/SCOF/tests/test_twin_service.py).

---

## 7. Related Decisions & Artifacts

* [ADR 018: Cognitive Twin Service Substrate](file:///d:/projects/SCOF_V1/SCOF/docs/adr/018_cognitive_twin_service_substrate.md)
* [ADR 019: Operational Digital Twin Substrate Layer](file:///d:/projects/SCOF_V1/SCOF/docs/adr/019_operational_digital_twin_substrate_layer.md)
* [ADR 022: Minimalist Bounded Worker Concurrency](file:///d:/projects/SCOF_V1/SCOF/docs/adr/022_minimalist_bounded_worker_concurrency.md)
* [Digital Twin Service Architecture Specification](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/01_digital_twin_service_architecture.md)
