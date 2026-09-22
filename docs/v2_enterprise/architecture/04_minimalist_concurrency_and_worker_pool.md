# Minimalist Concurrency & Worker Pool Architecture

## 1. Executive Summary & Design Philosophy

When multiple cognitive specialist agents deliberate concurrently, they may simultaneously submit simulation requests to the Digital Twin Service (e.g., the Inventory Agent evaluating safety stock depletion while the Transportation Agent simulates an air-freight reroute).

### The Over-Engineering Trap
In complex distributed systems, it is tempting to layer elaborate scheduling algorithms: dynamic priority scoring, deadline monotonic scheduling, deficit round-robin fairness, aging decay formulas, and admission control quotas.

For SCOF V2, **this layering is explicitly rejected**. Piling complex scheduling mechanisms on top of the simulation layer adds fragility and latency overhead without solving core supply chain problems.

### The Minimalist Design Principle
> *"A disciplined architecture avoids solving secondary problems with heavy academic machinery. It adopts proven, minimalist primitives that guarantee correctness, predictable latency, and resource containment."*

SCOF locks a **Minimalist Concurrency Model: A Fixed 4-Tier Priority Queue backed by a Bounded Worker Pool with FIFO dispatching per tier and in-memory scenario branch overlays.**

---

## 2. The 4-Tier Priority Queue Structure

Incoming tasks submitted to the Twin Service are assigned one of four fixed, deterministic priority levels:

```text
+===============================================================================+
| PRIORITY LEVEL                                   | TYPICAL OPERATIONAL TASK   |
+===============================================================================+
| P0: System Emergency & Threshold Violations      | Cold-chain thermal failure |
|     (Preempts queue; immediate dispatch)         | Critical asset breakdown   |
+--------------------------------------------------+----------------------------+
| P1: CD2F Consensus Arbitration                   | Final candidate comparison |
|     (High priority; time-budgeted deliberation)  | Arbitration trade-offs     |
+--------------------------------------------------+----------------------------+
| P2: Specialist Agent What-If Deliberation        | Scenario branch exploration|
|     (Normal priority; standard agent traffic)    | Single-agent what-if tests |
+--------------------------------------------------+----------------------------+
| P3: Background Analytics & Benchmark Evaluation  | D10 batch benchmarking     |
|     (Low priority; executes during idle cycles)  | Long-horizon risk heatmaps |
+===============================================================================+
```

### Deterministic Assignment Rules:
* Tasks do not dynamically compute complex priority floating-point scores.
* Priority is strictly derived from the caller's operational context:
  - System telemetry interrupt $\implies$ **P0**
  - CD²F arbitration engine $\implies$ **P1**
  - Specialist agent exploring claims $\implies$ **P2**
  - Batch benchmark runner $\implies$ **P3**

---

## 3. Bounded Worker Pool Execution Model

To prevent unconstrained concurrency from exhausting database connection pools, memory, or CPU cores, execution is constrained by a bounded worker pool:

```text
+-------------------------------------------------------------------------------+
|                       INCOMING SIMULATION REQUESTS                            |
|        Agent Queries   |   CD2F Inquiries   |   Emergency Triggers            |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                         4-TIER PRIORITY QUEUE                                 |
|                                                                               |
|   [P0 Queue] [ E1 ] -> [ E2 ]                    (Highest Priority)           |
|   [P1 Queue] [ C1 ] -> [ C2 ] -> [ C3 ]                                       |
|   [P2 Queue] [ A1 ] -> [ A2 ] -> [ A3 ] -> [ A4 ]                             |
|   [P3 Queue] [ B1 ] -> [ B2 ]                    (Lowest Priority)            |
+---------------------------------------+---------------------------------------+
                                        |
                                        | Pulls next highest priority task
                                        | (Strict FIFO within level)
                                        v
+-------------------------------------------------------------------------------+
|                          BOUNDED WORKER POOL                                  |
|                                                                               |
|     [ Worker 1 ]       [ Worker 2 ]       [ Worker 3 ]       [ Worker 4 ]     |
|       (Active)           (Active)           (Active)           (Idle)         |
|                                                                               |
|   Fixed Concurrency Limit (W = 4..8) | Non-Blocking In-Memory Isolation       |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                     IN-MEMORY SCENARIO OVERLAYS                               |
|   Worker 1: Branch A State   |   Worker 2: Branch B State   |   Worker 3: L2  |
|   (Zero cross-worker locking on shared Day-0 baseline reference)              |
+-------------------------------------------------------------------------------+
```

### Operational Rules of the Worker Pool:
1. **Bounded Concurrency ($W$):** The number of concurrent simulation workers is bounded (default $W = 4$, configurable based on available CPU cores).
2. **Strict Priority Dispatch:** Workers always pull tasks from the non-empty queue with the highest priority (P0 before P1, P1 before P2, P2 before P3).
3. **FIFO Within Tier:** Within the same priority level, tasks are served in strict First-In, First-Out order. No task within a tier can starve an earlier task in that same tier.
4. **Execution Timeout Budget:** Every worker execution is bounded by a strict hard timeout (default $1,000\text{ ms}$). If a simulation exceeds its SLA budget, it is safely aborted, returning an incomplete status rather than blocking the worker pool.

---

## 4. Non-Blocking Read Isolation & Branch Overlays

Concurrent agent queries must never create database lock contention:

* **Day-0 Baseline (Layer 2) is Immutable:** Reads against the Day-0 baseline operational state (PostgreSQL tables, Neo4j graph) are read-only and non-blocking. Any number of workers can read Layer 2 simultaneously without locking.
* **Scenario Overlays are Branch-Local:** When Worker 1 simulates Branch A and Worker 2 simulates Branch B, their state modifications (inventory deductions, transit updates) exist exclusively in separate, in-memory copy-on-write overlay dictionaries.
* **Zero Cross-Worker Contention:** Worker 1 and Worker 2 share no writable memory. They run completely decoupled and parallel.

---

## 5. Formal Research Frontiers (Documented for Future Scale)

While the minimalist model is locked for V2 implementation, clear frontiers are formally established for post-MVP investigation:

1. **Starvation Prevention via Aging:** Under sustained high-load crisis scenarios, continuous P1 consensus traffic could theoretically starve P2 agent what-if explorations. An aging function promoting P2 tasks to P1 after duration $\tau_{\text{starve}}$ may be evaluated.
2. **Dynamic Work-Stealing Pools:** Evaluating whether worker threads should dynamically reallocate queue partitions based on simulation horizon length.
3. **Empirical Concurrency Benchmarking:** Measuring the exact latency degradation curve as concurrent agent count scales from $N=4$ to $N=32$ across large-scale retail networks.
