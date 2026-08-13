from typing import Dict, List, Optional
from pydantic import BaseModel
from scof_shared.schemas.consensus_bundle import ConsensusBundle
from scof_shared.schemas.decision_record import AgentWeightBreakdown
from services.consensus.src.accuracy_tracker import AccuracyTracker

class ArbitrationResult(BaseModel):
    winning_recommendation: Optional[str]
    decision_confidence: float
    wcs: float
    agent_weights: Dict[str, AgentWeightBreakdown]
    recommendation_tallies: Dict[str, float]

def run_arbitration(bundle: ConsensusBundle, tracker: AccuracyTracker) -> ArbitrationResult:
    agent_weights = {}
    recommendation_tallies = {}
    
    # 1. Compute effective weights
    for agent_id, claim in bundle.normalized_claims.items():
        hist_acc = tracker.get_accuracy(agent_id)
        effective_weight = claim.stated_confidence * hist_acc
        
        agent_weights[agent_id] = AgentWeightBreakdown(
            stated_confidence=claim.stated_confidence,
            historical_accuracy=hist_acc,
            effective_weight=effective_weight
        )
        
        # Aggregate tallies
        rec = claim.recommendation
        if rec not in recommendation_tallies:
            recommendation_tallies[rec] = 0.0
        recommendation_tallies[rec] += effective_weight

    sum_all_tallies = sum(recommendation_tallies.values())
    if sum_all_tallies == 0:
        return ArbitrationResult(
            winning_recommendation=None,
            decision_confidence=0.0,
            wcs=0.0,
            agent_weights=agent_weights,
            recommendation_tallies={}
        )

    # 2. Find max weighted tally (WCS computation)
    max_weighted_tally = max(recommendation_tallies.values())
    wcs = max_weighted_tally / sum_all_tallies

    # 3. Tie-breaking protocol
    tied_recs = [rec for rec, tally in recommendation_tallies.items() if abs(tally - max_weighted_tally) < 1e-9]
    
    if len(tied_recs) == 1:
        winner = tied_recs[0]
    else:
        # Tie-break level A: max effective weight among supporting agents
        max_supporter_weight = {rec: 0.0 for rec in tied_recs}
        max_stated_conf = {rec: 0.0 for rec in tied_recs}
        
        for agent_id, claim in bundle.normalized_claims.items():
            rec = claim.recommendation
            if rec in tied_recs:
                weight = agent_weights[agent_id].effective_weight
                stated_conf = claim.stated_confidence
                if weight > max_supporter_weight[rec]:
                    max_supporter_weight[rec] = weight
                if stated_conf > max_stated_conf[rec]:
                    max_stated_conf[rec] = stated_conf

        # Find recs with highest max supporter weight
        highest_supporter_w = max(max_supporter_weight.values())
        tied_a = [rec for rec, w in max_supporter_weight.items() if abs(w - highest_supporter_w) < 1e-9]
        
        if len(tied_a) == 1:
            winner = tied_a[0]
        else:
            # Tie-break level B: max stated confidence
            highest_stated_c = max(max_stated_conf[rec] for rec in tied_a)
            tied_b = [rec for rec in tied_a if abs(max_stated_conf[rec] - highest_stated_c) < 1e-9]
            
            if len(tied_b) == 1:
                winner = tied_b[0]
            else:
                # Level C: Unresolved state
                winner = None

    # Decision Confidence is mathematically identical to WCS if a winner exists
    decision_confidence = wcs if winner is not None else 0.0

    return ArbitrationResult(
        winning_recommendation=winner,
        decision_confidence=decision_confidence,
        wcs=wcs,
        agent_weights=agent_weights,
        recommendation_tallies=recommendation_tallies
    )
