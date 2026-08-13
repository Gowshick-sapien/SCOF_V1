# CD²F Algorithm Design

## 1. Input Normalization (`ConsensusBundle`)
The arbitration engine strictly respects the D05 immutability invariant. The engine receives a `ClaimBundle` and normalizes it into a `ConsensusBundle`.

### 1.1 `impact_mapping`
Instead of hardcoding domain knowledge into the Python engine, impact parsing utilizes a dictionary from the domain profile (`consensus.yaml`):
```yaml
impact_mapping:
  "critical": "CRITICAL"
  "business-critical": "CRITICAL"
  "severe": "HIGH"
  "moderate": "MEDIUM"
  "minor": "LOW"
```

Claims with unparseable impact texts are excluded and logged in `excluded_claims`.

### 1.2 Partial Bundle Handling
If the incoming `ClaimBundle.status` is `"PARTIAL"`, the normalizer checks `len(successful_claims)` against `partial_bundle.min_participating_agents`. If the count is below threshold, arbitration short-circuits to produce a `HUMAN_ESCALATION` decision.

## 2. Confidence-Weighted Arbitration Pipeline

### 2.1 Effective Weight Formula
For each valid, normalized claim, the effective voting power is computed as:
$$ Effective\_Weight = Stated\_Confidence \times Rolling\_Historical\_Accuracy $$

*Note: Historical accuracy is strictly fetched via a read-only query to the Accuracy Tracker. Arbitration NEVER mutates accuracy state.*

### 2.2 Recommendation Grouping
Claims are grouped by exact string match of the `recommendation` field.
The *Weighted Tally* for a group is the sum of the `Effective_Weight` for all agents supporting it.

## 3. Core Metrics

### 3.1 Weighted Consensus Stability (WCS)
WCS is a stability/routing metric measuring the dominance of the winning recommendation:
$$ WCS = \frac{\text{Max\_Weighted\_Tally}}{\text{Sum\_All\_Tallies}} $$
Range: [0.0, 1.0]. A WCS of 1.0 means all participating agents align on the winning recommendation.

### 3.2 Decision Confidence
Decision Confidence is the explicit confidence field exposed to downstream consumers:
$$ Decision\_Confidence = \frac{\sum \text{Effective Weights (Winner)}}{\sum \text{Effective Weights (All)}} $$
*Note: Decision Confidence is numerically identical by design to WCS. They are named distinctly because they serve separate semantic roles (consumer API field vs. internal routing metric).*

## 4. Tie-Breaking Protocol
If multiple recommendation groups tie for the highest weighted tally:
1. **Max Supporter Weight**: For each tied group, find the maximum single-agent `Effective_Weight`. Prefer the group with the highest individual supporter weight.
2. **Max Stated Confidence**: If still tied, find the maximum `Stated_Confidence` among supporters. Prefer the group with the highest individual stated confidence.
3. **Unresolved State**: If deterministic tie-breaking cannot select a unique recommendation, arbitration returns `winner = None` (unresolved state). The engine produces `SLOW_PATH` or `HUMAN_ESCALATION` according to the escalation criteria; no arbitrary recommendation is selected.

## 5. Escalation Tiering
Escalation is purely deterministic and driven entirely by thresholds in `consensus.yaml`.

### 5.1 FAST_PATH
All of the following must be True:
- **Unanimity**: Only one distinct recommendation exists across all participating agents.
- **Confidence**: Minimum agent `Stated_Confidence` $\geq$ `fast_path.confidence_threshold`.
- **Impact**: Maximum ordinal impact $\leq$ `fast_path.max_impact_level`.

### 5.2 SLOW_PATH
If NOT `FAST_PATH`, all of the following must be True:
- **Confidence**: `Decision_Confidence` $\geq$ `slow_path.min_confidence`.
- **Impact**: Maximum ordinal impact $\leq$ `slow_path.max_impact_level`.
- **Stability**: `WCS` $\geq$ `human_escalation.consensus_stability_min`.

### 5.3 HUMAN_ESCALATION
If ANY of the following are True (or if `SLOW_PATH` criteria fail):
- **Stability**: `WCS` $<$ `human_escalation.consensus_stability_min`.
- **Impact**: Maximum ordinal impact $\geq$ `human_escalation.impact_level_trigger`.
- **Confidence**: `Decision_Confidence` $<$ `slow_path.min_confidence`.
- **Ambiguity**: Unresolved tie state (`winner = None`).
- **Partial Bundle**: `len(successful_claims)` $<$ `min_participating_agents`.
