# ADR 011: Empirical Evaluation Methodology — Cohen's Kappa & Ground Truth vs. Subjective LLM-as-a-Judge

* **Status**: Accepted
* **Date**: 2026-08-28
* **Deciders**: SCOF Core Architecture Team, Evaluation Leads
* **Consulted**: Research Scientists, Domain Specialists
* **Informed**: All Platform Developers

---

## 1. Context and Problem Statement

Evaluating autonomous multi-agent decision systems is notoriously challenging:
* Traditional automated unit tests check code logic, but fail to evaluate the **decision quality** of collaborative agent deliberations.
* Many modern generative AI projects rely on "LLM-as-a-Judge" (prompting GPT-4 or Claude to grade model outputs on a 1-to-5 scale). However, empirical research shows that LLM judges suffer from position bias, self-enhancement bias, non-deterministic drift, and lack supply chain operational grounding.
* Anecdotal evaluation ("we tested 3 scenarios and it looked reasonable") is scientifically indefensible and unacceptable for enterprise operations.

The evaluation harness needed an objective, statistically defensible methodology to validate Research Questions RQ1 through RQ4 and verify that the coordinator/consensus arbitration does not hallucinate or drift.

---

## 2. Decision Drivers

* **Statistical Defensibility**: Use of recognized psychometric and inter-rater reliability standards.
* **Ground-Truth Calibration**: Benchmarking against hand-curated expert mitigation decisions.
* **Multi-Dimensional Metrics**: Evaluation of accuracy, consensus stability, tie-breaker deadlocks, latency percentiles, and operational risk reduction.
* **Separation of Evaluator from System**: The evaluation harness must run as an independent microservice (`services/evaluation/`) benchmarking identical inputs across CD²F and comparative baselines.

---

## 3. Considered Options

* **Option 1: Subjective LLM-as-a-Judge Scoring**: Unstructured prompt grading.
* **Option 2: Pure Binary Exact-Match Strings**: Strict string equality without inter-rater statistics.
* **Option 3: Rigorous Statistical Benchmarking with Cohen's Kappa ($\kappa$) and Bounded Metrics**:
  * Cohen's Kappa for inter-rater agreement and escalation tier fidelity.
  * Weighted Consensus Stability ($\text{WCS}$).
  * Tie-Breaker Rate (TBR) and Pairwise Discordance Rate (PDR).
  * Latency percentile distributions (P50, P90, P99) split by Fast-Path and Slow-Path.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Statistical Benchmarking with Cohen's Kappa**

### Rationale:
1. **Cohen's Kappa ($\kappa$) for Inter-Rater Reliability**:
   * Measures agreement between predicted actions and ground truth while explicitly accounting for agreement occurring by chance:
     $$\kappa = \frac{P_o - P_e}{1 - P_e}$$
   * Enforces a target of $\kappa \ge 0.85$ (almost perfect agreement). Observed results achieved:
     * Recommendation Selection: $\kappa_{\text{rec}} = \mathbf{1.000}$
     * Escalation Tier Gating: $\kappa_{\text{tier}} = \mathbf{0.894}$ (vs. baselines $\kappa = 0.000$).
2. **Standardized Disruption Suite (`benchmark_suite.json`)**:
   * Evaluates a balanced 20-scenario suite spanning all 4 canonical disruption domains (`SUPPLIER_DELAY`, `TRANSPORTATION_FAILURE`, `DEMAND_SPIKE`, `ADVERSE_WEATHER`), proving domain generalizability.
3. **Comparative Baseline Isolation**:
   * Executes CD²F against identical ClaimBundles dispatched simultaneously to **Naive Majority Voting** and **Single Specialist Agent** baselines.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Provides scientific, reproducible answers to Research Questions **RQ1, RQ2, RQ3, and RQ4**.
* Proved mathematically that Naive Majority Voting deadlocks in **60.0%** of calibration cases, while CD²F achieves **0.0%**.
* Eliminates evaluation drift and protects against silent regression.

### Negative Consequences / Trade-offs:
* Requires authoring hand-labeled, multi-specialist ground-truth scenario files (`calibration_set.json`, `benchmark_suite.json`).

---

## 6. Implementation & Compliance Notes

* Implemented in [services/evaluation/src/metrics.py](file:///d:/projects/SCOF_V1/SCOF/services/evaluation/src/metrics.py) and [services/evaluation/src/harness.py](file:///d:/projects/SCOF_V1/SCOF/services/evaluation/src/harness.py).
* Standalone CLI benchmark runner in [services/evaluation/src/benchmark_runner.py](file:///d:/projects/SCOF_V1/SCOF/services/evaluation/src/benchmark_runner.py).
* Full empirical results published in [docs/deliverables/D10_integration_evaluation/results_report.md](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D10_integration_evaluation/results_report.md).
* Verified via `python -m pytest services/evaluation/tests/ -v` (40 / 40 tests passed).

---

## 7. Related Decisions & Artifacts

* [ADR 004: Consensus Arbitration Framework](./004_cd2f_consensus_arbitration.md)
* [ADR 005: Dual-Path Execution Routing Strategy](./005_dual_path_execution_routing.md)
* [D10 Results Report](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D10_integration_evaluation/results_report.md)
