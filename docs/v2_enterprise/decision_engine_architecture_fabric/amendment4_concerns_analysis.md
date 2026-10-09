# SCOF V2 Amendment 4 -- Critical Analysis and Response to the Amendment 3 Architecture Review

> [!IMPORTANT]
> This document does NOT alter any content in Amendment 3 or any predecessor document. It serves as the analytical basis for the Contract Freeze Pass (Amendment 4), which will incorporate the validated corrections.

## Executive Assessment

### Overall Position

The 86-point review of Amendment 3 is the most rigorous analysis the architecture has received. It correctly identifies that Amendment 3 is substantially better than Amendment 2, and that the conceptual architecture is now sound and should be frozen. The review's central conclusion -- that Amendment 3 is not yet implementation-contract ready because several contracts still contain contradictions that would produce incorrect runtime behavior -- is validated.

The review also provides a critical secondary analysis distinguishing what is truly Essential for V2 from what constitutes an Improvement or Future capability. This secondary classification is accepted as the governing scope for Amendment 4.

### My Classification of the Review's Findings

The review contains 86 numbered points. Below is my classification of every point, followed by detailed analysis.

**Accepted as Essential (must be in Amendment 4):** Points 4, 5, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19, 20, 21, 22, 26, 27, 28, 34, 35, 36, 43, 44, 49, 74, 77 (blockers 1-12).

**Accepted as Improvement (listed in Amendment 4 as future enhancement, NOT in the architecture revision):** Points 11, 12, 13, 23, 25, 29, 31, 32, 37, 38, 39, 40, 42, 45, 46, 47, 50, 51, 52, 53, 54, 55, 56, 57, 60, 61, 62, 63, 64, 65, 66, 68, 78 (non-blocking items 1-25).

**Accepted as correct with no action needed (review affirms Amendment 3):** Points 1, 2, 3, 24, 30, 33, 41, 58, 59, 67, 69, 70, 71, 72, 73, 75, 76, 79, 80, 81, 82, 83, 84, 85, 86.

### Governing Principle for Amendment 4

The review's secondary analysis provides the definitive scoping principle:

> "V2 must demonstrate that a set of bounded specialist agents, reasoning over a common enterprise snapshot with governed evidence, can generate structured actions, evaluate those actions through a bounded Digital Twin, and have those candidates arbitrated by CD2F into an auditable decision whose quality can be compared against V1."

Everything inside that sentence is Essential for V2. Everything outside it is an Improvement or Future capability. Amendment 4 will correct only the Essential contract defects. Improvements and Future items will be listed at the end of Amendment 4 as a backlog, not embedded in the architecture revision.

---

## Part I: Analysis of Architecture Direction (Points 1-3)

### Point 1 -- Architecture Direction: GO

**My position: AGREE.**

The review confirms that the fundamental architecture is coherent and lists 20+ frozen architectural decisions. I agree with every item on that list. No further conceptual redesign is warranted.

### Point 2 -- Implementation Readiness: NO-GO for immediate D3

**My position: AGREE.**

The distinction between "GO for architecture freeze" and "HOLD for implementation-contract freeze" is precisely correct. Amendment 4 is the contract-freeze pass that closes this gap. After Amendment 4, the correct verdict should be GO for D3.

### Point 3 -- What Amendment 3 Successfully Fixed

**My position: AGREE.**

The review correctly identifies that Amendment 3 is substantially better than Amendment 2 and that the changes are not cosmetic. The centralized ClaimTypeRegistry, the ActionIntent/ActionImpact separation, the structured evidence assessment, the proper Pareto concept, the Twin requirement classification, the reliability decomposition, the event sequencing, and the evaluation hardening are all genuine architectural improvements.

---

## Part II: Essential Contract Defects (Points 4-22, 26-28, 34-36, 43-44, 49)

These are the defects that must be corrected in Amendment 4 because they can produce incorrect runtime behavior or create implementation ambiguity.

---

### Point 4 -- Claim Vocabulary Is Not Completely Closed (EvidenceClass vs ClaimType)

**Review says:** Section 7 uses `claim_type: current_state`, `claim_type: topological`, `claim_type: forecast` which are NOT entries in the ClaimTypeRegistry. Two different vocabularies share the same field name.

**My position: AGREE. This is a real contract defect.**

The review is correct that the critical-fact profile uses a different concept than the ClaimTypeRegistry. `current_state`, `topological`, and `forecast` describe the *epistemic class* of evidence (what kind of knowledge it is), while `supplier_operational_assessment` and `inventory_position_assessment` describe the *domain proposition* being made (what the agent is claiming).

These are orthogonal dimensions:

```
A claim can be:
    supplier_operational_assessment     (proposition type)
    based on current_state evidence     (evidence class)

Or:
    demand_assessment                   (proposition type)
    based on forecast evidence          (evidence class)
```

Sharing the field name `claim_type` for both is genuinely ambiguous.

