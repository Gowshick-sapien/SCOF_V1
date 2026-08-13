# Deliverable D6 Implementation Plan -- CD2F Consensus Engine

## Goal Description
Deliverable D6 builds and validates the Consensus-Driven Collaborative Decision Framework (CD2F) arbitration engine in isolation against fixture data, before trusting it on live agent output from D5. D6 is the research core of SCOF and delivers:
1. **ConsensusBundle Normalization Layer** (`shared/scof_shared/schemas/consensus_bundle.py`) defining the intermediate artifact that preserves the immutable D5 `ClaimBundle` source reference and adds consensus-specific derived information (normalized claims, exclusion reasons, engine version fingerprint) for the arbitration pipeline.
2. **Confidence-Weighted Arbitration Pipeline** (`services/consensus/src/arbitration.py`) implementing the `ConsensusBundle`-to-decision pipeline that combines each agent's stated confidence with its rolling historical accuracy to compute effective vote weights, aggregate recommendations, and produce a final decision with quantified Weighted Consensus Stability (WCS).
3. **Escalation Tiering Engine** (`services/consensus/src/escalation.py`) implementing three-tier routing logic (fast path / slow path / human escalation) where every threshold -- including the behaviorally distinct `slow_path.min_confidence` -- drives routing decisions. All criteria are read from the Domain Profile's `consensus.yaml`, ensuring zero hardcoded escalation logic.
4. **Judge Calibration Module** (`services/consensus/src/calibration.py`) computing Cohen's kappa inter-rater agreement between CD2F arbitration outputs and a hand-labeled scenario set (`profiles/mvp-electronics/scenarios/calibration_set.json`), measuring agreement independently over both final recommendation (`recommendation_kappa`) and escalation tier (`escalation_tier_kappa`), with configurable check frequency and minimum kappa threshold from `consensus.yaml`.
5. **Baseline Comparators** (`services/consensus/src/baselines/`) implementing both a single-agent baseline and a naive majority voting baseline, returning `EvaluationDecision` records with an explicit `decision_method` discriminator, used purely as evaluation comparators for D10 benchmarking (not in production decisions).
6. **Reasoning Trail Builder** (`services/consensus/src/reasoning_trail.py`) constructing per-decision reasoning trails and AI Meeting Log entries documenting every agent's claim, the weighting computation, the escalation tier determination, and the final decision rationale.
7. **Decision Record Output Schema** (`shared/scof_shared/schemas/decision_record.py`) defining the Pydantic contract for the CD2F output: final decision, reasoning trail, escalation tier, WCS score, per-agent weight breakdown, and explicit `decision_method = "CD2F"` discriminator.
8. **Outcome Feedback Module** (`services/consensus/src/accuracy_tracker.py`) implementing an explicit outcome-feedback lifecycle where accuracy updates are an external operation triggered by adjudicated outcomes -- never by the arbitration pipeline itself. Arbitration is strictly read-only with respect to agent accuracy state.
9. **Consensus Configuration Loader** (`shared/scof_shared/profile/consensus_config.py`) providing typed Pydantic models for parsing `consensus.yaml` with validation of threshold ranges, impact level enumerations, and profile-declared `impact_mapping` rules.
10. **Fixture Test Data** (`services/consensus/fixtures/`) containing hand-crafted mock claim bundles covering agreement, disagreement, conflicting-evidence, and partial-bundle scenarios with hand-worked expected outputs.
11. **Automated Verification Script** (`scripts/verify_d6.py`) callable via `make verify-d6` to validate arbitration correctness, escalation tier routing, calibration computation, and baseline comparator output.

---

## Prerequisites Check

> [!NOTE]
> - **Prerequisite Deliverables**: D6 is designed to be tested in isolation against fixture data. It does not require D3/D4/D5 to be running. However, the shared library (`shared/scof_shared/schemas/`) must be installed, as D6 imports `StructuredClaim`, `ClaimBundle`, and `EvidenceItem` schemas established by prior deliverables.
> - **Domain Profile**: [`profiles/mvp-electronics/consensus.yaml`](../../../profiles/mvp-electronics/consensus.yaml) must exist with `fast_path`, `slow_path`, `human_escalation`, `calibration`, and `impact_mapping` configuration blocks.
> - **Calibration Scenarios**: [`profiles/mvp-electronics/scenarios/calibration_set.json`](../../../profiles/mvp-electronics/scenarios/) must be populated with hand-labeled scenario data (created as part of this deliverable).
> - **Repository Structure**: Monorepo scaffolding, `shared/` library, and `docs/deliverables/D06_consensus_engine/` documentation structure are established.
> - **D05 Contract**: D05's `ClaimBundle` is an immutable frozen Pydantic model. D06 must not mutate it. D06 creates a distinct `ConsensusBundle` from it, per the D05 architectural invariant documented in [`langgraph_design.md`](../D05_orchestration/langgraph_design.md).

---

## User Review Required & Design Refinements Incorporated

