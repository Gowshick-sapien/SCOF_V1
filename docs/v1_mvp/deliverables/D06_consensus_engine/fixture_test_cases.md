# Fixture Test Cases

## Overview
D6 uses hand-worked fixture tests to validate the arbitration engine independently of D5. The automated script `verify_d6.py` runs the CD²F engine against these fixtures and validates the resulting `DecisionRecord` against expected configurations.

## Test Cases

### 1. Agreement Case (`agreement_case.json`)
**Scenario**: All four participating agents agree perfectly.
- **Claims**: 4 claims, all recommending "Re-route to Backup Supplier A".
- **Confidence**: High stated confidence across all agents (~0.90).
- **Impact**: LOW.
- **Expected Outcome**:
  - **Decision Method**: `CD2F`
  - **WCS**: Near 1.0.
  - **Escalation Tier**: `FAST_PATH` (unanimous agreement + high individual confidence + low impact).

### 2. Disagreement Case (`disagreement_case.json`)
**Scenario**: Participating agents are split across two valid recommendations.
- **Claims**:
  - 2 agents recommend "Restock immediately via air freight".
  - 2 agents recommend "Wait for scheduled maritime shipment".
- **Confidence**: Mixed stated confidence (0.60 - 0.85).
- **Impact**: MEDIUM.
- **Expected Outcome**:
  - **Decision Method**: `CD2F`
  - **WCS**: ~0.50 - 0.75.
  - **Escalation Tier**: `SLOW_PATH` (not unanimous, but winning decision confidence $\geq$ `slow_path.min_confidence`).

### 3. Conflicting Evidence Case (`conflicting_evidence_case.json`)
**Scenario**: High-confidence agents actively recommend conflicting courses of action on a severe disruption.
- **Claims**: Direct contradictory recommendations.
- **Confidence**: High stated confidence (>0.85).
- **Impact**: CRITICAL.
- **Expected Outcome**:
  - **Decision Method**: `CD2F`
  - **Escalation Tier**: `HUMAN_ESCALATION` (triggered explicitly by maximum ordinal impact level $\geq$ `CRITICAL`).

### 4. Partial Bundle Case (`partial_bundle_case.json`)
**Scenario**: A `ClaimBundle` fails to meet minimum participation thresholds (e.g. 3 of 4 agents failed upstream).
- **Claims**: 1 valid claim.
- **Bundle Status**: `PARTIAL`.
- **Expected Outcome**:
  - **Decision Method**: `CD2F`
  - **Escalation Tier**: `HUMAN_ESCALATION`
  - **Reasoning**: Fails the `partial_bundle.min_participating_agents` policy check during normalizer initialization.
