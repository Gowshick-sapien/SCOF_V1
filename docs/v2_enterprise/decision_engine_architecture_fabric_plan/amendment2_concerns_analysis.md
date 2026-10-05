# SCOF V2 Architecture Audit -- Critical Analysis & Response

## Document Purpose

This document responds to every substantive finding in the Critical Architecture Audit of the SCOF V2 D3-D10 Revised Architecture. For each of the 64 audit points, I provide: my verdict, detailed rationale, and concrete solutions for open-ended questions. Where the audit identifies a genuine flaw, I state the correction. Where it raises a design question, I propose the primary solution and alternatives.

> [!IMPORTANT]
> This document does NOT alter the existing revised architecture. It serves as the analytical basis for the Architecture Hardening Revision (Document 2), which will incorporate only the P0-level corrections into the architecture.

---

## Verdicts Summary

### Contradiction Register Response

| # | Audit Finding | Severity | My Verdict | Action |
| :--- | :--- | :--- | :--- | :--- |
| 1 | D7/D9 deliverable numbering conflicts | CRITICAL | AGREE | Fix in hardening |
| 2 | EXPLORE before DELIBERATE vs actual flow | CRITICAL | AGREE | Reorder cognitive model |
| 3 | Neo4j called authoritative fact vs D2 projection | CRITICAL | AGREE | Correct hierarchy |
| 4 | Evidence sufficiency = agent presence | CRITICAL | AGREE | Redesign gate |
| 5 | Tier-1 "auto-commit" vs mandatory HITL | CRITICAL | AGREE | Resolve terminology |
| 6 | Twin before evidence gate | CRITICAL | AGREE | Reorder LangGraph |
| 7 | Global evidence hierarchy vs proposition-specific | MODERATE | AGREE | Redesign as claim-type-dependent |
| 8 | CD2F without formal objective model | CRITICAL | AGREE | Define objective function |
| 9 | Twin "all candidates" without budget | CRITICAL | AGREE | Add candidate budget |
| 10 | Postgres authority vs Twin runtime state | MODERATE | AGREE | Clarify Twin state contract |
| 11 | Outbox guarantee overstated | MODERATE | AGREE | Correct language |
| 12 | Coordinator monolith risk | MODERATE | AGREE | Decompose into services |
| 13 | Deliberation Table mutable vs replay | MODERATE | AGREE | Event-source model |
| 14 | No decision snapshot / state versioning | CRITICAL | AGREE | Add snapshot semantics |
| 15 | No cross-examination termination policy | MODERATE | AGREE | Add bounds |
| 16 | R_i feedback/self-reinforcement | MODERATE | AGREE | Add lifecycle governance |
| 17 | No explicit policy layer | CRITICAL | AGREE | Define policy layer |
| 18 | CandidateAction parameters untyped | MODERATE | AGREE | Add typed schemas |
| 19 | No execution compensation/replanning | MODERATE | PARTIALLY AGREE | Scope appropriately |
| 20 | No cancellation propagation | MODERATE | AGREE | Add cancellation model |

---

## Detailed Response by Audit Section

---

### Audit Section 3: Amendment 1 -- Agent Ownership Enforcement

**Audit Finding:** Ownership is semantic prose, not machine-enforced.

**VERDICT: AGREE**

The audit is correct that saying "Procurement owns supplier performance" is a documentation constraint, not a runtime-enforceable one. Without machine-readable ownership contracts, nothing prevents an agent from straying into another's domain.

**Primary Solution: DomainOwnershipPolicy in Agent Card V2**

```python
class DomainOwnershipPolicy(BaseModel):
    """Machine-enforceable ownership boundaries for each agent."""
    
    # What this agent authoritatively owns
    owned_entity_types: list[str]       # ["supplier_performance", "contract_terms"]
    owned_metric_types: list[str]       # ["otif_score", "lead_time_distribution"]
    owned_claim_types: list[str]        # ["supplier_operational_assessment"]
    
    # What this agent may propose as candidate actions
    permitted_action_types: list[str]   # ["alternate_supplier", "po_reallocation"]
    
    # What this agent explicitly consumes from others
    consumes_from: dict[str, list[str]] # {"risk_resilience": ["supplier_financial_distress"]}
    
    # Hard boundary: things this agent may never claim or propose
    forbidden_claim_types: list[str]    # ["supplier_creditworthiness"]
    forbidden_action_types: list[str]   # ["financial_exposure_override"]
```

**Enforcement mechanism:** The Coordinator validates every `AgentProposal` against the agent's `DomainOwnershipPolicy` before posting it to the Deliberation Table. If a proposal contains a claim type or candidate action type in the `forbidden_*` lists, the Coordinator rejects it with a schema validation error and requests a revised output from the agent.

This converts ownership from documentation into a runtime-enforced property.

**Alternative:** Enforce at the MCP level -- if an agent's MCP tool bindings do not include tools required for a given claim type, the agent physically cannot produce evidence for that claim. This is weaker but requires no post-hoc validation.

**Decision:** Adopt the primary solution. Include `DomainOwnershipPolicy` in Agent Card V2. Embed in hardening revision.

---

### Audit Section 4: RAG MCP Latency

**Audit Finding:** MCP is now in the latency-critical data plane. The architecture cannot simultaneously assume MCP governance + multiple retrievals + LLM + cross-examination + Twin + CD2F within aggressive targets.

**VERDICT: AGREE**

The audit correctly identifies that adding MCP as an intermediary adds serialization/deserialization and network round-trip overhead to every retrieval. For six agents each making 3-5 MCP calls, this is non-trivial.

**Primary Solution: Two-Class Retrieval Model**

```
CLASS 1: CONTROLLED SYNCHRONOUS RETRIEVAL (MCP-governed)
    - Full JSON-RPC round-trip
    - Audit-traced via MCP tool invocation log
    - For: complex queries, multi-table joins, graph traversals
    - Latency budget: per-call < 20ms

CLASS 2: LOCAL HOT-PATH RETRIEVAL (in-process read-through cache)
    - Pre-authorized data patterns loaded into agent-local cache at session start
    - Cache populated from MCP at session initialization
    - Subsequent reads are in-process, zero-network-hop
    - For: repeated lookups of the same entity during a single reasoning chain
    - Examples: same supplier profile, same inventory position, same contract terms
    - Cache scope: single deliberation session only (no cross-session persistence)
    - Cache key: (session_id, agent_id, entity_type, entity_id)
```

The key insight: during a single bounded reasoning chain (max 3 iterations), an agent often queries the same entity multiple times. The first retrieval goes through MCP (audit-traced). Subsequent retrievals of the same entity within the same session hit the local cache.

**Alternative:** Pre-fetch all likely-needed entities via a single batched MCP call at the start of agent processing, then reason entirely from local cache. This is simpler but requires predicting what the agent will need before it starts reasoning.

**Decision:** Adopt the primary solution. Define two retrieval classes in the RAG section of the hardening revision.

---

### Audit Section 5: Neo4j Authority -- CRITICAL

**Audit Finding:** Neo4j is called "Level 1 AUTHORITATIVE_FACT" alongside PostgreSQL, but the frozen V2 architecture explicitly defines Neo4j as a materialized topology projection, not a System of Record.

**VERDICT: AGREE -- This is the most important factual correction in the audit.**

The frozen D1/D2 architecture is clear:
- PostgreSQL = System of Record (operational facts)
- Neo4j = Materialized topology projection (derived from PostgreSQL via batch/streaming sync)

If `supplier.status = SUSPENDED` in PostgreSQL but Neo4j's projection has not yet been updated, Neo4j will still show `ACTIVE`. Treating both as Level 1 authoritative creates a false dual-source-of-truth.

**Correction: Proposition-Specific Authority Hierarchy**

The global linear hierarchy is replaced with a claim-type-dependent authority model:

