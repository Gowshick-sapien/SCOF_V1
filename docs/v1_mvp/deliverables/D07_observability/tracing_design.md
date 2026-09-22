# Lineage Tracing Design

## Objective
Ensure that every agent turn and consensus decision is fully inspectable via LangSmith, and that this observability layer shares the same correlation identifiers as the runtime execution.

## 1. LangSmith Integration
LangSmith is chosen as the observability backend due to its native integration with LangGraph (used in D5).
- **Placement**: Tracing configuration and callback injection occur explicitly within the D5 Orchestrator (`services/coordinator/src/orchestrator.py`), not inside the isolated D6 engine.
- **Granular Spans**: The `StateGraph` nodes are tagged to differentiate claim collection, normalization, arbitration, and escalation.

## 2. Correlation Tagging
The `X-` correlation headers introduced in D5's A2A protocol dictate the tags applied to the LangSmith runs. This ensures the observability lineage exactly matches the execution lineage:
- `trace_id`
- `scenario_id`
- `bundle_id` (The D5 immutable `ClaimBundle` ID)
- `consensus_bundle_id` (The D6 derived bundle ID)
- `decision_id`
- `profile_version`

## 3. End-to-End Verification
The acceptance criteria for D7 observability is not merely HTTP CRUD success. The `verify_d7.py` script validates the lineage end-to-end:
`D5 LangGraph → D6 CD²F → D7 Observability → LangSmith Trace`

It asserts that a single execution produces a traceable record whose `scenario_id`, `bundle_id`, and `decision_id` remain intact across the entire provenance chain.
