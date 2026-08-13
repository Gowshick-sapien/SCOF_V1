# Deliverable D6 — CD²F Consensus Engine

## Objective
Build and validate the Consensus-Driven Collaborative Decision Framework (CD²F) arbitration engine in isolation against fixture data. D6 serves as the research core of SCOF, calculating confidence-weighted decisions from raw multi-agent claims.

---

## Requirements Summary (from SRS)
- **FR-6.1**: Confidence-weighted voting arbitration pipeline (stated confidence × rolling historical accuracy).
- **FR-6.2**: Escalation tiering logic (fast path / slow path / human escalation).
- **FR-6.3**: Judge calibration check against hand-labeled scenario set computing multi-dimensional Cohen's kappa.
- **FR-6.4**: Baseline comparators (single-agent and naive majority voting).
- **FR-6.5**: Outputs: Final Decision + Reasoning Trail + Escalation Tier + WCS.
- **FR-6.6**: Thresholds, impact mapping, and calibration rules configured via Domain Profile (`consensus.yaml`).

---

## Architecture Overview
The CD²F engine operates on an explicitly validated, immutable input contract (`ClaimBundle`) originating from D5. The pipeline follows these primary stages:
1. **Normalization**: `ClaimBundle` → `ConsensusBundle` (adds impact parsing, validates partial bundle policies, and preserves `source_bundle_id`).
2. **Arbitration**: Evaluates claims using `effective_weight = stated_confidence * historical_accuracy`. Computes weighted tallies, decision confidence, and Weighted Consensus Stability (WCS).
3. **Escalation**: Routes the final decision to `FAST_PATH`, `SLOW_PATH`, or `HUMAN_ESCALATION` based strictly on thresholds defined in `consensus.yaml`.
4. **Output**: Generates a `DecisionRecord` containing the final recommendation, reasoning trail, and execution metadata (with `decision_method = CD2F`).

---

## Prerequisites
- **D05 Output Contract**: Immutable `ClaimBundle`.
- **Domain Profile**: `profiles/mvp-electronics/consensus.yaml` (must include `fast_path`, `slow_path`, `human_escalation`, `calibration`, `partial_bundle`, and `impact_mapping`).
- **Calibration Set**: `profiles/mvp-electronics/scenarios/calibration_set.json` (minimum 5 hand-labeled scenarios per tier).

---

## Document Index
1. [Implementation Plan](./implementation_plan.md) — The technical design and execution roadmap.
2. [CD²F Algorithm Design](./cd2f_algorithm_design.md) — Mathematical and algorithmic specification of arbitration and escalation.
3. [Calibration Design](./calibration_design.md) — Multi-dimensional Cohen's kappa calculation methodology.
4. [Baseline Design](./baseline_design.md) — Specifications for the baseline comparators.
5. [Design Decisions](./design_decisions.md) — Architectural justifications and design logs.
6. [Fixture Test Cases](./fixture_test_cases.md) — Hand-worked verification expected outputs.
7. [Acceptance Evidence](./acceptance_evidence.md) — Log of automated testing and acceptance criteria checks.

---

## Standalone Acceptance Criteria ("Definition of Done")
- [ ] Consensus Engine pipeline completely decouples from D5 orchestrator execution.
- [ ] Validates `ConsensusBundle` mapping from immutable `ClaimBundle`s without data leakage.
- [ ] Correctly applies the `stated_confidence * historical_accuracy` weight formula.
- [ ] Behaviorally routes properly to all 3 escalation tiers based on profile config variables (including `slow_path.min_confidence`).
- [ ] Accurate calculation of Weighted Consensus Stability (WCS).
- [ ] Computes multi-dimensional Cohen's kappa correctly against the hand-labeled scenario set.
- [ ] Baseline comparators function properly and produce `EvaluationDecision` with appropriate `decision_method`.
- [ ] Passes all hand-worked test cases covering Agreement, Disagreement, Conflicting Evidence, and Partial Bundles via `verify_d6.py`.
- [ ] `accuracy_tracker` relies exclusively on explicit, out-of-band updates (`record_outcome`) and utilizes atomic JSON writes.
