# Calibration Design

## Objective
The calibration module ensures that the CD²F engine produces reliable and acceptable decisions when compared against human ground-truth labels. It uses multi-dimensional Cohen's kappa to quantify inter-rater agreement.

## Scenario Dataset
The engine is calibrated against a dataset stored in `profiles/mvp-electronics/scenarios/calibration_set.json`.
- The dataset must contain a minimum of 15-25 hand-labeled scenarios.
- Must ensure distribution across all three escalation tiers (minimum 5 per tier) to prevent undefined kappa edge cases.

Each item contains a synthetic `ClaimBundle` and a `ground_truth` object:
```json
"ground_truth": {
    "expected_recommendation": "Switch to backup supplier",
    "expected_escalation_tier": "SLOW_PATH",
    "reasoning": "Moderate confidence with split recommendations warrants slow path."
}
```

## Multi-Dimensional Kappa
We compute Cohen's kappa independently over two distinct dimensions of the engine's output:
1. **Recommendation Kappa (`recommendation_kappa`)**: Evaluates the agreement between the engine's `final_recommendation` and `expected_recommendation`.
2. **Escalation Tier Kappa (`escalation_tier_kappa`)**: Evaluates the agreement between the engine's `escalation_tier` and `expected_escalation_tier`.

## Evaluation Criteria
- **Threshold**: Both `recommendation_kappa` and `escalation_tier_kappa` must individually meet or exceed the `min_kappa` threshold specified in `consensus.yaml` (typically `0.70`).
- **Exact Match Rate**: The fraction of scenarios where *both* the recommendation and escalation tier match ground truth simultaneously. Provided as an additional sanity metric.

## Edge Case Handling
1. **Single-class samples**: If the calibration set or engine predictions contain only one class (e.g. all `FAST_PATH`), kappa is technically undefined. The module will report kappa as undefined with a warning, but will *not* fail the build if Exact Match Rate is 100%.
2. **Category absent from sample**: If a specific category (e.g. `HUMAN_ESCALATION`) is entirely absent, the module logs a per-category confusion breakdown with zero-count categories noted.
3. **Insufficient Set Size**: If the calibration set contains fewer than 5 scenarios, the module produces a warning that the calibration is statistically unreliable.

## Isolation Principle
The calibration engine evaluates historical accuracy but *never mutates production accuracy data*.
Outcome updates resulting from calibration use the explicit source `calibration_ground_truth`. This prevents the automated calibration loops from polluting the production performance history of live operational agents.