> [!IMPORTANT]
> **Key Refinements Incorporated for D6 (Architectural Enhancements)**:
> 1. **ConsensusBundle as Intermediate Artifact (D05 Contract Compliance)**: D05 produces an immutable `ClaimBundle`. D06 creates a distinct `ConsensusBundle` that preserves the source `ClaimBundle` reference (`source_bundle_id`) and adds consensus-derived fields (normalized claims, excluded claims with exclusion reasons, engine version, config fingerprint). The arbitration pipeline operates on `ConsensusBundle`, not directly on `ClaimBundle`. `DecisionRecord.consensus_bundle_id` traces back to the `ConsensusBundle`, which in turn traces to the source `ClaimBundle`.
> 2. **Effective Weight Formula**: `effective_weight = stated_confidence * rolling_historical_accuracy`. Historical accuracy is tracked per-agent as a rolling window (configurable window size) of adjudicated outcome correctness. For agents with no history (cold start), a configurable default accuracy (e.g., 0.50) is used. **Arbitration never mutates accuracy state** -- accuracy updates are an explicit, external outcome-feedback operation.
> 3. **Behaviorally Complete Escalation Tiers**: Every configuration field in `consensus.yaml` drives a specific routing decision:
>    - **FAST PATH**: Unanimous recommendation across all participating agents + minimum individual agent confidence >= `fast_path.confidence_threshold` + maximum claim impact level <= `fast_path.max_impact_level`.
>    - **SLOW PATH**: Not fast path + winning recommendation's weighted decision confidence >= `slow_path.min_confidence` + maximum claim impact level <= `slow_path.max_impact_level` + WCS >= `human_escalation.consensus_stability_min`.
>    - **HUMAN ESCALATION**: WCS < `human_escalation.consensus_stability_min` OR maximum claim impact level >= `human_escalation.impact_level_trigger` OR winning weighted decision confidence < `slow_path.min_confidence`.
>    - **Decision confidence** is defined mathematically as `sum(effective_weights of agents supporting the winning recommendation) / sum(all effective_weights)`, distinct from individual agent confidence.
> 4. **Profile-Declared Impact Mapping**: Impact level parsing uses an explicit `impact_mapping` dictionary declared in `consensus.yaml` (e.g., `{"critical": "CRITICAL", "business-critical": "CRITICAL", "severe": "HIGH", ...}`) rather than keyword rules buried in Python. This eliminates domain knowledge leakage into engine code.
> 5. **Weighted Consensus Stability (WCS)**: Formally defined as `max_weighted_tally / sum_all_tallies` -- the weighted dominance of the winning recommendation, not a general inter-agent agreement metric. Named and documented precisely to avoid misleading interpretation. Range [0.0, 1.0] where 1.0 = all effective weight supports one recommendation.
> 6. **Reasoning Trail as First-Class Output**: Every arbitration produces a structured reasoning trail documenting: (a) each agent's claim summary, (b) the computed effective weight per agent, (c) the recommendation grouping and weighted vote tallies, (d) the escalation tier determination rationale, and (e) the final decision justification. This directly feeds D7 observability and D9 AI Meeting Log.
> 7. **Fixture-First Validation Strategy**: D6 is validated entirely against hand-crafted fixture data (`services/consensus/fixtures/`) before any integration with live D5 agent output. Four fixture categories: agreement, disagreement, conflicting evidence, and partial bundle (missing agents).
> 8. **Multi-Dimensional Calibration**: Cohen's kappa is computed independently for `recommendation_kappa` (final recommendation agreement) and `escalation_tier_kappa` (escalation tier agreement). Both must meet the `min_kappa` threshold. The calibration report also includes overall exact-match rate and handles edge cases (single-class samples, undefined kappa, insufficient sample size).
> 9. **Explicit Outcome Feedback Lifecycle**: Accuracy updates are recorded via `record_outcome(agent_id, outcome_id, was_correct, source, timestamp)` where `source` is one of: `human_adjudication`, `realized_simulation_outcome`, `validated_operational_outcome`, `calibration_ground_truth`. Arbitration is strictly read-only. Calibration ground truth does not automatically flow into production accuracy unless explicitly specified.
> 10. **Deterministic Tie-Breaking**: When weighted vote tallies produce a tie: (a) for each tied recommendation, calculate the maximum effective weight among agents supporting that recommendation; prefer the recommendation with the higher max supporter weight, (b) if still tied, prefer the recommendation with the higher maximum single-agent stated confidence among its supporters, (c) if still tied, escalate to slow path.
> 11. **Partial Bundle Handling Policy**: `ClaimBundle` with `status = "PARTIAL"` (failed/unresponsive agents) is arbitrated only if the number of successful claims meets a configurable `min_participating_agents` threshold (from `consensus.yaml`). Below that threshold, the engine returns `HUMAN_ESCALATION` with rationale citing insufficient agent participation. Absent agents are treated as abstentions (they do not count toward any recommendation tally, and WCS is computed over participating agents only).
> 12. **Decision Method Discriminator**: All decision-producing functions (`CD2F`, `SINGLE_AGENT`, `NAIVE_MAJORITY`) set an explicit `decision_method` field on their output. Baselines return `EvaluationDecision` (a subclass with `decision_method` set and escalation metadata clearly marked as comparator-only), preventing D9/D10 consumers from mistaking baseline metadata for production routing.
> 13. **Atomic JSON Store for Accuracy Tracker**: The MVP JSON-backed accuracy store uses atomic temp-file-plus-rename writes to prevent read-modify-write races under concurrent FastAPI requests. Includes deterministic initialization (empty tracker on first use) and corruption recovery (fallback to empty state with logged warning).

---

## Open Questions

> [!NOTE]
> None. All architectural enhancements have been integrated into the implementation plan.

---

## Proposed Changes

### Shared Library -- Consensus Configuration (`shared/scof_shared/profile/`)

#### [NEW] [consensus_config.py](../../../shared/scof_shared/profile/consensus_config.py)
- Typed Pydantic model for parsing `consensus.yaml` with the following structure:
  - `FastPathConfig`: `confidence_threshold` (float, 0.0-1.0), `max_impact_level` (Literal `LOW`/`MEDIUM`/`HIGH`/`CRITICAL`).
  - `SlowPathConfig`: `min_confidence` (float, 0.0-1.0 -- the minimum weighted decision confidence for slow-path eligibility), `max_impact_level` (Literal).
  - `HumanEscalationConfig`: `consensus_stability_min` (float, 0.0-1.0), `impact_level_trigger` (Literal).
  - `CalibrationConfig`: `frequency` (str), `min_kappa` (float, 0.0-1.0).
  - `PartialBundleConfig`: `min_participating_agents` (int, default 2).
  - `AccuracyConfig`: `default_accuracy` (float, default 0.50), `window_size` (int, default 50).
  - `ImpactMapping`: `Dict[str, Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]]` -- profile-declared keyword-to-level mapping. No domain-specific keyword parsing logic in Python.
  - `ConsensusConfig`: Top-level model aggregating all config blocks with field validators ensuring threshold consistency (e.g., `fast_path.confidence_threshold` > `slow_path.min_confidence`).
