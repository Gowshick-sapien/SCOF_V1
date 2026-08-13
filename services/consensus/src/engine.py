import uuid
from datetime import datetime, timezone
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.decision_record import DecisionRecord
from scof_shared.profile.consensus_config import ConsensusConfig
from services.consensus.src.config import ENGINE_VERSION
from services.consensus.src.normalizer import normalize_claim_bundle
from services.consensus.src.arbitration import run_arbitration
from services.consensus.src.escalation import determine_escalation_tier
from services.consensus.src.reasoning_trail import build_reasoning_trail
from services.consensus.src.accuracy_tracker import AccuracyTracker

def run_consensus(bundle: ClaimBundle, config: ConsensusConfig, tracker: AccuracyTracker) -> DecisionRecord:
    # 1. Normalization
    consensus_bundle_or_decision = normalize_claim_bundle(bundle, config)
    if isinstance(consensus_bundle_or_decision, DecisionRecord):
        # Short-circuited (e.g. PARTIAL bundle failed policy)
        return consensus_bundle_or_decision
        
    consensus_bundle = consensus_bundle_or_decision

    # 2. Arbitration
    arbitration_result = run_arbitration(consensus_bundle, tracker)

    # 3. Escalation
    tier, rationale = determine_escalation_tier(consensus_bundle, arbitration_result, config)

    # 4. Reasoning Trail
    trail, meeting_log = build_reasoning_trail(consensus_bundle, arbitration_result, tier, rationale)

    # 5. Output Construction
    decision = DecisionRecord(
        decision_id=str(uuid.uuid4()),
        scenario_id=consensus_bundle.scenario_id,
        consensus_bundle_id=consensus_bundle.consensus_bundle_id,
        source_bundle_id=consensus_bundle.source_bundle_id,
        decision_method="CD2F",
        final_recommendation=arbitration_result.winning_recommendation,
        decision_confidence=arbitration_result.decision_confidence,
        weighted_consensus_stability=arbitration_result.wcs,
        escalation_tier=tier,
        escalation_rationale=rationale,
        agent_weights=arbitration_result.agent_weights,
        recommendation_tallies=arbitration_result.recommendation_tallies,
        reasoning_trail=trail,
        meeting_log_entries=meeting_log,
        timestamp=datetime.now(timezone.utc),
        profile_name=consensus_bundle.profile_name,
        profile_version=consensus_bundle.profile_version,
        engine_version=ENGINE_VERSION
    )
    
    return decision