**Amendment 4 action:** Create a canonical `EvidenceClass` enum. Rename the critical-fact profile fields to use `evidence_class` instead of `claim_type`. This is a straightforward field rename with a new enum, not a conceptual change.

---

### Point 5 -- Claim Registry Validation Fail-Open Bug

**Review says:** If `source_card` is None (nonexistent agent referenced in `consumes_from`), the validator silently passes instead of erroring.

**My position: AGREE. This is a genuine validation gap.**

The current code:

```python
source_card = find_agent(agent_cards, source_agent)
if source_card and claim not in source_card.ownership_policy.owned_claim_types:
    errors.append(...)
```

The `if source_card and ...` short-circuits when `source_card` is None, meaning a reference to a nonexistent agent is silently accepted. The document explicitly claims "All contract references must be valid," so this is a direct contradiction.

**Amendment 4 action:** Add explicit None check before the ownership validation. If `source_card` is None, append an error indicating the source agent does not exist.

---

### Point 6 -- ActionRegistry Is Not Yet the Single Source of Truth

**Review says:** The architecture has `ActionTypeRegistry` (enum-like), `ActionDefinition` (object), and several independent maps (Twin handler, execution capability, policy action lists) that can drift.

**My position: AGREE. Unification is Essential.**

The review correctly identifies that maintaining separate `ActionTypeRegistry`, `ActionDefinition`, and independent handler/capability maps recreates the drift problem. For V2, we need one canonical `ActionRegistry` containing `ActionDefinition` objects that serve as the single source of truth for all action-related metadata.

**Amendment 4 action:** Merge `ActionTypeRegistry` and `ActionDefinition` into a unified `ActionRegistry`. Every reference to action types, Twin handlers, execution capabilities, and policy constraints must derive from this registry. The enum-like namespace becomes an accessor pattern on the registry, not a separate entity.

---

### Point 7 -- CandidateAction Has Duplicated action_type

**Review says:** `CandidateAction.action_type` and `CandidateAction.intent.action_type` can disagree.

**My position: AGREE. This is a structural correctness issue.**

The review provides a clear example where `action_type: "switch_supplier"` and `intent.action_type: "reroute_shipment"` could coexist. This must be structurally impossible.

**Amendment 4 action:** Remove `CandidateAction.action_type` as a top-level field. Derive it from `intent.action_type` via a computed property. If an indexed/database field is needed, it should be generated from the intent at persistence time, not independently supplied.

---

### Point 8 -- ActionIntent Wording: "No Numbers" Is Misleading

**Review says:** The document says agents provide "ONLY intent, structural parameters" with "no numbers," but schemas contain `quantity: int`, `target_days_of_supply: float`, `override_factor: float`.

**My position: AGREE on the wording issue. The schemas are correct; the prose is misleading.**

The review correctly distinguishes between:
- **Decision parameters** (what the agent wants to do): `quantity = 500`, `target_days_of_supply = 14.0`
- **Impact estimates** (what the action will cost/cause): `incremental_cost = $12,400`, `lead_time_delta = +3.2 days`

The architecture correctly prevents LLM-generated impact estimates. But the wording "no numbers" could lead developers to incorrectly reject valid quantitative decision parameters.

**Amendment 4 action:** Correct the prose to say: "ActionIntent contains structural decision parameters (identifiers, modes, quantities, targets). It does NOT contain impact estimates (costs, deltas, scores). Impact estimates are computed by the DeterministicImpactEvaluator and the Digital Twin."

---

### Point 9 -- DeterministicImpactEvaluator Is Overclaimed

**Review says:** The evaluator claims "authoritatively computed impact" but some outputs (`service_level_delta`, `risk_delta`, `inventory_health_delta`) come from models that are predictions, not deterministic derivations from authoritative facts.

**My position: AGREE. The epistemic claim is too strong.**

The review is correct that there is a fundamental distinction between:
- **Deterministic derivation** from authoritative facts: route rate lookup, contract price, current capacity, carrier eligibility
- **Model-based prediction**: expected service level, probability of delay, risk reduction, expected demand trajectory

Calling both "authoritative" conflates two different levels of confidence.

**Amendment 4 action:** Restructure the impact model into two tiers. Rename the service to `ImpactEvaluationService` (dropping the overclaimed "Deterministic" prefix). Distinguish `BaselineImpact` (from authoritative facts) and `PredictiveImpactEstimate` (from models). Both are computed by the service, not by the LLM, but their confidence semantics differ.

---

### Point 10 -- Three-Layered Impact Model

**Review says:** The impact pipeline should be Deterministic Baseline -> Predictive Estimate -> Twin Counterfactual, not one flat "deterministic" evaluator.

**My position: AGREE. This is the correct epistemic hierarchy for V2.**

This directly follows from Point 9. The three tiers are:

