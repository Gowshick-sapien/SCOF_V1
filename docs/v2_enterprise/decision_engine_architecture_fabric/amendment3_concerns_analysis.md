# SCOF V2 Architecture Hardening Review -- Critical Analysis & Response

## Document Purpose

This document provides an ultra-detailed critical analysis of and response to the 80-point Architecture Review conducted against the SCOF V2 Architecture Hardening Revision (Amendment 2). For every finding raised by the review, this document states a verdict (AGREE, PARTIALLY AGREE, or DISAGREE), provides detailed rationale grounded in the SCOF architectural context, and identifies the concrete action to be taken.

> [!IMPORTANT]
> This document does NOT alter any content in Amendment 2 or any predecessor document. It serves as the analytical basis for the Architecture Refinement Revision (Amendment 3), which will incorporate the validated corrections.

## Executive Assessment

### Overall Position

The review is **the most technically rigorous audit** this architecture has received. Its core verdict -- that the Architecture Hardening Revision is architecturally sound but not yet implementation-contract-ready -- is correct.

However, the review itself contains a spectrum of findings that must be differentiated:

1. **Genuinely critical contract defects** that would cause implementation failure (broken claim vocabularies, unsafe pruning, incorrect Pareto semantics). These must be fixed before coding.

2. **Legitimate refinements** that improve correctness but are not blockers (snapshot consistency model, action intent/impact separation, evidence freshness decomposition). These should be incorporated.

3. **Technically correct but scope-inappropriate concerns** that conflate research-grade formalism with pragmatic implementation readiness (exact replay guarantees, container image digests for reproducibility, MCDA alternatives). These are noted but deferred.

4. **Points where the review itself is wrong or overstates the problem** (R_i floor criticism, event partitioning concerns, the claim that the existing SRS "blocks" implementation). These are rebutted.

The critical path is clear: **fix the contract-level defects, incorporate the legitimate refinements, and begin D3 implementation.** There is no need for another full architectural redesign -- the review itself confirms this.

---

## Verdicts Summary

### P0 Corrections (Review Sections that require immediate architectural action)

| Review Section | Finding | My Verdict | Action |
| :--- | :--- | :--- | :--- |
| 15 | Broken cross-agent claim contracts | AGREE | Create ClaimTypeRegistry |
| 16 | Broken candidate action type coverage | AGREE | Create ActionTypeRegistry |
| 18 | Action params mix intent with impact | AGREE | Separate ActionIntent from DeterministicImpact |
| 19 | Candidate pruning eliminates best action before Twin | AGREE | Restrict pre-Twin pruning to deterministic criteria |
| 22 | Candidate-relative normalization creates instability | AGREE | Use policy-fixed reference scales |
| 21 | Pareto check is not actual Pareto analysis | AGREE | Implement proper Pareto frontier analysis |
| 10 | Post-snapshot evidence contradiction with Invariant 8 | AGREE | Reject or quarantine post-snapshot evidence |
| 5 | Evidence sufficiency uses average freshness (conceals stale critical facts) | AGREE | Add critical-evidence-specific assessment |
| 25 | Twin timeout allows CD2F without simulation | PARTIALLY AGREE | Add TwinRequired/TwinOptional policy |
| 9 | Hard-coded safety policy contradicts profile-driven policy | AGREE | Separate platform invariants from domain regulations |
| 47 | DecisionPolicy has duplicate sources of truth | AGREE | Deduplicate and clarify policy boundaries |
| 57 | B0-B7 ablation ladder incomplete | AGREE | Define complete ladder with exact configurations |
| 59 | Calibration metric is correlation, not calibration | AGREE | Replace with proper calibration metrics |
| 58 | Statistical test too prescriptive | AGREE | Define distribution-appropriate test protocol |

### P1 Corrections (Review Sections that should be fixed during D3/D4)

| Review Section | Finding | My Verdict | Action |
| :--- | :--- | :--- | :--- |
| 11 | Snapshot does not guarantee common database state | PARTIALLY AGREE | Add consistency epoch concept |
| 12 | Historical scenario freshness wrongly defined | AGREE | Make freshness relative to observation_cutoff |
| 17 | Candidate ownership ambiguous for shared actions | AGREE | Add ActionDefinition with ownership model |
| 20 | Candidate pruning must be uncertainty-aware | AGREE | Use confidence-bound-based retention |
| 23 | Objective weight transformations underdefined | PARTIALLY AGREE | Define normalization functions per metric |
| 26 | Twin trigger based on USD too narrow | AGREE | Replace with multi-dimensional materiality policy |
| 28 | R_i floor of 0.20 forces unreliable influence | DISAGREE | Floor prevents permanent lockout; add advisory-only status |
| 29 | R_i not fully outcome-causal | PARTIALLY AGREE | Separate prediction/claim/action reliability |
| 31 | Event sequence allocation underspecified | AGREE | Define PostgreSQL session-scoped sequence |
| 32 | Aggregate version vs session sequence relationship undefined | AGREE | Define explicit relationship |
| 36 | Hot-path cache keying too coarse | AGREE | Extend key with capability and query hash |
| 37 | Governance should fail closed for critical retrieval | AGREE | Add fail-closed policy for critical evidence |
| 38 | Capability authorization incomplete | PARTIALLY AGREE | Extend with agent-capability binding |
| 39 | Cancellation has race conditions | AGREE | Add terminal-state guards |
| 40 | Execution outcome model incomplete | PARTIALLY AGREE | Add verification_status for real-world execution |
| 41 | Replanning needs explicit state inheritance | AGREE | Bind causation and post-execution snapshot |
| 42 | DecisionRecord actual_outcome is untyped dict | AGREE | Create OutcomeObservation schema |
| 46 | Some failure responses too permissive | PARTIALLY AGREE | Make fallback policy claim-criticality-dependent |
| 48 | Policy versioning needs hash | AGREE | Add policy_hash and profile_hash |
| 51 | Snapshot needs trigger-state binding | AGREE | Add trigger_event_sequence to snapshot |
| 53 | Twin manifest reproducibility overstated | PARTIALLY AGREE | Qualify "exact" with environment requirements |

### P2 Corrections (Evaluation/Research hardening, during D10)

| Review Section | Finding | My Verdict | Action |
| :--- | :--- | :--- | :--- |
| 44 | Tier-1 RAG creates correlated errors across agents | AGREE | Measure shared-evidence correlation in D10 |
| 45 | Deliberation loop independence requires evaluation distinction | AGREE | Separate Round-1 vs Round-2 metrics |
| 60 | Cohen's Kappa needs clarification | PARTIALLY AGREE | Use appropriate inter-rater metric |
| 61 | Hindsight optimal can create evaluator leakage | AGREE | Define independent oracle methodology |
| 62 | Twin calibration vs evaluation data must be separated | AGREE | Enforce train/eval split for Twin |
| 63 | D10 needs policy sensitivity analysis | AGREE | Add policy perturbation tests |
| 64 | B0 must be frozen before D3 experiments | AGREE | Freeze B0 definition in Amendment 3 |

### Points Where I Diverge from the Review

| Review Section | Finding | My Verdict | Rationale |
| :--- | :--- | :--- | :--- |
| 24 | CD2F should not claim to be "pure computation" | DISAGREE | CD2F IS pure over a materialized context; the review conflates upstream complexity with CD2F's own computation |
| 27 | Simulation fidelity composite is arbitrary | PARTIALLY DISAGREE | Composite is calibratable; the alternative (no composite) is worse |
| 28 | R_i min floor of 0.20 is problematic | DISAGREE | Floor prevents permanent agent exclusion; advisory-only status is a refinement, not a floor removal |
| 33 | Event partitioning by session is questionable | DISAGREE | At SCOF scale (hundreds, not millions of sessions), session-based partitioning is appropriate |
| 34 | Replay is not truly exact | PARTIALLY DISAGREE | The architecture already labels EXACT vs ANALYTICAL replay types; the review's concern is addressed by refinement, not redesign |
| 49 | Policy precedence needs a formal type system | PARTIALLY DISAGREE | Formal type system is premature; the textual hierarchy is sufficient until implementation reveals specific conflicts |
| 54 | Preemption is underspecified | PARTIALLY AGREE | But full preemption semantics are an implementation concern for D8, not an architecture-level defect |
| 55 | Worker reservation is over-allocated | DISAGREE | These are explicitly labeled as profile defaults, not architecture |
| 56 | MCP latency target of 20ms is aggressive | PARTIALLY AGREE | It is a benchmark target, and the architecture treats it as such |
| 65-67 | Cross-document drift is the biggest practical blocker | PARTIALLY DISAGREE | It is a documentation task, not an architecture defect; it does not block D3 coding |
| 68-69 | Patch document format is dangerous | AGREE conceptually but DISAGREE on timing | The merged document should be created AFTER Amendment 3, not before |

---

## Detailed Response by Review Section

---

### Review Section 1: Executive Verdict

**Review Finding:** The hardening revision should not yet be frozen as the final implementation contract. There are contract inconsistencies, mathematical problems, state semantics problems, and cross-document contradictions.

**VERDICT: AGREE**

The review's executive verdict is correct. The architecture is conceptually sound but has contract-level gaps that would cause implementation divergence. The review correctly identifies that the remaining work is precision engineering, not conceptual redesign.

Where I differ from the review is on the **severity weighting**. The review lists 12 "critical" items, but several of those (e.g., cross-document D3-D10 mismatch, B0-B7 incomplete definition) are documentation completeness issues, not architectural defects. A more precise classification would be:

- **Architecture-breaking defects:** 6 (broken vocabularies, pruning logic, Pareto semantics, snapshot contradiction, action intent/impact conflation, normalization instability)
- **Contract refinement needs:** 6 (snapshot consistency, Twin timeout policy, policy deduplication, evidence freshness decomposition, calibration metrics, statistical protocol)
- **Documentation completeness:** 2 (B0-B7 definition, cross-document sync)

**Action:** Produce Amendment 3 addressing all architecture-breaking defects and contract refinements. Schedule documentation sync as a parallel workstream.

---

### Review Section 2: What the Hardening Revision Achieved

**Review Finding:** The hardening revision correctly moves SCOF toward a governed cognitive decision fabric model.

**VERDICT: AGREE**

The review correctly identifies that the architecture has matured from "multi-agent consensus" to "governed cognitive decision fabric." The cognitive pipeline ordering, the separation of concerns between Twin/CD2F/ExecutionPolicy, and the Deliberation Table as cognitive workspace are all validated as architecturally correct.

No action required. This section confirms the architectural direction.

---

### Review Section 3: Invariant 1 -- Source Authority

**Review Finding:** PASS with minor wording refinement. Neo4j "owns topology projection" should be refined to "owns the materialized topology representation."

**VERDICT: AGREE on the refinement, but the impact is LOW.**

The review's suggested rewording is more precise:

