# SCOF Benchmark Methodology & Evaluation Protocol (D10)

## 1. Overview & Objective

This document defines the formal benchmark evaluation protocol for SCOF Deliverable D10. It establishes the testing methodology, comparative baselines, and state isolation guarantees required to scientifically answer Research Questions RQ1–RQ4.

---

## 2. The Four Comparative Baselines

To prove the empirical efficacy of the CD²F dynamic consensus engine, SCOF is evaluated against four comparative operational baselines across all 20 canonical disruption scenarios:

| Baseline ID | Baseline Name | Decision Logic | Purpose |
| :--- | :--- | :--- | :--- |
| **B1** | **Single-Agent Demand** | Decides mitigation purely on demand projections, ignoring transport and supplier constraints. | Tests the vulnerability of localized, uncoordinated demand optimization. |
| **B2** | **Single-Agent Inventory** | Decides mitigation purely on holding stock and buffer preservation. | Tests the risk of inventory hoarding and missed sales opportunities. |
| **B3** | **Naive Unweighted Voting** | Each agent casts one equal vote; majority recommendation wins. | Tests whether unweighted voting causes deadlocks or enables low-confidence majorities. |
| **B4** | **Static Priority Heuristic** | Fixed hierarchy: Transport always overrides Supplier, which overrides Inventory, which overrides Demand. | Tests traditional rigid corporate command hierarchies. |
| **SCOF** | **CD²F Consensus Engine** | Multi-factor confidence weighting ($W_i = w_i \times c_i$), greedy bias override, and tri-tier risk gating. | **The Proposed Framework** |

---

## 3. Strict State Isolation Protocol (ADR 015)

To guarantee that benchmark results are valid and reproducible:
1. **Pre-Run Invariant:** Each scenario run initializes against the clean Day-0 baseline (Layer 2).
2. **Execution Sandbox:** All simulated disruptions, inventory deductions, and routing changes occur in an ephemeral Layer 3 context tagged by `scenario_id` and `sim_run_id`.
3. **Post-Run Cleanup:** Upon run completion, decision metrics, latency timestamps, and reasoning trails are persisted to `scof.decision_records`, while the Layer 3 ephemeral state is discarded.
4. **Zero Cross-Scenario Contamination:** Scenario B never inherits or observes state mutations produced by Scenario A.