1. **BaselineImpact** -- from authoritative facts only (route rates, contract prices, current capacity, hard eligibility). These values are deterministically correct given the snapshot.
2. **PredictiveImpactEstimate** -- from models (demand forecast, risk models, service level prediction). These values are the system's best estimate but carry uncertainty.
3. **SimulationResult** -- from the Digital Twin. These values are counterfactual projections under specific scenario assumptions.

**Amendment 4 action:** Introduce the three-tier impact model as an Essential correction. The `ActionImpact` schema will be restructured to carry both `BaselineImpact` (authoritative) and `PredictiveImpactEstimate` (model-based), with confidence metadata for each.

---

### Point 14 -- Critical Evidence Criticality Definition Is Partly Circular

**Review says:** "A fact is critical if removing it would change candidate ranking" is circular because candidate ranking does not exist when the evidence gate runs.

**My position: AGREE. The primary criticality definition must be pre-ranking.**

The review correctly identifies the logical dependency:

```
Evidence sufficiency -> determines whether to proceed
                     -> depends on candidate ranking (by definition)
                     -> candidate ranking depends on evidence
                     -> circular
```

**Amendment 4 action:** Redefine critical evidence with a two-phase model:

1. **Profile-defined criticality** (primary, pre-ranking): Critical facts are defined by the disruption profile, entity type, and action class. This is known before candidate ranking.
2. **Sensitivity-discovered criticality** (secondary, post-ranking): Additional facts discovered to be decision-sensitive through post-hoc analysis. This triggers a criticality escalation, not the original definition.

---

### Point 15 -- Marginal Evidence Sufficiency Is Internally Inconsistent

**Review says:** `MARGINALLY_SUFFICIENT` and `INSUFFICIENT` conditions can overlap because `all_critical_facts_sufficient == False` can coexist with `critical_facts_present >= critical_facts_identified`.

**My position: AGREE. The verdict logic has a real contradiction.**

The issue: a critical fact can be present (incrementing `critical_facts_present`) but below its configured freshness threshold (setting `all_critical_facts_sufficient = False`). This fact then simultaneously satisfies `MARGINALLY_SUFFICIENT` (present) and `INSUFFICIENT` (not sufficient).

**Amendment 4 action:** Introduce explicit criticality tiers with precedence:

```
HARD_CRITICAL:   missing/stale -> NO_AUTONOMOUS_DECISION (absolute block)
DEGRADED_CRITICAL: present but below preferred threshold -> PROCEED_ONLY_IF_POLICY_ALLOWS
IMPORTANT:       missing -> degraded confidence (no block)
SUPPLEMENTARY:   missing -> no blocking effect
```

The verdict uses strict precedence: any HARD_CRITICAL failure overrides all other conditions.

---

### Point 16 -- Snapshot LSN Arithmetic Is Invalid

**Review says:** `enterprise_state_version - neo4j_source_lsn` is meaningless if they are different version domains (business version number vs. PostgreSQL WAL LSN).

**My position: AGREE. This is a genuine technical error.**

The review is correct. If `enterprise_state_version` is an application-level integer and `neo4j_source_lsn` is a PostgreSQL WAL position (`0/7A31BC0`), arithmetic subtraction is meaningless. They are different coordinate systems.

**Amendment 4 action:** Replace the lag computation with a common consistency model. Define a `snapshot_epoch` (monotonically increasing integer allocated per snapshot) that all subsystems track. Each subsystem reports its last processed `snapshot_epoch`. Consistency assessment compares epochs, not heterogeneous version identifiers.

---

### Point 17 -- Correct Snapshot Model

**Review says:** Use a common snapshot coordinate with each subsystem reporting its projection position in compatible terms.

**My position: AGREE. This is the direct correction for Point 16.**

**Amendment 4 action:** Define `DecisionSnapshot` with:
- `snapshot_epoch: int` -- the common consistency coordinate
- `postgres_snapshot_epoch: int` -- PostgreSQL's position
- `neo4j_projection_epoch: int` -- Neo4j's materialized-through position
- `pgvector_corpus_epoch: int` -- pgvector's indexed-through position
- `observation_cutoff: datetime` -- the temporal boundary

Consistency assessment:
```
FULLY_CONSISTENT: all projection epochs == snapshot_epoch
ACCEPTABLE_LAG: max lag <= policy.max_projection_lag
STALE_PROJECTION: lag exceeds policy threshold
```

---

### Point 18 -- Snapshot Advancement Cannot Restart Only Affected Agents

**Review says:** Restarting only affected agents creates a split-snapshot session where different agents reason about different world states, violating the invariant that all agents share the same observation boundary.

**My position: AGREE. This is a critical invariant violation.**

The review correctly identifies that partial restart creates:
```
Inventory -> Snapshot V2
Logistics -> Snapshot V1
Finance   -> Snapshot V1
```
This violates the fundamental invariant.

**Amendment 4 action:** Snapshot advancement must invalidate the entire session's cognitive state. If a critical state change is detected and the session is still in the deliberation phase, create a new session version (`session_epoch`) with a fresh snapshot, and ALL agents must re-reason from the new snapshot. Partial restart is explicitly prohibited.