```
PostgreSQL:
    authoritative operational facts

Neo4j:
    authoritative representation of the current
    materialized topology projection, subject to
    projection freshness/version

No operational fact may be made authoritative
solely because it exists in Neo4j.
```

This is a documentation refinement. The architectural mechanism (projection freshness metadata, staleness detection, PostgreSQL-wins conflict resolution) is already correctly specified in Amendment 2 Sections 5.2-5.4. The invariant prose should be updated to match the mechanism.

**Action:** Update Invariant 1 wording in Amendment 3.

---

### Review Section 4: Invariant 2 -- Cognitive Workspace Boundary

**Review Finding:** PASS. The Deliberation Table correctly prevents becoming an operational database. Minor wording issue: "events are the source of truth" could be misinterpreted as contradicting Invariant 1.

**VERDICT: AGREE**

The review correctly identifies a potential misinterpretation. The phrase "events are the source of truth" in Section 16.1 of Amendment 2 is contextually correct (it refers to the deliberation event stream), but without qualification, it could be read as a global statement that contradicts PostgreSQL's System of Record status.

**Correction:**

```
DeliberationEvents are authoritative for
the historical cognitive session state.

PostgreSQL operational tables remain authoritative
for enterprise operational state.
```

**Action:** Clarify the event-sourcing authority scope in Amendment 3.

---

### Review Section 5: Invariant 3 -- Evidence Sufficiency (avg_evidence_freshness conceals stale critical facts)

**Review Finding:** Using `avg_evidence_freshness` can conceal a catastrophically stale critical fact (99 fresh items + 1 stale critical item = 0.99 average).

**VERDICT: AGREE -- This is one of the review's strongest findings.**

The review is correct that averaging freshness across all evidence items is a statistical weakness that can mask a single stale critical fact controlling the decision outcome.

Amendment 2's `EvidenceSufficiencyAssessment` already includes `critical_facts_present: bool`, which partially addresses this. But the review correctly identifies that presence alone is insufficient -- the critical fact must also be fresh, authoritative, and consistent.

**Primary Solution: Critical Evidence Assessment**

The evidence sufficiency gate must operate on two levels:

```python
class EvidenceSufficiencyAssessment(BaseModel):
    # ... existing fields ...
    
    # NEW: Critical evidence specific assessment
    critical_evidence: CriticalEvidenceAssessment

class CriticalEvidenceAssessment(BaseModel):
    """Assessment of evidence items that are decision-critical.
    A decision is 'critical-fact-dependent' if removing that fact
    would change the candidate ranking."""
    
    critical_facts_identified: int
    critical_facts_present: int
    critical_facts_fresh: int          # Within freshness threshold
    critical_facts_authoritative: int  # From authoritative source for claim type
    
    # Worst-case metrics (not averages)
    min_critical_freshness: float      # Freshness of the STALEST critical fact
    min_critical_authority: str        # Authority level of the WEAKEST critical fact
    
    # Verdict
    all_critical_facts_sufficient: bool
```

**Verdict Logic Enhancement:**

```
SUFFICIENT:
    overall_domain_coverage >= 0.80
    AND overall_avg_freshness >= 0.60
    AND critical_evidence.all_critical_facts_sufficient == True
    AND consistency.contradiction_severity != "BLOCKING"

Where all_critical_facts_sufficient =
    critical_facts_present == critical_facts_identified
    AND min_critical_freshness >= policy.min_critical_freshness (default 0.80)
    AND min_critical_authority meets claim-type authority requirements
```

The key change: the gate now explicitly evaluates critical facts individually, not as part of an average. A single stale critical fact can independently trigger INSUFFICIENT even if the overall average is high.

**What counts as a "critical fact"?** This is determined by the disruption type profile. For a supplier-delay disruption:

```yaml
disruption_profiles:
  supplier_delay:
    critical_facts:
      - entity: affected_supplier
        claim_type: current_state
        required_fields: [status, capacity, lead_time]
      - entity: affected_inventory
        claim_type: current_state
        required_fields: [position, days_of_supply]
      - entity: alternate_suppliers
        claim_type: topological
        required_fields: [availability, capacity]
```

**Action:** P0. Add CriticalEvidenceAssessment to Amendment 3.

---

### Review Section 6: Invariant 4 -- Candidate Discipline

**Review Finding:** PASS conceptually, but undermined by the pruning algorithm.

**VERDICT: AGREE**

This is a cross-reference to Sections 19-20. The invariant itself is correct. The violation is in the implementation of pruning, which is addressed under Sections 19-22.

**Action:** No change to Invariant 4. Fix the pruning algorithm (see Sections 19-22 response).

---

### Review Section 7: Invariant 5 -- Counterfactual Isolation

**Review Finding:** PASS -- strong.

**VERDICT: AGREE**

The three-layer state isolation model (Layer 1 frozen historical truth, Layer 2 baseline operational state, Layer 3 scenario runtime) is correctly maintained. The SimulationManifest properly enforces isolation boundaries. No changes needed.

**Action:** None.

---

### Review Section 8: Invariant 6 -- Decision Authority Hierarchy

**Review Finding:** PASS -- one of the strongest parts.

**VERDICT: AGREE**

The separation of LLM (propose/interpret/explain), deterministic systems (calculate/validate), Twin (evaluate counterfactuals), CD2F (arbitrate), and Execution Adapter (act) is correctly specified. No changes needed.

**Action:** None.

---

### Review Section 9: Invariant 7 -- Policy Authority (Hard-Coded Safety Contradiction)

**Review Finding:** PARTIAL FAILURE. The invariant says "policy is profile-driven" but Section 13.3 hard-codes "cold-chain quarantine" and "regulatory recall" as domain-specific non-negotiable rules.

**VERDICT: AGREE -- This is a genuine contradiction.**

The review correctly identifies that hard-coding domain-specific regulatory rules (cold-chain quarantine, regulatory recall) violates the principle that domain context is declarative and profile-driven.

However, the review's proposed solution needs refinement. The review suggests separating "platform safety invariants" from "profile-defined domain regulations." I agree with the principle but need to define what constitutes a legitimate platform invariant vs. what must remain profile-defined.

**Platform Safety Invariants (legitimate to hard-code):**

These are domain-agnostic safety properties that no profile should be able to override:

```
- No autonomous execution in contexts not explicitly marked production-ready
- No external side effects from read-only capabilities
- No mutation of Layer 1 or Layer 2 state from Twin operations
- No execution without decision approval
- No decision without evidence sufficiency assessment
```

These are structural safety properties of the platform, not domain-specific rules.

**Profile-Defined Domain Regulations (must NOT be hard-coded):**

```
- Cold-chain temperature requirements
- Pharmaceutical regulatory recall procedures
- Perishable goods shelf-life rules
- Hazardous material transport regulations
- Dual-source procurement requirements
```

These are domain-specific and must come from the profile, not from platform code.

**Corrected Precedence:**

```
1. PLATFORM SAFETY INVARIANTS          (hard-coded, domain-agnostic)
       No profile can override these.
       
2. PROFILE REGULATORY CONSTRAINTS      (from profile, domain-specific)
       Cold-chain, recall, hazmat -- defined in profile YAML.
       
3. ENTERPRISE HARD CONSTRAINTS         (from DecisionPolicy.hard_constraints)
       Capacity limits, budget thresholds.
       
4. PROFILE-SPECIFIC POLICIES           (from DecisionPolicy)
       Objective weights, evidence thresholds.
       
5. SOFT OBJECTIVES                     (from DecisionPolicy.soft_constraints)
       Preferred carrier, sustainability targets.
       
6. AGENT PREFERENCES                   (lowest authority)
       Agent's recommended_action_id.
```

The key change: Level 1 is now explicitly "domain-agnostic platform safety" and Level 2 is "domain-specific regulations from the profile." The examples "cold-chain quarantine" and "regulatory recall" move from Level 1 to Level 2.

**Action:** P0. Fix policy precedence hierarchy in Amendment 3.

---

### Review Section 10: Invariant 8 -- State Freshness (Post-Snapshot Evidence Contradiction)

**Review Finding:** PARTIAL FAILURE. The invariant says "no agent can use evidence newer than observation_cutoff" but Section 7.2 says post-snapshot evidence is "allowed but noted."

**VERDICT: AGREE -- This is a direct internal contradiction.**

Amendment 2 Section 7.2 explicitly says:

```
If evidence.data_as_of > snapshot.observation_cutoff:
    Flag as "post-snapshot evidence" (allowed but noted)
```

This directly violates Invariant 8 which states:

```
No agent can use evidence newer than the session's observation_cutoff.
```

The review is correct: you cannot simultaneously forbid and permit post-snapshot evidence.

**Resolution:**

Post-snapshot evidence must be **rejected from the decision state**, not merely flagged. If the system detects that critical state has changed since the snapshot, the correct response is one of:

```
OPTION A: Reject the evidence. Continue with snapshot-consistent data.
           Use when: the post-snapshot evidence is non-critical or
           the decision is time-sensitive.

OPTION B: Advance the snapshot. Restart the affected agents.
           Use when: the post-snapshot evidence is critical and
           the decision is not yet past the evidence gate.

OPTION C: Quarantine as POST_SNAPSHOT_AUXILIARY.
           The evidence is recorded for audit but does NOT
           influence the EvidenceSufficiencyAssessment, does NOT
           feed into CD2F scoring, and does NOT affect the
           decision outcome.
           Use when: the evidence is informational but not
           decision-critical.
```

The default must be **reject** (Option A), with Option B available as an explicit coordinator decision. Option C is for edge cases where the information is useful for the human reviewer (HITL) but must not contaminate the automated decision path.

**Action:** P0. Fix in Amendment 3. Remove the "allowed but noted" language. Implement reject-by-default with explicit snapshot advancement as the alternative.

---

### Review Section 11: Decision Snapshot -- Deeper Consistency Problem

**Review Finding:** PostgreSQL LSN, Neo4j projection version, and pgvector index version represent three different world-state versions. Agents may still reason over different world versions.

**VERDICT: PARTIALLY AGREE**

The review correctly identifies that the three version numbers can represent different consistency points. In theory:

```
PostgreSQL LSN = 500
Neo4j projection based on LSN = 480
pgvector index based on LSN = 470
```

means agents are reasoning over three different states.

However, the review's proposed solution (a "common consistency epoch") is architecturally cleaner but introduces significant implementation complexity. Requiring all three systems to converge to a common epoch before any decision session starts would add latency and introduce a new synchronization bottleneck.

**Pragmatic Solution:**

Rather than requiring a global consistency epoch, the DecisionSnapshot should:

1. Record the **lag** between each projection and the PostgreSQL baseline:

