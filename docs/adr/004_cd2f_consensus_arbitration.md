# ADR 004: Consensus Arbitration Framework — CD²F Dynamic Continuous Weighting vs. Majority Voting & LLM-as-a-Judge

* **Status**: Accepted
* **Date**: 2026-08-10
* **Deciders**: SCOF Core Architecture Team, Research Leads
* **Consulted**: Consensus Engine Developers, Evaluation Engineers
* **Informed**: All Platform Developers

---

## 1. Context and Problem Statement

In a multi-agent supply chain orchestration framework, specialist agents frequently generate divergent, conflicting mitigation recommendations. For example, during a supplier lead-time extension:
* The **Inventory Agent** may recommend consuming internal safety stock to minimize holding costs.
* The **Supplier Agent** may recommend switching volume to an alternate secondary supplier.
* The **Transportation Agent** may recommend booking expedited air freight.

The system requires an arbitration mechanism to evaluate these competing claims and select a single winning mitigation action, quantify the stability of the agreement, and determine whether the decision can execute autonomously or must escalate to human oversight.

Traditional methods rely on either simple majority voting, unweighted democratic tallying, or a single centralized LLM acting as an unconstrained judge.

---

## 2. Decision Drivers

* **Zero Tie-Breaker Vulnerability**: Discrete vote counting regularly deadlocks on multi-option panels, forcing arbitrary alphabetical or random tie-breaking.
* **Continuous Multi-Factor Weighting**: Ability to incorporate an agent's historical accuracy ($w_i$) and real-time situational confidence ($c_i$).
* **Mitigation of Isolated Greedy Bias**: Protection against single agents asserting inflated confidence ($c = 0.99$) on flawed, localized actions.
* **Mathematically Bounded Stability Metric**: Continuous consensus metric $\text{WCS} \in [0.0, 1.0]$ to inform downstream operational risk gating.
* **Deterministic & Sub-Second Latency**: Computational execution within $< 50\text{ ms}$, avoiding slow, multi-second recursive LLM judge calls.

---

## 3. Considered Options

* **Option 1: Naive Majority Voting**: Discrete democratic tally (each agent gets 1.0 vote). Deadlocks resolved alphabetically.
* **Option 2: Unconstrained LLM-as-a-Judge**: Passing all raw agent claims to an external LLM prompt asking it to pick the winner.
* **Option 3: CD²F (Consensus-Driven Collaborative Decision Framework)**: Continuous composite weighting with Weighted Consensus Stability ($\text{WCS}$) and calibrated tier gating.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — CD²F Dynamic Arbitration Engine**

### Rationale:
1. **Mathematical Deadlock Elimination**:
   * Under Naive Majority Voting, empirical evaluation proved that **60.0%** of split calibration scenarios deadlocked, forcing an arbitrary decision.
   * Under CD²F, each claim $k$ is scored using continuous composite weights:
     $$W(k) = \sum_{i \in \text{Claimants}(k)} w_i \cdot c_i$$
     In continuous real space ($\mathbb{R}^+$), ties occur with near-zero probability, reducing the tie-breaker rate to **0.0%**.
2. **Resilience to Single-Agent Hallucination**:
   * When a single agent claims high confidence ($c=0.99$) on an aggressive action (`Cancel Backorders`), single-agent baselines greedily execute it. CD²F aggregates corroborated domain evidence from other agents to elect the systemically sound option (`Fulfill from Hub A`) and flags `consensus_divergence_detected: true`.
3. **Deterministic Speed**:
   * CD²F executes in pure NumPy vector arithmetic in **$< 5\text{ ms}$**, whereas an LLM-as-a-Judge call requires $1500\text{ ms}$ to $4000\text{ ms}$ and introduces prompt drift.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* **0.0% Tie-Breaker Rate**: Deterministic resolution without arbitrary fallback.
* **Quantifiable Stability**: $\text{WCS} = \frac{W_{\text{winner}}}{\sum W_{\text{all}}}$ directly drives automated escalation tiering.
* High speed ($< 5\text{ ms}$ compute) enables overall Fast-Path resolution $< 335\text{ ms}$.
* High inter-rater agreement against expert ground truth ($\kappa_{\text{rec}} = 1.000$).

### Negative Consequences / Trade-offs:
* Requires historical accuracy tracking ($w_i$) per agent, managed via configuration or sliding windows.

---

## 6. Implementation & Compliance Notes

* Microservice implementation in [services/consensus/src/engine.py](file:///d:/projects/SCOF_V1/SCOF/services/consensus/src/engine.py).
* Exposed on port `8020` via FastAPI (`POST /consensus/arbitrate`).
* Validated in unit tests [test_benchmark_runner.py](file:///d:/projects/SCOF_V1/SCOF/services/evaluation/tests/test_benchmark_runner.py) and full-loop verification `scripts/verify_d6.py`.

---

## 7. Related Decisions & Artifacts

* [ADR 005: Dual-Path Execution Routing Strategy](./005_dual_path_execution_routing.md)
* [ADR 011: Empirical Evaluation & Calibration](./011_empirical_evaluation_cohens_kappa.md)
* [D6 Consensus Engine Documentation](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D06_consensus_engine/README.md)
