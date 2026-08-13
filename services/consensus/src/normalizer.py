import hashlib
import uuid
from datetime import datetime, timezone
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.consensus_bundle import ConsensusBundle, NormalizedClaim
from scof_shared.schemas.decision_record import DecisionRecord
from scof_shared.profile.consensus_config import ConsensusConfig
from services.consensus.src.config import ENGINE_VERSION

def normalize_claim_bundle(bundle: ClaimBundle, config: ConsensusConfig) -> ConsensusBundle | DecisionRecord:
    # Hash the config for reproducibility
    config_fingerprint = hashlib.sha256(config.model_dump_json().encode("utf-8")).hexdigest()
    
    normalized_claims = {}
    excluded_claims = {}
    
    for agent_id, claim in bundle.claims.items():
        if not claim.impact:
            excluded_claims[agent_id] = "Missing impact field"
            continue
            
        impact_key = claim.impact.lower()
        if impact_key not in config.impact_mapping:
            excluded_claims[agent_id] = f"Unparseable impact text: '{claim.impact}' not in impact_mapping"
            continue
            
        parsed_impact_level = config.impact_mapping[impact_key]
        
        normalized_claims[agent_id] = NormalizedClaim(
            agent_id=agent_id,
            recommendation=claim.recommendation,
            stated_confidence=claim.confidence,
            parsed_impact_level=parsed_impact_level,
            priority=claim.priority,
            evidence_count=len(claim.evidence),
            original_impact_text=claim.impact
        )
        
    participating_agents = list(bundle.claims.keys())
    successful_agents = list(normalized_claims.keys())
    
    # Partial Bundle Policy Check
    if bundle.status == "PARTIAL":
        if len(successful_agents) < config.partial_bundle.min_participating_agents:
            # Short-circuit to HUMAN_ESCALATION
            return DecisionRecord(
                decision_id=str(uuid.uuid4()),
                scenario_id=bundle.scenario_id,
                consensus_bundle_id="short-circuited",
                source_bundle_id=bundle.bundle_id,
                decision_method="CD2F",
                final_recommendation=None,
                decision_confidence=0.0,
                weighted_consensus_stability=0.0,
                escalation_tier="HUMAN_ESCALATION",
                escalation_rationale=f"Bundle was PARTIAL and participating agents ({len(successful_agents)}) < min_participating_agents ({config.partial_bundle.min_participating_agents})",
                agent_weights={},
                recommendation_tallies={},
                reasoning_trail=[],
                meeting_log_entries=[],
                timestamp=datetime.now(timezone.utc),
                profile_name=bundle.profile_name,
                profile_version=bundle.profile_version,
                engine_version=ENGINE_VERSION
            )

    return ConsensusBundle(
        consensus_bundle_id=str(uuid.uuid4()),
        source_bundle_id=bundle.bundle_id,
        scenario_id=bundle.scenario_id,
        profile_name=bundle.profile_name,
        profile_version=bundle.profile_version,
        participating_agents=participating_agents,
        successful_agents=successful_agents,
        failed_agents=bundle.failed_agents,
        normalized_claims=normalized_claims,
        excluded_claims=excluded_claims,
        engine_version=ENGINE_VERSION,
        config_fingerprint=config_fingerprint,
        timestamp=datetime.now(timezone.utc)
    )