```python
class DecisionSnapshot(BaseModel):
    # ... existing fields ...
    
    # Consistency assessment
    neo4j_lag_behind_pg: int           # PostgreSQL LSN - Neo4j source LSN
    pgvector_lag_behind_pg: int        # PostgreSQL LSN - pgvector corpus LSN
    
    # Consistency verdict
    consistency_class: Literal[
        "FULLY_CONSISTENT",             # All projections current
        "ACCEPTABLE_LAG",               # Lag within policy thresholds
        "STALE_PROJECTION",             # One or more projections significantly behind
    ]
```

2. The EvidenceSufficiencyService factors consistency class into its assessment:

```
If consistency_class == "STALE_PROJECTION":
    AND stale projection is critical for this disruption type:
        -> Flag in evidence quality assessment
        -> Reduce freshness score for affected evidence
        -> If critical: trigger projection refresh before proceeding
```

3. For topological claims sourced from a stale Neo4j projection, the system cross-validates against PostgreSQL source tables before treating them as authoritative.

This is pragmatically implementable without requiring a global consistency barrier while still detecting and handling the consistency gap the review identifies.

**Action:** P1. Add consistency assessment to DecisionSnapshot in Amendment 3.

---

### Review Section 12: Historical Scenario Freshness

**Review Finding:** `max_fact_age_minutes = 5` is relative to wall-clock time, which makes historical scenario replay impossible (all historical facts appear "stale").

**VERDICT: AGREE -- This is a genuine defect in the freshness model.**

The review correctly identifies that freshness must be relative to the decision's observation time, not to wall-clock `now`.

For a live operational decision:
```
fact_age = now - fact.data_as_of
```

For a historical replay or evaluation scenario:
```
fact_age = observation_cutoff - fact.data_as_of
```

The correction is straightforward:

```python
def compute_fact_age(fact: EvidenceItem, snapshot: DecisionSnapshot) -> timedelta:
    """Fact age is always relative to the decision's observation boundary,
    not to wall-clock time."""
    return snapshot.observation_cutoff - fact.data_as_of
```

This ensures that historical scenarios from 2026-01-01 are evaluated against 2026-01-01 freshness windows, not against today's date.

**Action:** P1. Fix freshness computation in Amendment 3.

---

### Review Section 13: D3-D10 Canonical Numbering (Internal PASS, External FAIL)

**Review Finding:** The canonical numbering is internally consistent but the existing SRS, implementation plan, and repository structure still use the old decomposition.

**VERDICT: PARTIALLY AGREE on the problem, DISAGREE on the severity.**

The review is factually correct that the project's broader documentation has not been updated. However, the review overstates this as "the biggest practical blocker." It is a **documentation synchronization task**, not an architectural defect. It does not block D3 implementation because:

1. D3 (Cognitive Agent Runtime) is a new component that does not exist in the old repository structure.
2. The team working on V2 architecture is the same team that will implement D3 -- there is no risk of two engineers reading different D-number definitions.
3. The old SRS was written for V1 scope. V2 is an architectural evolution that necessarily supersedes parts of the old SRS.

That said, the review is correct that this synchronization must happen. It should be a parallel workstream, not a blocker for D3 coding.

**Action:** P1 (parallel workstream). Create a cross-document reconciliation plan. The architecture evolution document should explicitly declare which predecessor documents are superseded by the hardening revision.

---

### Review Sections 14-15: Agent Ownership -- Broken Claim Contract References

**Review Finding:** The `consumes_from` contracts reference claim types that do not exist in the owning agent's `owned_claim_types`.

**VERDICT: AGREE -- This is a genuine contract-breaking defect.**

The review identifies specific broken references:

| Consumer | References | Owner | Actually Owns |
| :--- | :--- | :--- | :--- |
| Inventory | `supplier_capacity_assessment` | Procurement | `supplier_operational_assessment`, `procurement_cost_analysis`, `alternate_sourcing_feasibility` |
| Logistics | `corridor_risk_assessment` | Risk | `supplier_financial_distress`, `systemic_risk_assessment`, `cascade_failure_analysis`, `regulatory_compliance_status` |
| Risk | `route_vulnerability_assessment` | Logistics | `transport_feasibility`, `route_optimization_analysis`, `carbon_impact_assessment` |
| Risk | `inventory_concentration_data` | Inventory | `inventory_viability_assessment`, `replenishment_analysis`, `asset_condition_report` |
| Finance | `transport_cost_data`, `revenue_impact_data` | Logistics, Demand | Not declared as owned claims |

This means the machine-enforceable ownership system cannot be implemented from the document as written. An agent configured to consume `supplier_capacity_assessment` from Procurement would never receive it because Procurement does not produce a claim of that type.

**Root Cause:** The ownership contracts were written with natural-language intent ("I need capacity data from Procurement") rather than referencing the exact claim types defined in the owning agent's contract.

**Solution: Canonical ClaimTypeRegistry**

A single registry of all valid claim types, from which all agent contracts derive:

```python
class ClaimTypeRegistry:
    """Single source of truth for all claim types in the system.
    Every owned_claim_type, consumed claim reference, and
    forbidden_claim_type must reference an entry in this registry."""
    
    # Procurement & Supplier Agent
    SUPPLIER_OPERATIONAL_ASSESSMENT = "supplier_operational_assessment"
    PROCUREMENT_COST_ANALYSIS = "procurement_cost_analysis"
    ALTERNATE_SOURCING_FEASIBILITY = "alternate_sourcing_feasibility"
    SUPPLIER_CAPACITY_ASSESSMENT = "supplier_capacity_assessment"  # NEW: was missing
    
    # Risk & Resilience Agent
    SUPPLIER_FINANCIAL_DISTRESS = "supplier_financial_distress"
    SYSTEMIC_RISK_ASSESSMENT = "systemic_risk_assessment"
    CASCADE_FAILURE_ANALYSIS = "cascade_failure_analysis"
    REGULATORY_COMPLIANCE_STATUS = "regulatory_compliance_status"
    CORRIDOR_RISK_ASSESSMENT = "corridor_risk_assessment"  # NEW: was missing
    GEOPOLITICAL_RISK_ASSESSMENT = "geopolitical_risk_assessment"  # NEW
    
    # Demand & Commerce Agent
    DEMAND_ASSESSMENT = "demand_assessment"
    COMMERCIAL_IMPACT_ANALYSIS = "commercial_impact_analysis"
    PRICING_RECOMMENDATION = "pricing_recommendation"
    REVENUE_IMPACT_ASSESSMENT = "revenue_impact_assessment"  # NEW: was missing
    
    # Inventory & Asset Management Agent
    INVENTORY_VIABILITY_ASSESSMENT = "inventory_viability_assessment"
    REPLENISHMENT_ANALYSIS = "replenishment_analysis"
    ASSET_CONDITION_REPORT = "asset_condition_report"
    INVENTORY_CONCENTRATION_ASSESSMENT = "inventory_concentration_assessment"  # NEW
    
    # Logistics & Transport Agent
    TRANSPORT_FEASIBILITY = "transport_feasibility"
    ROUTE_OPTIMIZATION_ANALYSIS = "route_optimization_analysis"
    CARBON_IMPACT_ASSESSMENT = "carbon_impact_assessment"
    ROUTE_VULNERABILITY_ASSESSMENT = "route_vulnerability_assessment"  # NEW
    TRANSPORT_COST_ASSESSMENT = "transport_cost_assessment"  # NEW
    
    # Financial & Enterprise Value Agent
    ECONOMIC_CONSEQUENCE_ASSESSMENT = "economic_consequence_assessment"
    COST_IMPACT_ANALYSIS = "cost_impact_analysis"
    WORKING_CAPITAL_PROJECTION = "working_capital_projection"
```

**Validation rule:** At system startup, the Coordinator validates that every `consumes_from` reference in every agent's DomainOwnershipPolicy resolves to an `owned_claim_type` in the referenced agent's policy. If any reference is broken, the system fails to start with a clear error message.

**Action:** P0. Create ClaimTypeRegistry and fix all agent contracts in Amendment 3.

---

### Review Section 16: Broken Candidate Action Type Coverage

**Review Finding:** Agent ownership contracts permit action types (e.g., `promotion_adjustment`, `demand_signal_override`, `risk_mitigation_recommendation`, `compliance_hold`, `financial_impact_flag`, `budget_escalation`) that have no corresponding typed schema in the `ActionParams` discriminated union.

**VERDICT: AGREE -- This is a genuine contract-breaking defect.**

The review is correct that the set of `permitted_action_types` across all agents and the set of typed `ActionParams` schemas are not closed over the same vocabulary. A Demand agent permitted to produce `promotion_adjustment` would have its action rejected by schema validation because no `PromotionAdjustmentParams` exists.

**Solution: Canonical ActionTypeRegistry + Missing Schemas**

```python
class ActionTypeRegistry:
    """Single source of truth for all action types.
    Every permitted_action_type, typed schema, Twin handler,
    execution capability, and policy constraint must derive
    from this registry."""
    
    # Logistics domain
    REROUTE_SHIPMENT = "reroute_shipment"
    EXPEDITE_SHIPMENT = "expedite_shipment"
    CHANGE_FREIGHT_MODE = "change_freight_mode"
    
    # Procurement domain
    SWITCH_SUPPLIER = "switch_supplier"
    INCREASE_PURCHASE_ORDER = "increase_purchase_order"
    CANCEL_PURCHASE_ORDER = "cancel_purchase_order"
    EXPEDITE_PURCHASE_ORDER = "expedite_purchase_order"
    
    # Inventory domain
    REALLOCATE_INVENTORY = "reallocate_inventory"
    ADJUST_SAFETY_STOCK = "adjust_safety_stock"
    QUARANTINE_INVENTORY = "quarantine_inventory"
    
    # Demand domain (NEW schemas needed)
    PROMOTION_ADJUSTMENT = "promotion_adjustment"
    DEMAND_SIGNAL_OVERRIDE = "demand_signal_override"
    
    # Risk domain (NEW schemas needed)
    RISK_MITIGATION_RECOMMENDATION = "risk_mitigation_recommendation"
    COMPLIANCE_HOLD = "compliance_hold"
    
    # Finance domain (NEW schemas needed)
    FINANCIAL_IMPACT_FLAG = "financial_impact_flag"
    BUDGET_ESCALATION = "budget_escalation"
    
    # Universal
    DO_NOTHING = "do_nothing"
```

**Missing typed schemas to create:**