- Provides `load_consensus_config(profile_path: Path) -> ConsensusConfig` factory function.

#### [MODIFY] [loader.py](../../../shared/scof_shared/profile/loader.py)
- Import and integrate `ConsensusConfig` and `load_consensus_config` into the profile loader so that `consensus.yaml` is loaded alongside `topology.yaml` and `agents.yaml`.

#### [MODIFY] [__init__.py](../../../shared/scof_shared/profile/__init__.py)
- Export `ConsensusConfig` and `load_consensus_config` from the profile package.

---

### Shared Library -- ConsensusBundle Schema (`shared/scof_shared/schemas/`)

#### [NEW] [consensus_bundle.py](../../../shared/scof_shared/schemas/consensus_bundle.py)
- Pydantic model defining the intermediate consensus artifact created by D6 from D5's immutable `ClaimBundle`:
  - `consensus_bundle_id`: str (UUID, unique to this consensus processing run).
  - `source_bundle_id`: str (references the originating `ClaimBundle.bundle_id` from D5).
  - `scenario_id`: str (propagated from source bundle).
  - `profile_name`: str (propagated from source bundle).
  - `profile_version`: str (propagated from source bundle).
  - `participating_agents`: List[str] (agents included in arbitration).
  - `successful_agents`: List[str] (agents whose claims passed normalization).
  - `failed_agents`: Dict[str, str] (agents excluded from arbitration, propagated from source).
  - `normalized_claims`: Dict[str, `NormalizedClaim`] (claims after impact level parsing and validation, keyed by agent_id).
  - `excluded_claims`: Dict[str, str] (agent_id -> exclusion reason, for claims that failed normalization or were excluded by policy).
  - `engine_version`: str (consensus engine semantic version, e.g., "1.0.0").
  - `config_fingerprint`: str (SHA-256 hash of the `ConsensusConfig` used, for reproducibility).
  - `timestamp`: datetime (UTC).
- `NormalizedClaim` sub-model:
  - `agent_id`: str.
  - `recommendation`: str.
  - `stated_confidence`: float (0.0-1.0).
  - `parsed_impact_level`: Literal `LOW`/`MEDIUM`/`HIGH`/`CRITICAL` (resolved via `impact_mapping`).
  - `priority`: Literal `HIGH`/`MEDIUM`/`LOW`.
  - `evidence_count`: int.
  - `original_impact_text`: str (the raw `impact` string from the StructuredClaim, preserved for audit).

---

### Shared Library -- Decision Record Schema (`shared/scof_shared/schemas/`)

#### [NEW] [decision_record.py](../../../shared/scof_shared/schemas/decision_record.py)
- Pydantic model defining the CD2F output contract:
  - `decision_id`: str (UUID).
  - `scenario_id`: str (links to input scenario).
  - `consensus_bundle_id`: str (links to the `ConsensusBundle` that was arbitrated).
  - `source_bundle_id`: str (links to the original D5 `ClaimBundle`, propagated for convenience).
  - `decision_method`: Literal `CD2F` / `SINGLE_AGENT` / `NAIVE_MAJORITY` (explicit discriminator).
  - `final_recommendation`: str (the chosen action).
  - `decision_confidence`: float (weighted decision confidence = sum of effective weights supporting the winning recommendation / sum of all effective weights, range 0.0-1.0).
  - `weighted_consensus_stability`: float (WCS = max_weighted_tally / sum_all_tallies, range 0.0-1.0).
  - `escalation_tier`: Literal `FAST_PATH` / `SLOW_PATH` / `HUMAN_ESCALATION`.
  - `escalation_rationale`: str (why this tier was selected).
  - `agent_weights`: Dict[str, `AgentWeightBreakdown`] containing `stated_confidence`, `historical_accuracy`, `effective_weight` per agent.
  - `recommendation_tallies`: Dict[str, float] mapping each distinct recommendation to its weighted vote total.
  - `reasoning_trail`: List[`ReasoningStep`] (ordered sequence of reasoning steps).
  - `meeting_log_entries`: List[`MeetingLogEntry`] (human-readable discussion entries for D9 AI Meeting Log).
  - `timestamp`: datetime (UTC).
  - `profile_name`: str.
  - `profile_version`: str.
  - `engine_version`: str.
- `AgentWeightBreakdown` sub-model: `stated_confidence` (float), `historical_accuracy` (float), `effective_weight` (float).
- `ReasoningStep` sub-model: `step_index` (int), `step_type` (Literal), `content` (str), `data` (Optional Dict).

#### [NEW] [evaluation_decision.py](../../../shared/scof_shared/schemas/evaluation_decision.py)
- `EvaluationDecision`: Subclass (or sibling) of `DecisionRecord` used exclusively by baseline comparators.
  - Inherits all fields from `DecisionRecord`.
  - `decision_method` is constrained to `SINGLE_AGENT` or `NAIVE_MAJORITY`.
  - `is_comparator_only`: bool = True (explicit flag preventing production consumption).
  - `baseline_metadata`: Dict[str, Any] (e.g., which agent was selected for single-agent baseline).
  - Escalation tier metadata is populated for structural compatibility but clearly documented as comparator-derived, not CD2F-routed.

#### [NEW] [meeting_log.py](../../../shared/scof_shared/schemas/meeting_log.py)
- Pydantic model for AI Meeting Log entries:
  - `MeetingLogEntry`: `step_index` (int), `speaker` (str, agent_id or "COORDINATOR"), `statement_type` (Literal `CLAIM` / `WEIGHT_REPORT` / `TALLY` / `ESCALATION` / `DECISION`), `content` (str, human-readable), `timestamp` (datetime).

#### [MODIFY] [__init__.py](../../../shared/scof_shared/schemas/__init__.py)
- Export `ConsensusBundle`, `NormalizedClaim`, `DecisionRecord`, `EvaluationDecision`, `AgentWeightBreakdown`, `ReasoningStep`, `MeetingLogEntry` from the schemas package.

