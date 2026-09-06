# ADR 005: Execution Routing Strategy — Dual-Path Gating (Fast-Path vs. Slow-Path / Human Escalation)

* **Status**: Accepted
* **Date**: 2026-08-10
* **Deciders**: SCOF Core Architecture Team, Safety & Operations Leads
* **Consulted**: Platform Engineers, Supply Chain Domain Experts
* **Informed**: All Platform Developers

---

## 1. Context and Problem Statement

Enterprise supply chain networks present an acute operational tension:
1. **Response Velocity**: In high-throughput logistics, delays measured in hours create supply line gridlock, stockouts, and carrier detention penalties. Sub-second automated response times are required.
2. **Operational Safety & Liability**: Executing automated actions (e.g. canceling purchase orders or re-routing high-value freight) on low-confidence or conflicting predictions can result in catastrophic financial loss and contractual breach.

A binary system that either automates everything or requires human review for every event fails: full automation is reckless, while full human review recreates the 2-to-24 hour manual deliberation bottleneck.

---

## 2. Decision Drivers

* **Sub-Second SLA Compliance**: Fast resolution for routine disruptions ($\le 500\text{ ms}$).
* **Ironclad Guardrails for High-Risk Events**: Automated interception of contested claims or severe anomalies.
* **Calibrated Gating Fidelity**: Objective mathematical thresholds driven by Weighted Consensus Stability ($\text{WCS}$) and disruption severity, rather than arbitrary heuristics.
* **High Inter-Rater Reliability**: Agreement with expert risk assessment ($\kappa_{\text{tier}} \ge 0.85$).

---

## 3. Considered Options

* **Option 1: Unconditional Full Automation (Always Fast-Path)**: Execute winning recommendations immediately without escalation.
* **Option 2: Unconditional Human-in-the-Loop (Always Slow-Path)**: Present all recommendations to an operator for manual authorization.
* **Option 3: Dual-Path Calibrated Risk Gating**: Mathematical partition into **Fast-Path**, **Slow-Path Simulation**, and **Human Escalation**.

---

## 4. Decision Outcome

**Chosen Option**: **Option 3 — Dual-Path Calibrated Risk Gating**

### Rationale:
The CD²F engine enforces a deterministic multi-tier escalation policy based on two metrics:
1. **Weighted Consensus Stability ($\text{WCS}$)**: Bounded in $[0.0, 1.0]$.
2. **Disruption Severity ($S$)**: Bounded in $[0.0, 1.0]$.

$$\text{Tier} = \begin{cases} \text{FAST\_PATH} & \text{if } \text{WCS} \ge 0.70 \text{ and } S < 0.60 \\ \text{SLOW\_PATH} & \text{if } 0.50 \le \text{WCS} < 0.70 \text{ or } 0.60 \le S < 0.85 \\ \text{HUMAN\_ESCALATION} & \text{if } \text{WCS} < 0.50 \text{ or } S \ge 0.85 \end{cases}$$

1. **Fast-Path Execution**:
   * Resolves in **330.0 – 335.0 ms** median latency ($< 500\text{ ms}$ SLA).
   * Safely handles **60.0% of routine disruptions** autonomously with 100% accuracy.
2. **Slow-Path Simulation**:
   * Evaluates counterfactual fill rate preservation and holding costs before execution. Resolves in **510.0 ms** ($< 2000\text{ ms}$ SLA).
3. **Human Escalation**:
   * Flags high-severity disruptions (`HUMAN_ESCALATION`) directly on the Operations Console (`Ctrl + 1`), pausing autonomous execution and demanding operator sign-off.

---

## 5. Pros and Cons of the Selected Option

### Positive Consequences:
* Reconciles sub-second automated speed with enterprise safety.
* Achieved **$\kappa_{\text{tier}} = 0.894$** inter-rater reliability against expert hand-labeled escalation ground truth.
* Baselines (Naive Majority and Single-Agent) have $\kappa_{\text{tier}} = 0.0$ because they lack risk gating.

### Negative Consequences / Trade-offs:
* Requires defining baseline severity scales in `consensus.yaml` per Domain Profile.

---

## 6. Implementation & Compliance Notes

* Implemented in [services/consensus/src/engine.py](file:///d:/projects/SCOF_V1/SCOF/services/consensus/src/engine.py).
* Configurable thresholds defined in [profiles/mvp-electronics/consensus.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/consensus.yaml).
* Validated in automated test suite [test_metrics.py](file:///d:/projects/SCOF_V1/SCOF/services/evaluation/tests/test_metrics.py).

---

## 7. Related Decisions & Artifacts

* [ADR 004: Consensus Arbitration Framework](./004_cd2f_consensus_arbitration.md)
* [ADR 011: Empirical Evaluation & Calibration](./011_empirical_evaluation_cohens_kappa.md)
* [Research Results Report](file:///d:/projects/SCOF_V1/SCOF/docs/deliverables/D10_integration_evaluation/results_report.md)
