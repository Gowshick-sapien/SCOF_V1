import uuid
from datetime import datetime, timezone
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.evaluation_decision import EvaluationDecision
from services.consensus.src.config import ENGINE_VERSION

def run_single_agent_baseline(bundle: ClaimBundle, target_agent_id: str | None = None) -> EvaluationDecision:
    if not bundle.claims:
        raise ValueError("Cannot run baseline on empty ClaimBundle")
        
    if target_agent_id:
        if target_agent_id not in bundle.claims:
            raise ValueError(f"Target agent {target_agent_id} not in ClaimBundle")
        selected_agent = target_agent_id
        selected_claim = bundle.claims[selected_agent]
    else:
        # Default: select agent with highest stated confidence
        selected_agent = None
        max_conf = -1.0
        for agent_id, claim in bundle.claims.items():
            if claim.confidence > max_conf:
                max_conf = claim.confidence
                selected_agent = agent_id
        
        if selected_agent is None:
            raise RuntimeError("Failed to select an agent")

        selected_claim = bundle.claims[selected_agent]

    return EvaluationDecision(
        decision_id=str(uuid.uuid4()),
        scenario_id=bundle.scenario_id,
        consensus_bundle_id="N/A_BASELINE",
        source_bundle_id=bundle.bundle_id,
        decision_method="SINGLE_AGENT",
        final_recommendation=selected_claim.recommendation,
        decision_confidence=selected_claim.confidence,
        weighted_consensus_stability=1.0, # Trivial
        escalation_tier="FAST_PATH",      # Trivial unanimous
        escalation_rationale="Single agent baseline trivially selects FAST_PATH.",
        agent_weights={},
        recommendation_tallies={selected_claim.recommendation: 1.0},
        reasoning_trail=[],
        meeting_log_entries=[],
        timestamp=datetime.now(timezone.utc),
        profile_name=bundle.profile_name,
        profile_version=bundle.profile_version,
        engine_version=ENGINE_VERSION,
        is_comparator_only=True,
        baseline_metadata={"selected_agent_id": selected_agent}
    )