---

### Point 19 -- Freshness Has a WALL_CLOCK Contradiction

**Review says:** Section 9 permits `WALL_CLOCK` freshness reference, but Section 29 says all freshness uses `observation_cutoff`. These contradict.

**My position: AGREE. WALL_CLOCK must be removed from decision freshness.**

**Amendment 4 action:** Remove `WALL_CLOCK` from the `freshness_reference` field entirely. Decision evidence freshness is always relative to `observation_cutoff`. Wall-clock age is available only as operational telemetry outside the decision context.

---

### Point 20 -- Freshness Computation Has a Post-Snapshot Bug

**Review says:** `if fact_age <= timedelta(0): return 1.0` treats post-snapshot evidence (where `data_as_of > observation_cutoff`) as perfectly fresh, which contradicts the post-snapshot rejection rule.

**My position: AGREE. This is a real correctness bug.**

If the freshness function is called directly without the upstream validator, post-snapshot evidence receives a freshness score of 1.0 instead of being rejected. The function must enforce the invariant independently.

**Amendment 4 action:** Replace the `<= 0` condition with an explicit `PostSnapshotEvidenceError` raise. The freshness function must be self-contained:

```python
if data_as_of > snapshot.observation_cutoff:
    raise PostSnapshotEvidenceError(
        f"Evidence timestamp {data_as_of} is after "
        f"snapshot cutoff {snapshot.observation_cutoff}"
    )
```

---

### Point 21 -- Objective Normalization Sign Handling Is Wrong

**Review says:** `abs(raw_value) / reference_scale` destroys the direction of signed deltas. Cost savings (-$10k) and cost increases (+$10k) are treated identically.

**My position: AGREE. This is a genuine mathematical defect.**

This is one of the most important corrections. The current normalization:

```python
normalized = min(1.0, max(0.0, abs(raw_value) / reference_scale))
```

discards sign information. For directional metrics (cost delta, lead time delta, carbon delta, cash flow delta), the sign carries essential meaning:
- `cost_delta = -$10,000` means savings (good)
- `cost_delta = +$10,000` means additional cost (bad)

Treating both as `abs($10,000) / $100,000 = 0.1` is incorrect.

**Amendment 4 action:** Replace `abs()` normalization with direction-aware utility functions. Each metric definition carries an explicit `direction` and the normalization preserves sign:

```python
def normalize_signed_metric(raw_value: float, reference: float, direction: str) -> float:
    if direction == "MINIMIZE":  # lower is better (cost, risk, lead_time, carbon)
        return -min(max(raw_value / reference, -1.0), 1.0)
    elif direction == "MAXIMIZE":  # higher is better (service level)
        return min(max(raw_value / reference, -1.0), 1.0)
```

This way:
- cost_delta = -$10,000 -> normalized = +0.1 (positive utility: savings)
- cost_delta = +$10,000 -> normalized = -0.1 (negative utility: cost increase)

---

### Point 22 -- Reference Scale Saturation

**Review says:** When `raw_value > reference_scale`, the function saturates at 1.0, losing magnitude information for extreme outcomes.

**My position: ACCEPT AS ESSENTIAL for V2 with a simple solution.**

The review suggests piecewise linear or logarithmic utility. For V2, I agree that saturation must be policy-defined, but a simple bounded linear model with explicit saturation policy is sufficient. The key correction is making saturation behavior explicit and policy-controlled rather than implicit.

**Amendment 4 action:** Add a `saturation_policy` field to `ObjectiveNormalization` that defines behavior when values exceed the reference scale. Default is `CLIP` (current behavior, but now explicitly documented). Alternative policies (`LOGARITHMIC`, `PIECEWISE_LINEAR`) are listed as future enhancement options.

---

### Point 26 -- CD2F "Execution Authorization" Wording

**Review says:** Section 12 says "Proceed to execution authorization" but CD2F does not authorize execution; ExecutionPolicy does.

**My position: AGREE. This is a wording correction, but it matters for contract clarity.**

**Amendment 4 action:** Replace "Proceed to execution authorization" with "Proceed to ExecutionPolicy evaluation" in the Pareto analysis flow.

---

### Point 27 -- Twin Policy Naming Contradiction (BLOCKER 1)

**Review says:** Section 30 defines `twin_required_cost_usd` and `twin_recommended_cost_usd`, but Section 13 still uses `twin_required_cost_threshold`, `cascade_threshold`, `novelty_threshold`, `simulation_trigger_threshold_usd`.

**My position: AGREE. This is the clearest P0 blocker.**

The document has two SimulationPolicy schemas. Section 30 is the intended replacement; Section 13 retains the old names. This creates direct implementation ambiguity.

**Amendment 4 action:** Define one canonical `SimulationMaterialityThresholds` with the Section 30 names. Rewrite the classification logic in Section 13 to reference only the canonical names. No legacy field names survive.

---

### Point 28 -- Required Final Twin Policy