```
CURRENT-STATE CLAIM (e.g., "inventory is 500 units"):
    AUTHORITATIVE:  PostgreSQL (System of Record)
    DERIVED:        Neo4j projection (check projection_version)
    NON-AUTHORITATIVE: LLM interpretation

TOPOLOGICAL CLAIM (e.g., "DC-003 supplies stores S-101, S-102"):
    AUTHORITATIVE:  Neo4j projection (this IS its purpose)
    REFERENCE:      PostgreSQL source tables
    NON-AUTHORITATIVE: LLM interpretation

FORECAST CLAIM (e.g., "demand will increase 35%"):
    AUTHORITATIVE:  Validated ML model
    SUPPLEMENTARY:  Historical precedent (pgvector)
    NON-AUTHORITATIVE: LLM estimation

COUNTERFACTUAL CLAIM (e.g., "if we reroute, inventory at T+7 = 380"):
    AUTHORITATIVE:  Twin simulation (this IS its purpose)
    SUPPLEMENTARY:  Heuristic estimate
    NON-AUTHORITATIVE: LLM speculation

HISTORICAL-ANALOGUE CLAIM (e.g., "similar disruptions had 72% resolution"):
    AUTHORITATIVE:  Validated pgvector precedent with confirmed outcome
    SUPPLEMENTARY:  Generic LLM world knowledge
    NON-AUTHORITATIVE: Unvalidated LLM recall
```

**Every Neo4j evidence item now carries projection metadata:**

```python
class Neo4jEvidenceItem(EvidenceItem):
    """Evidence from Neo4j carries projection freshness metadata."""
    projection_version: str          # Version of the projection pipeline
    projected_at: datetime           # When this projection was last computed
    source_snapshot_version: str     # Which PostgreSQL state it was derived from
    projection_lag_ms: int           # Time since last sync from PostgreSQL
```

**Conflict resolution rule:** If a current-state claim from Neo4j contradicts PostgreSQL, PostgreSQL wins. The system logs a projection-staleness warning and triggers an immediate re-projection of the affected subgraph.

**Decision:** This is a P0 correction. Embed in the hardening revision.

---

### Audit Section 6: Outbox Guarantee

**Audit Finding:** "No split-brain" overstates the outbox guarantee. Outbox gives atomic persistence, not exactly-once end-to-end delivery.

**VERDICT: AGREE**

The transactional outbox guarantees that if PostgreSQL commits, the corresponding event intent is also persisted. It does NOT guarantee:
- Exactly-once delivery to Kafka (relay can retry, producing duplicates)
- Exactly-once processing by consumers (consumer can crash after processing but before committing offset)

**Correction: Accurate guarantee statement + idempotency contract**

Replace the current guarantee with:

> "PostgreSQL provides authoritative durable state. Kafka provides at-least-once event distribution via the outbox relay. Consumers achieve effective exactly-once state transitions through idempotent processing with aggregate version checks."

**Core event contract (must be part of the architecture, not deferred to D8):**

```python
class SCOFEvent(BaseModel):
    """Base contract for all events in the SCOF event backbone."""
    event_id: str                    # Globally unique, generated at source
    aggregate_type: str              # "deliberation_item", "verdict", "session"
    aggregate_id: str                # The entity this event relates to
    aggregate_version: int           # Monotonically increasing per aggregate
    event_type: str                  # "item.posted", "verdict.submitted"
    causation_id: str                # ID of the event that caused this event
    correlation_id: str              # Links all events in a single decision session
    producer_id: str                 # Which component produced this event
    schema_version: str              # Event schema version for evolution
    payload: dict                    # Event-specific payload
    timestamp: datetime
```

**Consumer idempotency rule:** Before applying an event, consumers check `aggregate_version`. If `event.aggregate_version <= current_stored_version`, the event is a duplicate and is discarded.

**Decision:** Correct the guarantee language and embed the event contract in the hardening revision as a cross-cutting architectural contract.

---

### Audit Section 7: Priority Inversion

**Audit Finding:** P3 workloads can consume all Twin workers, blocking P0 cognitive paths.

**VERDICT: AGREE**

**Solution: Priority-Aware Admission Control**

```yaml
concurrency:
  twin_workers:
    total: 8
    reserved:
      P0: 2    # Always available for critical simulations
      P1: 2    # Always available for human-escalated
    shared:
      P2_P3: 4 # Shared pool, P2 preempts P3
    preemption:
      P0_can_preempt: [P1, P2, P3]
      P1_can_preempt: [P2, P3]
      P2_can_preempt: [P3]
      P3_can_preempt: []
  
  agent_workers:
    total: 12  # 2 per agent
    reserved:
      P0: 6    # One per agent
    shared:
      P1_P2_P3: 6
```

This directly reuses the [4-Tier Priority Queue](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/architecture/04_minimalist_concurrency_and_worker_pool.md) pattern already established for Twin Service concurrency, extended to the D3-D10 Cognitive Fabric.

**Decision:** Add to the hardening revision under the Priority/SLA section.

---

### Audit Section 8-9: Evidence Sufficiency Redesign -- CRITICAL

**Audit Finding:** "Agent presence != evidence sufficiency." A mandatory agent responding with stale, low-authority, or irrelevant evidence is not "sufficient."

**VERDICT: AGREE -- This is the second most important correction after Neo4j authority.**

**Primary Solution: Multi-Dimensional Evidence Sufficiency Assessment**

```python
class EvidenceSufficiencyAssessment(BaseModel):
    """Replaces the binary 'did agents respond?' check."""
    
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
        "SUFFICIENT",           # Proceed to Twin + CD2F
        "MARGINALLY_SUFFICIENT", # Proceed with elevated caution / reduced autonomy
        "INSUFFICIENT",          # Escalate to HITL
    ]
    insufficiency_reasons: list[str]
    
class DomainCoverageAssessment(BaseModel):
    """Are the required domains represented?"""
    mandatory_agents_responding: int
    mandatory_agents_expected: int
    coverage_score: float           # responding / expected
    missing_critical_domains: list[str]

class EvidenceQualityAssessment(BaseModel):
    """Is the evidence actually good enough?"""
    min_evidence_authority: EvidenceAuthority   # Lowest authority level present
    avg_evidence_freshness: float               # Average freshness across all evidence
    stale_evidence_count: int                   # Evidence items older than freshness threshold
    critical_facts_present: bool                # Are the core facts for this disruption type present?
    model_validity: float                       # Are the ML models applicable to this disruption type?
    
class ConsistencyAssessment(BaseModel):
    """Do the agents' evidence bases agree on observable facts?"""
    contradiction_count: int
    contradiction_severity: Literal["NONE", "MINOR", "MAJOR", "BLOCKING"]
    contradicted_facts: list[str]
```

**Composite verdict logic:**

```
domain_coverage >= 0.80
AND avg_evidence_freshness >= 0.60
AND critical_facts_present == True
AND contradiction_severity != "BLOCKING"
    --> SUFFICIENT

domain_coverage >= 0.60
AND avg_evidence_freshness >= 0.40
AND critical_facts_present == True
AND contradiction_severity != "BLOCKING"
    --> MARGINALLY_SUFFICIENT (CD2F applies caution penalty)

else
    --> INSUFFICIENT (HITL escalation)
```

Thresholds are configurable via the Decision Policy (see Audit Section 47).

**Decision:** P0 correction. This replaces the current binary agent-presence check.

---

### Audit Sections 10-11: CD2F Objective Function -- CRITICAL

**Audit Finding:** CD2F says "which candidate action is best justified" but never formally defines what "best" means. Without an explicit objective function, CD2F is still ultimately arbitrary.

**VERDICT: AGREE**

**Primary Solution: Deterministic Objective Function**

```python
class DecisionObjective(BaseModel):
    """The organization's definition of 'best'. Comes from the policy layer, 
    NOT from agents or LLMs."""
    
    # Objective vector weights (sum to 1.0)
    service_level_weight: float     # Importance of maintaining service levels
    cost_weight: float              # Importance of minimizing cost
    risk_weight: float              # Importance of minimizing risk
    inventory_weight: float         # Importance of inventory health
    lead_time_weight: float         # Importance of delivery speed
    carbon_weight: float            # Importance of sustainability
    
    # Hard constraints (violating any of these eliminates the candidate)
    hard_constraints: list[HardConstraint]
    
    # Soft constraints (penalty applied, but does not eliminate)
    soft_constraints: list[SoftConstraint]
    
    # Risk tolerance
    max_acceptable_risk: float      # Candidates exceeding this are eliminated
    
    # Financial autonomy
    max_autonomous_cost_usd: float  # Above this, escalate to HITL
    
    # Escalation sensitivity
    pareto_ambiguity_threshold: float  # If top candidates within this margin, escalate

class HardConstraint(BaseModel):
    constraint_id: str
    description: str
    metric: str                     # e.g., "reefer_capability", "capacity_available"
    operator: Literal[">=", "<=", "==", "!="]
    threshold: Any
    
class SoftConstraint(BaseModel):
    constraint_id: str
    description: str
    metric: str
    target: float
    penalty_per_unit_violation: float
```