```python
class PromotionAdjustmentParams(BaseModel):
    action_type: Literal["promotion_adjustment"] = "promotion_adjustment"
    promotion_id: str
    adjustment_type: Literal["delay", "cancel", "modify", "extend"]
    original_start_date: str         # ISO 8601
    new_start_date: Optional[str]    # ISO 8601
    revenue_impact_estimate: float   # To be replaced by deterministic evaluation

class DemandSignalOverrideParams(BaseModel):
    action_type: Literal["demand_signal_override"] = "demand_signal_override"
    sku_id: str
    facility_id: str
    override_type: Literal["increase", "decrease", "hold"]
    override_period_days: int
    override_factor: float           # Multiplier applied to base forecast

class RiskMitigationRecommendationParams(BaseModel):
    action_type: Literal["risk_mitigation_recommendation"] = "risk_mitigation_recommendation"
    risk_type: Literal["supplier_financial", "geopolitical", "concentration", "cascade"]
    affected_entity_type: str
    affected_entity_id: str
    mitigation_strategy: str
    urgency: Literal["immediate", "short_term", "medium_term"]

class ComplianceHoldParams(BaseModel):
    action_type: Literal["compliance_hold"] = "compliance_hold"
    entity_type: str
    entity_id: str
    hold_reason: Literal["regulatory", "quality", "safety", "audit"]
    hold_scope: Literal["full", "partial"]
    hold_duration_days: Optional[int]

class FinancialImpactFlagParams(BaseModel):
    action_type: Literal["financial_impact_flag"] = "financial_impact_flag"
    decision_id: str
    flag_type: Literal["budget_exceed", "margin_erosion", "working_capital", "penalty"]
    threshold_exceeded: str
    impact_amount_usd: float         # To be replaced by deterministic evaluation

class BudgetEscalationParams(BaseModel):
    action_type: Literal["budget_escalation"] = "budget_escalation"
    budget_category: str
    current_allocation_usd: float
    requested_additional_usd: float
    justification_claim_ids: list[str]
    escalation_authority: str
```

**Action:** P0. Create ActionTypeRegistry and all missing typed schemas in Amendment 3.

---

### Review Section 17: Candidate Ownership Ambiguity

**Review Finding:** Multiple agents can propose `adjust_safety_stock` and `quarantine_inventory`. The architecture needs to distinguish `action_owner` from `action_proposer`.

**VERDICT: AGREE**

The review correctly identifies that shared action types create ambiguity about who owns the parameter authority. When both Demand and Inventory propose `adjust_safety_stock` with different parameters, who is authoritative?

**Solution: ActionDefinition with ownership model**

```python
class ActionDefinition(BaseModel):
    """Canonical definition of an action type with ownership semantics."""
    action_type: str
    
    # Who owns the action
    primary_owner_agent: str          # Agent with parameter authority
    
    # Who may propose the action
    permitted_proposers: list[str]    # Agents who can suggest this action
    
    # Authority over action parameters
    parameter_authority: str          # Agent that validates/sets parameters
    
    # Authority over impact assessment  
    impact_authority: str             # Agent (or deterministic service) that computes impact
    
    # Which execution capability handles this
    execution_capability_id: str
```

**Example:**

```yaml
adjust_safety_stock:
  primary_owner: inventory_asset
  permitted_proposers: [inventory_asset, demand_commerce]
  parameter_authority: inventory_asset
  impact_authority: deterministic_impact_service
  execution_capability: inventory_management_capability

quarantine_inventory:
  primary_owner: inventory_asset
  permitted_proposers: [inventory_asset, risk_resilience]
  parameter_authority: inventory_asset
  impact_authority: deterministic_impact_service
  execution_capability: inventory_management_capability
```

When Demand proposes `adjust_safety_stock`, it provides the **intent** (why safety stock should change, by how much conceptually). Inventory, as `parameter_authority`, validates and refines the specific parameters. The `deterministic_impact_service` computes the authoritative impact.

**Action:** P1. Add ActionDefinition model in Amendment 3.

---

### Review Section 18: Action Parameters Mix Intent with Derived Impact

**Review Finding:** Typed action schemas include fields like `estimated_transit_days` and `incremental_cost_usd` which are numerical impact values. The LLM agent populates these, but the architecture simultaneously says LLM numerical values are non-authoritative.

**VERDICT: AGREE -- This is a genuine architectural contradiction.**

The review correctly identifies that `RerouteShipmentParams` containing `incremental_cost_usd` creates a channel for LLM-generated numbers to enter the decision path without deterministic validation. The architecture cannot simultaneously say "LLM numbers are non-authoritative" and accept LLM-populated cost fields in typed action schemas.

**Solution: Separate ActionIntent from DeterministicImpactEvaluation**

```python
# WHAT THE AGENT PROPOSES (intent only, no authoritative numbers)
class RerouteShipmentIntent(BaseModel):
    action_type: Literal["reroute_shipment"] = "reroute_shipment"
    shipment_id: str
    original_carrier_id: str
    new_carrier_id: str
    new_route_lane_id: str
    freight_mode: Literal["road", "air", "sea", "rail", "multimodal"]
    # NO cost or time estimates -- those come from deterministic evaluation

# WHAT THE DETERMINISTIC EVALUATOR COMPUTES (authoritative numbers)
class RerouteShipmentImpact(BaseModel):
    estimated_transit_days: int       # From carrier capability data + route model
    incremental_cost_usd: float      # From freight rate tables + surcharges
    carbon_delta_kg: float           # From emission factors
    capacity_utilization: float      # From carrier capacity model
    data_sources: list[str]          # Which authoritative sources were used
    computation_timestamp: datetime
```

The CandidateAction then becomes:

```python
class CandidateAction(BaseModel):
    action_id: str
    action_type: str
    intent: ActionIntent              # Agent-provided intent (no authoritative numbers)
    impact: Optional[ActionImpact]    # Deterministic evaluation (filled by ImpactEvaluator)
    supporting_claims: list[str]
    evidence: list[EvidenceItem]
```

The `ActionImpactEvaluator` is a deterministic service (not an LLM) that:
1. Takes the `ActionIntent`
2. Queries authoritative data sources (freight rates, capacity models, cost tables)
3. Computes the authoritative `ActionImpact`
4. Records which data sources were used

This ensures no LLM-generated numbers enter the CD2F scoring pipeline.

**Action:** P0. Implement intent/impact separation in Amendment 3.

---

### Review Section 19: Candidate Pruning Logic Is Dangerous

**Review Finding:** Dominance pruning and top-K selection occur before Twin simulation, based on LLM-estimated scores. This can eliminate the genuinely best candidate before the Twin evaluates it.

**VERDICT: AGREE -- This is a critical correctness defect.**

The review's example is compelling: if Candidate A has high LLM-estimated cost but would actually cause much less downstream stockout (which only the Twin can reveal), pruning A before the Twin means the best action is never evaluated.

**Correction: Restrict pre-Twin pruning to deterministic criteria only**

The candidate normalization pipeline should be restructured:

```
STEP 1: EXTRACT
    Collect all candidate actions

STEP 2: SCHEMA VALIDATION
    Reject candidates with invalid/missing parameters
    DETERMINISTIC: yes -- schema validation is binary

STEP 3: ENTITY VALIDATION  
    Verify referenced entities exist
    DETERMINISTIC: yes -- entity existence is factual

STEP 4: HARD-CONSTRAINT PRE-CHECK
    Eliminate candidates violating hard constraints
    DETERMINISTIC: yes -- hard constraints are binary
    Source: DecisionPolicy.hard_constraints + deterministic impact evaluation

STEP 5: DEDUPLICATION
    Merge semantically identical candidates
    DETERMINISTIC: yes -- structural comparison

STEP 6: SAFE DOMINANCE PRUNING (REVISED)
    A candidate is dominated ONLY if:
        - It is strictly worse than another on ALL dimensions
        - Using DETERMINISTIC impact evaluations, not LLM estimates
        - The comparison uses authoritative computed values
    
    If the impact evaluation is uncertain (based on LLM estimates):
        -> DO NOT prune. Retain for Twin evaluation.

STEP 7: CANDIDATE BUDGET ENFORCEMENT (REVISED)
    If remaining candidates > max_simulation_branches:
        -> Retain top-K by UPPER CONFIDENCE BOUND, not point estimate
        -> Always retain at least one candidate per domain
        -> Always include "do nothing + buffer" baseline
    
    Selection criterion:
        UCB(c) = estimated_score(c) + alpha * uncertainty(c)
    
    This ensures high-uncertainty candidates with potential upside
    are not eliminated before the Twin can evaluate them.

STEP 8: COMBINATION SYNTHESIS
    (unchanged)
```

The key changes:
- Step 6 only prunes based on **deterministic** impact evaluations, never LLM estimates
- Step 7 uses **upper confidence bound** rather than point estimates for budget enforcement
- No candidate is eliminated before Twin unless it is provably infeasible or provably dominated by deterministic criteria

**Action:** P0. Fix candidate pruning algorithm in Amendment 3.

---

### Review Section 20: Candidate Pruning Must Be Uncertainty-Aware

**Review Finding:** A candidate with high estimated score and high uncertainty should not be discarded because its point estimate is slightly lower than a candidate with low uncertainty.

**VERDICT: AGREE**

This is a corollary to Section 19. The solution (upper confidence bound for top-K selection) is already incorporated in the revised Step 7 above.

**Action:** Covered by Section 19 response.

---

### Review Section 21: Pareto Check Is Not Actual Pareto Analysis

**Review Finding:** The architecture checks if two scalar scores are close (`|J1 - J2| < threshold`) and calls this "Pareto ambiguity." This is score proximity, not Pareto analysis.

**VERDICT: AGREE -- The terminology is incorrect and the logic is incomplete.**

The review is technically correct. Pareto dominance requires comparing candidates across **all objective dimensions independently**, not comparing their weighted scalar scores.

Two candidates can have:
- Nearly identical scalar scores (J1 approximately equal to J2)
- But one strictly dominates the other on every dimension

In that case, calling it "Pareto ambiguity" is wrong -- there is a clear winner.

Conversely, two candidates can have:
- Very different scalar scores
- But each is superior on a different critical dimension

This is genuine Pareto non-dominance, but the scalar comparison would miss it.

**Corrected Implementation:**

```
STAGE 4: PARETO AND AMBIGUITY ANALYSIS (Revised)

    STEP 4a: PARETO DOMINANCE
        For each pair of feasible candidates (A, B):
            If A >= B on EVERY objective dimension
            AND A > B on at least ONE dimension:
                -> B is Pareto-dominated by A
                -> Remove B from the Pareto frontier
        
        Output: Pareto frontier (set of non-dominated candidates)
    
    STEP 4b: FRONTIER ANALYSIS
        If Pareto frontier has exactly ONE candidate:
            -> Clear winner. Proceed to execution authorization.
        
        If Pareto frontier has > 1 candidate:
            -> Compute weighted scalar scores for frontier candidates
            -> If |J_final(rank_1) - J_final(rank_2)| < policy.ambiguity_threshold:
                -> GENUINE PARETO AMBIGUITY
                -> Generate trade-off summary showing dimensional comparison
                -> HITL escalation with Pareto frontier visualization
            -> Else:
                -> Policy weights resolve the trade-off
                -> Select rank_1 as winner
                -> Record that selection was policy-weight-dependent (not Pareto-dominant)
    
    STEP 4c: DECISION CONFIDENCE CLASSIFICATION
        decision_confidence = categorize based on:
            - Was the winner Pareto-dominant? (highest confidence)
            - Was the winner policy-weight-selected from a small frontier?
            - Was the winner barely distinguishable from alternatives?
```