**Review says:** There should be one canonical `SimulationMaterialityThresholds` referenced everywhere.

**My position: AGREE. This is the direct implementation of the Point 27 correction.**

**Amendment 4 action:** See Point 27. One canonical policy, one canonical classification function, no legacy names.

---

### Point 34 -- Single-Writer Needs Database Invariant

**Review says:** Application-level assumption that the Coordinator is the only writer is insufficient. The database must enforce `UNIQUE(session_id, sequence_number)`.

**My position: AGREE. This is cheap to implement and provides a genuine safety net.**

For V2, this is at the borderline between Essential and Improvement. However, the database constraint is trivially implementable (`UNIQUE(session_id, sequence_number)` and `CHECK(sequence_number > 0)`) and prevents a class of future bugs entirely. The cost-benefit ratio strongly favors inclusion.

**Amendment 4 action:** Add explicit database constraints to the event store schema. This is a one-line SQL addition per constraint, not a significant implementation effort.

---

### Point 35 -- Terminal State Guard Is Not Atomic

**Review says:** Read-check-write on session status can race. Two consumers can see `status = ACTIVE` simultaneously; one closes, the other writes a late event.

**My position: AGREE for the contract specification. Implementation atomicity depends on deployment model.**

For V2's single-Coordinator model, the risk is low because the Coordinator serializes event posting. However, the contract should specify the requirement so that any future multi-instance deployment does not introduce the race. The correction is to couple event insertion with status validation in a single transaction.

**Amendment 4 action:** Specify that terminal state transitions and event insertion must occur within a single database transaction. Add explicit transition table (ACTIVE -> CANCELLED/CLOSED/EXPIRED; terminal states are absorbing).

---

### Point 36 -- Terminal Event Types Are Too Permissive

**Review says:** The system could allow `CLOSED -> CANCELLED` or `EXPIRED -> CLOSED` without a transition table.

**My position: AGREE. A legal transition matrix is Essential.**

**Amendment 4 action:** Define the canonical session state machine:

```
ACTIVE -> CANCELLED   (explicit cancellation)
ACTIVE -> CLOSED      (successful completion)
ACTIVE -> EXPIRED     (timeout)

CANCELLED -> (absorbing)
CLOSED    -> (absorbing)
EXPIRED   -> (absorbing)
```

Late terminal events against already-terminal sessions are idempotent no-ops.

---

### Point 43 -- Policy Hash Is Self-Referential

**Review says:** `policy_hash = SHA-256(serialized policy content)` where `policy_hash` itself is part of the serialized object creates a self-reference. Also, `computed_at` would make the hash change on every computation.

**My position: AGREE. This is a real implementation bug.**

**Amendment 4 action:** Define canonical serialization that explicitly excludes integrity metadata:

```python
def canonical_policy_payload(policy: DecisionPolicy) -> dict:
    return policy.model_dump(
        exclude={"policy_hash", "profile_hash", "computed_at"}
    )

policy_hash = SHA256(canonical_json(canonical_policy_payload(policy)))
```

Make the exclusion set explicit in the architecture contract.

---

### Point 44 -- Required Policy Hash Model

**Review says:** Verification should recompute the hash from the canonical payload and compare.

**My position: AGREE. This is the direct implementation of Point 43.**

**Amendment 4 action:** See Point 43. The canonical hash computation and verification are specified as a single correction.

---

### Point 49 -- B3/B4 Ablation Ladder Duplication

**Review says:** B3 already includes "evidence sufficiency gate active." B4 adds "evidence sufficiency gate." This is a duplication error.

**My position: AGREE. The ablation ladder has a clear definitional overlap.**

**Amendment 4 action:** Correct the ladder:

```
B2: independent specialists (no cross-examination, no evidence gate)
B3: B2 + cross-examination (NO evidence gate)
B4: B3 + evidence sufficiency gate
```

This ensures each step adds exactly one new component, enabling clean attribution.

---

### Point 74 -- Final State Revalidation Before Execution

**Review says:** Insert a "Final State Revalidation" step between ExecutionPolicy and the Execution Adapter. The decision was computed against a specific snapshot; the world may have changed.

**My position: AGREE. This is Essential if V2 performs any form of execution.**

Even if V2's execution is primarily applying actions to the Twin Layer 3 (simulated execution), the principle of revalidating that the decision context has not been invalidated is a fundamental safety mechanism. It is the runtime equivalent of optimistic concurrency control.

**Amendment 4 action:** Add `StateRevalidation` step to the canonical pipeline between ExecutionPolicy and Execution. The execution authorization carries `approved_snapshot_epoch`. Before execution, verify that the current world state is compatible with the approved snapshot. If not: `STALE_AUTHORIZATION -> replan`.

---

## Part III: Confirmed Architectural Decisions (Points 24, 30, 33, 41, 58, 59, 67, 73, 79, 80)

These points affirm Amendment 3's direction. No changes required.