**CD2F Formal Arbitration Process:**

```
STAGE 1: FEASIBILITY FILTER
    For each candidate:
        For each hard_constraint:
            If candidate violates constraint -> ELIMINATE
    Output: feasible_candidates

STAGE 2: OBJECTIVE SCORE
    For each feasible candidate c:
        J(c) = (
            w_service * service_level_delta(c)
          - w_cost    * cost_impact(c)
          - w_risk    * risk_score(c)
          - w_inv     * inventory_degradation(c)
          - w_lead    * lead_time_increase(c)
          - w_carbon  * carbon_increase(c)
        )
    
    Apply soft constraint penalties:
        J_adj(c) = J(c) - sum(penalty for each soft constraint violation)

STAGE 3: UNCERTAINTY ADJUSTMENT
    For each candidate c:
        J_final(c) = J_adj(c) - lambda * uncertainty(c)
    
    Where uncertainty(c) is derived from:
        - Evidence authority quality (Level 1 evidence = low uncertainty)
        - Evidence freshness
        - Agent reliability (R_i)
        - Simulation fidelity
        - Sample size of supporting precedents

STAGE 4: PARETO CHECK
    If |J_final(A) - J_final(B)| < pareto_ambiguity_threshold:
        -> PARETO_AMBIGUITY -> HITL escalation with trade-off summary
    
    If single dominant candidate:
        -> SELECT

STAGE 5: EXECUTION AUTHORIZATION
    If cost_impact > max_autonomous_cost_usd:
        -> TIER_3 (HITL required regardless of confidence)
    
    If uncertainty(selected) > uncertainty_threshold:
        -> TIER_2 (extended deliberation)
    
    Else:
        -> TIER_1 (approved for execution policy check)
```

This is deterministic, auditable, and reproducible. No LLM involved in the scoring. The LLM's contribution ends at the agent proposal stage; CD2F is pure computation.

**Alternative:** Multi-Criteria Decision Analysis (MCDA) with TOPSIS or ELECTRE methods. These are more sophisticated but harder to explain to stakeholders.

**Decision:** Adopt the primary solution. The deterministic weighted objective with uncertainty adjustment is the right balance of rigor and interpretability for SCOF.

---

### Audit Sections 12-13: R_i Lifecycle & Self-Reinforcement

**Audit Finding:** R_i can create feedback loops (poorly-performing agents lose influence, get fewer opportunities to demonstrate improvement; well-performing agents get self-reinforcing advantages).

**VERDICT: AGREE**

**Solution: R_i Governance Policy**

```python
class ReliabilityGovernancePolicy(BaseModel):
    """Controls R_i computation to prevent feedback loops."""
    
    # Temporal controls
    evaluation_window_days: int = 90       # Only consider last N days
    minimum_sample_size: int = 10          # Below this, use prior
    cold_start_prior: float = 0.50         # Default R_i for new/retrained agents
    
    # Decay
    decay_half_life_days: int = 30         # Older evaluations decay exponentially
    
    # Stratification (R_i computed separately for each stratum)
    stratify_by: list[str] = [
        "disruption_type",       # Different R_i per disruption class
        "decision_class",        # Routine vs emergency
        "model_version",         # Retrained model gets fresh R_i
    ]
    
    # Anti-lock-out
    min_r_i: float = 0.20                  # No agent's R_i can fall below this
    max_r_i: float = 0.95                  # No agent's R_i can exceed this
    
    # Confidence interval
    compute_confidence_interval: bool = True  # Report CI alongside point estimate
    
    # Update policy
    update_frequency: str = "per_session"  # Update after every decision session
    batch_recalibration_cron: str = "weekly"  # Full recalibration weekly

class ReliabilityScore(BaseModel):
    """Enhanced R_i with governance metadata."""
    agent_id: str
    disruption_type: str
    model_version: str
    
    # Core metrics
    accuracy: float
    calibration: float
    constraint_violation_rate: float
    outcome_quality: float
    
    # Composite
    composite_r_i: float
    confidence_interval: tuple[float, float]  # (lower, upper) at 95% CI
    
    # Governance metadata
    sample_size: int
    evaluation_window_start: datetime
    evaluation_window_end: datetime
    is_cold_start: bool
    prior_used: bool
```

The `min_r_i = 0.20` floor prevents permanent lock-out. The stratification by `model_version` means a retrained/improved agent starts with a fresh cold-start prior rather than inheriting its predecessor's poor score.

**Decision:** Adopt. Include in hardening revision.

---

### Audit Section 13: Twin Candidate Explosion -- CRITICAL

**Audit Finding:** Six agents producing 3 candidates each = 18 candidates. With combinations, the search space explodes.

**VERDICT: AGREE**

**Primary Solution: Candidate Budget + Normalization Pipeline**

```yaml
twin:
  candidate_budget:
    max_raw_candidates_per_session: 20     # Total from all agents
    max_candidates_per_agent: 4            # Per-agent limit
    max_combined_actions: 3                # Max composite candidates
    max_simulation_branches: 8             # Total Twin simulations
    max_simulation_horizon_days: 28
    max_parallel_simulations: 4
```

**Candidate normalization pipeline (between cross-examination and Twin dispatch):**

```
STEP 1: EXTRACT
    Collect all candidate actions from all agent proposals
    Raw candidates: up to 24 (6 agents x 4 max)

STEP 2: SCHEMA VALIDATION
    Validate every candidate against its typed action schema
    Reject malformed candidates (LLM produced invalid parameters)

STEP 3: ENTITY VALIDATION
    Verify referenced entities exist in D2
    (e.g., carrier_id "CR-9999" does not exist -> reject)

STEP 4: CONSTRAINT PRE-CHECK
    Quick hard-constraint check (no simulation needed)
    (e.g., proposed route has no reefer capability for perishable -> eliminate)

STEP 5: DEDUPLICATION
    Merge semantically identical candidates from different agents
    (e.g., both Procurement and Risk recommend switching to SUP-0112)

STEP 6: DOMINANCE PRUNING
    If candidate A is strictly worse than B on ALL objective dimensions
    -> eliminate A

STEP 7: TOP-K SELECTION
    Rank remaining candidates by estimated objective score
    Select top K candidates (K = max_simulation_branches)
    Always include: "do nothing + buffer" baseline

STEP 8: COMBINATION SYNTHESIS (if warranted)
    Generate up to max_combined_actions composite candidates
    Only for non-conflicting candidates from different domains
    (e.g., Procurement switch supplier + Logistics alternate route)

OUTPUT: Normalized candidate set (max 8 + 1 baseline = 9 simulations)
```

**Decision:** P0 correction. Embed in hardening revision.

---

### Audit Section 14: Evidence Sufficiency Gate Ordering -- CRITICAL

**Audit Finding:** The LangGraph state machine runs Twin simulation BEFORE the evidence sufficiency gate, wasting compute on decisions that may be escalated to HITL.

**VERDICT: AGREE**

This is a straightforward ordering error. The corrected LangGraph sequence:

```
cross_examination
    -> [blocking_critiques? -> revision -> fan_in_revised]
    -> evidence_sufficiency_gate              (MOVED UP)
    -> [sufficient?]
        -> INSUFFICIENT: hitl_escalation -> END
        -> MARGINALLY_SUFFICIENT: proceed with caution flag
        -> SUFFICIENT: proceed
    -> candidate_extraction
    -> candidate_normalization                 (NEW)
    -> [twin_simulation_needed?]
        -> YES: twin_dispatch -> twin_collect
        -> NO: proceed
    -> cd2f_arbitration
    -> [execution_authorization]
        -> ...
```

This prevents burning Twin simulation budget on decisions where evidence is already known to be insufficient.

**Decision:** P0 correction. Reorder in hardening revision.

---

### Audit Section 15: Cognitive Stage Ordering -- CRITICAL

