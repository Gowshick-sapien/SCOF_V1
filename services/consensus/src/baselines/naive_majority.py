import uuid
from datetime import datetime, timezone
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.evaluation_decision import EvaluationDecision
from services.consensus.src.config import ENGINE_VERSION

def run_naive_majority_baseline(bundle: ClaimBundle) -> EvaluationDecision:
    if not bundle.claims:
        raise ValueError("Cannot run baseline on empty ClaimBundle")

    tallies = {}
    for claim in bundle.claims.values():
        rec = claim.recommendation
        tallies[rec] = tallies.get(rec, 0) + 1
        
    max_votes = max(tallies.values())
    tied_recs = [rec for rec, votes in tallies.items() if votes == max_votes]
    
    # Tie-breaking: alphabetical sort to demonstrate naive failure mode
    tied_recs.sort()
    winner = tied_recs[0]
    
    wcs = max_votes / sum(tallies.values())
    
    return EvaluationDecision(
        decision_id=str(uuid.uuid4()),
        scenario_id=bundle.scenario_id,
        consensus_bundle_id="N/A_BASELINE",
        source_bundle_id=bundle.bundle_id,
        decision_method="NAIVE_MAJORITY",
        final_recommendation=winner,
        decision_confidence=wcs,
        weighted_consensus_stability=wcs, 
        escalation_tier="SLOW_PATH", # Trivial illustration of multi-agent voting
        escalation_rationale="Naive majority baseline trivially selects SLOW_PATH for multi-agent.",
        agent_weights={},
        recommendation_tallies={rec: float(v) for rec, v in tallies.items()},
        reasoning_trail=[],
        meeting_log_entries=[],
        timestamp=datetime.now(timezone.utc),
        profile_name=bundle.profile_name,
        profile_version=bundle.profile_version,
        engine_version=ENGINE_VERSION,
        is_comparator_only=True,
        baseline_metadata={"tie_breaker_used": len(tied_recs) > 1}
    )