### Point 24 -- Pareto Analysis Is Conceptually Correct

**CONFIRMED.** The Pareto dominance definition is correct. The review's suggestion to rename `PARETO_DOMINANT` to `SINGLETON_PARETO_FRONTIER` is accepted as a wording improvement.

### Point 30 -- R_i Influence Status Is a Good Improvement

**CONFIRMED.** FULL/REDUCED/ADVISORY graduated status is the correct model.

### Point 33 -- Event Sequence Allocation Is Much Better

**CONFIRMED.** Single-writer model with PostgreSQL transaction is correct.

### Point 41 -- OutcomeObservation Is a Good Replacement

**CONFIRMED.** Typed observation model is correct.

### Point 58 -- Policy Sensitivity Is Excellent

**CONFIRMED.** Retained as-is.

### Point 59 -- Oracle Independence Is Correct

**CONFIRMED.** Oracle must not reuse Twin calibration data.

### Point 67 -- Post-Snapshot Evidence Handling Is Much Better

**CONFIRMED.** Post-snapshot evidence rejection and quarantine model is correct.

### Point 73 -- Final Cognitive Loop Is Correct in Principle

**CONFIRMED.** The pipeline from TRIGGER through REPLAY/EVALUATION is architecturally sound.

### Point 79 -- What Would Not Change

**CONFIRMED.** All items on the "do not reopen" list are agreed.

### Point 80 -- Architecture Has Reached "Don't Redesign" Point

**CONFIRMED.** The remaining problems are contract precision, mathematical semantics, state consistency, and evaluation validity. That is exactly where an architecture should be at this stage.

---

## Part IV: Items Classified as Improvement (Not Essential for V2)

These items are valid architectural observations but are NOT required for V2 to demonstrate its central thesis. They will be listed at the end of Amendment 4 as future enhancement options.

### Point 11 -- Pre-Twin Pruning and Predicted Impact

**Classification: IMPROVEMENT.**

The concern that "deterministic" impact includes model predictions, making pruning less safe, is valid in theory. However, for V2, the impact evaluator uses authoritative data sources (not LLM output). The models are validated domain models, not arbitrary predictions. The pruning is already substantially safer than the pre-Amendment-3 state. Full epistemic stratification of pruning inputs is an improvement.

### Point 12/13 -- UCB Is Not Actually Safe Pruning

**Classification: ESSENTIAL wording correction + IMPROVEMENT for coverage-aware budgeting.**

The wording change from "safe pruning" to "budgeted candidate selection" is Essential. The sophisticated coverage-aware budget selection (mandatory reservations per domain, per policy-critical class, etc.) is an Improvement. V2 can use the simpler model with the corrected wording.

**Amendment 4 action (Essential part only):** Rename "Safe Candidate Pruning" to "Candidate Budget Selection." Add explicit wording that UCB budget enforcement is a heuristic, not a proof of safety. Retain the baseline and per-domain coverage guarantees already in Amendment 3 Step 8. The elaborate coverage-reservation model is listed as future enhancement.

### Point 23 -- Reference Scale Saturation Model

**Classification: IMPROVEMENT (beyond the basic saturation policy fix).**

Logarithmic utility, sigmoid utility, and piecewise-linear utility are valid improvements. V2 uses bounded linear with explicit saturation. More sophisticated utility functions are future enhancement.

### Point 25 -- Pareto Should Include Uncertainty Semantics

**Classification: IMPROVEMENT.**

Point-estimate Pareto is accepted for V2. Interval/robust/stochastic Pareto is future enhancement.

### Point 29 -- Twin Materiality Novelty Is Underdefined

**Classification: IMPROVEMENT.**

For V2, materiality assessment can use simple policy-defined thresholds. Sophisticated learned materiality models with provenance are future enhancement.

### Point 31 -- R_i Has a Causal Attribution Problem

**Classification: IMPROVEMENT.**

Decomposed reliability metrics already exist in Amendment 3. The concern about confounded `action_outcome_quality` is valid but does not block V2. Advanced causal attribution is future enhancement.

### Point 32 -- Action Outcome Should Control for Selection Bias

**Classification: IMPROVEMENT.**

Exposure count, selection rate, scenario difficulty, and confidence intervals for R_i are improvements. V2's basic decomposed reliability is sufficient.

### Point 37 -- Cache Key Needs Full Parameters Hash

**Classification: IMPROVEMENT.**

The current key (session_id, snapshot_id, agent_id, capability_id, query_hash) is adequate for V2. Full canonical invocation hashing is improvement.

### Point 38 -- Governance Class Assignment Authority

**Classification: IMPROVEMENT.**

For V2, governance class can be defined per capability in the MCP capability card. Dynamic governance class assignment is improvement.

### Point 39 -- Replanning Exclusion Is Too Coarse

**Classification: IMPROVEMENT.**

For V2, basic `excluded_action_ids` is sufficient. Entity/capability/failure-class-specific exclusion is improvement.