**Audit Finding:** The six-stage model says EXPLORE (Twin) before DELIBERATE (cross-examination), but the actual pipeline does DELIBERATE before EXPLORE.

**VERDICT: AGREE**

The actual execution sequence is:

```
KNOW         (RAG retrieval)
UNDERSTAND   (Agent claim generation)
DELIBERATE   (Cross-examination, critique, revision)
EXPLORE      (Twin counterfactual simulation)
DECIDE       (CD2F arbitration)
EXPLAIN      (Observability trace)
```

The conceptual model must match the implementation. But I also agree with the audit's observation that DELIBERATE and EXPLORE can interact iteratively (Twin reveals unexpected outcome -> targeted re-deliberation -> revised candidate -> re-simulate).

**Corrected cognitive model:**

```
                    KNOW
                      |
                 UNDERSTAND
                      |
                 DELIBERATE
                /           \
       revise/critique    candidate actions
                              |
                           EXPLORE
                        Digital Twin
                              |
                  [if unexpected outcome]
                        |            |
                   re-deliberate    proceed
                        |            |
                        +-----+------+
                              |
                           DECIDE
                            CD2F
                              |
                           EXPLAIN
```

The key change: DELIBERATE -> EXPLORE -> DECIDE is the primary flow, with an optional EXPLORE -> DELIBERATE loop for unexpected simulation results.

**Decision:** P0 correction. Redraw the cognitive model in the hardening revision.

---

### Audit Section 16: Twin Scenario-State Contract

**Audit Finding:** The Twin's scenario-state semantics are under-specified. No definition of how scenarios are created, cloned, isolated, named, garbage-collected, or reproduced.

**VERDICT: AGREE**

**Solution: Twin Simulation Manifest**

```python
class SimulationManifest(BaseModel):
    """Complete specification for a reproducible Twin simulation."""
    
    # Identity
    simulation_id: str
    session_id: str
    candidate_action_id: str
    
    # Baseline binding
    baseline_snapshot_id: str            # Which Layer-2 snapshot this starts from
    baseline_snapshot_version: int       # Snapshot sequence number
    baseline_data_as_of: datetime        # When the snapshot was taken
    
    # Branch isolation
    parent_branch_id: Optional[str]      # None = root branch from baseline
    branch_version: int
    scenario_isolation_mode: Literal[
        "COPY_ON_WRITE",                 # Standard: isolated fork
        "FULL_CLONE",                    # For deterministic replay
    ]
    
    # Simulation parameters
    simulation_clock_start: datetime
    simulation_clock_end: datetime
    time_horizons: list[int]             # [7, 14, 28] days
    action_set: list[CandidateAction]    # Actions applied to the branch
    action_set_hash: str                 # SHA-256 of the action set
    
    # Reproducibility
    model_version: str                   # Twin model version
    profile_version: str                 # Domain profile version
    random_seed: int                     # For stochastic elements
    input_state_hash: str                # SHA-256 of the starting state
    
    # Lifecycle
    created_at: datetime
    completed_at: Optional[datetime]
    gc_eligible_after: datetime          # When this branch can be garbage-collected
    
    # Guarantee
    # same input_state_hash + same action_set_hash + same model_version
    # + same random_seed = identical simulation_result
```

**Garbage collection policy:**

```yaml
twin:
  scenario_lifecycle:
    active_retention: "until_session_resolved"
    archive_retention_days: 30
    gc_policy: "delete_branch_state_after_archive"
    max_concurrent_branches: 16
```

**Decision:** P0 correction. Add Twin simulation manifest to hardening revision.

---

### Audit Section 17: Evidence Hierarchy -- Proposition-Specific

**Audit Finding:** The global linear hierarchy (FACT > COMPUTED > MODEL > SIMULATION > PRECEDENT > LLM) is conceptually wrong because simulation may be more authoritative than ML for counterfactual claims, while ML may be more authoritative than simulation for probability estimates.

**VERDICT: AGREE**

This was already addressed in my Neo4j correction above (Audit Section 5). The authority hierarchy is now claim-type-dependent, not globally linear.

**Decision:** Already included in Neo4j correction. No additional action.

---

### Audit Section 18: "LLM Cannot Calculate" Nuance

**Audit Finding:** The rule should be "LLM-generated numerical values are non-authoritative unless independently verified" rather than "LLMs cannot do arithmetic."

**VERDICT: AGREE**

The architectural intent is correct (LLM numbers must not be authoritative). The framing should be refined.

**Correction:** Replace "LLMs Do Not Calculate" with:

> **LLM-Produced Values Are Non-Authoritative.** An LLM may perform intermediate arithmetic during reasoning, but any numerical value that appears in a `StructuredClaim` or `CandidateAction` must have `source != LLM_INTERPRETATION` for it to be treated as reliable by CD2F. If the only source for a critical number is LLM reasoning, the evidence quality assessment reduces the claim's authority.

**Decision:** Refinement for hardening revision. The architectural mechanism (ValueWithProvenance) already enforces this; the prose needs updating.

---

### Audit Section 19: Coordinator Monolith Risk

**Audit Finding:** The Coordinator now owns: table management, routing, Tier-1 RAG, capability resolution, cross-examination, evidence gating, Twin dispatch, CD2F handoff, audit emission. Risk of becoming the new monolith.

**VERDICT: AGREE**

**Primary Solution: Internal Service Decomposition**

The Coordinator remains a single logical component (one LangGraph state machine), but its implementation is decomposed into distinct internal services:

```
Coordinator (LangGraph State Machine)
    |
    +-- RoutingService
    |     Computes domain affinity scores
    |     Applies threshold configuration
    |     Owns: affinity pipeline, agent assignment
    |
    +-- DeliberationService
    |     Manages table items, sessions, lifecycle
    |     Owns: session creation, item posting, verdict collection
    |
    +-- EvidenceSufficiencyService
    |     Evaluates multi-dimensional sufficiency
    |     Owns: coverage, quality, consistency assessment
    |
    +-- CandidateService
    |     Extracts, validates, normalizes, prunes candidates
    |     Owns: candidate budget enforcement
    |
    +-- SimulationDispatchService
    |     Creates simulation manifests, dispatches to Twin
    |     Collects results, attaches to decision package
    |     Owns: simulation budget, Twin interface
    |
    +-- AuditService
    |     Emits complete decision traces
    |     Owns: observability event production
    |
    +-- ExecutionPolicyService
          Applies authorization rules
          Owns: tier determination, HITL escalation logic
```

Each service is:
- Independently testable (unit tests with mocked dependencies)
- Independently replaceable
- Clearly bounded in responsibility
- Invoked by the LangGraph state machine as a step in the workflow

The Coordinator state machine orchestrates these services. It does not contain their logic.

**Decision:** Adopt as architectural pattern. Document in hardening revision.

---

### Audit Section 20: Deliberation Table -- Event Sourcing vs. CRUD

**Audit Finding:** The table has mutable fields (status, verdicts, assigned_agents) but the architecture emphasizes replay and auditability. The design is halfway between event sourcing and CRUD.

**VERDICT: AGREE**

**Primary Solution: Event-Sourced Deliberation with Materialized Views**

```python
class DeliberationEvent(BaseModel):
    """Immutable event in the deliberation event stream."""
    event_id: str
    session_id: str
    sequence_number: int              # Monotonically increasing within session
    event_type: Literal[
        "SESSION_STARTED",
        "ITEM_POSTED",
        "ITEM_SCOPED",
        "ITEM_ASSIGNED",
        "VERDICT_SUBMITTED",
        "CRITIQUE_SUBMITTED",
        "REVISION_SUBMITTED",
        "ENDORSEMENT_SUBMITTED",
        "EVIDENCE_GATE_EVALUATED",
        "CANDIDATE_EXTRACTED",
        "SIMULATION_DISPATCHED",
        "SIMULATION_COMPLETED",
        "CD2F_SUBMITTED",
        "DECISION_RESOLVED",
        "SESSION_CLOSED",
        "SESSION_CANCELLED",
    ]
    actor: str                        # agent_id, "coordinator", "human:operator_id"
    payload: dict                     # Event-specific data
    timestamp: datetime
    causation_id: str                 # Which event caused this event
    correlation_id: str               # = session_id (links all events in a session)
```

