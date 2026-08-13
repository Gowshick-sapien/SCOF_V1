from typing import Literal, Tuple
from scof_shared.schemas.consensus_bundle import ConsensusBundle
from scof_shared.profile.consensus_config import ConsensusConfig
from services.consensus.src.arbitration import ArbitrationResult

IMPACT_ORDINALS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}

def determine_escalation_tier(
    bundle: ConsensusBundle, 
    arbitration_result: ArbitrationResult, 
    config: ConsensusConfig
) -> Tuple[Literal["FAST_PATH", "SLOW_PATH", "HUMAN_ESCALATION"], str]:

    # 1. Gather metrics
    num_distinct_recs = len(arbitration_result.recommendation_tallies)
    
    min_stated_confidence = 1.0
    max_impact_ordinal = 0
    
    for agent_id, claim in bundle.normalized_claims.items():
        if claim.stated_confidence < min_stated_confidence:
            min_stated_confidence = claim.stated_confidence
            
        impact_ord = IMPACT_ORDINALS[claim.parsed_impact_level]
        if impact_ord > max_impact_ordinal:
            max_impact_ordinal = impact_ord

    wcs = arbitration_result.wcs
    decision_confidence = arbitration_result.decision_confidence
    winner = arbitration_result.winning_recommendation

    # Edge case: No winner due to unresolvable tie
    if winner is None:
        return "HUMAN_ESCALATION", "Unresolved tie-breaker; no unique recommendation could be determined."

    # 2. Check FAST PATH
    fast_path_cfg = config.fast_path
    fp_impact_ord = IMPACT_ORDINALS[fast_path_cfg.max_impact_level]
    
    is_unanimous = (num_distinct_recs == 1)
    fp_conf_ok = (min_stated_confidence >= fast_path_cfg.confidence_threshold)
    fp_impact_ok = (max_impact_ordinal <= fp_impact_ord)
    
    if is_unanimous and fp_conf_ok and fp_impact_ok:
        rationale = f"All criteria met for FAST_PATH: Unanimous agreement, min agent confidence {min_stated_confidence:.2f} >= {fast_path_cfg.confidence_threshold}, max impact ordinal {max_impact_ordinal} <= {fp_impact_ord}."
        return "FAST_PATH", rationale

    # 3. Check HUMAN ESCALATION (override triggers)
    he_cfg = config.human_escalation
    he_impact_ord = IMPACT_ORDINALS[he_cfg.impact_level_trigger]
    sp_cfg = config.slow_path
    
    he_stability_fail = (wcs < he_cfg.consensus_stability_min)
    he_impact_fail = (max_impact_ordinal >= he_impact_ord)
    he_conf_fail = (decision_confidence < sp_cfg.min_confidence)
    
    if he_stability_fail or he_impact_fail or he_conf_fail:
        rationale_parts = []
        if he_stability_fail:
            rationale_parts.append(f"WCS {wcs:.2f} < {he_cfg.consensus_stability_min}")
        if he_impact_fail:
            rationale_parts.append(f"Max impact ordinal {max_impact_ordinal} >= {he_impact_ord}")
        if he_conf_fail:
            rationale_parts.append(f"Decision confidence {decision_confidence:.2f} < {sp_cfg.min_confidence}")
            
        return "HUMAN_ESCALATION", "Triggered by: " + "; ".join(rationale_parts)

    # 4. Check SLOW PATH (fallback if human escalation didn't trigger)
    # At this point, we know WCS >= he_cfg.consensus_stability_min and decision_confidence >= sp_cfg.min_confidence
    sp_impact_ord = IMPACT_ORDINALS[sp_cfg.max_impact_level]
    
    sp_impact_ok = (max_impact_ordinal <= sp_impact_ord)
    
    if sp_impact_ok:
        rationale = f"Criteria met for SLOW_PATH: Decision confidence {decision_confidence:.2f} >= {sp_cfg.min_confidence}, WCS {wcs:.2f} >= {he_cfg.consensus_stability_min}, max impact ordinal {max_impact_ordinal} <= {sp_impact_ord}."
        return "SLOW_PATH", rationale
        
    # If even slow path impact is exceeded (though it should have been caught by human escalation if configured properly, this is a safety net)
    return "HUMAN_ESCALATION", f"Max impact ordinal {max_impact_ordinal} exceeded SLOW_PATH max {sp_impact_ord}."
