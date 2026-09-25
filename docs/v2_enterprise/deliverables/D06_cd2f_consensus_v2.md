# Deliverable D06 (V2): CD2F Consensus & Dispute Resolution Engine

## 1. Overview & Objectives

Deliverable D06 replaces the simple static confidence voting of V1 with the **Consensus and Dispute Resolution Framework (CD2F)**. CD2F is a mathematically rigorous multi-agent arbitration engine designed to resolve conflicting claims among specialist agents, detect and neutralize greedy local optimizations, and enforce tri-tier escalation gating ([ADR ADR 015](file:///d:/projects/SCOF_V1/SCOF/docs/adr/015_cd2f_consensus_arbitration.md)).

### Role in the Five-Tier State Hierarchy (ADR ADR 017):
* Specialist agents produce **Tier 4 Agent Recommendations** (Structured Claims).
* CD2F arbitrates these claims into an authoritative **Tier 5 CD2F Decision**.
* The approved decision is applied to **Tier 3 (Scenario Projection)** in the Twin sandbox.
* If operating in live enterprise deployment, real-world physical actuation is dispatched via the Execution Gateway only after Human-in-the-Loop (HITL) authorization.

---

## 2. Mathematical Formalization

### 2.1 Multi-Factor Composite Weighting
Each claim $C_i$ submitted by specialist agent $i$ is assigned an effective composite weight $W_i$:
$$W_i = w_i \times c_i \times R_i$$

Where:
* $w_i \in [0, 1]$: Domain priority weight dynamically modulated by disruption type (e.g., in a route closure, $w_{\text{transport}} = 0.40$; in a supplier outage, $w_{\text{supplier}} = 0.40$).
* $c_i \in [0, 1]$: Self-reported Bayesian confidence emitted in `StructuredClaimV2`.
* $R_i \in [0, 1]$: Empirical historical reliability factor tracking the agent's past prediction accuracy over preceding simulation cycles.

### 2.2 Conflict Metric & Cross-Domain Externality Penalty
To prevent greedy domain behavior (e.g., Procurement purchasing excess volume to capture bulk discounts, which exhausts DC warehouse capacity), CD2F evaluates total global landed impact:
$$\text{NetBenefit}(C_i) = \text{PrimarySavings}(C_i) - \sum_{j \ne i} \text{CrossDomainPenalty}(C_i, \text{Domain}_j)$$

If an action incurs negative net benefit across the enterprise network, its composite weight $W_i$ is penalized by an externality dampening factor $\gamma \in [0, 1]$.

---

## 3. Tri-Tier Escalation Gating

CD2F classifies resolution confidence into three operational tiers:

```text
                  ┌───────────────────────────────┐
                  │ Evaluate Claims & Net Benefit │
                  └───────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
     [ TIER 1 ]               [ TIER 2 ]               [ TIER 3 ]
  Automated Consensus    Heuristic Arbitration     Human-in-the-Loop
 - Clear supermajority   - Moderate disagreement   - High financial exposure
 - Low financial risk    - Business rule override  - Unresolvable deadlock
 - Instant execution     - Precedent alignment     - Dispatches to D09 Console
```

| Escalation Tier | Trigger Conditions | Resolution Mechanism | Execution SLA |
| :--- | :--- | :--- | :--- |
| **Tier 1: Automated Consensus** | Highest claim weight $W^* \ge 0.70$ and Net Benefit $> 0$ | Autonomous execution of highest-weighted claim $C^*$ | $\le 150\text{ ms}$ |
| **Tier 2: Heuristic Arbitration** | $0.50 \le W^* < 0.70$ or moderate inter-agent disagreement | Application of deterministic corporate tie-breakers (e.g., service level beats freight cost) | $\le 250\text{ ms}$ |
| **Tier 3: HITL Escalation** | $W^* < 0.50$ or financial exposure $> \$100,000$ | Generates structured comparison package with trade-off analysis dispatched to Desktop Console | Pauses for human input |

---

## 4. Interaction with Digital Twin Substrate

1. **High-Priority Simulation Queries (P1):** When CD2F evaluates candidate interventions, it issues simulation requests to the Twin Service with **Priority 1 (P1)** in the [Minimalist Concurrency Model](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/04_minimalist_concurrency_and_worker_pool.md), ensuring arbitration requests are never starved by routine agent exploratory queries.
2. **Approved Sandbox Application:** Upon reaching consensus, CD2F dispatches an `ApprovedAction` to the Twin via `POST /api/v2/twin/scenarios/{id}/actions`, which commits the action to Layer 3 and advances the simulation timeline.

---

## 5. Consensus Outcome Schema

When consensus resolves, CD2F outputs a formal `ConsensusOutcome` object:

```python
class ConsensusOutcome(BaseModel):
    consensus_id: str
    scenario_id: str
    tier_resolved: Literal["TIER_1", "TIER_2", "TIER_3"]
    winning_claim_id: str
    selected_action: str
    participating_agents: list[str]
    effective_weights: dict[str, float]
    conflict_score: float
    projected_financial_exposure_usd: float
    rationale: str
    escalation_reason: Optional[str] = None
```

---

## 6. Acceptance Criteria & Verification Evidence

1. **Resolution Latency Gate:** Tiers 1 and 2 arbitration resolve in $\le 250\text{ ms}$.
2. **Greedy Bias Rejection Gate:** CD2F successfully rejects at least 95% of synthetic "greedy procurement" proposals that violate warehouse storage bounds.
3. **Escalation Accuracy Gate:** 100% of scenarios with financial exposure $> \$100,000$ are strictly gated to Tier 3 human approval.
4. **Determinism Gate:** Identical input claims and weights yield identical consensus outcomes across repeated runs.
