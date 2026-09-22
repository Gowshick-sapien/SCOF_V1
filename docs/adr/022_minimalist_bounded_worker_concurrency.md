# ADR 022: Minimalist Bounded Worker Concurrency Model

* **Status**: Accepted

---

## 1. Context and Problem Statement

When multiple specialist agents deliberate simultaneously, they issue concurrent simulation requests to the Digital Twin Service (e.g., Inventory simulating safety stock depletion while Transportation simulates an expedited corridor).

Two extreme failure modes were evaluated:
1. **Unconstrained Spawning:** Spawning unlimited asynchronous worker threads or coroutines, causing connection pool exhaustion, high memory contention, and CPU thrashing.
2. **Over-Engineered Scheduling:** Building a complex distributed scheduler featuring dynamic priority scoring, aging decay curves, fair-share deficit round-robin, and admission control quotas.

The architectural challenge was to establish a concurrency model that guarantees resource containment and deterministic latency without turning task scheduling into a fragile research project.

---

## 2. Decision Drivers

* **Predictable Execution Latency:** Bounded queue wait times and hard execution timeout budgets.
* **Resource Containment:** Preventing runaway simulation tasks from starving memory or database connection pools.
* **Architectural Minimalism:** Rejecting layered complexity in favor of clean, proven engineering primitives.
* **Non-Blocking Isolation:** Ensuring concurrent workers modifying different scenario branches do not lock each other or block baseline reads.

---

## 3. Considered Options

* **Option 1 — Unconstrained Async Spawning:** Spin up a new worker coroutine for every incoming query without limits.
* **Option 2 — Dynamic Fair-Share Scheduler:** Implement dynamic aging, priority score decay formulas, per-agent quotas, and preemption controllers.
* **Option 3 — Minimalist 4-Tier Priority Queue with Bounded Worker Pool:** Enforce a fixed 4-tier Priority Queue (P0 System Emergency, P1 CD²F Consensus, P2 Agent Deliberation, P3 Background Analytics) backed by a fixed-capacity Bounded Worker Pool ($W = 4..8$ workers) with FIFO dispatching per tier and in-memory branch overlays.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Minimalist 4-Tier Priority Queue with Bounded Worker Pool**

### Rationale:
1. **Proven Simplicity:** The 4-tier priority queue maps directly to enterprise operational realities without arbitrary mathematical tuning.
2. **Strict Resource Bounds:** The bounded worker pool guarantees that no more than $W$ simulation kernels execute simultaneously, protecting system memory and database connections.
3. **Deterministic FIFO Fairness:** Within any priority level, tasks are dispatched in strict arrival order, eliminating starvation within a class.
4. **Copy-on-Write Concurrency:** Workers read immutable Day-0 baselines without locks; branch mutations occur in isolated in-memory overlays.
5. **Research Definement:** Complex scheduling ideas (aging formulas, preemption) are formally documented as future research frontiers rather than blocking current implementation.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Zero risk of connection pool exhaustion or CPU starvation.
* Implementation requires $< 300$ lines of clean, testable Python code.
* Highly predictable sub-second SLA compliance ($< 500\text{ ms}$).
* Clean separation of concerns between queuing, dispatching, and simulation.

### Negative Consequences / Trade-offs:
* Under sustained, extreme P1 consensus load, lower-tier P2 agent tasks may experience queue queuing delays.
* Mitigated by short simulation execution durations ($< 150\text{ ms}$) and strict execution timeout budgets ($1,000\text{ ms}$).

---

## 6. Implementation & Compliance Notes

* Architectural specification in [Minimalist Concurrency & Worker Pool Architecture](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/04_minimalist_concurrency_and_worker_pool.md).
* Integrated into the simulation kernel in Deliverable [D01](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D01_enterprise_simulation_foundation.md).
* Concurrency stress-tested under 50 simultaneous agent requests in Deliverable [D10](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/deliverables/D10_benchmarking_evaluation_v2.md).

---

## 7. Related Decisions & Artifacts

* [ADR 012: Containerized Polyglot Microservices](file:///d:/projects/SCOF_V1/SCOF/docs/adr/012_containerized_polyglot_microservices.md)
* [ADR 018: Cognitive Twin Service Substrate](file:///d:/projects/SCOF_V1/SCOF/docs/adr/018_cognitive_twin_service_substrate.md)
* [ADR 019: Operational Digital Twin Substrate Layer](file:///d:/projects/SCOF_V1/SCOF/docs/adr/019_operational_digital_twin_substrate_layer.md)
* [Minimalist Concurrency Architecture Specification](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/04_minimalist_concurrency_and_worker_pool.md)