```python
class DeliberationSessionView(BaseModel):
    """Materialized projection of the current session state.
    Derived from replaying DeliberationEvents. 
    This is what agents and the Coordinator read."""
    
    session_id: str
    current_status: str
    items: list[DeliberationItemView]
    verdicts: list[DeliberationVerdictView]
    current_sequence: int
    last_event_at: datetime
```

**Storage:**

```
DeliberationEvents -> PostgreSQL (immutable append-only table)
                   -> Kafka (via outbox, for distribution)
                   -> Redis (materialized session view for fast reads)
```

**Replay:** To reconstruct any session's exact state at any point:

```python
events = db.query(
    "SELECT * FROM deliberation_events WHERE session_id = ? ORDER BY sequence_number"
)
state = replay(events, up_to_sequence=N)
```

**Decision:** Adopt event sourcing for the Deliberation Table. This cleanly resolves the mutability vs. replay tension.

---

### Audit Section 21: Session/Proposal Versioning

**Audit Finding:** Proposals get revised but there is no explicit version lineage.

**VERDICT: AGREE**

**Solution:** Add versioning to all mutable decision objects:

```python
class VersionedProposal(BaseModel):
    proposal_id: str
    proposal_version: int             # Monotonically increasing
    parent_proposal_id: Optional[str] # Previous version's ID
    parent_version: Optional[int]
    agent_id: str
    session_id: str
    
    # Content (same as AgentProposal)
    claim: StructuredClaim
    candidate_actions: list[CandidateAction]
    recommended_action_id: str
    
    # Revision metadata
    revision_trigger: Optional[str]   # Which critique triggered this revision
    changes_from_parent: list[str]    # Summary of what changed
```

**CD2F always references the latest version** but retains the full lineage for audit.

**Decision:** Include in hardening revision.

---

### Audit Section 22-23: Decision Snapshot & Time Consistency -- CRITICAL

**Audit Finding:** Different agents can reason over different world-states if there is no session-level consistency boundary.

**VERDICT: AGREE**

**Primary Solution: DecisionSnapshot**

Every `DecisionSession` is bound to a declared observation boundary:

```python
class DecisionSnapshot(BaseModel):
    """The declared world-state boundary for a decision session."""
    snapshot_id: str
    session_id: str
    
    # State binding
    enterprise_state_version: int        # PostgreSQL WAL LSN or sequence
    neo4j_projection_version: str        # Which projection epoch
    pgvector_index_version: str          # Embedding index version
    
    # Temporal boundary
    observation_cutoff: datetime          # No evidence newer than this is used
    
    # Freshness policy
    max_fact_age_minutes: int = 5         # Critical current-state facts must be
                                          # within this age
    max_model_age_hours: int = 24         # ML model outputs within this age
    max_precedent_age_days: int = 365     # Historical precedents within this age
    
    # Consistency check
    snapshot_hash: str                    # Hash of the snapshot parameters
```

**Enforcement:** The Coordinator creates the `DecisionSnapshot` at session start. The `ContextPackage` sent to agents includes the snapshot binding. Every `EvidenceItem` produced by agents must have `data_as_of <= snapshot.observation_cutoff`. Evidence items that violate the freshness policy are flagged in the evidence quality assessment.

**Stale-Decision Check:** Before execution (after CD2F approval, before Execution Adapter):

```python
if current_enterprise_state_version != decision.snapshot.enterprise_state_version:
    # World changed during deliberation
    if change_affects_decision(current_state, decision):
        # Material change -> invalidate
        decision.status = "STALE"
        trigger_revalidation(decision)
    else:
        # Immaterial change -> proceed
        log_warning("State changed during deliberation, but change is immaterial")
```

**Decision:** P0 correction. Embed in hardening revision.

---

### Audit Section 25: Pareto-Frontier Decisions

**Audit Finding:** Some decisions have no objectively "best" candidate. The system should recognize Pareto frontiers and escalate.

**VERDICT: AGREE**

Already addressed in the CD2F objective function (Stage 4: Pareto Check). If `|J_final(A) - J_final(B)| < pareto_ambiguity_threshold`, the system outputs a `PARETO_SET` and escalates to HITL with a trade-off summary rather than pretending arbitrary weights determine a "winner."

**Decision:** Already covered by CD2F redesign.

---

### Audit Section 26: Candidate Feasibility Before Twin

**Audit Finding:** LLM-generated candidate parameters could be invalid. Twin should not discover basic schema invalidity after expensive setup.

**VERDICT: AGREE**

Already addressed in the candidate normalization pipeline (Steps 2-4: schema validation, entity validation, constraint pre-check). Malformed or infeasible candidates are eliminated before reaching the Twin.

**Decision:** Already covered by candidate normalization.

---

### Audit Section 27: Cross-Examination Termination Policy

**Audit Finding:** The deliberation loop has no maximum round count.

**VERDICT: AGREE**

**Solution:**

```yaml
deliberation:
  cross_examination:
    max_rounds: 2                     # Maximum critique-revision cycles
    max_critiques_per_agent: 3        # Per round
    max_total_critiques_per_session: 18  # Hard cap (6 agents x 3)
    
  termination_conditions:             # Session advances to next phase when ANY is true:
    - "no_blocking_critiques"         # No unresolved blocking conflicts
    - "max_rounds_reached"            # Hit the max_rounds limit
    - "candidate_set_unchanged"       # Revisions did not change any candidate actions
    - "evidence_convergence"          # All agents' revised claims agree on key facts
    - "deadline_imminent"             # SLA budget nearly exhausted
```

**Decision:** Include in hardening revision.

---

### Audit Section 28: Contradiction Taxonomy

**Audit Finding:** The system needs to distinguish between data contradictions, model disagreements, policy conflicts, action conflicts, and temporal disagreements.

**VERDICT: AGREE**

**Solution:**

```python
class ConflictRecord(BaseModel):
    conflict_id: str
    session_id: str
    
    conflict_type: Literal[
        "DATA_CONTRADICTION",       # Same proposition, different factual values
        "MODEL_DISAGREEMENT",       # Same forecast target, different predictions
        "POLICY_CONFLICT",          # Same facts, different objective priorities
        "ACTION_CONFLICT",          # Mutually incompatible proposed actions
        "TEMPORAL_DISAGREEMENT",    # Different observation windows producing different facts
    ]
    
    agent_a_id: str
    agent_b_id: str
    proposition: str                 # What is being disputed
    agent_a_value: Any
    agent_b_value: Any
    
    # Resolution
    resolution_method: Optional[Literal[
        "AUTHORITY_HIERARCHY",       # Higher-authority source wins
        "FRESHNESS",                 # More recent data wins
        "CROSS_REFERENCE",           # Third source validates one side
        "UNRESOLVABLE",              # Must escalate to CD2F as open conflict
    ]]
    resolved_value: Optional[Any]
    
    severity: Literal["MINOR", "MAJOR", "BLOCKING"]
```

For `DATA_CONTRADICTION`: resolve by checking which source has higher authority (PostgreSQL > Neo4j projection). For `TEMPORAL_DISAGREEMENT`: resolve by using the DecisionSnapshot's `observation_cutoff`. For `ACTION_CONFLICT`: pass to CD2F as an explicit trade-off for arbitration.

**Decision:** Include in hardening revision.

---

### Audit Section 37: Tier-1 Auto-Commit vs. HITL Execution -- CRITICAL

**Audit Finding:** CD2F "Tier-1 auto-commit" contradicts the execution boundary that requires HITL authorization for real-world actuation.

**VERDICT: AGREE -- This is a genuine contradiction.**

The confusion arises from collapsing three distinct concepts:

1. **Decision approval** (CD2F approves an action) -- this CAN be autonomous
2. **Scenario application** (Twin applies to Layer 3) -- this is always autonomous
3. **Real-world execution** (Execution Adapter sends PO to ERP) -- this REQUIRES policy check

**Correction:**

```
CD2F Tier-1 = APPROVED_FOR_EXECUTION_POLICY_CHECK

    |
    v

ExecutionPolicyService evaluates:
    
    Is this a scenario-only decision (benchmark/evaluation)?
        -> Apply to Twin Layer 3 immediately. No HITL needed. Done.
    
    Is this a real-world actuation?
        -> Check execution_autonomy_profile:
            
            Profile permits autonomous actuation for this action type?
            AND cost < max_autonomous_cost_usd?
            AND risk < max_autonomous_risk?
                -> AUTO_EXECUTE via Execution Adapter
            
            Else:
                -> HITL_AUTHORIZATION_REQUIRED
                -> Queue in D09 Desktop Console
```