This is a genuine Pareto analysis followed by policy-based selection within the Pareto frontier, which is mathematically correct.

**Action:** P0. Replace the scalar proximity check with proper Pareto analysis in Amendment 3.

---

### Review Section 22: Candidate-Relative Normalization Creates Decision Instability

**Review Finding:** Normalizing metrics to [0,1] relative to the candidate set means adding or removing a candidate changes the scores of all other candidates. This violates decision stability.

**VERDICT: AGREE -- This is a genuine mathematical defect.**

The review's example is clear: if cost(A)=100, cost(B)=200, then A gets 0.0 and B gets 1.0. Adding cost(C)=1000 changes A's normalized score without A itself changing. This means the ranking can be manipulated by introducing irrelevant candidates (a form of the "independence of irrelevant alternatives" violation).

**Correction: Policy-Fixed Reference Scales**

Each objective dimension should be normalized against a **policy-defined reference scale**, not against the candidate set:

```python
class ObjectiveNormalization(BaseModel):
    """Policy-defined reference scales for objective normalization.
    These scales are fixed per profile, independent of the candidate set."""
    
    cost_reference_usd: float = 100000.0       # Reference cost scale
    risk_reference: float = 1.0                 # Risk is already [0,1]
    service_reference_pct: float = 100.0        # Service level reference
    lead_time_reference_days: float = 30.0      # Reference lead time
    carbon_reference_kg: float = 10000.0        # Reference carbon scale
    cash_flow_reference_usd: float = 50000.0    # Reference cash flow scale
    inventory_reference_days: float = 30.0      # Reference days-of-supply

def normalize_cost(cost_delta: float, ref: ObjectiveNormalization) -> float:
    """Normalize cost impact against policy reference scale."""
    return min(1.0, max(0.0, cost_delta / ref.cost_reference_usd))
```

This means:
- A candidate with cost_delta = $50,000 always normalizes to 0.5 (against $100,000 reference)
- This normalization is the same regardless of what other candidates exist
- The reference scales are defined in the profile YAML and can be tuned empirically

