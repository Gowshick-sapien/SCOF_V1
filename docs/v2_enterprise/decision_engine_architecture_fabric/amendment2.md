# SCOF V2 Architecture Hardening Revision

> [!IMPORTANT]
> This is a targeted hardening patch, not a full rewrite. It addresses the 20 contradictions and open questions identified by the critical architecture audit. Unaffected sections of the revised architecture remain authoritative.

---

## Table of Contents

1. [Ten Architectural Invariants (Frozen)](#1-ten-architectural-invariants)
2. [Canonical D3-D10 Numbering (Frozen)](#2-canonical-d3-d10-numbering)
3. [Corrected Cognitive Model: Six Stages (Replaces Section 1)](#3-corrected-cognitive-model)
4. [Agent Ownership Policy Enforcement (Extends Section 2)](#4-agent-ownership-policy-enforcement)
5. [Proposition-Specific Evidence Authority (Replaces Section 4.2)](#5-proposition-specific-evidence-authority)
6. [Evidence Sufficiency Redesign (Replaces Section 10)](#6-evidence-sufficiency-redesign)
7. [Decision Snapshot & Temporal Consistency (New Section)](#7-decision-snapshot--temporal-consistency)
8. [Candidate Normalization Pipeline (New Section)](#8-candidate-normalization-pipeline)
9. [Typed Candidate Action Schemas (Replaces CandidateAction in Section 5)](#9-typed-candidate-action-schemas)
10. [Twin Simulation Manifest & Budget (Extends Section 11)](#10-twin-simulation-manifest--budget)
11. [CD2F Formal Objective Function (Replaces Section 12.3)](#11-cd2f-formal-objective-function)
12. [Execution Authorization Clarification (Replaces Section 12.4 Step 6 and Section 19)](#12-execution-authorization-clarification)
13. [Decision Policy Layer (New Section)](#13-decision-policy-layer)
14. [Corrected LangGraph State Machine (Replaces Section 16.1)](#14-corrected-langgraph-state-machine)
15. [Coordinator Service Decomposition (Extends Section 2.3)](#15-coordinator-service-decomposition)
16. [Event-Sourced Deliberation Table (Extends Section 8)](#16-event-sourced-deliberation-table)
17. [Cross-Examination Governance (New Section)](#17-cross-examination-governance)
18. [R_i Lifecycle Governance (Extends Section 12.5)](#18-r_i-lifecycle-governance)
19. [Transactional Outbox Correction & Event Contract (Corrects Section 13)](#19-transactional-outbox-correction--event-contract)
20. [Contradiction Taxonomy (Extends ConflictRecord)](#20-contradiction-taxonomy)
21. [Failure Taxonomy & Response Map (New Section)](#21-failure-taxonomy--response-map)
22. [Cancellation Propagation (New Section)](#22-cancellation-propagation)
23. [Execution Outcome & Replanning (New Section)](#23-execution-outcome--replanning)
24. [Decision Record (New Section)](#24-decision-record)
25. [Replay Manifest (New Section)](#25-replay-manifest)
26. [Two-Class Retrieval Model (Extends Section 6)](#26-two-class-retrieval-model)
27. [Priority-Aware Admission Control (Extends Section 9)](#27-priority-aware-admission-control)
28. [Redis Governance (Extends Section 6.2)](#28-redis-governance)
29. [Capability Versioning & Side-Effect Classification (Extends Section 15)](#29-capability-versioning--side-effect-classification)
30. [Corrected Unified Architecture Diagram (Replaces Section 20)](#30-corrected-unified-architecture-diagram)
31. [Revised Implementation Sequencing (Replaces Section 21)](#31-revised-implementation-sequencing)

---

## 1. Ten Architectural Invariants

> [!IMPORTANT]
> These ten invariants supersede the seven amendments. They are the non-negotiable properties of the D3-D10 architecture. Every design decision, implementation choice, and evaluation criterion must be validated against these invariants.

### Invariant 1: Source Authority

```
PostgreSQL owns operational facts (System of Record).
Neo4j owns topology projection (derived, not authoritative for operational state).
No dual truth. No ambiguity.
```

### Invariant 2: Cognitive Workspace Boundary

```
The Deliberation Table stores decision artifacts (claims, critiques, verdicts, directives).
It NEVER stores or replicates enterprise operational truth.
```

### Invariant 3: Evidence Sufficiency

```
Agent response != sufficient evidence.
Evidence sufficiency is a multi-dimensional assessment of:
coverage, freshness, authority, consistency, and critical-fact presence.
```

### Invariant 4: Candidate Discipline

```
No unbounded candidate or simulation expansion.
Candidate budget and simulation budget are explicit, configurable limits.
```

### Invariant 5: Counterfactual Isolation

```
The Digital Twin can mutate ONLY isolated Layer-3 scenario state.
It cannot modify Layer-1 (historical fact) or Layer-2 (baseline operational state).
Every simulation is bound to a reproducible manifest.
```

### Invariant 6: Decision Authority Hierarchy

```
LLM: proposes, interprets, explains (non-authoritative for numbers).
Deterministic systems: calculate, validate, enforce constraints.
CD2F: arbitrates using a formal objective function.
Execution Adapter: acts (with policy-gated authorization).
```

### Invariant 7: Policy Authority

```
The organization's Decision Policy defines:
objectives, constraints, autonomy, escalation, and risk tolerance.
LLMs, agents, and CD2F do NOT define what "good" means.
Policy comes from the domain profile, not from inference.
```

### Invariant 8: State Freshness

```
Every decision is bound to a declared world-state snapshot.
All agents in a session reason over the same observation boundary.
No agent can use evidence newer than the session's observation_cutoff.
```

### Invariant 9: Execution Safety

```
Decision approval (CD2F Tier-1) != physical execution.
Decision approval and execution authorization are SEPARATE gates.
The execution gate is controlled by organizational policy, not by CD2F confidence.
```

### Invariant 10: Replayability

```
Every decision is reconstructable from:
state snapshot + evidence + model versions + policy version +
candidate actions + simulations + events + random seeds.
```

---

## 2. Canonical D3-D10 Numbering

> [!IMPORTANT]
> This table is FROZEN. Every reference in every document, diagram, heading, table, and code comment must use exactly this mapping. No exceptions.

| D | Name | Responsibility | Phase |
| :--- | :--- | :--- | :--- |
| **D1** | Enterprise World & Simulation Foundation | Frozen | Complete |
| **D2** | Enterprise Knowledge & Data Fabric | Frozen | Complete |
| **D3** | Cognitive Agent Runtime | Single-agent bounded reasoning, ReasoningService, ML+LLM hybrid, vertical research slice | Phase 1 |
| **D4** | Specialist Federation & Agent Cards | 6-agent expansion, Agent Card V2, DomainOwnershipPolicy, A2A lifecycle | Phase 2 |
| **D5** | Agentic Retrieval & Evidence Fabric | SCOFRetriever, MCP-governed retrieval, evidence provenance, two-tier RAG | Phase 3 |
| **D6** | Cognitive Orchestration & Deliberation | LangGraph state machine, Deliberation Table, domain affinity routing, cross-examination, evidence sufficiency gate | Phase 4 |
| **D7** | CD2F Arbitration & Counterfactual Decision | CD2F objective function, Twin counterfactual evaluation, candidate normalization, DecisionSnapshot, DecisionPolicy | Phase 5 |
| **D8** | Event & Runtime Backbone | Kafka topic architecture, transactional outbox, SCOFEvent contract, consumer idempotency, API Gateway | Phase 6 |
| **D9** | Observability, Explainability & Desktop Console | Decision trace, evidence visualization, trade-off explanation, Tauri v2 HITL console, DecisionRecord archival | Phase 7 |
| **D10** | Evaluation & Benchmark | Benchmark suite, ablation baseline ladder, R_i calibration, SLA validation, anti-overfitting measures, RQ1-RQ4 | Phase 8 |

**Cross-reference rule:** If the revised architecture document references D07 for observability or D05/D06 for orchestration, those references should be mentally re-mapped to D9 and D6 respectively. This hardening revision uses only the canonical numbering above.

---

## 3. Corrected Cognitive Model

> [!WARNING]
> **REPLACES Section 1 of the revised architecture.** The cognitive stage ordering has been corrected to match the actual execution pipeline.

### 3.1 Six Cognitive Stages (Corrected Order)

```
                    KNOW
                      |
                      v
                 UNDERSTAND
                      |
                      v
                 DELIBERATE
                /           \
       revise/critique    candidate actions
                              |
                              v
                    EVIDENCE GATE
                    (must pass before
                     expensive simulation)
                              |
                   insufficient |  sufficient
                       |                |
                      HITL              v
                                    EXPLORE
                                 Digital Twin
                                      |
                        [if unexpected outcome]
                              |            |
                       re-deliberate    proceed
                              |            |
                              +-----+------+
                                    |
                                    v
                                 DECIDE
                                  CD2F
                                    |
                                    v
                                 EXPLAIN
```

| Stage | Component | Core Question |
| :--- | :--- | :--- |
| **KNOW** | D1/D2 + Agentic RAG | What facts, context, and precedents are relevant? |
| **UNDERSTAND** | Specialist Agents (ML + LLM) | What does each domain expert conclude from the evidence? |
| **DELIBERATE** | Coordinator + Deliberation Table + Cross-Examination | Where do experts agree and disagree? Can conflicts be resolved? |
| **EXPLORE** | Digital Twin (counterfactual sandbox) | What happens if we take each proposed action? |
| **DECIDE** | CD2F (with DecisionPolicy) | Which candidate action is best justified by evidence, constraints, policy, and simulated outcomes? |
| **EXPLAIN** | D9 Observability | Complete provenance chain from trigger to outcome. |

### 3.2 DELIBERATE-EXPLORE Interaction Loop

The primary flow is: DELIBERATE -> EXPLORE -> DECIDE.

However, an optional feedback loop exists:

```
EXPLORE (Twin simulation) reveals unexpected outcome
    |
    v
Twin result violates expectation threshold?
    |
    +-- NO:  proceed to DECIDE
    |
    +-- YES: targeted re-deliberation (max 1 iteration)
             |
             v
             Coordinator posts Twin result to Deliberation Table
             Affected agents receive targeted re-assessment request
             Agents revise candidate actions based on simulation insight
             |
             v
             Re-normalize candidates
             Re-simulate revised candidates
             |
             v
             Proceed to DECIDE
```

**Bound:** This EXPLORE -> DELIBERATE loop executes at most **once**. If the second simulation still produces unexpected results, the system proceeds to CD2F with the available evidence and flags elevated uncertainty.

---

## 4. Agent Ownership Policy Enforcement

> [!IMPORTANT]
> **EXTENDS Section 2 of the revised architecture.** Adds machine-enforceable ownership contracts to the existing agent roster.

### 4.1 DomainOwnershipPolicy Schema

Every agent's Agent Card V2 includes a DomainOwnershipPolicy:

```python
class DomainOwnershipPolicy(BaseModel):
    """Machine-enforceable ownership boundaries for each agent.
    Validated by the Coordinator before posting proposals to the Deliberation Table."""
    
    # What this agent authoritatively owns
    owned_entity_types: list[str]
    owned_metric_types: list[str]
    owned_claim_types: list[str]
    
    # What this agent may propose as candidate actions
    permitted_action_types: list[str]
    
    # What this agent explicitly consumes from others
    consumes_from: dict[str, list[str]]  # {agent_id: [claim_types]}
    
    # Hard boundary: types this agent may NEVER claim or propose
    forbidden_claim_types: list[str]
    forbidden_action_types: list[str]
```

### 4.2 Per-Agent Ownership Contracts

```yaml
# Procurement & Supplier Agent
ownership:
  owned_entity_types:
    - supplier_operational_performance
    - purchase_order
    - contract_terms
    - vendor_qualification
  owned_metric_types:
    - otif_score
    - lead_time_distribution
    - defect_rate
    - supplier_capacity
  owned_claim_types:
    - supplier_operational_assessment
    - procurement_cost_analysis
    - alternate_sourcing_feasibility
  permitted_action_types:
    - switch_supplier
    - increase_purchase_order
    - cancel_purchase_order
    - expedite_purchase_order
  consumes_from:
    risk_resilience:
      - supplier_financial_distress
      - supplier_concentration_risk
      - geopolitical_risk_score
  forbidden_claim_types:
    - supplier_creditworthiness
    - supplier_bankruptcy_probability
    - financial_exposure_assessment
  forbidden_action_types:
    - financial_exposure_override
    - regulatory_waiver

# Risk & Resilience Agent
ownership:
  owned_entity_types:
    - supplier_financial_health
    - geopolitical_exposure
    - network_fragility
    - cascade_impact
  owned_metric_types:
    - financial_distress_score
    - concentration_risk_index
    - recovery_time_estimate
    - cascade_propagation_depth
  owned_claim_types:
    - supplier_financial_distress
    - systemic_risk_assessment
    - cascade_failure_analysis
    - regulatory_compliance_status
  permitted_action_types:
    - quarantine_inventory
    - risk_mitigation_recommendation
    - compliance_hold
  consumes_from:
    procurement_supplier:
      - supplier_operational_assessment
    logistics_transport:
      - route_vulnerability_assessment
    inventory_asset:
      - inventory_concentration_data
  forbidden_claim_types:
    - supplier_operational_performance
    - demand_forecast
    - cost_optimization
  forbidden_action_types:
    - switch_supplier
    - reroute_shipment

# Demand & Commerce Agent
ownership:
  owned_entity_types:
    - demand_forecast
    - sales_pattern
    - promotion_calendar
    - pricing_elasticity
  owned_metric_types:
    - forecast_accuracy
    - demand_volatility
    - seasonal_index
    - promotional_lift
  owned_claim_types:
    - demand_assessment
    - commercial_impact_analysis
    - pricing_recommendation
  permitted_action_types:
    - adjust_safety_stock
    - promotion_adjustment
    - demand_signal_override
  consumes_from:
    inventory_asset:
      - inventory_position
    risk_resilience:
      - external_threat_assessment
  forbidden_claim_types:
    - supplier_assessment
    - transport_feasibility
    - financial_exposure
  forbidden_action_types:
    - switch_supplier
    - reroute_shipment

# Inventory & Asset Management Agent
ownership:
  owned_entity_types:
    - inventory_position
    - storage_capacity
    - shelf_life
    - replenishment_schedule
    - goods_receipt
  owned_metric_types:
    - days_of_supply
    - fill_rate
    - inventory_turns
    - storage_utilization
  owned_claim_types:
    - inventory_viability_assessment
    - replenishment_analysis
    - asset_condition_report
  permitted_action_types:
    - reallocate_inventory
    - adjust_safety_stock
    - quarantine_inventory
  consumes_from:
    demand_commerce:
      - demand_assessment
    procurement_supplier:
      - supplier_capacity_assessment
  forbidden_claim_types:
    - transport_feasibility
    - supplier_financial_health
    - route_optimization
  forbidden_action_types:
    - switch_supplier
    - reroute_shipment

# Logistics & Transport Agent
ownership:
  owned_entity_types:
    - transport_lane
    - carrier_capability
    - route_status
    - fleet_asset
    - freight_mode
  owned_metric_types:
    - transit_time
    - route_reliability
    - carrier_performance
    - carbon_per_route
  owned_claim_types:
    - transport_feasibility
    - route_optimization_analysis
    - carbon_impact_assessment
  permitted_action_types:
    - reroute_shipment
    - expedite_shipment
    - change_freight_mode
  consumes_from:
    risk_resilience:
      - corridor_risk_assessment
    inventory_asset:
      - origin_destination_inventory
  forbidden_claim_types:
    - supplier_assessment
    - demand_forecast
    - financial_exposure
  forbidden_action_types:
    - switch_supplier
    - cancel_purchase_order

# Financial & Enterprise Value Agent
ownership:
  owned_entity_types:
    - cost_model
    - working_capital_impact
    - margin_structure
    - penalty_exposure
  owned_metric_types:
    - landed_cost
    - cash_impact
    - margin_delta
    - expedite_cost
    - penalty_liability
  owned_claim_types:
    - economic_consequence_assessment
    - cost_impact_analysis
    - working_capital_projection
  permitted_action_types:
    - financial_impact_flag
    - budget_escalation
  consumes_from:
    procurement_supplier:
      - procurement_cost_analysis
    logistics_transport:
      - transport_cost_data
    demand_commerce:
      - revenue_impact_data
  forbidden_claim_types:
    - supplier_assessment
    - demand_forecast
    - transport_feasibility
  forbidden_action_types:
    - switch_supplier
    - reroute_shipment
    - reallocate_inventory
```

### 4.3 Enforcement Mechanism

```
Agent produces AgentProposal
    |
    v
Coordinator validates against DomainOwnershipPolicy:
    
    For each claim in proposal.claim:
        If claim.claim_type in agent.ownership.forbidden_claim_types:
            -> REJECT proposal with AGENT_OWNERSHIP_VIOLATION
            -> Request revised output from agent
    
    For each action in proposal.candidate_actions:
        If action.action_type not in agent.ownership.permitted_action_types:
            -> REJECT action (remove from proposal)
            -> Log ownership boundary violation
    
    If proposal passes validation:
        -> Post to Deliberation Table
```

---

## 5. Proposition-Specific Evidence Authority

> [!WARNING]
> **REPLACES Section 4.2 (Evidence Authority Hierarchy) of the revised architecture.** The global linear hierarchy is replaced with a claim-type-dependent authority model.

### 5.1 Why the Global Hierarchy Was Wrong

The original hierarchy implied:

```
Level 1: PostgreSQL/Neo4j (same authority)
Level 2: Computed derivation
Level 3: ML model
Level 4: Simulation
Level 5: Precedent
Level 6: LLM
```

This was incorrect because:
- Neo4j is a materialized topology projection, not a System of Record
- Simulation may be more authoritative than ML for counterfactual claims
- ML may be more authoritative than simulation for probability estimates
- Authority depends on WHAT is being claimed, not just WHO produced it

### 5.2 Corrected Evidence Authority (Proposition-Specific)

```
CURRENT-STATE CLAIM
    "Inventory at DC-003 is 500 units"
    "Supplier SUP-0042 status is ACTIVE"
    
    Authority:
        1. PostgreSQL (System of Record) -- AUTHORITATIVE
        2. Neo4j projection (check projection_version, flag if stale)
        3. Redis cache (check cache_version against PostgreSQL)
        4. LLM interpretation -- NON-AUTHORITATIVE
    
    Conflict resolution: PostgreSQL wins. Always.

TOPOLOGICAL CLAIM
    "DC-003 supplies stores S-101, S-102, S-103"
    "Supplier SUP-0042 has 3 alternate transport lanes"
    
    Authority:
        1. Neo4j projection -- AUTHORITATIVE (this IS its purpose)
        2. PostgreSQL source tables (reference, not primary for topology)
        3. LLM interpretation -- NON-AUTHORITATIVE
    
    Conflict resolution: Neo4j projection wins for topology.
    But Neo4j carries projection freshness metadata (see 5.3).

FORECAST CLAIM
    "Demand will increase 35% next quarter"
    "Supplier delay probability is 72%"
    
    Authority:
        1. Validated ML model (with known accuracy metrics)
        2. Historical precedent (pgvector match with confirmed outcome)
        3. LLM estimation -- NON-AUTHORITATIVE
    
    Conflict resolution: ML model wins if calibration_score > 0.60.

COUNTERFACTUAL CLAIM
    "If we reroute to SUP-0112, inventory at T+7 will be 380"
    "Air freight will cost $45,000 more but arrive 5 days earlier"
    
    Authority:
        1. Twin simulation -- AUTHORITATIVE (this IS its purpose)
        2. Deterministic calculation (cost formulas)
        3. Heuristic estimate
        4. LLM speculation -- NON-AUTHORITATIVE
    
    Conflict resolution: Twin simulation wins for projected outcomes.

HISTORICAL-ANALOGUE CLAIM
    "In a similar scenario last year, we rerouted with 94% success"
    
    Authority:
        1. Validated pgvector precedent with confirmed outcome
        2. Generic LLM world knowledge
        3. Unvalidated LLM recall -- NON-AUTHORITATIVE
    
    Conflict resolution: Validated precedent with confirmed outcome wins.

COMPUTED-DERIVATION CLAIM
    "$128,421 landed cost", "3.8 days safety stock"
    
    Authority:
        1. Deterministic formula from Level-1 inputs -- AUTHORITATIVE
        2. ML approximation
        3. LLM arithmetic -- NON-AUTHORITATIVE
    
    Conflict resolution: Deterministic formula wins.
```

### 5.3 Neo4j Evidence Metadata Extension

Every evidence item sourced from Neo4j carries projection freshness metadata:

```python
class Neo4jEvidenceMetadata(BaseModel):
    """Additional metadata for evidence from Neo4j topology projection."""
    projection_version: str            # Version of the projection pipeline
    projected_at: datetime             # When this projection was last computed
    source_snapshot_version: str       # Which PostgreSQL WAL LSN it was derived from
    projection_lag_ms: int             # Time since last sync from PostgreSQL
    
    def is_stale(self, max_lag_ms: int = 60000) -> bool:
        return self.projection_lag_ms > max_lag_ms
```

**If Neo4j evidence is stale (projection_lag > threshold):**
- The evidence item is flagged with reduced authority
- The EvidenceSufficiencyAssessment downgrades the freshness score
- If the stale data is critical to the decision, the system logs a warning

### 5.4 LLM Non-Authoritative Rule (Refined)

The architectural rule is:

> **LLM-Produced Values Are Non-Authoritative.** An LLM may perform intermediate arithmetic during reasoning, but any numerical value that appears in a `StructuredClaim` or `CandidateAction` must have `source != LLM_INTERPRETATION` for it to be treated as reliable evidence by CD2F. If the only source for a critical number is LLM reasoning, the evidence quality assessment reduces the claim's authority, and CD2F applies an uncertainty penalty.

This is more precise than "LLMs cannot calculate." The LLM CAN do arithmetic; the result is simply not authoritative.

---

## 6. Evidence Sufficiency Redesign

> [!WARNING]
> **REPLACES Section 10 (Fail-Safe Behavior) of the revised architecture.** Agent presence is necessary but NOT sufficient. Evidence quality matters.

### 6.1 Multi-Dimensional Evidence Sufficiency Assessment

```python
class EvidenceSufficiencyAssessment(BaseModel):
    """Replaces the binary 'did mandatory agents respond?' check.
    Evidence sufficiency is evaluated across multiple dimensions."""
    
    session_id: str
    assessed_at: datetime
    
    # Dimension 1: Domain Coverage
    domain_coverage: DomainCoverageAssessment
    
    # Dimension 2: Evidence Quality
    evidence_quality: EvidenceQualityAssessment
    
    # Dimension 3: Consistency
    consistency: ConsistencyAssessment
    
    # Composite verdict
    verdict: Literal[
        "SUFFICIENT",              # Proceed to EXPLORE (Twin) + DECIDE (CD2F)
        "MARGINALLY_SUFFICIENT",   # Proceed with elevated caution, reduced autonomy
        "INSUFFICIENT",            # Escalate to HITL, do NOT proceed to Twin or CD2F
    ]
    insufficiency_reasons: list[str]
    
class DomainCoverageAssessment(BaseModel):
    """Are the required expert domains represented?"""
    mandatory_agents_responding: int
    mandatory_agents_expected: int
    coverage_score: float              # responding / expected
    missing_critical_domains: list[str]
    fallback_agents: list[str]         # Agents using deterministic fallback (ML-only)

class EvidenceQualityAssessment(BaseModel):
    """Is the evidence actually good enough for this decision?"""
    min_evidence_authority: str        # Lowest authority level in the evidence set
    avg_evidence_freshness: float      # Average freshness across all evidence [0, 1]
    stale_evidence_count: int          # Evidence items older than freshness threshold
    critical_facts_present: bool       # Are the core facts for this disruption type present?
    model_validity_score: float        # Are the ML models applicable to this disruption type?
    neo4j_projection_stale: bool       # Is the Neo4j projection out-of-date?
    
class ConsistencyAssessment(BaseModel):
    """Do the agents' evidence bases agree on observable facts?"""
    contradiction_count: int
    contradiction_severity: Literal["NONE", "MINOR", "MAJOR", "BLOCKING"]
    contradicted_facts: list[str]
    temporal_disagreement: bool        # Are agents using different observation windows?
```

### 6.2 Verdict Logic

```
SUFFICIENT:
    domain_coverage.coverage_score >= policy.min_domain_coverage (default 0.80)
    AND evidence_quality.avg_evidence_freshness >= policy.min_evidence_freshness (default 0.60)
    AND evidence_quality.critical_facts_present == True
    AND consistency.contradiction_severity != "BLOCKING"
    AND evidence_quality.model_validity_score >= 0.50

MARGINALLY_SUFFICIENT:
    domain_coverage.coverage_score >= 0.60
    AND evidence_quality.avg_evidence_freshness >= 0.40
    AND evidence_quality.critical_facts_present == True
    AND consistency.contradiction_severity != "BLOCKING"

    CD2F proceeds but:
        - Autonomy level reduced (max Tier-2, never Tier-1)
        - Uncertainty penalty applied to all candidate scores
        - Decision flagged for post-hoc review

INSUFFICIENT:
    Any of the above fail
    OR consistency.contradiction_severity == "BLOCKING"
    OR evidence_quality.critical_facts_present == False

    System action:
        - Do NOT run Twin simulation (saves compute)
        - Do NOT invoke CD2F
        - Escalate to HITL with explanation of what is missing
        - Audit: "Decision deferred: [specific reasons]"
```

All thresholds come from the DecisionPolicy (Section 13), loaded from the domain profile. They are NOT hard-coded.

---

## 7. Decision Snapshot & Temporal Consistency

> [!IMPORTANT]
> **NEW SECTION.** Ensures all agents in a decision session reason over the same world-state.

### 7.1 DecisionSnapshot Schema

```python
class DecisionSnapshot(BaseModel):
    """The declared world-state boundary for a decision session.
    Created by the Coordinator at session start.
    All evidence acquisition must respect this boundary."""
    
    snapshot_id: str
    session_id: str
    created_at: datetime
    
    # State binding
    enterprise_state_version: int        # PostgreSQL WAL LSN or custom sequence number
    neo4j_projection_version: str        # Which projection epoch is current
    pgvector_index_version: str          # Embedding index version
    
    # Temporal boundary
    observation_cutoff: datetime          # No evidence newer than this timestamp
    
    # Freshness policy (from DecisionPolicy)
    max_fact_age_minutes: int             # Current-state facts must be within this age
    max_model_age_hours: int              # ML model outputs must be within this age
    max_precedent_age_days: int           # Historical precedents within this age
    
    # Integrity
    snapshot_hash: str                    # SHA-256 of all snapshot parameters
```

### 7.2 Enforcement

1. **At session start:** The Coordinator creates a `DecisionSnapshot`, capturing the current PostgreSQL LSN, Neo4j projection version, and pgvector index version.

2. **In the ContextPackage:** The snapshot is included with every agent assignment. Agents are instructed to use data as-of `observation_cutoff`.

3. **Evidence validation:** Every `EvidenceItem` produced by agents is checked:
   ```
   If evidence.data_as_of > snapshot.observation_cutoff:
       Flag as "post-snapshot evidence" (allowed but noted)
   If evidence.data_as_of < (snapshot.observation_cutoff - max_fact_age_minutes):
       Flag as "stale evidence" (impacts evidence quality assessment)
   ```

4. **Pre-execution stale check:** After CD2F approval, before execution:
   ```python
   current_version = get_enterprise_state_version()
   if current_version != decision.snapshot.enterprise_state_version:
       changes = get_changes_since(decision.snapshot.enterprise_state_version)
       if changes_affect_decision(changes, decision):
           decision.status = "STALE"
           trigger_revalidation(decision)
       else:
           log_warning("Immaterial state change during deliberation")
           proceed_with_execution()
   ```

---

## 8. Candidate Normalization Pipeline

> [!IMPORTANT]
> **NEW SECTION.** Inserted between cross-examination and Twin simulation. Prevents candidate explosion and invalid simulations.

### 8.1 Pipeline Steps

```
After cross-examination is complete:

STEP 1: EXTRACT
    Collect all candidate actions from all revised agent proposals
    Raw candidates: up to N (6 agents x max_candidates_per_agent)

STEP 2: SCHEMA VALIDATION
    Validate every candidate against its typed action schema
    (see Section 9: Typed Candidate Action Schemas)
    Reject candidates with invalid/missing parameters

STEP 3: ENTITY VALIDATION
    Verify all referenced entity IDs exist in D2
    Example: carrier_id "CR-9999" does not exist in PostgreSQL -> reject
    Example: supplier_id "SUP-0112" exists but is SUSPENDED -> flag

STEP 4: CONSTRAINT PRE-CHECK
    Quick hard-constraint check (no simulation needed)
    Source: DecisionPolicy.hard_constraints
    Example: proposed route has no reefer capability for perishable goods -> eliminate
    Example: proposed PO quantity > supplier max capacity -> eliminate

STEP 5: DEDUPLICATION
    Merge semantically identical candidates from different agents
    Example: both Procurement and Risk recommend switching to SUP-0112
    with identical parameters -> merge into single candidate

STEP 6: DOMINANCE PRUNING
    If candidate A is strictly worse than B on ALL objective dimensions
    (all impact metrics inferior) -> eliminate A
    
STEP 7: TOP-K SELECTION
    Rank remaining candidates by estimated objective score
    (quick pre-score using DecisionObjective without simulation)
    Select top K candidates where K = simulation_policy.max_candidates
    ALWAYS include: "do nothing + buffer" baseline

STEP 8: COMBINATION SYNTHESIS (if warranted)
    Generate up to max_combined_actions composite candidates
    ONLY for non-conflicting candidates from different domains
    Example: Procurement switch supplier + Logistics alternate route
    
    Combination rules:
        - Actions from the same agent are NOT combined (already considered by the agent)
        - Combined actions must not violate any hard constraint
        - Max combined candidates: simulation_policy.max_combined_actions

OUTPUT: Normalized candidate set ready for Twin simulation
    Maximum: max_candidates + max_combined_actions + 1 baseline
```

### 8.2 Budget Configuration

```yaml
# From DecisionPolicy.simulation_policy
simulation_policy:
  max_candidates_per_agent: 4
  max_candidates_per_session: 20     # Total raw candidates before pruning
  max_simulation_branches: 8         # After normalization, max for Twin
  max_combined_actions: 3
  max_simulation_horizon_days: 28
  max_parallel_simulations: 4
  simulation_trigger_threshold_usd: 10000.0  # Below this, skip Twin
```

---

## 9. Typed Candidate Action Schemas

> [!WARNING]
> **REPLACES `CandidateAction.parameters: dict` in Section 5 of the revised architecture.** Untyped dictionaries are replaced with strongly typed, validated action schemas.

### 9.1 Revised CandidateAction

```python
class CandidateAction(BaseModel):
    """What the agent PROPOSES to do about its assessment.
    Parameters are now a discriminated union of typed schemas,
    NOT an arbitrary dict."""
    
    action_id: str
    action_type: str
    action_params: ActionParams          # Discriminated union (see 9.2)
    expected_impact: ImpactAssessment
    supporting_claims: list[str]
    evidence: list[EvidenceItem]
```

### 9.2 Action-Specific Typed Schemas

```python
from typing import Union, Literal

# Discriminated union of all known action types
ActionParams = Union[
    RerouteShipmentParams,
    SwitchSupplierParams,
    IncreasePurchaseOrderParams,
    CancelPurchaseOrderParams,
    ExpeditePurchaseOrderParams,
    ReallocateInventoryParams,
    ExpediteShipmentParams,
    QuarantineInventoryParams,
    AdjustSafetyStockParams,
    ChangeFreightModeParams,
    DoNothingParams,
]

class RerouteShipmentParams(BaseModel):
    action_type: Literal["reroute_shipment"] = "reroute_shipment"
    shipment_id: str
    original_carrier_id: str
    new_carrier_id: str
    new_route_lane_id: str
    freight_mode: Literal["road", "air", "sea", "rail", "multimodal"]
    estimated_transit_days: int
    incremental_cost_usd: float

class SwitchSupplierParams(BaseModel):
    action_type: Literal["switch_supplier"] = "switch_supplier"
    po_id: str
    original_supplier_id: str
    new_supplier_id: str
    product_id: str
    quantity: int
    new_lead_time_days: int
    price_delta_usd: float

class IncreasePurchaseOrderParams(BaseModel):
    action_type: Literal["increase_purchase_order"] = "increase_purchase_order"
    po_id: str
    supplier_id: str
    product_id: str
    additional_quantity: int
    new_total_quantity: int
    incremental_cost_usd: float

class CancelPurchaseOrderParams(BaseModel):
    action_type: Literal["cancel_purchase_order"] = "cancel_purchase_order"
    po_id: str
    supplier_id: str
    cancellation_reason: str
    penalty_usd: float

class ExpeditePurchaseOrderParams(BaseModel):
    action_type: Literal["expedite_purchase_order"] = "expedite_purchase_order"
    po_id: str
    supplier_id: str
    original_delivery_date: str       # ISO 8601
    requested_delivery_date: str      # ISO 8601
    expedite_cost_usd: float

class ReallocateInventoryParams(BaseModel):
    action_type: Literal["reallocate_inventory"] = "reallocate_inventory"
    source_facility_id: str
    destination_facility_id: str
    sku_id: str
    quantity: int
    transfer_cost_usd: float
    estimated_transfer_days: int

class ExpediteShipmentParams(BaseModel):
    action_type: Literal["expedite_shipment"] = "expedite_shipment"
    shipment_id: str
    current_freight_mode: str
    expedited_freight_mode: Literal["air", "express_road"]
    time_saved_days: int
    incremental_cost_usd: float

class QuarantineInventoryParams(BaseModel):
    action_type: Literal["quarantine_inventory"] = "quarantine_inventory"
    facility_id: str
    sku_id: str
    quantity: int
    reason: Literal["quality_failure", "shelf_life", "regulatory", "contamination"]
    quarantine_duration_days: int

class AdjustSafetyStockParams(BaseModel):
    action_type: Literal["adjust_safety_stock"] = "adjust_safety_stock"
    facility_id: str
    sku_id: str
    current_safety_stock: int
    new_safety_stock: int
    adjustment_reason: str

class ChangeFreightModeParams(BaseModel):
    action_type: Literal["change_freight_mode"] = "change_freight_mode"
    shipment_id: str
    original_mode: str
    new_mode: Literal["road", "air", "sea", "rail", "multimodal"]
    cost_delta_usd: float
    time_delta_days: int

class DoNothingParams(BaseModel):
    action_type: Literal["do_nothing"] = "do_nothing"
    buffer_period_days: int = 7       # Monitor period before re-evaluation
    monitoring_frequency_hours: int = 24
```

### 9.3 Schema Validation in Pipeline

The candidate normalization pipeline (Step 2) validates every `CandidateAction` against these schemas. If an LLM produces parameters that do not match the schema:
1. First attempt: retry the agent with a corrected prompt
2. Second failure: discard the candidate action, log schema violation
3. The agent's remaining valid candidates (if any) continue through the pipeline

---

## 10. Twin Simulation Manifest & Budget

> [!IMPORTANT]
> **EXTENDS Section 11 of the revised architecture.** Adds reproducibility contract and simulation budget.

### 10.1 SimulationManifest

```python
class SimulationManifest(BaseModel):
    """Complete specification for a reproducible Twin simulation.
    Same manifest + same baseline = identical simulation result."""
    
    # Identity
    simulation_id: str
    session_id: str
    candidate_action_id: str
    
    # Baseline binding (from DecisionSnapshot)
    baseline_snapshot_id: str
    baseline_snapshot_version: int
    baseline_data_as_of: datetime
    
    # Branch isolation
    scenario_id: str
    parent_branch_id: Optional[str]      # None = root branch from baseline
    branch_version: int
    isolation_mode: Literal[
        "COPY_ON_WRITE",                 # Standard: isolated fork
        "FULL_CLONE",                    # For deterministic replay
    ]
    
    # Simulation parameters
    simulation_clock_start: datetime
    simulation_clock_end: datetime
    time_horizons: list[int]             # [7, 14, 28] days
    action_set: list[CandidateAction]
    action_set_hash: str                 # SHA-256 of the serialized action set
    
    # Reproducibility
    twin_model_version: str
    profile_version: str
    random_seed: int
    input_state_hash: str                # SHA-256 of the baseline state
    
    # Lifecycle
    created_at: datetime
    completed_at: Optional[datetime]
    gc_eligible_after: datetime
    
    # Authority
    # Twin scenario state is authoritative ONLY within this scenario scope.
    # It is NEVER baseline authority.
    # It is NEVER enterprise operational truth.
```

### 10.2 Twin State Authority Rule

```
Twin Scenario State Authority:

    AUTHORITATIVE:
        - Within the scope of THIS simulation ONLY
        - For counterfactual claims about THIS candidate action
    
    NOT AUTHORITATIVE:
        - For enterprise operational state (Layer 1 / Layer 2)
        - For any other simulation branch
        - For any real-world claim
    
    Persistence:
        - Simulation input manifest: persisted in PostgreSQL (for replay)
        - Simulation result: persisted in PostgreSQL (for CD2F)
        - Branch runtime state: ephemeral, garbage-collected after archival
```

### 10.3 Simulation Lifecycle

```yaml
twin:
  scenario_lifecycle:
    active_retention: "until_session_resolved"
    archive_after_session: true                # Archive manifest + result to PostgreSQL
    branch_state_retention_days: 7             # Keep branch state for 7 days for replay
    gc_policy: "delete_branch_state_after_retention"
    max_concurrent_branches: 16
```

### 10.4 Simulation Fidelity (Enhanced)

```python
class SimulationFidelity(BaseModel):
    """How trustworthy is this simulation result?"""
    
    # Data fidelity
    baseline_data_freshness: float      # How fresh is the starting data?
    entity_coverage: float              # % of referenced entities present in the model
    
    # Model fidelity
    model_calibration_score: float      # How well does the model predict known outcomes?
    model_applicability: float          # Is this disruption type within the model's training domain?
    invariant_violations: int           # How many physical invariants were violated?
    
    # Composite
    composite_fidelity: float           # Weighted combination
    
    # Classification
    fidelity_class: Literal[
        "HIGH",       # > 0.80 composite, 0 invariant violations
        "MODERATE",   # 0.50-0.80 composite
        "LOW",        # < 0.50 composite OR invariant violations
    ]
```

---

## 11. CD2F Formal Objective Function

> [!WARNING]
> **REPLACES Section 12.3 (CD2F Arbitration Process) of the revised architecture.** The informal "best justified" language is replaced with a deterministic, auditable objective function.

### 11.1 Decision Objective (from Policy Layer)

```python
class DecisionObjective(BaseModel):
    """The organization's formal definition of 'best'.
    Loaded from DecisionPolicy. Never generated by agents or LLMs."""
    
    # Objective vector weights (normalized, sum to 1.0)
    weights: ObjectiveWeights
    
    # Hard constraints (violation = eliminate candidate)
    hard_constraints: list[HardConstraint]
    
    # Soft constraints (violation = penalty, not elimination)
    soft_constraints: list[SoftConstraint]
    
    # Risk tolerance
    max_acceptable_risk: float
    
    # Financial autonomy
    max_autonomous_cost_usd: float
    
    # Escalation sensitivity
    pareto_ambiguity_threshold: float   # If top candidates within this margin, escalate
    uncertainty_escalation_threshold: float

class ObjectiveWeights(BaseModel):
    service_level: float = 0.25
    cost: float = 0.25
    risk: float = 0.20
    inventory_health: float = 0.10
    lead_time: float = 0.10
    carbon: float = 0.05
    cash_flow: float = 0.05
    # Sum must equal 1.0

class HardConstraint(BaseModel):
    constraint_id: str
    description: str
    metric: str
    operator: Literal[">=", "<=", "==", "!=", "in", "not_in"]
    threshold: Any    # Type depends on operator

class SoftConstraint(BaseModel):
    constraint_id: str
    description: str
    metric: str
    target: float
    penalty_per_unit_violation: float
```

### 11.2 Formal Arbitration Process (Deterministic)

```
STAGE 1: FEASIBILITY FILTER
    For each candidate c:
        For each hard_constraint h in policy.hard_constraints:
            If c violates h:
                -> ELIMINATE c
                -> Record: eliminated_candidates[c] = "violated: {h.description}"
    
    Output: feasible_candidates (subset of all candidates)
    
    If feasible_candidates is empty:
        -> CD2F_NO_FEASIBLE_ACTION
        -> HITL escalation (Tier-3)

STAGE 2: OBJECTIVE SCORE
    For each feasible candidate c:
        
        J(c) = (
            w.service_level * normalized_service_level_delta(c)
          - w.cost          * normalized_cost_impact(c)
          - w.risk          * normalized_risk_score(c)
          - w.inventory     * normalized_inventory_degradation(c)
          - w.lead_time     * normalized_lead_time_increase(c)
          - w.carbon        * normalized_carbon_increase(c)
          - w.cash_flow     * normalized_cash_impact(c)
        )
    
    Normalization: All metrics scaled to [0, 1] range relative to the candidate set.
    Source: ImpactAssessment values (from agent proposals + simulation results)
    
    Soft constraint penalties:
        J_adj(c) = J(c) - sum(
            sc.penalty_per_unit_violation * violation_amount(c, sc)
            for sc in policy.soft_constraints
            if c violates sc
        )

STAGE 3: UNCERTAINTY ADJUSTMENT
    For each candidate c:
        
        uncertainty(c) = weighted_combination_of(
            1 - evidence_authority_quality(c),    # Lower authority = higher uncertainty
            1 - evidence_freshness(c),            # Stale evidence = higher uncertainty
            1 - agent_reliability_R_i(c),         # Lower R_i = higher uncertainty
            1 - simulation_fidelity(c),           # Lower fidelity = higher uncertainty
        )
        
        J_final(c) = J_adj(c) - lambda * uncertainty(c)
        
        where lambda = policy.uncertainty_penalty_weight (default 0.10)

STAGE 4: PARETO CHECK
    Sort candidates by J_final descending.
    
    If |J_final(rank_1) - J_final(rank_2)| < policy.pareto_ambiguity_threshold:
        -> PARETO_AMBIGUITY
        -> Generate trade-off summary showing where each candidate is superior
        -> HITL escalation (Tier-2 or Tier-3) with Pareto analysis
    
    If single dominant candidate:
        -> selected_candidate = rank_1

STAGE 5: EXECUTION AUTHORIZATION
    (See Section 12: Execution Authorization Clarification)
```

### 11.3 What CD2F Does NOT Do

- CD2F does NOT use LLM reasoning to select the winning candidate
- CD2F does NOT generate new candidate actions
- CD2F does NOT retrieve data (it uses pre-assembled evidence)
- CD2F does NOT call the Twin (simulation happens before CD2F)
- CD2F does NOT define what "good" means (policy defines it)

CD2F is a **pure computation engine** that takes: (candidates + evidence + simulation results + policy) and produces: (selected action + justification + trade-off summary).

---

## 12. Execution Authorization Clarification

> [!WARNING]
> **REPLACES the escalation check in Section 12.3 Step 6 and clarifies Section 19 (Execution Boundary Matrix).** Resolves the Tier-1 "auto-commit" contradiction.

### 12.1 Two Separate Gates

```
Gate 1: DECISION APPROVAL (CD2F)
    "Is this action well-supported by evidence, constraints, and simulation?"
    Output: ApprovedDecision with escalation_tier
    
    This CAN be autonomous (Tier-1 = CD2F approves without human review)

Gate 2: EXECUTION AUTHORIZATION (ExecutionPolicyService)
    "Is the organization willing to let this action be executed without human oversight?"
    Output: ExecutionAuthorization
    
    This is a SEPARATE check controlled by organizational policy
```

### 12.2 CD2F Escalation Tiers (Revised Meaning)

| Tier | Meaning | What Happens Next |
| :--- | :--- | :--- |
| **Tier-1** | High confidence, no constraint violations, simulation confirms, evidence sufficient | Decision is APPROVED. Proceeds to ExecutionPolicyService for authorization check. |
| **Tier-2** | Moderate confidence, or competing candidates close, or marginal evidence sufficiency | Extended deliberation round. If still Tier-2 after second pass, proceeds to ExecutionPolicyService with elevated caution flag. |
| **Tier-3** | Low confidence, or insufficient evidence, or high financial exposure, or Pareto ambiguity | HITL escalation. Human reviews decision in D9 console. Human can approve, reject, or modify. |

### 12.3 ExecutionPolicyService

```python
class ExecutionAuthorization(BaseModel):
    decision_id: str
    authorization: Literal[
        "AUTO_EXECUTE",              # Policy permits autonomous execution
        "HITL_REQUIRED",             # Policy requires human sign-off
        "SIMULATION_ONLY",           # Apply to Twin Layer 3 only (research context)
    ]
    reason: str
    policy_version: str

class ExecutionPolicyService:
    """Separate from CD2F. Applies organizational execution policy."""
    
    def authorize(
        self,
        decision: ApprovedDecision,
        policy: ExecutionPolicy,
        context: str  # "simulation", "benchmark", "production"
    ) -> ExecutionAuthorization:
        
        # In SCOF V2 research context: all actuation is simulated
        if context in ("simulation", "benchmark"):
            return ExecutionAuthorization(
                authorization="SIMULATION_ONLY",
                reason="Research context: apply to Twin Layer 3"
            )
        
        # Production context (future)
        if decision.selected_action.action_type in policy.hitl_required_action_types:
            return ExecutionAuthorization(
                authorization="HITL_REQUIRED",
                reason=f"Action type '{decision.selected_action.action_type}' requires human authorization"
            )
        
        if decision.cost_impact > policy.max_autonomous_cost_usd:
            return ExecutionAuthorization(
                authorization="HITL_REQUIRED",
                reason=f"Cost ${decision.cost_impact} exceeds autonomous limit ${policy.max_autonomous_cost_usd}"
            )
        
        if decision.risk_score > policy.max_autonomous_risk:
            return ExecutionAuthorization(
                authorization="HITL_REQUIRED",
                reason=f"Risk {decision.risk_score} exceeds autonomous limit {policy.max_autonomous_risk}"
            )
        
        return ExecutionAuthorization(
            authorization="AUTO_EXECUTE",
            reason="Within autonomous execution policy bounds"
        )
```

### 12.4 Flow Summary

```
CD2F approves decision (Tier-1)
    |
    v
ExecutionPolicyService.authorize(decision, policy, context)
    |
    +-- SIMULATION_ONLY:    Apply to Twin Layer 3. Done.
    |
    +-- AUTO_EXECUTE:       Execution Adapter sends to ERP/TMS/WMS.
    |                       (Future: only in production context)
    |
    +-- HITL_REQUIRED:      Queue in D9 Desktop Console for human review.
                            Human can: Approve / Reject / Modify.
```

---

## 13. Decision Policy Layer

> [!IMPORTANT]
> **NEW SECTION.** Centralizes all organizational decision-making policy. All policy parameters come from the domain profile YAML, not from code constants.

### 13.1 DecisionPolicy Schema

```python
class DecisionPolicy(BaseModel):
    """The organization's complete policy for decision-making.
    Loaded from profile YAML. Never generated by agents or LLMs.
    Consumed by: Coordinator, CD2F, EvidenceSufficiencyService,
    CandidateService, SimulationDispatchService, ExecutionPolicyService."""
    
    profile_id: str
    version: str
    
    # What "good" means
    objective: DecisionObjective
    
    # Evidence requirements
    evidence_policy: EvidencePolicy
    
    # Deliberation bounds
    deliberation_policy: DeliberationPolicy
    
    # Simulation requirements
    simulation_policy: SimulationPolicy
    
    # Routing configuration
    routing_policy: RoutingPolicy
    
    # R_i governance
    reliability_policy: ReliabilityGovernancePolicy
    
    # Execution authorization
    execution_policy: ExecutionPolicy
    
    # Priority/SLA mapping
    priority_sla_policy: PrioritySLAPolicy

class EvidencePolicy(BaseModel):
    min_domain_coverage: float = 0.80
    min_evidence_freshness: float = 0.60
    max_fact_age_minutes: int = 5
    max_model_age_hours: int = 24
    max_precedent_age_days: int = 365
    
class DeliberationPolicy(BaseModel):
    max_cross_exam_rounds: int = 2
    max_critiques_per_agent: int = 3
    max_total_critiques_per_session: int = 18
    independence_enforcement: bool = True       # Phase 1 independent assessment
    explore_deliberate_loop_max: int = 1        # Max EXPLORE->DELIBERATE re-loops
    
class SimulationPolicy(BaseModel):
    max_candidates_per_agent: int = 4
    max_candidates_per_session: int = 20
    max_simulation_branches: int = 8
    max_combined_actions: int = 3
    max_simulation_horizon_days: int = 28
    max_parallel_simulations: int = 4
    simulation_trigger_threshold_usd: float = 10000.0
    always_include_do_nothing_baseline: bool = True

class RoutingPolicy(BaseModel):
    assigned_threshold: float = 0.60
    optional_threshold: float = 0.40
    minimum_assigned_agents: int = 1
    force_assign_if_none_above_threshold: bool = True

class ExecutionPolicy(BaseModel):
    max_autonomous_cost_usd: float = 50000.0
    max_autonomous_risk: float = 0.30
    hitl_required_action_types: list[str] = ["cancel_purchase_order"]
    autonomous_permitted_contexts: list[str] = ["simulation", "benchmark"]

class PrioritySLAPolicy(BaseModel):
    p0_fast_path_enabled: bool = True
    p0_cognitive_path_enabled: bool = True
    p0_reserved_twin_workers: int = 2
    p1_reserved_twin_workers: int = 2
```

### 13.2 Profile YAML Extension

```yaml
# profiles/mvp-electronics/decision_policy.yaml
decision_policy:
  version: "1.0.0"
  
  objective:
    weights:
      service_level: 0.25
      cost: 0.25
      risk: 0.20
      inventory_health: 0.10
      lead_time: 0.10
      carbon: 0.05
      cash_flow: 0.05
    hard_constraints:
      - constraint_id: "reefer_required"
        description: "Perishable goods require temperature-controlled transport"
        metric: "reefer_capability"
        operator: "=="
        threshold: true
      - constraint_id: "capacity_available"
        description: "Proposed quantity must not exceed facility capacity"
        metric: "capacity_utilization"
        operator: "<="
        threshold: 0.95
    soft_constraints:
      - constraint_id: "preferred_carrier"
        description: "Prefer contracted carriers over spot market"
        metric: "is_preferred_carrier"
        target: 1.0
        penalty_per_unit_violation: 0.05
    max_acceptable_risk: 0.70
    max_autonomous_cost_usd: 50000.0
    pareto_ambiguity_threshold: 0.05
    uncertainty_escalation_threshold: 0.40
  
  evidence_policy:
    min_domain_coverage: 0.80
    min_evidence_freshness: 0.60
    max_fact_age_minutes: 5
    max_model_age_hours: 24
  
  deliberation_policy:
    max_cross_exam_rounds: 2
    max_critiques_per_agent: 3
    independence_enforcement: true
  
  simulation_policy:
    max_simulation_branches: 8
    max_combined_actions: 3
    max_parallel_simulations: 4
    simulation_trigger_threshold_usd: 10000.0
  
  execution_policy:
    max_autonomous_cost_usd: 50000.0
    max_autonomous_risk: 0.30
    hitl_required_action_types:
      - cancel_purchase_order
```

### 13.3 Policy Precedence

When multiple policy sources conflict, the following precedence applies:

```
1. SAFETY / REGULATORY CONSTRAINTS       (non-negotiable, hard-coded)
       Examples: cold-chain quarantine, regulatory recall
       
2. ENTERPRISE HARD CONSTRAINTS           (from DecisionPolicy.hard_constraints)
       Examples: capacity limits, reefer requirements
       
3. PROFILE-SPECIFIC POLICIES             (from DecisionPolicy)
       Examples: objective weights, evidence thresholds
       
4. SOFT OBJECTIVES                       (from DecisionPolicy.soft_constraints)
       Examples: preferred carrier preference
       
5. AGENT PREFERENCES                     (lowest authority)
       Examples: agent's recommended_action_id
```

---

## 14. Corrected LangGraph State Machine

> [!WARNING]
> **REPLACES Section 16.1 of the revised architecture.** Evidence sufficiency gate is moved BEFORE Twin simulation. Candidate normalization is added. Independence enforcement is added.

```
START
    |
    v
ingest_and_route
    |
    v
create_decision_snapshot              (NEW: capture world-state boundary)
    |
    v
tier1_rag_preretrieval
    |
    v
capability_bind
    |
    v
parallel_fan_out                       (agents receive snapshot + base context ONLY,
    |                                    NOT other agents' claims -- independence)
    v
fan_in_collate
    |
    v
cross_examination                      (targeted: agents see ONLY relevant conflicts,
    |                                    not all claims -- reduces conformity bias)
    v
[CONDITIONAL: blocking_critiques?]
    +-- YES: revision_round -> fan_in_revised
    +-- NO:  proceed
    |
    v
evidence_sufficiency_gate              (MOVED UP: before expensive simulation)
    |
    v
[CONDITIONAL: sufficient?]
    +-- INSUFFICIENT:     hitl_escalation -> END
    +-- MARGINALLY:       proceed (with caution flag)
    +-- SUFFICIENT:       proceed
    |
    v
candidate_extraction
    |
    v
candidate_normalization                (NEW: schema/entity/constraint/dedup/prune/topK)
    |
    v
[CONDITIONAL: twin_simulation_needed?]
    +-- YES: twin_dispatch -> twin_collect
    |        |
    |        v
    |        [CONDITIONAL: unexpected_outcome?]
    |            +-- YES (first time): targeted_re_deliberation
    |            |                     -> re_normalize -> re_simulate
    |            +-- NO / YES (second time): proceed
    +-- NO:  proceed
    |
    v
cd2f_arbitration
    |
    v
[CONDITIONAL: cd2f_result_tier?]
    +-- TIER_1: execution_policy_check -> execute_or_hitl -> archive -> END
    +-- TIER_2: extended_deliberation -> parallel_fan_out (cycle, max 1)
    +-- TIER_3: hitl_escalation -> await_human -> execute_or_hitl -> archive -> END
    +-- NO_FEASIBLE: hitl_escalation -> END
    +-- PARETO:      hitl_with_tradeoff_summary -> await_human -> archive -> END
```

---

## 15. Coordinator Service Decomposition

> [!IMPORTANT]
> **EXTENDS Section 2.3 of the revised architecture.** The Coordinator remains a single logical component but its internals are decomposed into testable services.

```
Coordinator (LangGraph State Machine)
    |
    +-- RoutingService
    |     Input:  disruption event, agent cards
    |     Output: domain affinity scores, agent assignments
    |     Owns:   affinity pipeline, threshold application
    |     Testable: given event X, produces assignment Y
    |
    +-- DeliberationService
    |     Input:  session requests, agent verdicts
    |     Output: session lifecycle events, item management
    |     Owns:   session creation, item posting, event emission
    |     Testable: given items X, produces session state Y
    |
    +-- EvidenceSufficiencyService
    |     Input:  agent proposals, evidence items, policy
    |     Output: EvidenceSufficiencyAssessment
    |     Owns:   coverage, quality, consistency evaluation
    |     Testable: given evidence set X and policy Y, produces verdict Z
    |
    +-- CandidateService
    |     Input:  agent proposals
    |     Output: normalized candidate set
    |     Owns:   extraction, validation, dedup, pruning, top-K, combination
    |     Testable: given proposals X and budget Y, produces candidates Z
    |
    +-- SimulationDispatchService
    |     Input:  candidate set, DecisionSnapshot
    |     Output: SimulationManifests, dispatched to Twin
    |     Owns:   manifest creation, Twin interface, result collection
    |     Testable: given candidates X and snapshot Y, produces manifests Z
    |
    +-- AuditService
    |     Input:  all deliberation events
    |     Output: complete decision trace
    |     Owns:   observability event production, trace assembly
    |
    +-- ExecutionPolicyService
          Input:  ApprovedDecision, ExecutionPolicy, context
          Output: ExecutionAuthorization
          Owns:   tier determination, HITL escalation, policy application
          Testable: given decision X and policy Y, produces authorization Z
```

Each service is:
- A Python class with a clear interface
- Independently unit-testable with mocked dependencies
- Independently replaceable
- Invoked by the LangGraph state machine as discrete steps

The Coordinator state machine calls:
```python
routing_result = routing_service.compute_assignments(event, agent_cards)
sufficiency = evidence_service.assess(proposals, evidence, policy)
candidates = candidate_service.normalize(proposals, policy.simulation_policy)
manifests = simulation_service.dispatch(candidates, snapshot)
authorization = execution_policy_service.authorize(decision, policy.execution_policy, context)
```

---

## 16. Event-Sourced Deliberation Table

> [!IMPORTANT]
> **EXTENDS Section 8 of the revised architecture.** Resolves the mutable-state vs. replay tension by adopting event sourcing.

### 16.1 Core Principle

```
EVENTS are the source of truth (immutable, append-only).
VIEWS are derived state (materialized projections for fast reads).
```

### 16.2 Deliberation Event Schema

```python
class DeliberationEvent(BaseModel):
    """Immutable event in the deliberation event stream.
    Stored in PostgreSQL (append-only).
    Distributed via Kafka (outbox).
    Materialized in Redis (current session view)."""
    
    event_id: str                        # Globally unique
    session_id: str                      # Which decision session
    sequence_number: int                 # Monotonically increasing within session
    
    event_type: Literal[
        "SESSION_STARTED",
        "SNAPSHOT_BOUND",                # DecisionSnapshot attached to session
        "ITEM_POSTED",
        "ITEM_SCOPED",
        "AGENTS_ASSIGNED",
        "PROPOSAL_SUBMITTED",
        "CRITIQUE_SUBMITTED",
        "REVISION_SUBMITTED",
        "ENDORSEMENT_SUBMITTED",
        "EVIDENCE_GATE_EVALUATED",
        "CANDIDATE_EXTRACTED",
        "CANDIDATE_NORMALIZED",
        "SIMULATION_DISPATCHED",
        "SIMULATION_COMPLETED",
        "RE_DELIBERATION_TRIGGERED",
        "CD2F_SUBMITTED",
        "DECISION_RESOLVED",
        "EXECUTION_AUTHORIZED",
        "EXECUTION_COMPLETED",
        "SESSION_CLOSED",
        "SESSION_CANCELLED",
    ]
    
    actor: str                           # agent_id, "coordinator", "cd2f", "human:op_id"
    payload: dict                        # Event-specific data (typed per event_type)
    timestamp: datetime
    causation_id: str                    # Which event caused this event
    correlation_id: str                  # = session_id
```

### 16.3 Materialized Session View

```python
class DeliberationSessionView(BaseModel):
    """Derived projection of the current session state.
    Rebuilt by replaying DeliberationEvents.
    Stored in Redis for fast reads by agents and Coordinator."""
    
    session_id: str
    status: str
    snapshot_id: str
    current_sequence: int
    
    items: list[DeliberationItemView]
    proposals: list[AgentProposal]
    critiques: list[AgentCritique]
    revised_proposals: list[AgentProposal]
    candidates: list[CandidateAction]
    simulations: list[SimulationResult]
    
    sufficiency_assessment: Optional[EvidenceSufficiencyAssessment]
    arbitration_result: Optional[CD2FArbitrationResult]
    
    last_event_at: datetime
```

### 16.4 Replay Capability

```python
def replay_session(session_id: str, up_to_sequence: Optional[int] = None) -> DeliberationSessionView:
    """Reconstruct session state at any point by replaying events."""
    events = db.query(
        "SELECT * FROM deliberation_events WHERE session_id = %s ORDER BY sequence_number",
        [session_id]
    )
    
    if up_to_sequence:
        events = [e for e in events if e.sequence_number <= up_to_sequence]
    
    view = DeliberationSessionView(session_id=session_id)
    for event in events:
        apply_event(view, event)
    
    return view
```

### 16.5 Storage

```
PostgreSQL:
    deliberation_events    (append-only, immutable, partitioned by session_id)
    --> Authority for replay and audit

Kafka:
    scof.deliberation.events    (via outbox)
    Key: session_id             (ordering within session)
    --> Transport and distribution

Redis:
    session:{session_id}:view   (materialized projection)
    session:{session_id}:version (sequence counter for staleness check)
    --> Fast reads for active sessions
```

---

## 17. Cross-Examination Governance

> [!IMPORTANT]
> **NEW SECTION.** Adds termination bounds and independence enforcement to the cross-examination process.

### 17.1 Termination Policy

```yaml
# From DecisionPolicy.deliberation_policy
deliberation:
  max_cross_exam_rounds: 2
  max_critiques_per_agent: 3
  max_total_critiques_per_session: 18

  termination_conditions:
    # Session advances to the next phase when ANY condition is met:
    - no_blocking_critiques        # No unresolved blocking conflicts remaining
    - max_rounds_reached           # Hit max_cross_exam_rounds
    - candidate_set_unchanged      # Revisions did not change any candidate actions
    - evidence_convergence         # Agents' revised claims agree on key facts
    - deadline_imminent            # SLA budget nearly exhausted (< 20% remaining)
```

### 17.2 Two-Phase Independence Protocol

```
PHASE 2: INITIAL INDEPENDENT ASSESSMENT
    
    Each agent receives:
        + Base context package (Coordinator's Tier-1 RAG)
        + Their own deep retrieval results (Tier-2 RAG)
        + The disruption event description
        + DecisionSnapshot binding
    
    Each agent does NOT receive:
        - Other agents' claims
        - Other agents' evidence
        - Other agents' candidate actions
        - Other agents' confidence scores
    
    Purpose: Ensure INDEPENDENT initial assessment.
    
    Output: Independent AgentProposal per agent.

PHASE 3: TARGETED CROSS-EXAMINATION
    
    The Coordinator identifies:
        - Data contradictions (same fact, different values)
        - Claims that affect another agent's domain (via affected_domains)
        - Candidate actions that interact with another domain
    
    Each agent receives ONLY:
        - The specific claims from specific agents that conflict with
          or affect this agent's domain
        - NOT the full set of all claims
        - NOT other agents' confidence scores (prevents anchoring)
    
    Purpose: Structured conflict resolution without conformity bias.
    
    Output: Targeted critiques and revisions.
```

---

## 18. R_i Lifecycle Governance

> [!IMPORTANT]
> **EXTENDS Section 12.5 of the revised architecture.** Adds feedback-loop prevention, temporal windowing, and cold-start policy.

```python
class ReliabilityGovernancePolicy(BaseModel):
    """Controls R_i computation to prevent feedback loops
    and self-reinforcing biases."""
    
    # Temporal controls
    evaluation_window_days: int = 90
    minimum_sample_size: int = 10
    cold_start_prior: float = 0.50         # Default R_i for new/retrained agents
    
    # Decay
    decay_half_life_days: int = 30         # Older evaluations weighted less
    
    # Stratification
    stratify_by: list[str] = [
        "disruption_type",                 # Different R_i per disruption class
        "decision_class",                  # Routine vs. emergency
        "model_version",                   # Retrained model gets fresh R_i
    ]
    
    # Anti-lock-out
    min_r_i: float = 0.20                  # Floor: no agent can be fully excluded
    max_r_i: float = 0.95                  # Ceiling: no agent can dominate
    
    # Confidence reporting
    compute_confidence_interval: bool = True  # Report 95% CI alongside point estimate
    
    # Update policy
    update_frequency: str = "per_session"
    batch_recalibration_cron: str = "weekly"

class ReliabilityScore(BaseModel):
    """Enhanced R_i with governance metadata."""
    agent_id: str
    disruption_type: str
    model_version: str
    decision_class: str
    
    # Core metrics
    accuracy: float
    calibration: float
    constraint_violation_rate: float
    outcome_quality: float
    
    # Composite
    composite_r_i: float
    confidence_interval: tuple[float, float]   # (lower, upper) at 95% CI
    
    # Governance metadata
    sample_size: int
    evaluation_window_start: datetime
    evaluation_window_end: datetime
    is_cold_start: bool
    prior_used: bool
    clamped: bool                              # True if min/max clamp was applied
```

---

## 19. Transactional Outbox Correction & Event Contract

> [!WARNING]
> **CORRECTS Section 13.2 guarantee statement and Section 14 event semantics.**

### 19.1 Corrected Guarantee

**Old (incorrect):**
> "No split-brain."

**Corrected:**
> PostgreSQL provides authoritative durable state. The transactional outbox guarantees that if PostgreSQL commits a state change, the corresponding event intent is also durably persisted (in the same transaction). Kafka provides at-least-once event distribution via the outbox relay. Consumers achieve effective exactly-once state transitions through idempotent processing with aggregate version checks.

### 19.2 Core Event Contract (Architectural, Not Deferred to D8)

```python
class SCOFEvent(BaseModel):
    """Base contract for ALL events in the SCOF event backbone.
    This is a cross-cutting architectural contract, not a D8 implementation detail."""
    
    event_id: str                        # Globally unique (UUID v7 recommended)
    aggregate_type: str                  # "deliberation_item", "verdict", "session", etc.
    aggregate_id: str                    # The entity this event relates to
    aggregate_version: int               # Monotonically increasing per aggregate
    event_type: str                      # "item.posted", "verdict.submitted", etc.
    causation_id: str                    # ID of the event that caused this event
    correlation_id: str                  # Links all events in a single decision session
    producer_id: str                     # Which component produced this event
    schema_version: str                  # Event schema version for forward compatibility
    payload: dict                        # Event-specific payload
    timestamp: datetime
```

### 19.3 Consumer Idempotency Rule

```
Before applying any event:
    current_version = get_aggregate_version(event.aggregate_id)
    
    If event.aggregate_version <= current_version:
        -> Duplicate event. Discard. Log.
    
    If event.aggregate_version > current_version + 1:
        -> Out-of-order event. Queue for re-ordering or request replay.
    
    If event.aggregate_version == current_version + 1:
        -> Apply event. Update aggregate version.
```

### 19.4 Kafka Topic Ordering

For topics where ordering matters within a decision session:

```
Kafka partition key = session_id
```

This ensures all events for a single decision session are ordered within the same partition.

---

## 20. Contradiction Taxonomy

> [!IMPORTANT]
> **EXTENDS the ConflictRecord concept.** Provides structured conflict classification for CD2F.

```python
class ConflictRecord(BaseModel):
    conflict_id: str
    session_id: str
    
    conflict_type: Literal[
        "DATA_CONTRADICTION",       # Same observable, different factual values
        "MODEL_DISAGREEMENT",       # Same target variable, different predictions
        "POLICY_CONFLICT",          # Same facts, different objective priorities
        "ACTION_CONFLICT",          # Mutually incompatible proposed actions
        "TEMPORAL_DISAGREEMENT",    # Different observation windows
    ]
    
    agent_a_id: str
    agent_b_id: str
    proposition: str                 # What is being disputed
    agent_a_value: Any
    agent_a_evidence: list[str]      # Evidence IDs supporting agent A
    agent_b_value: Any
    agent_b_evidence: list[str]      # Evidence IDs supporting agent B
    
    # Resolution
    resolution_method: Optional[Literal[
        "AUTHORITY_HIERARCHY",       # Higher-authority source wins
        "FRESHNESS_WINS",            # More recent data wins
        "SNAPSHOT_ENFORCED",         # DecisionSnapshot cutoff resolves
        "CROSS_REFERENCE",           # Third source validates one side
        "UNRESOLVABLE",              # Escalated to CD2F as open conflict
    ]]
    resolved_value: Optional[Any]
    resolution_explanation: Optional[str]
    
    severity: Literal["MINOR", "MAJOR", "BLOCKING"]
```

### Resolution Rules by Conflict Type

| Conflict Type | Primary Resolution | Fallback |
| :--- | :--- | :--- |
| DATA_CONTRADICTION | Authority hierarchy (PostgreSQL > Neo4j projection > Redis cache) | Cross-reference via fresh MCP query |
| MODEL_DISAGREEMENT | Compare model calibration scores; higher-calibration model wins | Pass both to CD2F as uncertainty factor |
| POLICY_CONFLICT | Policy precedence hierarchy (Section 13.3) | HITL escalation |
| ACTION_CONFLICT | Pass to CD2F for trade-off analysis | Pareto set if irreconcilable |
| TEMPORAL_DISAGREEMENT | DecisionSnapshot.observation_cutoff enforces consistent timestamp | Re-fetch with consistent cutoff |

---

## 21. Failure Taxonomy & Response Map

> [!IMPORTANT]
> **NEW SECTION.** Provides a structured failure classification with deterministic response mapping.

```python
class FailureType(str, Enum):
    # Agent failures
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    AGENT_SCHEMA_FAILURE = "AGENT_SCHEMA_FAILURE"
    AGENT_TOOL_FAILURE = "AGENT_TOOL_FAILURE"
    AGENT_OWNERSHIP_VIOLATION = "AGENT_OWNERSHIP_VIOLATION"
    
    # Retrieval failures
    RETRIEVAL_FAILURE = "RETRIEVAL_FAILURE"
    RETRIEVAL_STALE = "RETRIEVAL_STALE"
    RETRIEVAL_EMPTY = "RETRIEVAL_EMPTY"
    
    # Evidence failures
    EVIDENCE_CONTRADICTION = "EVIDENCE_CONTRADICTION"
    EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"
    MISSING_CRITICAL_DOMAIN = "MISSING_CRITICAL_DOMAIN"
    
    # Twin failures
    TWIN_TIMEOUT = "TWIN_TIMEOUT"
    TWIN_INVARIANT_VIOLATION = "TWIN_INVARIANT_VIOLATION"
    TWIN_LOW_FIDELITY = "TWIN_LOW_FIDELITY"
    TWIN_BUDGET_EXHAUSTED = "TWIN_BUDGET_EXHAUSTED"
    
    # CD2F failures
    CD2F_NO_FEASIBLE_ACTION = "CD2F_NO_FEASIBLE_ACTION"
    CD2F_PARETO_AMBIGUITY = "CD2F_PARETO_AMBIGUITY"
    CD2F_POLICY_CONFLICT = "CD2F_POLICY_CONFLICT"
    
    # Execution failures
    EXECUTION_REJECTED = "EXECUTION_REJECTED"
    EXECUTION_PARTIAL = "EXECUTION_PARTIAL"
    
    # State failures
    STATE_CHANGED = "STATE_CHANGED"
    DECISION_STALE = "DECISION_STALE"
    
    # Lifecycle
    SESSION_CANCELLED = "SESSION_CANCELLED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
```

### Response Map

| Failure | Response | Escalation |
| :--- | :--- | :--- |
| AGENT_TIMEOUT | Use deterministic ML-only fallback | If critical domain, flag in sufficiency assessment |
| AGENT_SCHEMA_FAILURE | Retry once with corrected prompt; then fallback | Log for prompt engineering review |
| AGENT_TOOL_FAILURE | Retry once; then fallback | Log for MCP/tool debugging |
| AGENT_OWNERSHIP_VIOLATION | Reject proposal, request revision | Log for ownership policy review |
| RETRIEVAL_FAILURE | Retry with cache; if unavailable, use stale data with warning | Flag in evidence quality |
| RETRIEVAL_STALE | Proceed with warning; reduce freshness score | Flag in sufficiency assessment |
| EVIDENCE_INSUFFICIENT | HITL escalation (Tier-3) | Do not proceed to Twin or CD2F |
| TWIN_TIMEOUT | Proceed to CD2F without simulation results | CD2F applies higher uncertainty |
| TWIN_INVARIANT_VIOLATION | Eliminate the candidate that caused violation | Log for scenario debugging |
| TWIN_LOW_FIDELITY | Proceed but apply fidelity penalty in CD2F | Flag in decision record |
| CD2F_NO_FEASIBLE_ACTION | HITL escalation with elimination reasons | Human must provide alternative |
| CD2F_PARETO_AMBIGUITY | HITL with trade-off summary | Human selects from Pareto set |
| STATE_CHANGED | Revalidate decision against new state | If material change, rerun affected evidence |
| SESSION_CANCELLED | Propagate cancellation (Section 22) | Archive partial session |

---

## 22. Cancellation Propagation

> [!IMPORTANT]
> **NEW SECTION.** Defines how a cancelled decision session propagates through all components.

```
CancellationEvent received (from human operator or system timeout)
    |
    v
1. DecisionSession.status -> "CANCELLED"
   DeliberationEvent(type="SESSION_CANCELLED") appended
    |
    v
2. LangGraph: interrupt current workflow execution
    |
    v
3. A2A: cancel all active tasks for this session_id
    |
    v
4. MCP: cancel in-flight tool calls (best-effort, may complete)
    |
    v
5. Twin: cancel all pending/running simulations for this session_id
   Release scenario branches for immediate GC
    |
    v
6. Kafka: publish SESSION_CANCELLED event (via outbox)
    |
    v
7. Redis: update session cache (status = CANCELLED)
    |
    v
8. Deliberation Table: all POSTED/IN_PROGRESS items -> WITHDRAWN
    |
    v
9. Audit: emit cancellation trace with partial session summary
```

---

## 23. Execution Outcome & Replanning

> [!IMPORTANT]
> **NEW SECTION.** Defines what happens after execution (simulation or real-world).

```python
class ExecutionOutcome(BaseModel):
    decision_id: str
    execution_type: Literal["SIMULATION", "REAL_WORLD"]
    
    status: Literal[
        "APPLIED",                # Successfully applied
        "INVARIANT_VIOLATION",    # Twin rejected (physical constraint violated)
        "PARTIAL_APPLICATION",    # Some actions applied, others failed
        "REJECTED",               # Execution Adapter or human rejected
    ]
    
    applied_actions: list[str]    # action_ids that succeeded
    failed_actions: list[FailedAction]
    timestamp: datetime
    
class FailedAction(BaseModel):
    action_id: str
    failure_reason: str
    compensating_action: Optional[str]
    replan_required: bool
```

### Replanning Trigger

```
If any FailedAction has replan_required == True:
    |
    v
    Create new DecisionSession with:
        trigger = ExecutionFailureEvent(
            original_decision_id,
            failed_actions,
            current_state_after_partial_execution
        )
    
    The system re-deliberates with knowledge of:
        - What was originally decided
        - Which parts succeeded
        - Which parts failed and why
        - The current (post-partial-execution) state
```

---

## 24. Decision Record

> [!IMPORTANT]
> **NEW SECTION.** The final, durable business artifact for every decision.

```python
class DecisionRecord(BaseModel):
    """The final, immutable business artifact.
    Created when a DecisionSession closes.
    Stored permanently in PostgreSQL.
    Indexed in pgvector for precedent retrieval."""
    
    record_id: str
    session_id: str
    
    # Context
    trigger: DisruptionEvent
    snapshot: DecisionSnapshot
    policy_version: str
    
    # Process summary
    agents_consulted: list[str]
    evidence_sufficiency: EvidenceSufficiencyAssessment
    candidate_count_raw: int
    candidate_count_normalized: int
    simulation_count: int
    cross_exam_rounds: int
    total_deliberation_duration_ms: float
    
    # Decision
    selected_action: CandidateAction
    arbitration_result: CD2FArbitrationResult
    
    # Execution
    execution_authorization: ExecutionAuthorization
    execution_outcome: ExecutionOutcome
    
    # Provenance
    replay_manifest_ref: str           # Reference to stored DecisionReplayManifest
    full_event_log_ref: str            # Reference to complete event sequence
    
    # Post-hoc (populated later)
    human_assessment: Optional[str]
    actual_outcome: Optional[dict]     # Real-world outcome for R_i calibration
    outcome_recorded_at: Optional[datetime]
```

**Distinction:**
- `DecisionSession` = the working process (events stream during deliberation)
- `DeliberationSessionView` = the current materialized state (for real-time queries)
- `DecisionRecord` = the durable business artifact (immutable after session closes)

---

## 25. Replay Manifest

> [!IMPORTANT]
> **NEW SECTION.** Everything needed to reconstruct or analytically replay a decision.

```python
class DecisionReplayManifest(BaseModel):
    """Complete specification for decision replay/reconstruction."""
    
    decision_id: str
    session_id: str
    
    # State
    enterprise_snapshot: DecisionSnapshot
    
    # Models
    agent_model_versions: dict[str, str]    # agent_id -> model version hash
    llm_model_id: str
    llm_model_version: str
    twin_model_version: str
    embedding_model_version: str
    
    # Configuration
    profile_version: str
    policy_version: str
    prompt_versions: dict[str, str]         # agent_id -> prompt template hash
    
    # Reproducibility
    random_seeds: dict[str, int]            # component -> seed (for stochastic elements)
    
    # Events
    event_count: int
    event_log_ref: str                      # Reference to stored event sequence
    
    # Replay classification
    replay_type: Literal[
        "EXACT",         # Same state + same models + same seeds = identical replay
        "ANALYTICAL",    # Different models/state; replay the decision logic
    ]
    
    replay_fidelity_notes: list[str]        # Any factors that may affect replay fidelity
```

---

## 26. Two-Class Retrieval Model

> [!IMPORTANT]
> **EXTENDS Section 6 of the revised architecture.** Adds in-process caching to reduce MCP overhead.

```
CLASS 1: CONTROLLED SYNCHRONOUS RETRIEVAL (MCP-governed)
    - Full JSON-RPC round-trip to MCP server
    - Audit-traced via MCP tool invocation log
    - Used for: initial queries, complex joins, graph traversals
    - Latency budget: < 20ms per call (network + serialization)

CLASS 2: LOCAL HOT-PATH RETRIEVAL (in-process read-through cache)
    - First retrieval: MCP call (audit-traced, result cached)
    - Subsequent retrievals of same entity: in-process cache hit (zero network)
    - Cache scope: single agent reasoning chain within single session
    - Cache key: (session_id, agent_id, entity_type, entity_id)
    - Cache eviction: automatic at end of agent reasoning chain
    - NOT a long-lived cache, NOT cross-session
```

**Rationale:** During a bounded reasoning chain (max 3 iterations), an agent often re-queries the same supplier profile or inventory position. The first retrieval goes through MCP (governance-compliant). Subsequent reads of the same entity skip MCP overhead.

---

## 27. Priority-Aware Admission Control

> [!IMPORTANT]
> **EXTENDS Section 9 of the revised architecture.** Prevents priority inversion.

```yaml
concurrency:
  twin_workers:
    total: 8
    reserved:
      P0: 2    # Always available for critical simulations
      P1: 2    # Always available for human-escalated work
    shared:
      P2_P3: 4 # Shared pool; P2 preempts P3
    preemption:
      P0_can_preempt: [P1, P2, P3]
      P1_can_preempt: [P2, P3]
      P2_can_preempt: [P3]
      P3_can_preempt: []
  
  agent_workers:
    total: 12
    reserved:
      P0: 6    # One per agent for critical work
    shared:
      P1_P2_P3: 6
  
  llm_inference:
    max_concurrent_requests: 4
    priority_queue: true
    P0_timeout_ms: 3000
    P2_timeout_ms: 8000
```

---

## 28. Redis Governance

> [!IMPORTANT]
> **EXTENDS Section 6.2 of the revised architecture.** Defines governance at the policy level, not the mechanism level.

```python
class GovernedDataAccessRecord(BaseModel):
    """All data access -- whether via MCP or direct -- produces this record."""
    
    access_id: str
    agent_id: str
    session_id: str
    data_source: Literal["postgresql", "neo4j", "pgvector", "redis"]
    access_mechanism: Literal["mcp", "direct"]
    query_description: str             # Human-readable query description
    query_hash: str                    # Reproducible query fingerprint
    timestamp: datetime
    data_returned_hash: str            # Hash of returned data
    
    # Governance metadata
    authorized: bool
    audited: bool                      # Always True if governance is working
```

**Rule:** Governance is the POLICY (every access is authorized, audited, and reproducible). MCP is one enforcement mechanism. Application-level logging is another. The governance requirement is satisfied regardless of which mechanism is used.

---

## 29. Capability Versioning & Side-Effect Classification

> [!IMPORTANT]
> **EXTENDS Section 15 of the revised architecture.** MCP capabilities carry version and side-effect metadata.

```python
class CapabilityCard(BaseModel):
    """Extended capability declaration for the Dynamic Capability Registry."""
    
    capability_id: str
    version: str                        # Semver
    schema: dict                        # JSON Schema for parameters and return type
    
    side_effect_class: Literal[
        "READ_ONLY",                    # Pure data retrieval
        "SCENARIO_MUTATION",            # Modifies Twin scenario state only
        "EXTERNAL_SIDE_EFFECT",         # Calls external system (ERP, carrier API)
    ]
    
    authorization_scope: Literal[
        "AGENT",                        # Any agent can invoke
        "COORDINATOR",                  # Only coordinator can invoke
        "EXECUTION_ADAPTER",            # Only execution adapter can invoke
    ]
    
    latency_class: Literal["fast", "medium", "slow"]
    cacheable: bool
    cache_ttl_seconds: Optional[int]
    domain_tags: list[str]
    data_freshness: Literal["real_time", "near_real_time", "batch"]
```

**Runtime enforcement:**
- Agents can ONLY bind capabilities with `side_effect_class = READ_ONLY`
- Twin can bind `READ_ONLY` and `SCENARIO_MUTATION`
- Execution Adapter can bind `EXTERNAL_SIDE_EFFECT` (with policy gate)

---

## 30. Corrected Unified Architecture Diagram

> [!WARNING]
> **REPLACES Section 20 of the revised architecture.** Corrected D-numbers, evidence gate ordering, candidate normalization, and policy layer.

```
+=============================================================================+
|                   SCOF V2 COGNITIVE DECISION FABRIC                        |
|              (D3 through D10 -- Architecture Hardening Revision)           |
+=============================================================================+
|                                                                             |
|  TEN ARCHITECTURAL INVARIANTS (Frozen -- see Section 1)                    |
|                                                                             |
|  +--[D9: OBSERVABILITY, EXPLAINABILITY & DESKTOP CONSOLE]---------------+  |
|  | Tauri v2 | Decision Trace | HITL Escalation | What-If Lab              |  |
|  | Evidence Visualization | Trade-off Explanations | DecisionRecord       |  |
|  +----------------------------------------------------------------------|  |
|       |                    ^                                                |
|       | REST/WS            | Push Events                                   |
|       v                    |                                                |
|  +--[D8: EVENT & RUNTIME BACKBONE (Kafka + Outbox)]--------------------+  |
|  | FastAPI | WebSocket | Transactional Outbox -> Kafka Topics           |  |
|  | SCOFEvent Contract | Consumer Idempotency | Aggregate Versioning     |  |
|  +----------------------------------------------------------------------|  |
|       |                    ^                    ^                           |
|       v                    |                    |                           |
|  +--[D10: EVALUATION]-----+  +--[DECISION POLICY LAYER]--+               |
|  | Ablation Baseline       |  | DecisionPolicy (from      |               |
|  | Ladder (B0-B7)          |  |   profile YAML)           |               |
|  | Anti-overfitting        |  | Objective weights         |               |
|  | R_i Calibration         |  | Hard/soft constraints     |               |
|  | SLA Validation          |  | Execution policy          |               |
|  +-------------------------+  | Policy precedence         |               |
|                               +---------------------------+               |
|                                          |                                 |
|  +=================================================================+      |
|  |        LANGGRAPH ORCHESTRATION KERNEL (D6)                     |      |
|  |        + Coordinator (decomposed into services)                |      |
|  |                                                                 |      |
|  |  [Ingest] -> [Snapshot] -> [RAG T1] -> [Route] -> [Bind] ->   |      |
|  |  -> [Fan-Out (independent)] -> [Fan-In] ->                     |      |
|  |  -> [Cross-Exam (targeted)] ->                                 |      |
|  |  -> [Evidence Sufficiency Gate] ->                              |      |
|  |  -> [Candidate Normalization] ->                                |      |
|  |  -> [Twin Simulation (budgeted)] ->                             |      |
|  |  -> [CD2F Arbitration (objective function)] ->                  |      |
|  |  -> [Execution Policy Check] -> [Execute/Escalate]             |      |
|  +=================================================================+      |
|       |              |              |              |              |         |
|       v              v              v              v              v         |
|  +=================================================================+      |
|  |     LANGCHAIN AGENT REASONING LAYER (D3/D4)                   |      |
|  |     + Agent-Internal Tier-2 RAG (MCP-Governed)                |      |
|  |     + DomainOwnershipPolicy enforcement                       |      |
|  |     + Typed CandidateAction schemas                           |      |
|  |                                                                 |      |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  | | Demand &          | | Inventory &       | | Procurement &     |     |
|  | | Commerce          | | Asset Mgmt        | | Supplier          |     |
|  | | [ownership card]  | | [ownership card]  | | [ownership card]  |     |
|  | | [ML + Bounded LLM]| | [ML + Bounded LLM]| | [ML + Bounded LLM]|     |
|  | | [two-class RAG]   | | [two-class RAG]   | | [two-class RAG]   |     |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  |                                                                 |      |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  | | Logistics &       | | Financial &       | | Risk &            |     |
|  | | Transport         | | Enterprise Value  | | Resilience        |     |
|  | | [ownership card]  | | [ownership card]  | | [ownership card]  |     |
|  | | [ML + Bounded LLM]| | [ML + Bounded LLM]| | [ML + Bounded LLM]|     |
|  | | [two-class RAG]   | | [two-class RAG]   | | [two-class RAG]   |     |
|  | +-------------------+ +-------------------+ +-------------------+     |
|  |                                                                 |      |
|  +=================================================================+      |
|       |                                                                    |
|  +=================================================================+      |
|  |     DELIBERATION TABLE (Event-Sourced Cognitive Workspace)     |      |
|  |                                                                 |      |
|  |  Events:     PostgreSQL (append-only, immutable)               |      |
|  |  Views:      Redis (materialized session projection)           |      |
|  |  Transport:  Kafka (via outbox, keyed by session_id)           |      |
|  |  Replay:     replay_session(session_id, up_to_sequence)        |      |
|  +=================================================================+      |
|       |                                                                    |
|       v                                                                    |
|  +=================================================================+      |
|  |     DIGITAL TWIN -- COUNTERFACTUAL EVALUATOR (D7)             |      |
|  |                                                                 |      |
|  |  Receives: normalized candidates (budgeted, validated)         |      |
|  |  Binds to: DecisionSnapshot baseline                           |      |
|  |  Returns:  SimulationResult per candidate (with fidelity)      |      |
|  |  Produces: SimulationManifest (reproducible)                   |      |
|  |  Enforces: physical invariants, capacity, mass conservation    |      |
|  |  Authority: ONLY within isolated Layer-3 scenario scope        |      |
|  +=================================================================+      |
|       |                                                                    |
|       v                                                                    |
|  +=================================================================+      |
|  |     CD2F EVIDENCE-BASED ARBITRATION ENGINE (D7)               |      |
|  |                                                                 |      |
|  |  Objective:  DecisionObjective (from DecisionPolicy)           |      |
|  |  Process:    FEASIBILITY -> SCORE -> UNCERTAINTY -> PARETO ->  |      |
|  |              AUTHORIZATION                                     |      |
|  |  Math:       J(c) = weighted_objective - penalty - uncertainty  |      |
|  |  Output:     selected action + justification + trade-off       |      |
|  |  Then:       ExecutionPolicyService (separate gate)            |      |
|  +=================================================================+      |
|       |                                                                    |
|       v                                                                    |
|  +=================================================================+      |
|  |     D1 + D2: ENTERPRISE DATA FABRIC (Frozen Baseline)         |      |
|  |                                                                 |      |
|  |  PostgreSQL: System of Record (operational facts)              |      |
|  |  Neo4j:      Topology projection (derived, not dual SoR)      |      |
|  |  pgvector:   Semantic precedent memory                         |      |
|  |  Redis:      Derived cache (governed, not authoritative)       |      |
|  +=================================================================+      |
|                                                                             |
|  CROSS-CUTTING:                                                            |
|  Kafka = event backbone (via outbox, at-least-once, idempotent consumers) |
|  MCP   = governed capability access (versioned, side-effect classified)   |
|  A2A   = agent task contract + health + capability                        |
|  D10   = ablation baselines B0-B7, anti-overfitting, statistical rigor    |
|                                                                             |
+=============================================================================+
```

---

## 31. Revised Implementation Sequencing

> [!WARNING]
> **REPLACES Section 21 of the revised architecture.** D3 scope expanded with vertical research slice. D10 includes ablation ladder.

### Phase 1: Cognitive Agent Runtime + Vertical Research Slice (D3)

**Build:**
- ReasoningService abstraction
- Model provider interface (Ollama initial, swappable)
- Structured output parsing with schema validation
- Bounded tool calling (max iterations, timeout)
- Evidence provenance tracking (EvidenceItem, ValueWithProvenance)
- Deterministic fallback mechanism
- Typed CandidateAction schemas
- Transform ONE agent (Procurement & Supplier -- richest domain)

**Vertical Research Slice (NEW):**
- ONE agent produces ONE structured proposal with ONE candidate action
- ONE minimal Twin simulation (apply action, advance T+7, check KPIs)
- ONE minimal CD2F evaluation (feasibility + objective score, no cross-exam, no multi-agent)
- ONE evaluation metric (did the action improve the target KPI vs. do-nothing baseline?)

**Evaluation Gate:**
> Can one agent produce valid, structured, evidence-backed proposals? Does the minimal agent -> candidate -> Twin -> score -> evaluate loop produce measurably better decisions than a rule-based heuristic (B0) for supplier-delay disruptions?

### Phase 2: Specialist Federation (D4)

**Build:**
- Expand to all six agents
- Agent Card V2 with capability declarations
- DomainOwnershipPolicy per agent (with enforcement)
- Domain-specific RAG configurations
- A2A task lifecycle protocol
- Ownership boundary validation

**Evaluation Gate:**
> Do specialist boundaries improve task performance over a single generalist agent (B1 vs B2)? Does domain-specific RAG improve retrieval precision?

### Phase 3: Evidence Fabric & Retrieval (D5)

**Build:**
- SCOFRetriever with MCP-governed retrieval
- Two-class retrieval model (MCP + local hot-path cache)
- DomainRetrievalConfig per agent
- Coordinator Tier-1 pre-retrieval
- Proposition-specific evidence authority hierarchy
- Neo4j projection freshness metadata
- GovernedDataAccessRecord for Redis
- CapabilityCard with versioning and side-effect classification

**Evaluation Gate:**
> Does MCP-governed RAG improve factual grounding? Does evidence provenance reduce hallucination? Does the two-class retrieval model meet latency targets?

### Phase 4: Cognitive Orchestration & Deliberation (D6)

**Build:**
- LangGraph V2 state machine (corrected ordering: evidence gate before Twin)
- DecisionSnapshot binding at session start
- Event-sourced Deliberation Table
- Domain affinity scoring pipeline
- Two-phase independence protocol (cross-examination)
- Cross-examination termination policy
- Evidence sufficiency gates (multi-dimensional)
- Two-dimensional priority/SLA system
- Priority-aware admission control
- Coordinator service decomposition
- DecisionPolicy loading from profile YAML
- Contradiction taxonomy and resolution
- Cancellation propagation

**Evaluation Gate:**
> Does orchestrated deliberation with cross-examination produce better decisions than independent agents (B2 vs B3)? Does the evidence sufficiency gate prevent bad automated decisions? Does the independence protocol reduce conformity bias?

### Phase 5: CD2F + Counterfactual Decision (D7)

**Build:**
- Candidate normalization pipeline (8-step)
- Twin simulation dispatch with SimulationManifest
- Twin candidate budget enforcement
- CD2F formal objective function (deterministic)
- Pareto ambiguity detection
- Execution authorization separation (ExecutionPolicyService)
- Conflict-to-CD2F pipeline
- R_i governance policy with anti-feedback-loop measures
- SimulationFidelity assessment
- Execution outcome model
- Replanning trigger

**Evaluation Gate:**
> Does Twin simulation + evidence-based arbitration beat naive majority voting (B3 vs B5 vs B6)? Do simulated outcomes correlate with actual outcomes? Does the formal objective function produce more consistent decisions than informal arbitration? Statistical significance: p < 0.05, paired t-test on decision quality score.

### Phase 6: Event & Runtime Backbone (D8)

**Build:**
- Transactional outbox implementation
- Kafka V2 topic architecture (keyed by session_id)
- SCOFEvent contract enforcement
- Consumer idempotency with aggregate versioning
- Redis derived cache population via Kafka consumers
- API Gateway V2 endpoints

**Evaluation Gate:**
> Does Kafka eventing improve auditability and replay without adding unacceptable latency?

### Phase 7: Observability, Explainability & Desktop Console (D9)

**Build:**
- Complete decision trace: trigger -> snapshot -> retrieval -> tool calls -> ML results -> LLM reasoning -> claims -> critiques -> candidates -> normalization -> simulations -> CD2F -> decision -> execution
- Evidence provenance visualization
- Trade-off explanation rendering
- DecisionRecord creation and archival
- Decision replay capability (using DecisionReplayManifest)
- Failure taxonomy logging and dashboards
- Tauri v2 HITL console integration

**Evaluation Gate:**
> Is every decision fully traceable from trigger to outcome? Can a human reviewer understand WHY a decision was made? Can a decision be replayed (EXACT or ANALYTICAL) from its manifest?

### Phase 8: Final Evaluation (D10)

**Build:**
- Full benchmark suite across all 4 disruption classes
- Ablation baseline ladder (B0 through B7)
- Anti-overfitting measures (held-out scenarios, parameter perturbation, distribution shift, noise injection, model misspecification)
- R_i accuracy validation against actual outcomes
- SLA target validation on actual hardware
- Statistical significance testing (p < 0.05, confidence intervals)
- Decision quality scoring with formal metrics
- Cross-model comparison on ReasoningService interface

**Evaluation Metrics:**

| Metric | Target |
| :--- | :--- |
| Decision Quality Score (vs. B0 heuristic) | Statistically significant improvement (p < 0.05) |
| Constraint Violation Rate | < 5% of decisions |
| Service Level Preservation | >= 90% |
| Cost Efficiency (vs. hindsight optimal) | Within 15% |
| Human Agreement | >= 75% on blind sample |
| Calibration (confidence vs. outcome) | r >= 0.60 |
| Latency p95 | Within SLA targets |
| Explainability | >= 90% fully traceable |

**Gate:**
> Does the complete system (B7) satisfy RQ1-RQ4 benchmarks? Does each architectural layer contribute measurable value (ablation analysis)? Are SLA targets achievable on target hardware?

---

## Summary: What This Hardening Revision Changes

| # | Change | Type | Impact |
| :--- | :--- | :--- | :--- |
| 1 | Ten Architectural Invariants | NEW | Replaces 7 amendments |
| 2 | Canonical D3-D10 numbering | FIX | Resolves numbering conflicts |
| 3 | Cognitive stage ordering | FIX | DELIBERATE before EXPLORE |
| 4 | Agent ownership enforcement | EXTEND | DomainOwnershipPolicy |
| 5 | Proposition-specific evidence authority | REPLACE | Neo4j no longer dual SoR |
| 6 | Evidence sufficiency redesign | REPLACE | Multi-dimensional, not agent-presence |
| 7 | Decision snapshot | NEW | Temporal consistency |
| 8 | Candidate normalization | NEW | Prevents explosion |
| 9 | Typed candidate schemas | REPLACE | Discriminated union, not dict |
| 10 | Twin manifest & budget | EXTEND | Reproducibility + budget |
| 11 | CD2F formal objective | REPLACE | Deterministic scoring |
| 12 | Execution authorization | FIX | Separate decision from execution |
| 13 | Decision Policy Layer | NEW | Centralized policy |
| 14 | LangGraph reordering | REPLACE | Evidence gate before Twin |
| 15 | Coordinator decomposition | EXTEND | Internal services |
| 16 | Event-sourced Deliberation Table | EXTEND | Immutable events + views |
| 17 | Cross-examination governance | NEW | Bounds + independence |
| 18 | R_i lifecycle governance | EXTEND | Anti-feedback-loop |
| 19 | Event contract correction | FIX | Accurate guarantee + SCOFEvent |
| 20 | Contradiction taxonomy | NEW | Typed conflict classification |
| 21 | Failure taxonomy | NEW | Structured failure handling |
| 22 | Cancellation propagation | NEW | Session lifecycle |
| 23 | Execution outcome | NEW | Replanning model |
| 24 | Decision Record | NEW | Durable business artifact |
| 25 | Replay manifest | NEW | Decision reconstruction |
| 26 | Two-class retrieval | EXTEND | MCP + local cache |
| 27 | Priority admission control | EXTEND | Anti-inversion |
| 28 | Redis governance | EXTEND | Policy-level governance |
| 29 | Capability versioning | EXTEND | Side-effect classification |
| 30 | Architecture diagram | REPLACE | Corrected diagram |
| 31 | Implementation sequencing | REPLACE | D3 vertical slice + D10 ablation |

---

> [!IMPORTANT]
> After this hardening revision, the architecture reaches the maturity level described by the audit as "strong architecture whose remaining problems are mostly formalization, state semantics, policy semantics, and lifecycle correctness." All 20 contradictions from the audit's register are resolved. The architecture is ready for D3 implementation.