**The key distinction:** CD2F Tier-1 means "the decision is high-confidence and well-supported." It does NOT mean "execute without human oversight." The execution boundary is a SEPARATE gate controlled by organizational policy, not by CD2F confidence.

**In the SCOF V2 research context:** All actuation is simulated (Layer 3). Real-world execution adapters do not exist yet. Therefore Tier-1 = apply to Twin Layer 3 immediately. But the architecture must not bake in that assumption because it would become a dangerous default when real-world adapters are eventually built.

**Decision:** P0 correction. Separate decision-approval from execution-authorization in the hardening revision.

---

### Audit Section 38: Execution Compensation / Replanning

**Audit Finding:** No model for what happens when execution fails or is partially completed.

**VERDICT: PARTIALLY AGREE**

The audit is correct that execution failure/compensation is architecturally important. However, in the current SCOF V2 scope, execution is entirely simulated (Twin Layer 3). Real-world execution adapters are explicitly labeled as future scope. Designing a full compensation/saga model for adapters that do not exist yet is premature.

**What IS needed now:** A model for what happens when the Twin simulation itself reveals problems AFTER CD2F approval:

```python
class ExecutionOutcome(BaseModel):
    decision_id: str
    execution_type: Literal["SIMULATION", "REAL_WORLD"]
    status: Literal[
        "APPLIED",             # Successfully applied to Twin Layer 3
        "INVARIANT_VIOLATION",  # Twin rejected (physical constraint violated)
        "PARTIAL_APPLICATION",  # Some actions applied, others failed
        "REJECTED",             # Execution Adapter rejected (for real-world)
    ]
    
    applied_actions: list[str]
    failed_actions: list[FailedAction]
    
class FailedAction(BaseModel):
    action_id: str
    failure_reason: str
    compensating_action: Optional[str]  # If partial, what was undone
    replan_required: bool
```

**If `replan_required = True`:** The Coordinator creates a new `DecisionSession` with the failure context as the trigger event. The system re-deliberates with the knowledge that the original plan failed.

**Decision:** Include the execution outcome model. Defer full saga/compensation to when real-world adapters are built.

---

### Audit Section 39: Stale-Decision Invalidation

**Audit Finding:** If the world changes during deliberation, the approved decision may be based on stale state.

**VERDICT: AGREE**

Already addressed by the `DecisionSnapshot` + stale-check before execution (Audit Section 22-23).

**Decision:** Already covered.

---

### Audit Section 40: Cross-Examination Conformity Bias

**Audit Finding:** Agents seeing each other's claims during cross-examination may bias toward conformity rather than independent assessment.

**VERDICT: AGREE**

**Solution: Two-Phase Independence Protocol**

```
PHASE 2 (INITIAL ASSESSMENT): 
    Agents receive:
        - Base context package (from Coordinator Tier-1 RAG)
        - Their own deep retrieval results (Tier-2 RAG)
        - The disruption event
    
    Agents DO NOT receive:
        - Other agents' claims
        - Other agents' evidence
        - Any information about what other agents concluded
    
    -> Produces independent initial proposals

PHASE 3 (TARGETED CROSS-EXAMINATION):
    Agents receive:
        - ONLY the claims from other agents that the Coordinator
          identifies as potentially conflicting with this agent's domain
    
    Agents DO NOT receive:
        - The full set of all claims (prevents conformity pressure)
        - Other agents' confidence scores (prevents anchoring)
    
    -> Produces targeted critiques on specific factual/constraint conflicts
```

The Coordinator selects which claims to route to which agents for critique based on:
- `affected_domains` in the claim (if a Procurement claim affects Logistics, route it to Logistics)
- Detected data contradictions (if Demand and Inventory disagree on a fact, route both claims for cross-check)

This preserves independence during initial inference while still enabling structured conflict resolution.

**Decision:** Include in hardening revision.

---

### Audit Section 41: Typed Candidate Action Schemas

**Audit Finding:** `CandidateAction.parameters: dict` is too weak. Arbitrary dictionaries recreate LLM ambiguity at the most dangerous interface.

**VERDICT: AGREE**

**Solution: Action-Specific Typed Schemas**

```python
class CandidateAction(BaseModel):
    action_id: str
    action_type: str
    action_params: ActionParams          # Discriminated union, not dict
    expected_impact: ImpactAssessment
    supporting_claims: list[str]
    evidence: list[EvidenceItem]

# Discriminated union of all known action types
ActionParams = Union[
    RerouteShipmentParams,
    SwitchSupplierParams,
    IncreasePurchaseOrderParams,
    ReallocateInventoryParams,
    ExpediteShipmentParams,
    QuarantineInventoryParams,
    AdjustSafetyStockParams,
    CancelPurchaseOrderParams,
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

class QuarantineInventoryParams(BaseModel):
    action_type: Literal["quarantine_inventory"] = "quarantine_inventory"
    facility_id: str
    sku_id: str
    quantity: int
    reason: Literal["quality_failure", "shelf_life", "regulatory", "contamination"]
    quarantine_duration_days: int

# ... (similar for each action type)
```

**Benefits:**
- Schema validation catches LLM-generated nonsense before it reaches the Twin
- CD2F can reason over strongly typed parameters
- Entity validation can check referenced IDs against D2
- The Twin receives guaranteed-valid action specifications

**Decision:** Include in hardening revision.

---

### Audit Section 42: Capability Versioning

**Audit Finding:** MCP tools need versioning and side-effect classification.

**VERDICT: AGREE**

```python
class CapabilityCard(BaseModel):
    capability_id: str
    version: str                    # Semver
    schema: dict                    # JSON Schema for parameters
    
    # Classification
    side_effect_class: Literal[
        "READ_ONLY",                # Pure data retrieval
        "SCENARIO_MUTATION",        # Modifies Twin scenario state only
        "EXTERNAL_SIDE_EFFECT",     # Calls external system (ERP, carrier API)
    ]
    
    # Governance
    authorization_scope: Literal[
        "AGENT",                    # Any agent can invoke
        "COORDINATOR",              # Only coordinator can invoke
        "EXECUTION_ADAPTER",        # Only execution adapter can invoke
    ]
    
    # Performance
    latency_class: Literal["fast", "medium", "slow"]  # <10ms, <100ms, >100ms
    cacheable: bool
    cache_ttl_seconds: Optional[int]
    
    # Domain
    domain_tags: list[str]
    data_freshness: str             # "real-time", "near-real-time", "batch"
```

**Runtime enforcement:** The Dynamic Capability Registry only binds `READ_ONLY` capabilities to agents. `SCENARIO_MUTATION` capabilities are only bindable to the Twin. `EXTERNAL_SIDE_EFFECT` capabilities are only bindable to the Execution Adapter.

**Decision:** Include in hardening revision.

---

### Audit Section 43: Redis Governance

**Audit Finding:** The Redis exception creates a governance asymmetry. Define governance at the policy level, not the mechanism level.

**VERDICT: AGREE**

**Solution: GovernedDataAccessPolicy**

```python
class GovernedDataAccessPolicy(BaseModel):
    """All data access obeys this policy, regardless of mechanism."""
    
    access_id: str                   # Unique per access event
    agent_id: str
    session_id: str
    data_source: Literal["postgresql", "neo4j", "pgvector", "redis"]
    access_mechanism: Literal["mcp", "direct"]   # How it was accessed
    query_hash: str                  # Reproducible query fingerprint
    timestamp: datetime
    data_returned_hash: str          # Hash of returned data (for audit)
    
    # Governance metadata
    authorized: bool                 # Was this access authorized by the capability registry?
    audited: bool                    # Was this access logged?
```

**Rule:** Every data access, whether through MCP or direct Redis, produces a `GovernedDataAccessPolicy` record. MCP generates these automatically via the tool invocation trace. Direct Redis access generates them via application-level logging.

The governance is the **policy**, not the mechanism. MCP is one enforcement tool. Application logging is another.

**Decision:** Include in hardening revision.

---

### Audit Sections 44-45: D-Number Consistency -- CRITICAL

