# Baseline Comparators Design

## Objective
The baseline comparators establish lower bounds for CD²F engine performance evaluation in D10 (Benchmarking). They determine whether complex confidence-weighted multi-agent arbitration meaningfully outperforms simpler architectures.

## Important Semantic Guardrails
Baseline algorithms share the input contract (`ClaimBundle`) with the CD²F engine, but to avoid downstream semantic confusion, they:
- Implement a distinct return type: `EvaluationDecision` (which subclasses or shadows `DecisionRecord`).
- Hardcode the `is_comparator_only = True` flag.
- Set the `decision_method` discriminant explicitly to either `SINGLE_AGENT` or `NAIVE_MAJORITY`.

Baseline outputs *must not* be routed as valid production decisions. Any escalation metadata they produce is purely illustrative.

---

## 1. Single-Agent Baseline
*Research Question: "Does multi-agent collaboration actually add value, or could we just ask the most confident agent?"*

### Mechanics
1. Inspects the `ClaimBundle`.
2. Default behavior: Selects the single agent with the highest `stated_confidence`. (Optionally accepts a targeted `agent_id` for targeted comparisons).
3. Immediately adopts that agent's recommendation.
4. **Escalation**: Trivially set to `FAST_PATH` (as there is only one agent, there is technically unanimous agreement).

## 2. Naive Majority Voting Baseline
*Research Question: "Does historical accuracy and confidence-weighting add value, or is simple democratic voting sufficient?"*

### Mechanics
1. Inspects the `ClaimBundle`.
2. Assigns exactly 1 unweighted vote to every participating agent's recommendation. (Ignores `stated_confidence` and `historical_accuracy`).
3. Groups votes by exact string match.
4. **Tie-breaking**: Deterministic alphabetical sort of the recommendation string. (Intentionally simplistic to demonstrate naive failure modes).
5. **Escalation**: Trivially set to `SLOW_PATH` to denote basic multi-agent compilation.

*Known Failure Mode: Amplifies shared hallucination. If two agents are consistently wrong but agree with each other, naive majority will adopt their error, whereas CD²F will penalize their effective weight over time via the `accuracy_tracker`.*