**The reference scales must be:**
- Profile-defined (from DecisionPolicy)
- Domain-calibrated (based on the enterprise's typical decision magnitudes)
- Versioned (changes to reference scales are tracked)

**Action:** P0. Replace candidate-relative normalization with policy-fixed reference scales in Amendment 3.

---

### Review Section 23: Objective Weight Transformations Underdefined

**Review Finding:** How are INR, days, risk probability, fill rate, and CO2 converted into comparable normalized values?

**VERDICT: PARTIALLY AGREE**

The review is correct that the transformation from raw units to normalized scores is as important as the weights. The policy-fixed reference scales (Section 22 correction) partially address this, but the normalization functions themselves need specification.

**Solution:** Each objective dimension gets a normalization function defined in the profile:

```yaml
normalization:
  cost:
    type: linear
    reference_scale_usd: 100000
    direction: minimize    # Higher cost = worse
  risk:
    type: direct           # Already [0,1]
    direction: minimize
  service_level:
    type: gap_from_target
    target: 98.0           # Target service level %
    reference_gap: 10.0    # 10% gap = normalized 1.0
    direction: minimize    # Larger gap = worse
  lead_time:
    type: linear
    reference_scale_days: 30
    direction: minimize
  carbon:
    type: linear
    reference_scale_kg: 10000
    direction: minimize
  cash_flow:
    type: linear
    reference_scale_usd: 50000
    direction: minimize
  inventory_health:
    type: gap_from_target
    target_dos: 14.0       # Target days of supply
    reference_gap_dos: 10.0
    direction: minimize
```

These are profile-defined and empirically tunable during D10 evaluation.

**Action:** P1. Add normalization function specifications in Amendment 3.

---

### Review Section 24: CD2F Should Not Claim to Be "Pure"

**Review Finding:** CD2F depends on upstream subsystem outputs (R_i, evidence authority, simulation fidelity). Calling it "pure computation" obscures this dependency.

**VERDICT: DISAGREE**

CD2F IS a pure computation engine in the formal sense: given the same `DecisionContext` (evidence, claims, impacts, simulations, reliability scores, policy), it produces the same output deterministically. The fact that the inputs are produced by complex upstream subsystems does not make CD2F impure -- it makes the **system** complex.

The review's suggested alternative phrasing:

> "CD2F is a deterministic arbitration engine over an explicitly materialized DecisionContext"

is more precise, and I will adopt it as documentation improvement, but the architectural claim is not wrong.

**Action:** Documentation refinement. Update CD2F description in Amendment 3.

---

### Review Section 25: Twin Timeout Handling

**Review Finding:** Allowing CD2F to proceed without simulation results after Twin timeout undermines the architecture's central counterfactual decision mechanism.

**VERDICT: PARTIALLY AGREE**

The review is correct that universally allowing CD2F to proceed without simulation undermines the Twin's purpose. However, the review's proposed three-tier solution (TwinRequired/TwinOptional/TwinAdvisory) is the right direction.

**Correction:**

```python
class TwinRequirement(str, Enum):
    REQUIRED = "REQUIRED"          # Twin must complete; timeout -> HITL
    RECOMMENDED = "RECOMMENDED"    # Twin should run; timeout -> CD2F with degraded flag
    ADVISORY = "ADVISORY"          # Twin runs if budget allows; timeout -> CD2F normally

# Determination logic (in DecisionPolicy)
def determine_twin_requirement(
    disruption: DisruptionEvent,
    candidates: list[CandidateAction],
    policy: SimulationPolicy
) -> TwinRequirement:
    
    # If any candidate has external side effects above threshold
    if any(c.impact.total_cost_usd > policy.twin_required_cost_threshold
           for c in candidates):
        return TwinRequirement.REQUIRED
    
    # If disruption type is novel (low precedent match)
    if disruption.precedent_confidence < 0.50:
        return TwinRequirement.REQUIRED
    
    # If decision involves multi-domain cascade
    if disruption.cascade_potential > 0.70:
        return TwinRequirement.REQUIRED
    
    # Standard cases
    if any(c.impact.total_cost_usd > policy.simulation_trigger_threshold_usd
           for c in candidates):
        return TwinRequirement.RECOMMENDED
    
    return TwinRequirement.ADVISORY
```

**Failure response by requirement level:**

```
REQUIRED + timeout -> NO autonomous decision. HITL escalation. (Tier-3)
RECOMMENDED + timeout -> CD2F proceeds with DEGRADED_MODE flag.
                         Autonomy reduced (max Tier-2). Uncertainty penalty applied.
ADVISORY + timeout -> CD2F proceeds normally. Log timeout.
```

**Action:** P0. Add TwinRequirement determination to Amendment 3.

---

### Review Section 26: Twin Trigger Based on USD Is Too Narrow

**Review Finding:** `simulation_trigger_threshold_usd` assumes financial magnitude determines Twin necessity, but regulatory/safety/service-level impacts may be more important.

**VERDICT: AGREE**

The correction (multi-dimensional materiality assessment) is already partially addressed by the TwinRequirement determination logic above. The trigger should consider:

```python
class SimulationMateriality(BaseModel):
    """Multi-dimensional assessment of whether Twin simulation is warranted."""
    financial_exposure_usd: float
    service_level_impact: float         # Expected SL degradation
    risk_exposure: float                # Systemic risk score
    regulatory_relevance: bool          # Does this involve regulated products?
    cascade_potential: float            # Multi-node impact probability
    novelty_score: float               # How unlike historical precedents?
    
    def is_material(self, policy: SimulationPolicy) -> bool:
        return (
            self.financial_exposure_usd > policy.financial_threshold_usd
            or self.service_level_impact > policy.service_threshold
            or self.risk_exposure > policy.risk_threshold
            or self.regulatory_relevance
            or self.cascade_potential > policy.cascade_threshold
            or self.novelty_score > policy.novelty_threshold
        )
```

**Action:** P1. Replace USD-only trigger with SimulationMateriality in Amendment 3.

---

### Review Section 27: Simulation Fidelity Composite

**Review Finding:** `composite_fidelity` is an arbitrary scalar without defined weighting.

**VERDICT: PARTIALLY DISAGREE**

The composite is necessary for CD2F to apply a scalar uncertainty penalty. The weights should be profile-defined and empirically calibrated during D10, which is exactly what the evaluation phase is for. Requiring the weights to be formally defined before D3 implementation begins is premature.

**Refinement:** Make the fidelity weights explicitly configurable in the SimulationPolicy:

```yaml
simulation_policy:
  fidelity_weights:
    data_freshness: 0.25
    entity_coverage: 0.25
    calibration: 0.30
    applicability: 0.15
    invariant_penalty: 0.05    # Per violation
```

**Action:** P1. Add fidelity weight configuration to SimulationPolicy in Amendment 3.

---

### Review Section 28: R_i Floor of 0.20 Is Problematic

**Review Finding:** Forcing `min_r_i = 0.20` means a repeatedly failing agent continues influencing decisions.

**VERDICT: DISAGREE**

The R_i floor exists to prevent **permanent exclusion**, which is a worse failure mode than temporary over-inclusion. An agent permanently locked out at R_i = 0 can never recover, even if its model is retrained and improved. The floor ensures every agent always has a minimum opportunity to contribute.

However, the review's suggestion of an **advisory-only status** is a legitimate refinement:

```python
class AgentInfluenceStatus(str, Enum):
    FULL = "FULL"               # R_i >= 0.40: full participation
    REDUCED = "REDUCED"         # 0.20 <= R_i < 0.40: participates but proposals are 
                                # flagged for extra scrutiny
    ADVISORY = "ADVISORY"       # R_i < 0.20: proposals are recorded but do NOT enter
                                # CD2F scoring. Agent continues generating proposals
                                # for R_i recalibration purposes.
```

This is better than removing the floor entirely. The agent at ADVISORY status still runs (allowing its R_i to recover if its model improves) but does not influence decisions.

**Action:** P1. Add AgentInfluenceStatus to R_i governance in Amendment 3. Keep the floor at 0.20 for REDUCED status; below 0.20 becomes ADVISORY.

---

### Review Section 29: R_i Not Fully Outcome-Causal

**Review Finding:** If an agent proposes A but CD2F chooses B, the outcome tells you little about whether A's reasoning was correct. R_i can become a noisy proxy.

**VERDICT: PARTIALLY AGREE**

The review correctly identifies causal attribution as a measurement challenge. However, the architecture already includes stratified R_i (by disruption type, decision class, model version) which partially addresses this.

**Refinement:** Decompose R_i into sub-metrics:

```python
class DecomposedReliability(BaseModel):
    """Separate reliability dimensions for clearer causal attribution."""
    
    # Did the agent's claims about current state match reality?
    claim_accuracy: float
    
    # Did the agent's confidence scores correlate with actual accuracy?
    calibration_quality: float
    
    # Did the agent's proposed actions satisfy constraints?
    constraint_compliance: float
    
    # When the agent's proposed action WAS selected, did it work?
    # (Only measurable for sessions where this agent's action was chosen)
    action_outcome_quality: Optional[float]
    
    # Composite
    composite_r_i: float
```

The `action_outcome_quality` is only computed when the agent's action was actually selected, avoiding the causal attribution problem for non-selected proposals.

**Action:** P1. Add decomposed reliability metrics to Amendment 3.

---

### Review Section 30: Event-Sourced Deliberation Table Assessment

**Review Finding:** Strong improvement. The events/views split is architecturally sound.

**VERDICT: AGREE**

No action needed. Confirmation that the event-sourced Deliberation Table design is correct.

---

### Review Section 31: Event Sequence Allocation Underspecified

**Review Finding:** Six agents producing events concurrently need a defined mechanism for assigning monotonically increasing sequence numbers.

**VERDICT: AGREE**

**Solution: PostgreSQL Session-Scoped Sequence**

```sql
-- Each session gets a dedicated sequence for event ordering
CREATE SEQUENCE IF NOT EXISTS deliberation_seq_{session_id}
    START WITH 1 INCREMENT BY 1;

-- Or, more practically, use a session aggregate row:
UPDATE deliberation_sessions
SET current_sequence = current_sequence + 1
WHERE session_id = $1
RETURNING current_sequence;
```

In practice, the Coordinator is the single writer to the Deliberation Table event stream (agents submit proposals to the Coordinator, which posts events). This means sequence allocation is naturally serialized through the Coordinator's event posting logic, not distributed across agents.

**The Coordinator is the serialization point:**

```
Agent submits proposal -> Coordinator
Coordinator validates -> Coordinator posts PROPOSAL_SUBMITTED event
Coordinator assigns sequence_number from session counter
```

No concurrent writer contention exists because all events are posted by the Coordinator, not directly by agents.

**Action:** P1. Clarify that the Coordinator is the single event writer and define the sequence allocation mechanism in Amendment 3.

---

### Review Section 32: Aggregate Version vs Session Sequence

**Review Finding:** The relationship between `SCOFEvent.aggregate_version` and `DeliberationEvent.sequence_number` is undefined.

**VERDICT: AGREE**

**Clarification:**

```
aggregate_version:
    Monotonically increasing PER AGGREGATE INSTANCE.
    Used for consumer idempotency.
    Example: deliberation_item "DI-001" has aggregate_version 1, 2, 3...

sequence_number:
    Monotonically increasing PER SESSION.
    Used for session-level event ordering.
    Example: session "S-001" has sequence 1, 2, 3, 4...

Relationship:
    A single session event has BOTH a session sequence_number
    AND an aggregate_version for the aggregate it affects.
    
    These are INDEPENDENT orderings:
        sequence_number 72 might affect aggregate "DI-003" at aggregate_version 5
        sequence_number 73 might affect aggregate "DI-007" at aggregate_version 2
    
    Consumer idempotency uses aggregate_version.
    Session replay uses sequence_number.
```

**Action:** P1. Add explicit relationship definition in Amendment 3.

---

### Review Section 33: Event Partitioning by Session

**Review Finding:** Partitioning by session_id creates too many partitions at enterprise scale.

**VERDICT: DISAGREE**

At SCOF's operational scale (a research/enterprise decision system, not a high-frequency trading platform), the number of concurrent sessions is measured in hundreds, not millions. PostgreSQL handles this scale comfortably with session-based partitioning.

Furthermore, the primary access pattern is "retrieve all events for session X in order" -- which is exactly what session-based partitioning optimizes for.

If scale becomes a concern in the future, the migration path is well-understood: switch to time-based partitioning with a composite index on (session_id, sequence_number). But designing for hypothetical enterprise scale before D3 implementation is premature optimization.

**Action:** None. Note as a future scalability consideration.

---

### Review Section 34: Replay Is Not Truly Exact

**Review Finding:** LLM inference reproducibility depends on hardware, quantization, runtime, and floating-point behavior, not just model version and random seed.

**VERDICT: PARTIALLY AGREE -- but the architecture already addresses this.**

Amendment 2 Section 25 already defines two replay types:

```
EXACT:      Same state + same models + same seeds = identical replay
ANALYTICAL: Different models/state; replay the decision logic
```

The review is correct that EXACT replay is only achievable under controlled conditions. The refinement is to qualify what "EXACT" requires:

```python
class ReplayFidelityRequirements(BaseModel):
    """What is needed for EXACT replay."""
    requires_same_model_weights: bool = True
    requires_same_inference_engine: bool = True
    requires_same_quantization: bool = True
    requires_same_hardware_class: bool = True  # GPU type affects float behavior
    requires_same_decoding_params: bool = True
    requires_frozen_tool_responses: bool = True  # Must replay recorded tool outputs
    
    # If any requirement cannot be met, replay type is automatically ANALYTICAL
```

The key insight: for EXACT replay, the system should replay **recorded tool responses and retrieval results** rather than re-executing queries. This makes EXACT replay achievable regardless of infrastructure differences.

**Action:** P1. Qualify EXACT replay requirements and add tool response replay in Amendment 3.

---

### Review Section 35: Replay Manifest Needs Retrieval Artifacts

**Review Finding:** The manifest records `embedding_model_version` but not the actual retrieval results, query hashes, or tool outputs.

**VERDICT: AGREE**

For EXACT replay, the manifest must include references to recorded retrieval artifacts:

```python
class DecisionReplayManifest(BaseModel):
    # ... existing fields ...
    
    # Retrieval artifacts (NEW)
    retrieval_artifacts: list[RetrievalArtifact]
    tool_invocation_log: list[ToolInvocationRecord]
    
class RetrievalArtifact(BaseModel):
    retrieval_id: str
    agent_id: str
    capability_id: str
    query_hash: str
    result_ids: list[str]
    result_order: list[int]
    result_hash: str
    
class ToolInvocationRecord(BaseModel):
    invocation_id: str
    tool_id: str
    tool_version: str
    input_hash: str
    output_hash: str
    output_ref: str                # Reference to stored output
```

**Action:** P1. Add retrieval artifacts to ReplayManifest in Amendment 3.

---

### Review Section 36: Hot-Path Cache Keying Too Coarse

**Review Finding:** Cache key `(session_id, agent_id, entity_type, entity_id)` is insufficient because different queries about the same entity return different data.

**VERDICT: AGREE**

The review's example is correct: querying SUP-0042 for operational performance vs. financial risk vs. contract status returns different results but would share the same cache key.

**Corrected cache key:**

```python
cache_key = (
    session_id,
    snapshot_id,           # Snapshot binding
    agent_id,
    capability_id,         # Which MCP capability was invoked
    query_hash,            # Hash of query parameters
)
```

This ensures different queries about the same entity are cached separately, while identical queries within the same session hit the cache.

**Action:** P1. Fix cache key specification in Amendment 3.

---

### Review Section 37: Governance Should Fail Closed

**Review Finding:** If the audit logging fails, should the agent still be able to use the retrieved data?

**VERDICT: AGREE for critical evidence, PARTIALLY AGREE for general telemetry.**

**Correction:**

```python
class GovernedDataAccessPolicy(BaseModel):
    # ... existing fields ...
    
    # Governance failure policy
    audit_failure_policy: Literal[
        "FAIL_CLOSED",      # Retrieval fails if audit cannot be recorded
        "DEGRADE_WITH_WARNING",  # Retrieval proceeds but evidence is flagged
    ]
```

For evidence that feeds into the decision path (EvidenceSufficiencyAssessment, CD2F scoring):
- `audit_failure_policy = FAIL_CLOSED`

For operational telemetry and non-critical lookups:
- `audit_failure_policy = DEGRADE_WITH_WARNING`

**Action:** P1. Add audit failure policy to governance model in Amendment 3.

---

### Review Section 38: Capability Authorization Incomplete

**Review Finding:** `authorization_scope = AGENT` does not mean every agent should access every READ_ONLY capability.

**VERDICT: PARTIALLY AGREE**

The DomainOwnershipPolicy already constrains which agents access which capabilities via the `consumes_from` and `owned_entity_types` contracts. The capability authorization is implicitly agent-scoped through the ownership model.

However, making this explicit with a binding is cleaner:

```python
class AgentCapabilityBinding(BaseModel):
    agent_id: str
    capability_id: str
    permitted_entity_scope: list[str]  # Which entity types this agent can query
    read_only: bool = True
```

**Action:** P1. Add explicit agent-capability binding model in Amendment 3.

---

### Review Section 39: Cancellation Race Conditions

**Review Finding:** A Twin simulation completing after session cancellation could resurrect the session.

**VERDICT: AGREE**

**Correction: Terminal State Guard**

```python
def handle_event(event: DeliberationEvent, session: DeliberationSessionView):
    # Terminal state guard
    if session.status in {"CANCELLED", "CLOSED", "EXPIRED"}:
        if event.event_type not in {"SESSION_CANCELLED", "SESSION_CLOSED"}:
            # Reject late event
            log_warning(f"Rejected late event {event.event_id} for terminal session {session.session_id}")
            return  # Do not apply
    
    # Normal event processing
    apply_event(session, event)
```

Additionally, `SESSION_CANCELLED` must be idempotent -- receiving it multiple times (from Kafka at-least-once delivery) must not cause errors.

**Action:** P1. Add terminal state guards to event processing in Amendment 3.

---

### Review Sections 40-41: Execution Outcome and Replanning

**Review Finding:** Execution outcome needs verification status; replanning needs explicit state inheritance.

**VERDICT: PARTIALLY AGREE on 40, AGREE on 41.**

For Section 40: In the SCOF V2 research context, execution is entirely simulated (Twin Layer 3). Real-world execution adapters (ERP, TMS) do not exist yet. Adding `verification_status` for real-world execution is architecturally correct but not needed until real-world adapters are built. I will include the schema but mark it as future-scope.

For Section 41: The review is correct that replanning sessions must explicitly bind to the post-execution state:

```python
class ReplanningContext(BaseModel):
    """Context for a replanning decision session."""
    original_decision_id: str
    original_session_id: str
    execution_outcome: ExecutionOutcome
    post_execution_snapshot: DecisionSnapshot  # Snapshot AFTER partial execution
    causation_event_id: str
    
    # What the replanning session inherits
    inherited_constraints: list[HardConstraint]  # From original decision
    excluded_actions: list[str]  # Actions that already failed
```

**Action:** P1. Add ReplanningContext in Amendment 3.

---

### Review Section 42: DecisionRecord actual_outcome Is Untyped

**Review Finding:** `actual_outcome: Optional[dict]` should be a structured `OutcomeObservation`.

**VERDICT: AGREE**

```python
class OutcomeObservation(BaseModel):
    """Structured observation of actual outcomes for R_i calibration."""
    observation_id: str
    decision_id: str
    
    # Measurement window
    observation_window_start: datetime
    observation_window_end: datetime
    
    # Actual metrics (same dimensions as DecisionObjective)
    actual_cost_usd: Optional[float]
    actual_service_level: Optional[float]
    actual_lead_time_days: Optional[float]
    actual_risk_realized: Optional[bool]
    actual_inventory_position: Optional[float]
    actual_carbon_kg: Optional[float]
    actual_cash_impact_usd: Optional[float]
    
    # Data provenance
    data_source: str
    observed_at: datetime
    observation_snapshot_version: int
    
    # Quality
    observation_completeness: float   # What fraction of expected metrics are available
    observation_confidence: float     # How reliable is the measurement
```

**Action:** P1. Replace untyped dict with OutcomeObservation in Amendment 3.

---

### Review Sections 43-45: Cross-Examination, Tier-1 RAG Correlation, Deliberation Loop Independence

**Review Finding:** 
- Section 43: Independence protocol is correct.
- Section 44: Shared Tier-1 RAG can create correlated errors.
- Section 45: Round-2 outputs are simulation-informed and not independent.

**VERDICT:** AGREE on 44 and 45 (measurement concerns for D10), AGREE on 43 (confirmation).

These are evaluation methodology concerns, not architectural defects. The architecture is correct -- the measurement in D10 needs to account for:
1. Shared-evidence correlation (do agents agree because they are correct, or because they received the same wrong Tier-1 context?)
2. Round-1 vs Round-2 independence distinction (conformity analysis must separate pre-cross-examination from post-cross-examination reasoning)

**Action:** P2. Add shared-evidence correlation measurement and round distinction to D10 evaluation protocol in Amendment 3.

---

### Review Section 46: Failure Responses Too Permissive

**Review Finding:** `RETRIEVAL_FAILURE -> use stale data` and `AGENT_TIMEOUT -> ML-only fallback` should depend on claim criticality.

**VERDICT: PARTIALLY AGREE**

The review is correct that blanket fallback policies are too permissive for critical evidence. The failure response should be claim-criticality-dependent:

```python
def determine_fallback_policy(
    failure: FailureType,
    claim_criticality: Literal["CRITICAL", "IMPORTANT", "SUPPLEMENTARY"],
    policy: DecisionPolicy
) -> FailureResponse:
    
    if claim_criticality == "CRITICAL":
        if failure == FailureType.RETRIEVAL_FAILURE:
            return FailureResponse.HITL_ESCALATION  # Do not use stale data
        if failure == FailureType.AGENT_TIMEOUT:
            if policy.ml_fallback_validated_for_disruption_type:
                return FailureResponse.ML_FALLBACK_WITH_FLAG
            else:
                return FailureResponse.HITL_ESCALATION
    
    if claim_criticality == "IMPORTANT":
        return FailureResponse.FALLBACK_WITH_REDUCED_CONFIDENCE
    
    return FailureResponse.STANDARD_FALLBACK
```

**Action:** P1. Add claim-criticality-dependent fallback policy in Amendment 3.

---

### Review Section 47: DecisionPolicy Duplicate Sources of Truth

**Review Finding:** `DecisionObjective.max_autonomous_cost_usd` duplicates `ExecutionPolicy.max_autonomous_cost_usd`.

**VERDICT: AGREE**

**Resolution:** These serve different purposes but should not be independently configurable:

```
DecisionObjective.max_acceptable_risk:
    Used by CD2F to determine if a candidate is feasible.
    "Is this risk level acceptable for any decision?"

ExecutionPolicy.max_autonomous_risk:
    Used by ExecutionPolicyService to determine if HITL is required.
    "Is this risk level acceptable for AUTONOMOUS execution?"

Invariant:
    max_autonomous_risk <= max_acceptable_risk
    (You cannot autonomously execute something that is not even acceptable)

Similarly:
    max_autonomous_cost_usd (ExecutionPolicy) ONLY.
    Remove from DecisionObjective.
    CD2F does not need a cost threshold -- it uses the objective function.
    Only ExecutionPolicyService needs to check autonomous cost limits.
```

**Action:** P0. Deduplicate policy values and define invariant relationships in Amendment 3.

---

### Review Section 48: Policy Versioning Needs Hash

**Review Finding:** Two deployments can claim version "1.0.0" with different contents. Need policy_hash.

**VERDICT: AGREE**

```python
class DecisionPolicy(BaseModel):
    # ... existing fields ...
    
    # Integrity (NEW)
    policy_hash: str             # SHA-256 of the serialized policy content
    profile_hash: str            # SHA-256 of the complete profile
```

**Action:** P1. Add policy and profile hashes in Amendment 3.

---

### Review Sections 49-50: Policy Precedence Type System, Hard-Coded Safety

**Review Finding:** Policy precedence should be a formal type system, not a textual list. Hard-coded safety violates profile-driven architecture.

**VERDICT:** 
- Section 49: PARTIALLY DISAGREE. A formal type system for policy precedence is premature. The textual hierarchy with the corrections from Section 9 is sufficient.
- Section 50: AGREE. Already addressed in Section 9 response.

**Action:** Section 49: No action. Section 50: Covered by Section 9 response.

---

### Review Section 51: Snapshot Needs Trigger-State Binding

**Review Finding:** If Kafka delivers a disruption event at T=10:05 that occurred at T=10:00, the snapshot created at 10:05 includes state changes from 10:01-10:04 that are post-event.

**VERDICT: AGREE**

**Correction:**

```python
class DecisionSnapshot(BaseModel):
    # ... existing fields ...
    
    # Trigger binding (NEW)
    trigger_event_id: str
    trigger_event_timestamp: datetime
    trigger_event_sequence: Optional[int]   # Kafka offset or event sequence
    
    # The observation_cutoff should be trigger_event_timestamp for
    # scenarios where temporal consistency with the trigger is required.
    # For live operational decisions, observation_cutoff = now is acceptable.
```

For evaluation/replay scenarios:
```
observation_cutoff = trigger_event_timestamp
```

For live operational decisions:
```
observation_cutoff = session_start_time (= approximately now)
```

**Action:** P1. Add trigger-state binding to DecisionSnapshot in Amendment 3.

---

### Review Sections 52-53: Twin Manifest and Reproducibility

**Review Finding:** The manifest needs to distinguish world snapshot from scenario perturbation. "Same manifest = same result" requires container image digests.

**VERDICT: PARTIALLY AGREE on 52, PARTIALLY DISAGREE on 53.**

Section 52 (scenario baseline manifest): The SimulationManifest already contains `baseline_snapshot_id` and `action_set`. The scenario perturbation IS the action set applied to the baseline. No additional structure needed.

Section 53 (container image digests): This level of reproducibility (container_image_digest, dependency_lock_hash, simulation_engine_build_hash) is a deployment-time concern, not an architecture-level specification. The architecture should define WHAT needs to be reproducible; the CI/CD pipeline ensures HOW.

**Action:** P2. Note environmental reproducibility requirements in the ReplayManifest documentation.

---

### Review Section 54: Preemption Semantics Underspecified

**Review Finding:** "Preempt" needs to define: pause, cancel, checkpoint, kill, resume.

**VERDICT: PARTIALLY AGREE**

This is an implementation concern for D8 (Event & Runtime Backbone). The architecture should define the policy; the implementation defines the mechanism:

```python
class PreemptionPolicy(BaseModel):
    preemption_mode: Literal[
        "COOPERATIVE_CANCEL",    # Signal cancellation; worker finishes current unit
        "IMMEDIATE_CANCEL",      # Cancel immediately; branch state may be inconsistent
        "CHECKPOINT_CANCEL",     # Checkpoint current state, then cancel
    ]
    default_mode: str = "COOPERATIVE_CANCEL"
    max_cooperative_wait_ms: int = 5000
```

**Action:** P1. Add preemption policy to Amendment 3.

---

### Review Section 55: Worker Reservation

**Review Finding:** Worker allocations should be labeled as "initial policy" not architecture.

**VERDICT: DISAGREE**

Amendment 2 already places these values in the `SimulationPolicy` and `PrioritySLAPolicy` sections of the DecisionPolicy, which is loaded from the profile YAML. They ARE profile defaults, not architectural constants. The review's concern is already addressed.

**Action:** None.

---

### Review Section 56: MCP Latency Target

**Review Finding:** 20ms per MCP call is aggressive.

**VERDICT: PARTIALLY AGREE**

The 20ms target is a benchmark target for local Docker deployment. The architecture already treats latency as an evaluation criterion (D10). The target should be labeled as a benchmark expectation, not a guaranteed bound:

```yaml
retrieval_policy:
  mcp_latency_target_ms: 20       # Benchmark target, not guaranteed bound
  mcp_latency_budget_p95_ms: 50   # p95 latency budget including retries
```

**Action:** P1. Relabel latency target as benchmark in Amendment 3.

---

### Review Sections 57-64: Evaluation Design

**VERDICTS:**

| Section | Finding | Verdict | Rationale |
| :--- | :--- | :--- | :--- |
| 57 | B0-B7 incomplete | AGREE | Must define all 8 baselines explicitly |
| 58 | p<0.05 paired t-test too prescriptive | AGREE | Use distribution-appropriate tests |
| 59 | Calibration r>=0.60 is wrong metric | AGREE | Use Brier score, ECE, reliability diagrams |
| 60 | Cohen's Kappa needs clarification | PARTIALLY AGREE | Appropriate for binary; use Krippendorff for multi-class |
| 61 | Hindsight optimal can create evaluator leakage | AGREE | Separate oracle from Twin |
| 62 | Twin calibration vs evaluation split | AGREE | Enforce train/eval split |
| 63 | Policy sensitivity analysis needed | AGREE | Add to D10 protocol |
| 64 | B0 must be frozen before D3 | AGREE | Freeze B0 definition |

**Complete B0-B7 Ladder:**

| Baseline | Configuration | Components Enabled | What It Tests |
| :--- | :--- | :--- | :--- |
| B0 | Deterministic rule heuristic | No agents, no LLM, no Twin. Hard-coded if-then-else rules for supplier delay response. | Is intelligence better than rules? |
| B1 | Single generalist agent | One LLM+ML agent, no specialization, no cross-examination. Direct proposal to CD2F. | Does ML+LLM add value? |
| B2 | Six independent specialists | All six agents independently assess. No cross-examination. Proposals directly to CD2F. | Does specialization matter? |
| B3 | Specialists + cross-examination | B2 + Deliberation Table + cross-examination protocol. No Twin. | Does deliberation improve quality? |
| B4 | B3 + evidence sufficiency gate | B3 + multi-dimensional evidence gate. Insufficient evidence escalates to HITL. No Twin. | Does evidence gating prevent bad decisions? |
| B5 | B4 + Twin simulation | B4 + Twin counterfactual evaluation for all candidates. Naive scoring (no formal objective). | Does simulation add value? |
| B6 | B5 + formal CD2F | B5 + deterministic objective function, Pareto analysis, uncertainty adjustment. | Does formal arbitration beat naive scoring? |
| B7 | Full system | B6 + all governance (policy layer, execution authorization, R_i, replay, DecisionRecord). | Full system evaluation. |

**Corrected Evaluation Protocol:**

```yaml
evaluation:
  statistical_protocol:
    primary_test: paired_permutation_test
    secondary_test: wilcoxon_signed_rank       # If data is ordinal
    effect_size: cliffs_delta                   # Non-parametric effect size
    confidence_interval: 95%
    significance_level: 0.05
    multiple_comparison_correction: holm        # For pairwise ablation comparisons
    
  calibration_metrics:
    primary: expected_calibration_error          # ECE
    secondary: brier_score
    visualization: reliability_diagram
    slope_intercept: calibration_slope_and_intercept
    
  inter_rater_agreement:
    binary: cohens_kappa
    multiclass: krippendorffs_alpha
    weighted: quadratic_weighted_kappa           # When class ordering matters
    
  anti_overfitting:
    held_out_scenarios: true
    scenario_split: 80_train_20_eval
    parameter_perturbation: true
    perturbation_range: 10%
    distribution_shift: true
    noise_injection: true
    twin_calibration_eval_split: true
    policy_sensitivity_analysis: true
    candidate_pruning_ablation: true
    
  oracle:
    methodology: exhaustive_search_over_candidate_space
    independence: oracle_must_not_share_twin_calibration_data
    hindsight_definition: actual_outcome_at_T_plus_observation_window
```

**Action:** P0. Define complete B0-B7 ladder and corrected evaluation protocol in Amendment 3.

---

### Review Sections 65-70: Cross-Document Drift and Documentation

**VERDICT:** AGREE on the problem. These are documentation synchronization tasks, not architectural defects. The architecture evolution document should declare explicit supersession:

```yaml
supersedes:
  - document: "SRS V1 Agent Roster"
    section: "Five-agent MVP definition"
    superseded_by: "Amendment 2 Section 4: Six-agent roster with DomainOwnershipPolicy"
    
  - document: "Implementation Plan V1 D3-D10"
    section: "D3=Demand+Inventory, D4=Supplier+Transport, ..."
    superseded_by: "Amendment 2 Section 2: Canonical D3-D10 Numbering"
```

**Action:** P1. Create supersession declaration document.

---

### Review Sections 71-72: What to Freeze / Not Freeze

**VERDICT: AGREE**

The review's freeze list aligns with my assessment. The architectural foundations (six agents, Deliberation Table, event sourcing, MCP, A2A, LangGraph, Twin, CD2F, policy layer, DecisionRecord) are mature and should not be redesigned.

The review correctly identifies that specific numerical parameters (thresholds, weights, budgets, allocations) should remain profile defaults, not frozen architecture.

**Action:** Confirm freeze list in Amendment 3 preamble.

---

### Review Sections 73-75: Required Corrections Summary

**VERDICT: AGREE with prioritization adjustments.**

The review's P0/P1/P2 classification is largely correct. My response adjusts some priorities:

- P0-7 (snapshot semantics): Downgraded to P1 (pragmatic consistency assessment is sufficient; full consistency epoch is premature)
- P0-12 (calibration metric): Confirmed P0 (this is a fundamental measurement error)
- P0-14 (cross-document sync): Downgraded to P1 parallel workstream (does not block D3)
- P1-8 (per-session partitioning): Removed (DISAGREE with the concern at SCOF scale)

---

### Review Sections 76-80: Final Pipeline, Authority Model, Quality Assessment, GO/NO-GO

**VERDICT: AGREE with the final cognitive pipeline and authority model.**

The review's recommended final cognitive pipeline (Section 76) is essentially the same as Amendment 2's LangGraph state machine (Section 14) with the corrections applied. I adopt it.

The review's authority model (Section 77) correctly separates Policy, Evidence, Claims, Actions, Twin, CD2F, and Execution into distinct authority layers. I adopt it.

The review's final GO/NO-GO (Section 79-80) is correct:
- Architecture: GO
- Hardening strategy: GO  
- Exact document as written: NO-GO for immediate implementation
- After contract-correction pass: GO

**Action:** Produce Amendment 3 as the contract-correction pass.

---

## Summary: What Goes Into Amendment 3

### P0 Corrections (Architecture-breaking defects)

| # | Correction | Source Section |
| :--- | :--- | :--- |
| P0-1 | ClaimTypeRegistry: canonical claim vocabulary with agent contract fixes | Review 15 |
| P0-2 | ActionTypeRegistry: canonical action vocabulary with missing typed schemas | Review 16 |
| P0-3 | ActionIntent/ActionImpact separation: remove LLM-provided numbers from action schemas | Review 18 |
| P0-4 | Safe candidate pruning: restrict pre-Twin pruning to deterministic criteria, UCB for budget enforcement | Review 19-20 |
| P0-5 | Policy-fixed reference scales: replace candidate-relative normalization | Review 22 |
| P0-6 | Proper Pareto analysis: replace scalar proximity check with Pareto frontier computation | Review 21 |
| P0-7 | Post-snapshot evidence resolution: reject by default, snapshot advancement as explicit alternative | Review 10 |
| P0-8 | Critical evidence assessment: decompose evidence sufficiency to evaluate critical facts individually | Review 5 |
| P0-9 | Twin requirement classification: TwinRequired/Recommended/Advisory with appropriate failure responses | Review 25 |
| P0-10 | Policy precedence fix: separate platform invariants from domain regulations | Review 9 |
| P0-11 | Policy deduplication: remove max_autonomous_cost from DecisionObjective, clarify boundary between CD2F and ExecutionPolicy | Review 47 |
| P0-12 | Complete B0-B7 ablation ladder with exact configurations | Review 57 |
| P0-13 | Corrected calibration metrics (ECE, Brier score, reliability diagrams) | Review 59 |
| P0-14 | Distribution-appropriate statistical test protocol | Review 58 |
| P0-15 | CD2F description refinement: "deterministic arbitration over materialized DecisionContext" | Review 24 |

### P1 Corrections (Contract refinements for D3/D4)

| # | Correction | Source Section |
| :--- | :--- | :--- |
| P1-1 | ActionDefinition with ownership model | Review 17 |
| P1-2 | Snapshot consistency assessment (lag detection, not global epoch) | Review 11 |
| P1-3 | Historical freshness: relative to observation_cutoff, not wall-clock | Review 12 |
| P1-4 | Twin trigger: multi-dimensional materiality, not USD-only | Review 26 |
| P1-5 | R_i AgentInfluenceStatus (FULL/REDUCED/ADVISORY) | Review 28 |
| P1-6 | Decomposed reliability metrics | Review 29 |
| P1-7 | Event sequence allocation mechanism | Review 31 |
| P1-8 | Aggregate vs session sequence relationship | Review 32 |
| P1-9 | Hot-path cache key fix (include capability_id, query_hash) | Review 36 |
| P1-10 | Governance fail-closed policy for critical evidence | Review 37 |
| P1-11 | Terminal state guards for cancellation | Review 39 |
| P1-12 | ReplanningContext with post-execution snapshot | Review 41 |
| P1-13 | OutcomeObservation schema | Review 42 |
| P1-14 | Claim-criticality-dependent failure responses | Review 46 |
| P1-15 | Policy and profile hashes | Review 48 |
| P1-16 | Trigger-state binding in DecisionSnapshot | Review 51 |
| P1-17 | Replay manifest retrieval artifacts | Review 35 |
| P1-18 | EXACT replay qualification | Review 34 |
| P1-19 | Fidelity weight configuration | Review 27 |
| P1-20 | Objective normalization function specifications | Review 23 |
| P1-21 | Preemption policy | Review 54 |
| P1-22 | MCP latency target relabeling | Review 56 |
| P1-23 | Invariant wording refinements (1, 2) | Review 3, 4 |
| P1-24 | Capability authorization binding | Review 38 |
| P1-25 | Cross-document supersession declaration | Review 65-67 |

### P2 Corrections (Evaluation/Research, during D10)

| # | Correction | Source Section |
| :--- | :--- | :--- |
| P2-1 | Shared-evidence correlation measurement | Review 44 |
| P2-2 | Round-1 vs Round-2 independence distinction | Review 45 |
| P2-3 | Oracle independence from Twin calibration | Review 61 |
| P2-4 | Twin calibration/evaluation data split | Review 62 |
| P2-5 | Policy sensitivity analysis | Review 63 |
| P2-6 | Candidate pruning ablation | Review 19 |
| P2-7 | Environmental reproducibility documentation | Review 53 |

---

## Points Beyond the Review: Issues I Identified

The review is thorough, but there are additional concerns I identified during cross-referencing:

### Additional Finding 1: Concurrent Decision Session Interference

**Issue:** The architecture does not address what happens when two disruption events arrive simultaneously, affecting overlapping domains and agents. Two DecisionSessions with overlapping agent assignments could propose conflicting candidate actions that the architecture cannot detect because each session is isolated.

**Example:**
```
Session A: Supplier delay for Product X
Session B: Demand spike for Product X
```

Both sessions involve the same inventory position. Session A might deplete safety stock while Session B increases it. Neither session knows about the other's candidates.

**Proposed Solution:** The Coordinator should detect session overlap at the DecisionSnapshot level and either:
1. Merge overlapping sessions into a single compound session
2. Serialize overlapping sessions (process one first, then the other with updated state)
3. Flag overlap and escalate to HITL

This should be addressed in Amendment 3.

### Additional Finding 2: DeliberationEvent Payload Typing

**Issue:** The review criticizes `CandidateAction.parameters: dict` but does not note that `DeliberationEvent.payload: dict` has the same problem. Event payloads should be typed per event_type using a discriminated union, following the same pattern applied to CandidateAction.

**Proposed Solution:** Define typed payloads for each event type.

### Additional Finding 3: Agent Cognitive Budget Across Sessions

**Issue:** The architecture defines per-session budgets (max reasoning iterations, max tool calls) but does not define how agent resources are allocated across concurrent sessions. An agent running at maximum cognitive load for one session may degrade performance on another.

**Proposed Solution:** Add per-agent concurrent session limits to the DecisionPolicy.

---

> [!IMPORTANT]
> This analysis confirms the review's core conclusion: the architecture is sound, the remaining work is contract-level corrections. Amendment 3 should implement the P0 corrections, incorporate the P1 corrections where immediately relevant, and defer P2 corrections to the D10 evaluation phase.