**Audit Finding:** The document contains multiple incompatible D-number mappings. D07 means "Observability" in some places and "CD2F" in others.

**VERDICT: AGREE -- This must be fixed before any code is written.**

**Canonical D3-D10 Mapping (frozen):**

| D | Name | Responsibility | Implementation Phase |
| :--- | :--- | :--- | :--- |
| D1 | Enterprise World & Simulation Foundation | Frozen | Complete |
| D2 | Enterprise Knowledge & Data Fabric | Frozen | Complete |
| D3 | Cognitive Agent Runtime | Single-agent bounded reasoning chain, ReasoningService, ML+LLM hybrid | Phase 1 |
| D4 | Specialist Federation & Agent Cards | 6-agent expansion, Agent Card V2, ownership policies, A2A lifecycle | Phase 2 |
| D5 | Agentic Retrieval & Evidence Fabric | SCOFRetriever, MCP-governed retrieval, evidence provenance, two-tier RAG | Phase 3 |
| D6 | Cognitive Orchestration & Deliberation | LangGraph state machine, Deliberation Table, domain affinity routing, cross-examination, evidence sufficiency gate | Phase 4 |
| D7 | CD2F Arbitration & Counterfactual Decision | CD2F objective function, Twin counterfactual evaluation, candidate normalization, decision snapshot | Phase 5 |
| D8 | Event & Runtime Backbone | Kafka topic architecture, transactional outbox, event contract, consumer idempotency, API Gateway | Phase 6 |
| D9 | Observability, Explainability & Desktop Console | Decision trace, evidence visualization, trade-off explanations, Tauri v2 HITL console | Phase 7 |
| D10 | Evaluation & Benchmark | Benchmark suite, ablation experiments, R_i calibration, SLA validation, RQ1-RQ4 | Phase 8 |

**Rule:** Every reference in every document, diagram, heading, and table must use exactly this mapping. No exceptions.

**Decision:** P0 correction. Embed as the canonical table at the top of the hardening revision.

---

### Audit Section 47-48: Policy Layer -- CRITICAL

**Audit Finding:** Organizational policies (objectives, constraints, risk tolerances, autonomy permissions) are scattered across profile, thresholds, agent logic, CD2F, and execution boundaries. A dedicated policy layer is needed.

**VERDICT: AGREE**

**Solution: Decision Policy Layer**

```python
class DecisionPolicy(BaseModel):
    """The organization's complete policy for decision-making.
    Loaded from profile. Never generated by agents or LLMs."""
    
    profile_id: str
    version: str
    
    # CD2F Objective (see Section 10-11)
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
    max_fact_age_minutes: int = 5
    max_model_age_hours: int = 24
    max_precedent_age_days: int = 365
    min_domain_coverage: float = 0.80
    min_evidence_freshness: float = 0.60
    
class DeliberationPolicy(BaseModel):
    max_cross_exam_rounds: int = 2
    max_critiques_per_agent: int = 3
    independence_enforcement: bool = True
    
class SimulationPolicy(BaseModel):
    max_candidates: int = 8
    max_parallel_simulations: int = 4
    max_horizon_days: int = 28
    simulation_trigger_threshold_usd: float = 10000.0
    
class ExecutionPolicy(BaseModel):
    max_autonomous_cost_usd: float = 50000.0
    max_autonomous_risk: float = 0.30
    hitl_required_action_types: list[str] = ["cancel_purchase_order"]
    autonomous_permitted_contexts: list[str] = ["simulation", "benchmark"]

class RoutingPolicy(BaseModel):
    assigned_threshold: float = 0.60
    optional_threshold: float = 0.40
    minimum_assigned_agents: int = 1
```