---

### Domain Profile Update (`profiles/mvp-electronics/`)

#### [MODIFY] [consensus.yaml](../../../profiles/mvp-electronics/consensus.yaml)
- Extend existing configuration with new fields required by the refined D6 architecture:
  - `impact_mapping`: Explicit keyword-to-level mapping dictionary (e.g., `"critical": "CRITICAL"`, `"business-critical": "CRITICAL"`, `"severe": "HIGH"`, `"significant": "HIGH"`, `"moderate": "MEDIUM"`, `"minor": "LOW"`, `"negligible": "LOW"`).
  - `partial_bundle.min_participating_agents`: Minimum agent count for valid arbitration (default 2).
  - `accuracy.default_accuracy`: Cold-start default (0.50).
  - `accuracy.window_size`: Rolling window size (50).

---

### Consensus Engine Service (`services/consensus/`)

#### [NEW] [pyproject.toml](../../../services/consensus/pyproject.toml)
- Package manifest declaring dependencies: `scikit-learn` (for Cohen's kappa), `pydantic`, `fastapi`, `uvicorn`, `scof-shared`. `numpy` and `scipy` are excluded unless a concrete module requires them -- `scikit-learn` satisfies the calibration requirement, and the consensus algorithms use ordinary Python arithmetic.

#### [NEW] [Dockerfile](../../../services/consensus/Dockerfile)
- Container definition for running the D6 consensus engine service. Lightweight `python:3.11-slim` base image.

#### [NEW] [README.md](../../../services/consensus/README.md)
- Service-level README documenting purpose, usage, CLI interface, and fixture test instructions.

---

### Consensus Engine Source (`services/consensus/src/`)

#### [NEW] [__init__.py](../../../services/consensus/src/__init__.py)
- Package initialization for the consensus engine source module.

#### [NEW] [config.py](../../../services/consensus/src/config.py)
- Configuration module centralizing:
  - Domain Profile path (`SCOF_PROFILE_PATH` environment variable).
  - Consensus engine version string (`ENGINE_VERSION = "1.0.0"`).
  - Accuracy tracker storage path.
  - Logging configuration.

#### [NEW] [normalizer.py](../../../services/consensus/src/normalizer.py)
- ConsensusBundle normalization layer:
  1. **Input**: Immutable `ClaimBundle` from D5 + `ConsensusConfig`.
  2. **Claim Validation**: For each claim in the bundle, validate presence of required fields and parseable impact text.
  3. **Impact Level Resolution**: Parse each claim's `impact` string using the profile-declared `impact_mapping` dictionary. Claims with unparseable impact text are excluded with a documented reason.
  4. **Partial Bundle Policy Enforcement**: If `ClaimBundle.status == "PARTIAL"`, check that `len(successful_claims) >= min_participating_agents`. If below threshold, short-circuit to `HUMAN_ESCALATION` with rationale citing insufficient participation.
  5. **ConsensusBundle Assembly**: Construct a `ConsensusBundle` with `source_bundle_id`, normalized claims, excluded claims with reasons, engine version, and config fingerprint (SHA-256 of serialized `ConsensusConfig`).
  6. **Output**: `ConsensusBundle` ready for arbitration, or an early `DecisionRecord` with `HUMAN_ESCALATION` if the bundle fails minimum participation requirements.

#### [NEW] [arbitration.py](../../../services/consensus/src/arbitration.py)
- Core confidence-weighted voting arbitration pipeline:
  1. **Input**: `ConsensusBundle` (not raw `ClaimBundle`) + per-agent historical accuracies from the accuracy tracker (read-only query).
  2. **Weight Computation**: For each normalized claim, compute `effective_weight = stated_confidence * rolling_historical_accuracy` using read-only accuracy tracker queries. **Arbitration never mutates accuracy state.**
  3. **Recommendation Grouping**: Group normalized claims by their `recommendation` field (exact string matching for MVP; semantic grouping is a post-MVP extension).
  4. **Weighted Vote Aggregation**: Sum effective weights per recommendation group.
  5. **WCS Computation**: Calculate Weighted Consensus Stability as `max_weighted_tally / sum_all_tallies` (weighted dominance of the winning recommendation).
  6. **Decision Confidence Computation**: Calculate `decision_confidence = sum(effective_weights supporting winner) / sum(all effective_weights)`. This is numerically identical by design to WCS (the max weighted tally over sum of all tallies). They are named distinctly because they serve different semantic roles: WCS is a stability/routing metric, while decision confidence is the explicit confidence field exposed to consumers.
  7. **Tie-Breaking Protocol**: When tallies are tied: (a) for each tied recommendation, find the maximum effective weight among its supporting agents; prefer the recommendation whose max supporter weight is higher, (b) if still tied, prefer the recommendation whose supporters include the agent with the higher maximum stated confidence, (c) if deterministic tie-breaking cannot select a unique recommendation, arbitration returns `winner = None` (unresolved state), and the escalation engine produces `SLOW_PATH` or `HUMAN_ESCALATION` according to configured criteria; no arbitrary recommendation is selected.
  8. **Winner Selection**: Select the recommendation with the highest weighted vote total (after tie-breaking if needed).
  9. **Output**: Intermediate `ArbitrationResult` containing winning recommendation, decision confidence, WCS, per-agent weights, and tallies.

#### [NEW] [escalation.py](../../../services/consensus/src/escalation.py)
- Escalation tiering logic where every `consensus.yaml` field drives a specific routing decision:
  1. **Fast Path**: Triggered when ALL of the following hold:
     - Only one distinct recommendation exists across all participating agents (unanimous).
     - The minimum individual agent stated confidence among participating agents exceeds `fast_path.confidence_threshold`.
     - The maximum parsed impact level across all claims is at or below `fast_path.max_impact_level` (using ordinal comparison: `LOW < MEDIUM < HIGH < CRITICAL`).
  2. **Slow Path**: Triggered when fast path criteria are not met AND ALL of the following hold:
     - The winning recommendation's decision confidence (weighted) >= `slow_path.min_confidence`.
     - The maximum parsed impact level across all claims is at or below `slow_path.max_impact_level`.
     - WCS >= `human_escalation.consensus_stability_min`.
  3. **Human Escalation**: Triggered when ANY of the following hold:
     - WCS < `human_escalation.consensus_stability_min`.
     - The maximum parsed impact level across all claims meets or exceeds `human_escalation.impact_level_trigger`.
     - The winning recommendation's decision confidence < `slow_path.min_confidence`.
     - The `ConsensusBundle` failed partial bundle minimum participation (handled upstream in normalizer, but escalation records the rationale).
  4. **Rationale Generation**: Each tier determination produces a human-readable rationale string documenting which criteria were satisfied or violated.

#### [NEW] [calibration.py](../../../services/consensus/src/calibration.py)
- Judge calibration module with multi-dimensional kappa computation:
  1. **Input**: List of `(cd2f_decision: DecisionRecord, ground_truth: GroundTruthLabel)` pairs from the calibration set.
  2. **Recommendation Kappa**: Uses `sklearn.metrics.cohen_kappa_score` to compute inter-rater agreement between CD2F `final_recommendation` and ground truth `expected_recommendation`.
  3. **Escalation Tier Kappa**: Independently computes kappa between CD2F `escalation_tier` and ground truth `expected_escalation_tier`.
  4. **Exact Match Rate**: Fraction of scenarios where both recommendation and escalation tier match ground truth simultaneously.
  5. **Edge Case Handling**:
     - Single-class samples (all labels identical): report kappa as undefined with a warning, do not fail.
     - Category absent from sample: report per-category confusion breakdown with zero-count categories noted.
     - Insufficient calibration set size (fewer than 5 scenarios): report kappa as unreliable with a warning, do not automatically pass.
  6. **Calibration Report**: Returns `CalibrationReport` containing `recommendation_kappa`, `escalation_tier_kappa`, `exact_match_rate`, per-category confusion breakdown, sample size, and composite `pass_status` (True only if both kappas >= `min_kappa` and sample size is sufficient).
  7. **Calibration Runner**: `run_calibration(engine, calibration_set_path, consensus_config) -> CalibrationReport` loads the calibration set, runs each scenario through the arbitration pipeline, and computes kappas.

#### [NEW] [accuracy_tracker.py](../../../services/consensus/src/accuracy_tracker.py)
- Rolling historical accuracy tracker per agent with explicit outcome-feedback lifecycle:
  1. **Core Invariant**: Arbitration never mutates accuracy state. Accuracy updates are triggered exclusively by external outcome adjudication.
  2. **Record**: `record_outcome(agent_id: str, outcome_id: str, was_correct: bool, source: Literal["human_adjudication", "realized_simulation_outcome", "validated_operational_outcome", "calibration_ground_truth"], timestamp: datetime)` appends to the rolling window. The `source` field enables downstream analysis of accuracy by feedback source.
  3. **Query**: `get_accuracy(agent_id: str) -> float` returns the rolling accuracy for the agent (correct decisions / total decisions in the window). Returns `default_accuracy` from `ConsensusConfig` for agents with no history.
  4. **Window Management**: Maintains a fixed-size sliding window per agent (`accuracy.window_size` from config).
  5. **Storage**: JSON file-backed store with atomic temp-file-plus-rename writes to prevent read-modify-write races under concurrent FastAPI requests. Deterministic initialization (empty tracker JSON on first use). Corruption recovery: if JSON parsing fails, log a warning and fall back to empty state.
  6. **Isolation**: Calibration ground truth outcomes do not automatically flow into production accuracy tracking unless `source` is explicitly set to `calibration_ground_truth` by the caller. This prevents calibration runs from polluting production accuracy data.

#### [NEW] [reasoning_trail.py](../../../services/consensus/src/reasoning_trail.py)
- Reasoning trail and meeting log entry builder:
  1. **Claim Summary Steps**: For each agent's normalized claim, generates a `ReasoningStep` and `MeetingLogEntry` documenting the agent's recommendation, stated confidence, parsed impact level, priority, and key evidence count.
  2. **Weight Report Steps**: Documents the effective weight computation per agent (`stated_confidence * historical_accuracy = effective_weight`).
  3. **Tally Steps**: Documents the weighted vote aggregation results and WCS.
  4. **Escalation Steps**: Documents the escalation tier determination, listing which criteria were evaluated and which triggered the tier selection.
  5. **Decision Steps**: Documents the final decision, decision confidence, WCS, and overall justification.

#### [NEW] [engine.py](../../../services/consensus/src/engine.py)
- Top-level CD2F consensus engine orchestrator:
  1. Loads `ConsensusConfig` from the active Domain Profile.
  2. Accepts a `ClaimBundle` as input (the immutable D5 artifact).
  3. Normalizes into a `ConsensusBundle` via the normalizer (handles impact parsing, claim validation, partial bundle policy).
  4. If normalization triggers early human escalation (insufficient participation), returns a `DecisionRecord` immediately.
  5. Queries the accuracy tracker for per-agent historical accuracies (**read-only**).
  6. Executes the arbitration pipeline on the `ConsensusBundle` (`arbitration.py`).
  7. Determines escalation tier (`escalation.py`).
  8. Constructs reasoning trail and meeting log entries (`reasoning_trail.py`).
  9. Assembles and returns a complete `DecisionRecord` with `decision_method = "CD2F"`.
  10. Provides `run_consensus(claim_bundle: ClaimBundle) -> DecisionRecord` as the primary entry point.

#### [NEW] [main.py](../../../services/consensus/src/main.py)
- CLI entry point and optional FastAPI application:
  - CLI mode: `python -m services.consensus.src.main --fixture <path>` runs the engine against a fixture file and prints the `DecisionRecord`.
  - Server mode: `python -m services.consensus.src.main --serve` starts a FastAPI app exposing:
    - `POST /consensus/arbitrate` accepting a `ClaimBundle` and returning a `DecisionRecord`.
    - `POST /consensus/outcomes` accepting outcome feedback for the accuracy tracker.
    - `POST /consensus/calibrate` running calibration against the hand-labeled set.
    - `GET /consensus/accuracy/{agent_id}` querying an agent's current rolling accuracy.

---

### Baseline Comparators (`services/consensus/src/baselines/`)

#### [NEW] [__init__.py](../../../services/consensus/src/baselines/__init__.py)
- Package initialization exporting baseline functions.

#### [NEW] [single_agent.py](../../../services/consensus/src/baselines/single_agent.py)
- Single-agent baseline comparator:
  - Accepts a `ClaimBundle` and an optional `agent_id` parameter (defaults to the agent with the highest stated confidence).
  - Returns an `EvaluationDecision` with `decision_method = "SINGLE_AGENT"`, `is_comparator_only = True`.
  - Escalation tier is set to `FAST_PATH` (trivially, since only one agent is consulted) and clearly documented as comparator metadata, not CD2F routing.
  - `baseline_metadata` records which agent was selected and why.
  - Used as the lower-bound baseline: "Does multi-agent collaboration add value?"

#### [NEW] [naive_majority.py](../../../services/consensus/src/baselines/naive_majority.py)
- Naive majority voting baseline comparator:
  - Accepts a `ClaimBundle`.
  - Each agent gets exactly one unweighted vote for its recommendation (no confidence weighting, no historical accuracy).
  - The recommendation with the most votes wins. Ties broken by alphabetical order of recommendation string (simple, deterministic, intentionally simplistic).
  - Returns an `EvaluationDecision` with `decision_method = "NAIVE_MAJORITY"`, `is_comparator_only = True`.
  - Escalation tier is set to `SLOW_PATH` and clearly documented as comparator metadata.
  - Known failure mode: amplifies shared errors when homogeneous agents agree on the wrong answer. CD2F must outperform this.

---

### Fixture Test Data (`services/consensus/fixtures/`)

#### [NEW] [agreement_case.json](../../../services/consensus/fixtures/agreement_case.json)
- Mock `ClaimBundle` where all four agents (demand, inventory, supplier, transport) recommend the same action with high confidence (>0.85) and low impact. Expected outcome: fast-path decision with WCS near 1.0 and the unanimous recommendation selected.

#### [NEW] [disagreement_case.json](../../../services/consensus/fixtures/disagreement_case.json)
- Mock `ClaimBundle` where agents split into two opposing camps (e.g., 2 recommend "restock immediately", 2 recommend "wait for shipment") with moderate confidence (0.60-0.80) and medium impact. Expected outcome: slow-path decision determined by effective weight computation, with WCS between 0.50-0.75.

#### [NEW] [conflicting_evidence_case.json](../../../services/consensus/fixtures/conflicting_evidence_case.json)
- Mock `ClaimBundle` where agents present high-confidence (>0.85) but directly contradictory recommendations with critical impact. Expected outcome: human escalation triggered due to critical impact level.

#### [NEW] [partial_bundle_case.json](../../../services/consensus/fixtures/partial_bundle_case.json)
- Mock `ClaimBundle` with `status = "PARTIAL"`, containing claims from only 1 of 4 agents (below `min_participating_agents`). Expected outcome: human escalation triggered due to insufficient agent participation, with rationale citing the partial bundle policy.

#### [NEW] [expected_outputs.json](../../../services/consensus/fixtures/expected_outputs.json)
- Hand-worked expected `DecisionRecord` outputs for each fixture case, serving as ground truth for automated test validation. Documents the exact expected recommendation, escalation tier, approximate WCS range, and decision confidence for each case.

---

### Calibration Scenario Data (`profiles/mvp-electronics/scenarios/`)

#### [NEW] [calibration_set.json](../../../profiles/mvp-electronics/scenarios/calibration_set.json)
- Hand-labeled calibration set of 15-25 disruption scenarios, each containing:
  - `scenario_id`: Unique identifier.
  - `claim_bundle`: A complete `ClaimBundle` with mock agent claims.
  - `ground_truth`: Object containing:
    - `expected_recommendation`: The human-agreed correct decision.
    - `expected_escalation_tier`: The human-agreed correct escalation tier.
    - `reasoning`: Human rationale for the expected outcome.
  - Scenarios cover a distribution across all three escalation tiers and multiple disruption types (supplier delay, transport failure, demand spike, adverse weather).
  - At least 5 scenarios per escalation tier to ensure kappa computation is meaningful.

---

### Tests (`services/consensus/tests/`)

#### [NEW] [__init__.py](../../../services/consensus/tests/__init__.py)
- Package initialization for the consensus engine test module.

#### [NEW] [test_normalizer.py](../../../services/consensus/tests/test_normalizer.py)
- Unit tests for the ConsensusBundle normalization layer:
  - Test that source `ClaimBundle` is preserved (source_bundle_id matches).
  - Test impact level parsing using profile-declared `impact_mapping`.
  - Test claims with unparseable impact text are excluded with documented reasons.
  - Test partial bundle policy enforcement (`min_participating_agents` threshold).
  - Test config fingerprint is deterministic for the same configuration.
  - Test that the original `ClaimBundle` is never mutated.

#### [NEW] [test_arbitration.py](../../../services/consensus/tests/test_arbitration.py)
- Unit tests for the confidence-weighted voting pipeline:
  - Test effective weight computation with known confidence and accuracy values.
  - Test recommendation grouping and weighted tally aggregation.
  - Test WCS computation for unanimous, split, and scattered vote distributions.
  - Test decision confidence computation (distinct from WCS).
  - Test deterministic tie-breaking protocol: max supporter effective weight, then max stated confidence, then slow-path escalation.
  - Test cold-start agent handling (no historical accuracy data, uses default).
  - Test that arbitration performs zero writes to the accuracy tracker.

#### [NEW] [test_escalation.py](../../../services/consensus/tests/test_escalation.py)
- Unit tests for escalation tiering logic:
  - Test fast-path triggering: unanimous agreement, high individual confidence, low impact.
  - Test slow-path triggering: split recommendations, sufficient decision confidence >= `slow_path.min_confidence`, moderate stability, non-critical impact.
  - Test that `slow_path.min_confidence` being violated causes escalation to human (not slow path).
  - Test human escalation triggering: low WCS below `consensus_stability_min`.
  - Test human escalation triggering: critical impact level regardless of stability.
  - Test human escalation triggering: decision confidence below `slow_path.min_confidence`.
  - Test impact level ordinal comparison (`LOW < MEDIUM < HIGH < CRITICAL`).
  - Test edge cases: exactly-at-threshold values.

#### [NEW] [test_calibration.py](../../../services/consensus/tests/test_calibration.py)
- Unit tests for judge calibration module:
  - Test recommendation kappa computation with known agreement/disagreement distributions.
  - Test escalation tier kappa computation independently.
  - Test exact match rate computation.
  - Test calibration report pass/fail determination against `min_kappa` threshold (both kappas must pass).
  - Test edge case: single-class samples produce undefined kappa with warning, not failure.
  - Test edge case: insufficient sample size (< 5) produces unreliable warning.
  - Test calibration runner end-to-end with a small synthetic calibration set.

#### [NEW] [test_baselines.py](../../../services/consensus/tests/test_baselines.py)
- Unit tests for baseline comparators:
  - Test single-agent baseline selects the highest-confidence agent by default.
  - Test single-agent baseline returns the correct agent when explicitly specified.
  - Test naive majority voting correctly counts unweighted votes.
  - Test naive majority voting tie-breaking is deterministic (alphabetical).
  - Test that both baselines produce valid `EvaluationDecision` outputs with `is_comparator_only = True`.
  - Test that `decision_method` is correctly set to `SINGLE_AGENT` or `NAIVE_MAJORITY`.

#### [NEW] [test_reasoning_trail.py](../../../services/consensus/tests/test_reasoning_trail.py)
- Unit tests for reasoning trail and meeting log construction:
  - Test that all five step types (CLAIM, WEIGHT_REPORT, TALLY, ESCALATION, DECISION) are generated.
  - Test step ordering is correct.
  - Test meeting log entries are human-readable and contain expected content.

#### [NEW] [test_engine.py](../../../services/consensus/tests/test_engine.py)
- Integration tests for the top-level consensus engine:
  - Test end-to-end execution against `agreement_case.json` fixture, validating the output `DecisionRecord` matches expected outputs.
  - Test end-to-end execution against `disagreement_case.json` fixture.
  - Test end-to-end execution against `conflicting_evidence_case.json` fixture.
  - Test end-to-end execution against `partial_bundle_case.json` fixture (human escalation due to insufficient agents).
  - Test that changing `consensus.yaml` thresholds changes escalation tier outcomes without code changes.
  - Test that the `ConsensusBundle` intermediate artifact is correctly assembled with source traceability.
  - Test that `DecisionRecord.decision_method` is `"CD2F"` for all engine-produced decisions.

#### [NEW] [test_accuracy_tracker.py](../../../services/consensus/tests/test_accuracy_tracker.py)
- Unit tests for the agent accuracy tracker:
  - Test recording outcomes with explicit source and verifying rolling accuracy.
  - Test sliding window correctly evicts old outcomes.
  - Test cold-start default accuracy for unknown agents.
  - Test persistence: write, reload from file, verify state.
  - Test atomic write: concurrent simulated writes do not corrupt state.
  - Test corruption recovery: malformed JSON falls back to empty state with warning.
  - Test that `calibration_ground_truth` source outcomes are recorded but segregated.

---

### Scripts & Makefile (`scripts/`, `Makefile`)

#### [NEW] [verify_d6.py](../../../scripts/verify_d6.py)
- Comprehensive health verification script checking:
  1. Consensus engine module imports successfully.
  2. `ConsensusConfig` loads and validates from `profiles/mvp-electronics/consensus.yaml` (including `impact_mapping`, `partial_bundle`, `accuracy` blocks).
  3. All four fixture files (`agreement_case.json`, `disagreement_case.json`, `conflicting_evidence_case.json`, `partial_bundle_case.json`) are parseable as valid `ClaimBundle` objects.
  4. Running the engine against the agreement fixture produces a `FAST_PATH` decision with `decision_method = "CD2F"`.
  5. Running the engine against the conflicting evidence fixture produces a `HUMAN_ESCALATION` decision.
  6. Running the engine against the partial bundle fixture produces a `HUMAN_ESCALATION` decision with rationale citing insufficient agent participation.
  7. Both baseline comparators (single-agent, naive majority) produce valid `EvaluationDecision` outputs with `is_comparator_only = True`.
  8. `ConsensusBundle` intermediate artifacts preserve `source_bundle_id` traceability.
  9. Cohen's kappa computation (both recommendation and escalation tier) executes without error against a minimal synthetic calibration set.
  10. All `DecisionRecord` outputs contain non-empty reasoning trails and meeting log entries.
  11. Accuracy tracker atomic write/read cycle completes without error.

#### [MODIFY] [Makefile](../../../Makefile)
- Adding target `verify-d6` to run `python scripts/verify_d6.py`.

---

### Deliverable Documentation Package (`docs/deliverables/D06_consensus_engine/`)

#### [MODIFY] [README.md](../../../docs/deliverables/D06_consensus_engine/README.md)
- Updated overview, requirements summary, prerequisites, document set, module structure, and standalone acceptance criteria.

#### [NEW] [cd2f_algorithm_design.md](../../../docs/deliverables/D06_consensus_engine/cd2f_algorithm_design.md)
- Comprehensive CD2F algorithm documentation:
  - ConsensusBundle normalization from ClaimBundle (D05/D06 contract boundary).
  - Effective weight formula with mathematical definition.
  - Recommendation grouping mechanics.
  - Weighted vote aggregation.
  - Weighted Consensus Stability (WCS) metric: precise definition, naming rationale, numerical examples.
  - Decision confidence: mathematical definition distinguishing it from individual agent confidence.
  - Tie-breaking protocol with per-group max supporter weight comparison.
  - Escalation tier determination with full decision tree and behavioral mapping of every `consensus.yaml` field.
  - Partial bundle handling policy.
  - Worked examples with numerical computations for each fixture scenario.

#### [NEW] [calibration_design.md](../../../docs/deliverables/D06_consensus_engine/calibration_design.md)
- Judge calibration methodology:
  - Hand-labeled scenario set curation requirements (minimum 5 per escalation tier).
  - Multi-dimensional kappa: `recommendation_kappa` and `escalation_tier_kappa` computed independently.
  - Exact match rate definition.
  - Edge case handling: single-class samples, undefined kappa, insufficient sample size.
  - Frequency scheduling from `consensus.yaml`.
  - Kappa threshold interpretation and pass/fail criteria.

#### [NEW] [baseline_design.md](../../../docs/deliverables/D06_consensus_engine/baseline_design.md)
- Baseline comparator specifications:
  - Single-agent baseline mechanics and `EvaluationDecision` output contract.
  - Naive majority voting mechanics and known failure modes.
  - `decision_method` discriminator preventing consumer confusion.
  - How baselines map to RQ1 and RQ2 evaluation.

#### [NEW] [fixture_test_cases.md](../../../docs/deliverables/D06_consensus_engine/fixture_test_cases.md)
- Hand-worked expected outputs for each fixture case (agreement, disagreement, conflicting evidence, partial bundle): input claim bundle summary, step-by-step weight computation, tally aggregation, WCS calculation, escalation tier determination, and final decision with reasoning trail.

#### [NEW] [design_decisions.md](../../../docs/deliverables/D06_consensus_engine/design_decisions.md)
- Architectural design decisions for D6:
  - ConsensusBundle intermediate artifact rationale (D05 immutability preservation).
  - Effective weight formula rationale.
  - Profile-declared impact mapping (zero domain knowledge in Python).
  - WCS metric naming and definition precision.
  - Behaviorally complete escalation tiers (every config field drives routing).
  - Explicit outcome feedback lifecycle (arbitration never mutates accuracy).
  - Multi-dimensional calibration (recommendation + escalation tier kappa).
  - Partial bundle handling policy.
  - Decision method discriminator for baselines.
  - Atomic JSON store for accuracy tracker.
  - Deterministic tie-breaking with per-group supporter weight comparison.
  - Dependency minimization (scikit-learn only, no unnecessary numpy/scipy).

#### [NEW] [acceptance_evidence.md](../../../docs/deliverables/D06_consensus_engine/acceptance_evidence.md)
- Evidence log template and test execution outputs for D6 acceptance criteria.

---

## Verification Plan

### Automated Tests
1. **Consensus Engine Unit & Integration Test Suite**:
   ```bash
   pytest services/consensus/tests/
   ```
2. **CLI Fixture Execution (all four cases)**:
   ```bash
   python -m services.consensus.src.main --fixture services/consensus/fixtures/agreement_case.json
   python -m services.consensus.src.main --fixture services/consensus/fixtures/disagreement_case.json
   python -m services.consensus.src.main --fixture services/consensus/fixtures/conflicting_evidence_case.json
   python -m services.consensus.src.main --fixture services/consensus/fixtures/partial_bundle_case.json
   ```
3. **Automated Health & Correctness Verification Script**:
   ```bash
   make verify-d6
   ```
   or
   ```bash
   python scripts/verify_d6.py
   ```

### Manual Verification
1. **Fixture Output Inspection**:
   Run each fixture through the CLI and manually verify the output `DecisionRecord`:
   - Agreement case: `escalation_tier` is `FAST_PATH`, WCS is near 1.0, `decision_method` is `CD2F`.
   - Disagreement case: `escalation_tier` is `SLOW_PATH`, reasoning trail shows weight computation and decision confidence satisfying `slow_path.min_confidence`.
   - Conflicting evidence case: `escalation_tier` is `HUMAN_ESCALATION`, rationale cites critical impact level.
   - Partial bundle case: `escalation_tier` is `HUMAN_ESCALATION`, rationale cites insufficient agent participation below `min_participating_agents`.

2. **ConsensusBundle Traceability Verification**:
   Verify that each `DecisionRecord.consensus_bundle_id` traces to a `ConsensusBundle` whose `source_bundle_id` matches the input `ClaimBundle.bundle_id`. Verify the original `ClaimBundle` is not mutated.

3. **Threshold Sensitivity Verification**:
   Modify `consensus.yaml` thresholds (e.g., lower `fast_path.confidence_threshold` from 0.85 to 0.50) and re-run the disagreement fixture to confirm the escalation tier changes without any code changes.

4. **`slow_path.min_confidence` Behavioral Verification**:
   Set `slow_path.min_confidence` to 0.99 and re-run the disagreement fixture. Verify that the decision escalates to `HUMAN_ESCALATION` (because the winning decision confidence falls below 0.99), confirming `slow_path.min_confidence` is behaviorally active.

5. **Baseline Comparison Spot-Check**:
   Run the same fixture through the CD2F engine, single-agent baseline, and naive majority baseline. Verify the three produce different decisions for the disagreement case and that baseline outputs carry `decision_method = "SINGLE_AGENT"` / `"NAIVE_MAJORITY"` with `is_comparator_only = True`.

6. **Calibration Kappa Spot-Check**:
   Run the calibration module against the hand-labeled calibration set. Verify both `recommendation_kappa` and `escalation_tier_kappa` are reported with pass/fail status against `min_kappa` threshold (0.70).

7. **Outcome Feedback Isolation Verification**:
   Run an arbitration, then verify that the accuracy tracker's state did not change. Then explicitly call `record_outcome()` with `source = "human_adjudication"` and verify the tracker updates. Confirm that arbitration is read-only with respect to accuracy state.
