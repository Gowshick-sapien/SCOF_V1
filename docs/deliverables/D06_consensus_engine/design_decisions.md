# Architectural Design Decisions

## 1. D05 Immutability via `ConsensusBundle`
**Context**: The D05 architecture explicitly declared `ClaimBundle` as a frozen, immutable artifact representing raw network data. However, CD²F requires parsed impact levels and exclusionary policies.
**Decision**: Introduced the `ConsensusBundle` intermediate schema. The normalizer engine converts `ClaimBundle` $\rightarrow$ `ConsensusBundle`, parsing impact maps and handling exclusions, while storing a strict reference (`source_bundle_id`).
**Benefit**: Preserves D05's core architectural invariant while safely structuring data for D06 logic.

## 2. Externalizing `impact_mapping`
**Context**: Escalation routing required parsing text strings like "business-critical" or "moderate" into enum ordinal levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
**Decision**: The mapping logic is entirely externalized to `consensus.yaml`. Python code does no keyword scraping.
**Benefit**: Prevents the consensus engine from accumulating domain-specific knowledge and guarantees clean separation of configuration from execution code.

## 3. Explicit Outcome-Feedback Lifecycle
**Context**: Confidence-weighted voting requires a historical accuracy score for every agent. A closed loop where the CD²F engine automatically updates accuracy based on its own decisions creates an unacceptable self-reinforcing echo chamber.
**Decision**: Arbitration is strictly read-only on the `accuracy_tracker`. Accuracy updates are implemented via an explicit `record_outcome()` API, requiring a verified `source` (e.g. `validated_operational_outcome` or `human_adjudication`).
**Benefit**: Isolates decision generation from accuracy mutation, ensuring accuracy accurately reflects external ground truth.

## 4. Multi-Dimensional Calibration
**Context**: Cohen's kappa can measure inter-rater reliability, but "a decision" in CD²F is a composite of the final recommendation and the escalation tier.
**Decision**: Calibration independently calculates `recommendation_kappa` and `escalation_tier_kappa`. Both must meet the threshold.
**Benefit**: Guarantees the engine doesn't pass calibration by getting the recommendation right but completely failing on escalation logic (or vice versa).

## 5. Renaming to Weighted Consensus Stability (WCS)
**Context**: "Inter-agent agreement" implied a generic democratic measure, but the mathematical formula `max_weighted_tally / sum_all_tallies` actually measures the weighted dominance of the winning recommendation.
**Decision**: Explicitly defined the metric as Weighted Consensus Stability (WCS).
**Benefit**: Prevents misinterpretation of the metric by downstream D10 evaluations.

## 6. Deterministic Baseline Discrimination
**Context**: Single-agent and naive-majority baseline comparators produce outputs shaped identically to CD²F, which could accidentally leak into D9 (AI Meeting Logs) as actual operational routing.
**Decision**: Added `decision_method` discriminant (`CD2F`, `SINGLE_AGENT`, `NAIVE_MAJORITY`). Baselines return a subclassed `EvaluationDecision` with `is_comparator_only = True`.
**Benefit**: Maintains apples-to-apples D10 evaluation shape while architecturally blocking accidental downstream production consumption.