**All** of these parameters come from the domain profile YAML (extending the existing [Domain Binding Strategy](file:///d:/projects/SCOF_V1/SCOF/docs/v2_enterprise/domain_binding_strategy.md)). None of them are hard-coded constants in Python.

**Policy precedence:**

```
1. Safety / regulatory hard constraints      (non-negotiable)
2. Enterprise hard constraints               (from profile)
3. Profile-specific policies                 (from DecisionPolicy)
4. Soft objectives                           (weighted in CD2F)
5. Agent preferences                         (lowest authority)
```

**Decision:** P0 correction. This is a critical missing concept.

---

### Audit Section 33: Implementation Sequencing -- Vertical Research Slice

**Audit Finding:** The hardest research question ("does collaborative deliberation + simulation improve decisions?") should not wait until D7. Build a minimal vertical slice in D3.

**VERDICT: AGREE**

**Solution: D3 Includes Minimal End-to-End Vertical Slice**

Phase 1 (D3) scope is expanded to include a proof-of-concept vertical slice:

```
D3 Scope (revised):
    
    PRIMARY: Single-agent cognitive runtime (as currently defined)
    
    PLUS VERTICAL SLICE:
        1. ONE agent (Procurement & Supplier)
        2. produces ONE structured proposal
        3. with ONE candidate action
        4. ONE minimal Twin simulation (apply action, advance T+7)
        5. ONE minimal CD2F evaluation (feasibility + objective score)
        6. ONE evaluation metric (did the action improve the target KPI?)
    
    This is NOT the full pipeline. No cross-examination, no multi-agent,
    no Deliberation Table. Just: agent -> candidate -> Twin -> score -> evaluate.
    
    GATE: Does this minimal loop produce measurably better decisions
          than a rule-based heuristic for supplier-delay disruptions?
```

This proves (or disproves) the core hypothesis immediately, before investing in federation, orchestration, and cross-examination infrastructure.

**Decision:** Adopt. Revise D3 scope in hardening revision.

---

### Audit Section 34: Baseline Ablation Ladder

**Audit Finding:** D10 needs an explicit baseline ladder for ablation experiments.

**VERDICT: AGREE**

**Baseline ladder:**

| Baseline | Configuration | What It Tests |
| :--- | :--- | :--- |
| B0 | Rule-based heuristic (no ML, no LLM) | Is any intelligence better than deterministic rules? |
| B1 | Single specialist agent (ML + LLM, no federation) | Does domain specialization matter? |
| B2 | 6 independent specialists, no cross-examination | Does multi-perspective analysis add value? |
| B3 | 6 specialists + cross-examination, no Twin | Does cross-examination improve quality? |
| B4 | B3 + naive majority voting (old CD2F) | Does structured arbitration beat voting? |
| B5 | B3 + evidence-based CD2F, no Twin | Does evidence-based arbitration beat voting? |
| B6 | B5 + Twin counterfactual simulation | Does simulation improve decision quality? |
| B7 | Full system (B6 + all policy/governance) | Final system evaluation |

**What each comparison proves:**
- B1 vs B0: Value of ML+LLM over rules
- B2 vs B1: Value of specialist federation
- B3 vs B2: Value of cross-examination
- B5 vs B4: Value of evidence-based arbitration over voting
- B6 vs B5: Value of Twin simulation
- B7 vs B6: Value of governance/policy layer

**Decision:** Include in hardening revision D10 section.

---

### Audit Section 35: Twin Can Leak the Answer

**Audit Finding:** If the Twin uses the same rules as the scenario generator, CD2F can appear accurate by exploiting the simulator.

**VERDICT: AGREE**

**Solution: Evaluation must include anti-overfitting measures:**

```yaml
evaluation:
  anti_overfitting:
    held_out_scenarios: true         # 20% of scenarios never seen during development
    parameter_perturbation: true     # +-10% noise on Twin model parameters
    distribution_shift: true         # Test on disruption patterns not in training set
    noise_injection: true            # Add measurement noise to Twin inputs
    model_misspecification: true     # Deliberately miscalibrate one Twin parameter
    combination_stress: true         # Multi-disruption combinations not in catalog
```

**Decision:** Include in D10 evaluation section of hardening revision.

---

### Audit Section 50: D7 Evaluation Gate Formalization

**Audit Finding:** "Beats weighted voting" needs formal metrics and statistical significance.

**VERDICT: AGREE**

**Evaluation metrics for D7 gate:**

| Metric | Measurement | Statistical Requirement |
| :--- | :--- | :--- |
| Decision Quality Score | Composite KPI improvement vs. baseline | p < 0.05, paired t-test |
| Constraint Violation Rate | % of decisions violating hard constraints | Must be lower than B4 |
| Service Level Preservation | % of decisions maintaining target service level | >= 90% |
| Cost Efficiency | Average cost vs. optimal (hindsight) | Within 15% of optimal |
| Risk Exposure | Average risk score of selected actions | Lower than B4 |
| Human Agreement | % of decisions a human expert would also choose | >= 75% on sample |
| Calibration | Correlation between stated confidence and actual outcome | r >= 0.60 |
| Latency | p95 end-to-end decision time | Within SLA target |
| Explainability | Human evaluator can trace decision reasoning | >= 90% of decisions |

**Decision:** Include in hardening revision.

---

### Audit Section 51: Failure Taxonomy

**VERDICT: AGREE**

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

# Failure -> Response mapping
FAILURE_RESPONSE = {
    "AGENT_TIMEOUT": "DETERMINISTIC_FALLBACK",
    "AGENT_SCHEMA_FAILURE": "RETRY_ONCE_THEN_FALLBACK",
    "AGENT_TOOL_FAILURE": "RETRY_ONCE_THEN_FALLBACK",
    "RETRIEVAL_FAILURE": "RETRY_WITH_CACHE",
    "RETRIEVAL_STALE": "PROCEED_WITH_WARNING",
    "EVIDENCE_INSUFFICIENT": "HITL_ESCALATION",
    "TWIN_TIMEOUT": "CD2F_WITHOUT_SIMULATION",
    "TWIN_INVARIANT_VIOLATION": "ELIMINATE_CANDIDATE",
    "CD2F_NO_FEASIBLE_ACTION": "HITL_ESCALATION",
    "CD2F_PARETO_AMBIGUITY": "HITL_WITH_TRADEOFF_SUMMARY",
    "STATE_CHANGED": "REVALIDATE_DECISION",
    "SESSION_CANCELLED": "PROPAGATE_CANCELLATION",
}
```

**Decision:** Include in hardening revision.

---

### Audit Section 52: Cancellation Propagation

**VERDICT: AGREE**

```python
class CancellationEvent(BaseModel):
    session_id: str
    cancelled_by: str               # "human:operator_id" or "system:timeout"
    reason: str
    timestamp: datetime

# Propagation chain:
# 1. DecisionSession -> status = CANCELLED
# 2. LangGraph -> interrupt current workflow
# 3. A2A tasks -> cancel all active tasks for this session
# 4. MCP calls -> cancel if in-flight (best-effort)
# 5. Twin simulations -> cancel all pending simulations for this session
# 6. Kafka -> publish SESSION_CANCELLED event
# 7. Redis -> update session cache
# 8. Deliberation Table -> all pending items marked WITHDRAWN
```

**Decision:** Include in hardening revision.

---

### Audit Section 53: Replay Semantics

**Audit Finding:** True replay needs model versions, prompt versions, snapshot versions, random seeds, etc.

**VERDICT: AGREE**

```python
class DecisionReplayManifest(BaseModel):
    """Everything needed to reproduce a decision."""
    decision_id: str
    session_id: str
    
    # State
    enterprise_snapshot: DecisionSnapshot
    
    # Models
    agent_model_versions: dict[str, str]    # agent_id -> model version
    llm_model_version: str
    twin_model_version: str
    embedding_model_version: str
    
    # Configuration
    profile_version: str
    policy_version: str
    prompt_versions: dict[str, str]         # agent_id -> prompt template hash
    
    # Reproducibility
    random_seeds: dict[str, int]            # component -> seed
    
    # Events
    event_log: list[SCOFEvent]              # Complete event sequence
    
    replay_type: Literal[
        "EXACT",         # Same state + same models = deterministic replay
        "ANALYTICAL",    # Different models/state, replay the decision logic
    ]
```

**Decision:** Include in hardening revision as part of the DecisionRecord concept.

---

### Audit Section 55: Decision Record

**Audit Finding:** `DecisionSession` is the working process. The system needs a `DecisionRecord` as the final durable business artifact.

**VERDICT: AGREE**

```python
class DecisionRecord(BaseModel):
    """The final, durable business artifact. Immutable after creation."""
    record_id: str
    session_id: str
    
    # Context
    trigger: DisruptionEvent
    snapshot: DecisionSnapshot
    policy_version: str
    
    # Process summary
    agents_consulted: list[str]
    evidence_sufficiency: EvidenceSufficiencyAssessment
    candidate_count: int
    simulation_count: int
    cross_exam_rounds: int
    
    # Decision
    selected_action: CandidateAction
    arbitration_result: CD2FArbitrationResult
    
    # Execution
    execution_authorization: Literal["AUTO", "HITL_APPROVED", "HITL_REJECTED"]
    execution_outcome: ExecutionOutcome
    
    # Provenance
    replay_manifest: DecisionReplayManifest
    full_event_log_ref: str          # Reference to the complete event log
    
    # Post-hoc
    human_assessment: Optional[str]   # Human review/feedback
    actual_outcome: Optional[dict]    # Real-world outcome for R_i calibration
```

**Distinction:**
- `DecisionSession` = working process (mutable during deliberation)
- `DecisionRecord` = durable business artifact (immutable after session closes)

**Decision:** Include in hardening revision.

---

### Audit Section 60: Ten Architectural Invariants

**VERDICT: AGREE**

The audit proposes upgrading from 7 amendments to 10 invariants. I adopt all ten with minor refinements:

| # | Invariant | Refinement |
| :--- | :--- | :--- |
| 1 | Source authority: PostgreSQL owns operational facts, Neo4j owns topology projection. No dual truth. | Adopted as stated. |
| 2 | Cognitive workspace: Deliberation Table stores decision artifacts, never enterprise operational truth. | Adopted as stated. |
| 3 | Evidence sufficiency: Agent response != sufficient evidence. Multi-dimensional assessment required. | Adopted with the EvidenceSufficiencyAssessment model. |
| 4 | Candidate discipline: No unbounded candidate or simulation expansion. | Adopted with explicit budget. |
| 5 | Counterfactual isolation: Twin can mutate only isolated Layer-3 scenario state. | Adopted with SimulationManifest. |
| 6 | Decision authority: LLM proposes/interprets. Deterministic systems calculate. CD2F arbitrates. Execution Adapter acts. | Adopted as stated. |
| 7 | Policy authority: Organization policy defines objectives, constraints, autonomy, escalation. LLMs do not. | Adopted with DecisionPolicy model. |
| 8 | State freshness: Every decision is bound to a declared world-state snapshot/version. | Adopted with DecisionSnapshot. |
| 9 | Execution safety: Decision approval != physical execution. Separate gates. | Adopted with ExecutionPolicyService. |
| 10 | Replayability: Every decision is reconstructable from state + evidence + model versions + policy + actions + simulations + events. | Adopted with DecisionReplayManifest. |

**Decision:** Adopt all ten as the architectural invariant set.

---

## Summary: What Goes Into the Hardening Revision

### P0 Corrections (in the hardening revision document):

1. Canonical D3-D10 numbering table (frozen)
2. Corrected cognitive stage ordering (DELIBERATE before EXPLORE)
3. Neo4j authority correction (proposition-specific hierarchy)
4. Evidence sufficiency redesign (multi-dimensional, not agent-presence)
5. LangGraph reordering (evidence gate before Twin)
6. CD2F objective function (deterministic, with policy weights)
7. Tier-1 auto-commit resolution (separate decision-approval from execution-authorization)
8. Decision snapshot semantics (state versioning for temporal consistency)
9. Twin candidate budget + normalization pipeline
10. Twin simulation manifest (reproducibility contract)
11. Policy Layer definition (DecisionPolicy from profile)
12. Ten Architectural Invariants

### P1 Corrections (also included where immediately relevant):

13. Coordinator internal decomposition
14. Deliberation Table event-sourcing
15. Cross-examination termination policy + independence enforcement
16. Typed CandidateAction schemas
17. Contradiction taxonomy
18. R_i governance policy
19. Event contract (SCOFEvent with idempotency)
20. Failure taxonomy with response mapping
21. Cancellation propagation model
22. Execution outcome + replanning model
23. Decision Record (durable artifact vs working session)
24. Capability versioning + side-effect classification
25. D3 vertical research slice
26. D10 ablation baseline ladder