### Point 40 -- Replanning Must Revalidate Policy

**Classification: IMPROVEMENT.**

For V2, replanning can use the current policy. Sophisticated policy rebinding during replanning is improvement.

### Point 42 -- actual_risk_realized: bool Is Too Coarse

**Classification: IMPROVEMENT.**

For V2, a Boolean risk realization indicator is sufficient as a starting point. Rich risk realization model (severity, loss, class) is improvement.

### Point 45 -- Replay Contract Overclaims Exactness

**Classification: ESSENTIAL wording correction + IMPROVEMENT for full manifest.**

The wording must be corrected to say EXACT_SYSTEM replay is available ONLY when every required dependency is captured. The full manifest of every dependency (tokenizer version, container digest, CUDA runtime, etc.) is improvement. V2 uses TRACE and LOGICAL replay levels.

**Amendment 4 action (Essential part only):** Add `EXACT_SYSTEM_AVAILABLE` as a Boolean condition in the replay manifest. If the required dependencies are not fully captured, the replay type downgrades to `MODEL` or `LOGICAL`. The architecture does not claim exact replay is always possible.

### Point 46 -- Retrieval Artifacts Need Snapshot Binding

**Classification: IMPROVEMENT.**

Adding snapshot_id, capability_version, retrieval_policy_version, corpus_version, index_version, result_order_hash, and authorization_scope to retrieval artifacts is improvement. V2's current retrieval artifact schema is adequate for basic replay.

### Point 47 -- Concurrent Session Interference Is Not Enough

**Classification: IMPROVEMENT.**

Resource overlap, capability overlap, and constraint overlap detection are improvements over entity intersection. V2's entity-based overlap detection is sufficient for the research/MVP scope.

### Point 50/51 -- Ablation Ladder Does Not Isolate Variables Cleanly

**Classification: IMPROVEMENT.**

The B0-B7 ladder is an engineering progression, not a controlled experiment. Controlled component ablations (Twin ON/OFF, cross-exam ON/OFF, etc.) are improvement. V2 uses the B0-B7 ladder as its primary evaluation framework.

### Point 52 -- B0 Is Too Narrow

**Classification: IMPROVEMENT.**

Defining B0 for every disruption class is improvement. V2 starts with supplier-delay B0 as the primary baseline.

### Point 53 -- B0 Freeze Date Should Not Be Hard-Coded

**Classification: ESSENTIAL wording correction.**

Replace `FREEZE_DATE = "2026-10-15"` with a policy statement: "B0 must be frozen before any system-under-test evaluation begins."

### Point 54 -- Statistical Protocol: "Assumption-Free" Is Too Strong

**Classification: ESSENTIAL wording correction.**

Replace "assumption-free" with "distribution-light / non-parametric." One word change.

### Point 55 -- 30 Scenarios Is Not a Universal Guarantee

**Classification: IMPROVEMENT.**

Power analysis is improvement. 30 is retained as the MVP floor with a note that production evaluation should use power analysis to determine adequate sample size.

### Point 56 -- Scenario Splitting Needs Grouped Leakage Control

**Classification: IMPROVEMENT (HIGH PRIORITY).**

Group-aware splitting by supplier, SKU, facility, scenario family, time, and world seed is high-priority improvement. V2 uses stratified splitting by disruption type as the minimum.

### Point 57 -- Calibration Targets Are Policy Targets

**Classification: ESSENTIAL wording correction.**

Reframe ECE and Brier targets as "evaluation acceptance thresholds," not architectural truths.

### Point 60 -- Outcome Horizon Should Be Action-Specific

**Classification: IMPROVEMENT.**

Action-specific Twin horizons are improvement. V2 uses a bounded profile-configured horizon.

### Point 61 -- Twin Classification Needs Action-Level Overrides

**Classification: IMPROVEMENT.**

Candidate-level Twin materiality is improvement. V2 uses decision-level classification.

### Point 62 -- ActionDefinition Needs Versioning

**Classification: IMPROVEMENT.**

Full cryptographic versioning (schema hash, handler version, etc.) is improvement. V2 uses basic version metadata.

### Point 63 -- execution_capability_id Nullability

**Classification: ESSENTIAL schema correction.**

The schema says `execution_capability_id: str` but examples use `null` for advisory actions. The type must be `Optional[str]`.

**Amendment 4 action:** Change to `execution_capability_id: Optional[str]` with a consistency rule: `advisory_only == True` requires `execution_capability_id is None`.

### Point 64 -- simulatable and advisory_only Consistency Rules

**Classification: IMPROVEMENT.**

Explicit semantic documentation is improvement. The properties are already independently defined.

### Point 65 -- Action Ownership Needs constraint_authority

**Classification: IMPROVEMENT.**

For V2, the policy engine serves as constraint authority. Explicit per-action constraint_authority is improvement.

### Point 66 -- Evidence Authority Must Remain Proposition-Specific

**Classification: IMPROVEMENT.**

Already addressed by the EvidenceClass correction (Point 4). Proposition-specific authority semantics are maintained.

### Point 68 -- data_as_of Is Not Always Enough for Temporal Consistency

**Classification: IMPROVEMENT / FUTURE.**

Bitemporal semantics (valid_time, transaction_time, observed_time) are future enhancement. V2 uses `data_as_of` and `observation_cutoff`.

### Point 78 -- Non-Blocking But Important Corrections

**Classification: Mixed. See individual item analysis above.**

Items 1, 2, 7, 8 are handled as Essential. The remainder are classified as Improvement and listed in Amendment 4's future enhancement section.

---

## Part V: Blocker Resolution Map

The review lists 12 blockers in Point 77. Here is the resolution status for each:

| Blocker | Description | Essential? | Amendment 4 Resolution |
| :--- | :--- | :--- | :--- |
| 1 | Twin policy naming contradiction | ESSENTIAL | One canonical `SimulationMaterialityThresholds` |
| 2 | Invalid snapshot LSN arithmetic | ESSENTIAL | Common `snapshot_epoch` model |
| 3 | UCB described as safe pruning | ESSENTIAL (wording) | Rename to "budgeted candidate selection" |
| 4 | Signed objective normalization | ESSENTIAL | Direction-aware utility functions |
| 5 | Critical evidence vocabulary collision | ESSENTIAL | Separate `EvidenceClass` registry |
| 6 | Circular criticality definition | ESSENTIAL | Profile-defined primary + sensitivity-escalation secondary |
| 7 | Marginal sufficiency inconsistency | ESSENTIAL | Explicit criticality tiers with precedence |
| 8 | Policy hash self-reference | ESSENTIAL | Canonical payload excluding integrity metadata |
| 9 | Replay exactness overclaimed | ESSENTIAL (wording) | `EXACT_SYSTEM_AVAILABLE` condition |
| 10 | Concurrent session resource gaps | IMPROVEMENT | Listed as future enhancement |
| 11 | Terminal event guard atomicity | ESSENTIAL (contract) | Transactional state transition specification |
| 12 | B3/B4 ablation overlap | ESSENTIAL | B3 = cross-exam only; B4 = evidence gate |

**Result:** 11 of 12 blockers are resolved as Essential corrections. Blocker 10 (resource-level concurrent session detection) is classified as Improvement.

---

## Part VI: Summary of Amendment 4 Scope

### Essential Corrections (will be in Amendment 4 architecture revision):

1. Separate `EvidenceClass` registry from `ClaimTypeRegistry`
2. Fix claim registry validation fail-open bug
3. Unify ActionRegistry (merge ActionTypeRegistry and ActionDefinition)
4. Remove duplicated `CandidateAction.action_type`
5. Correct ActionIntent wording (decision parameters vs impact estimates)
6. Three-tier impact model (Baseline / Predictive / Counterfactual)
7. Fix critical evidence circularity (profile-defined primary criticality)
8. Fix marginal sufficiency inconsistency (tiered criticality with precedence)
9. Fix snapshot consistency model (common snapshot_epoch)
10. Fix snapshot advancement (full session restart, no partial restart)
11. Remove WALL_CLOCK freshness from decision context
12. Fix post-snapshot freshness bug (raise error, not return 1.0)
13. Fix signed objective normalization (direction-aware utility)
14. Rename UCB pruning to "budgeted candidate selection"
15. Unify Twin policy naming (one canonical SimulationMaterialityThresholds)
16. Fix CD2F "execution authorization" wording
17. Add database constraints for event sequence
18. Add session state transition matrix
19. Fix policy hash self-reference
20. Fix B3/B4 ablation overlap
21. Remove hard-coded B0 freeze date
22. Correct "assumption-free" to "non-parametric"
23. Correct calibration targets to "acceptance thresholds"
24. Fix execution_capability_id nullability
25. Add final state revalidation before execution
26. Bound replay exactness claim
27. Rename PARETO_DOMINANT to SINGLETON_FRONTIER
28. Add saturation_policy to ObjectiveNormalization

### Improvement / Future Items (will be listed at end of Amendment 4, NOT in architecture):

All items classified as IMPROVEMENT or FUTURE above, including but not limited to: uncertainty-aware Pareto, coverage-aware budget pruning, candidate-level Twin materiality, action-specific horizons, full retrieval lineage, resource conflict detection, sophisticated replanning, rich risk realization model, advanced R_i causal attribution, power analysis, grouped leakage control, advanced temporal semantics, logarithmic utility functions, full A2A delegation, bit-exact replay, and production concurrency.

---

> [!IMPORTANT]
> This analysis validates the review's central conclusion: the architecture is sound but the contracts need a final correction pass. Amendment 4 is that pass. It is not a conceptual redesign. It is the elimination of the remaining contradictions, the normalization of names, the correction of mathematical errors, and the explicit scoping of V2 vs future work. After Amendment 4, the architecture should be frozen and implementation should begin.
