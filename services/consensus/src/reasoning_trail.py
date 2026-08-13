from typing import Tuple, List
from datetime import datetime, timezone
from scof_shared.schemas.consensus_bundle import ConsensusBundle
from scof_shared.schemas.decision_record import ReasoningStep, MeetingLogEntry
from services.consensus.src.arbitration import ArbitrationResult

def build_reasoning_trail(
    bundle: ConsensusBundle,
    arbitration_result: ArbitrationResult,
    escalation_tier: str,
    escalation_rationale: str
) -> Tuple[List[ReasoningStep], List[MeetingLogEntry]]:
    
    reasoning_trail = []
    meeting_log = []
    step_idx = 1
    
    # 1. Claims & Weight Reports
    for agent_id, claim in bundle.normalized_claims.items():
        # Claim step
        reasoning_trail.append(ReasoningStep(
            step_index=step_idx,
            step_type="CLAIM",
            content=f"Agent {agent_id} recommended: '{claim.recommendation}' with confidence {claim.stated_confidence:.2f} and impact '{claim.parsed_impact_level}'.",
            data=claim.model_dump()
        ))
        meeting_log.append(MeetingLogEntry(
            step_index=step_idx,
            speaker=agent_id,
            statement_type="CLAIM",
            content=f"I recommend: '{claim.recommendation}'. My confidence is {claim.stated_confidence:.2f}.",
            timestamp=datetime.now(timezone.utc)
        ))
        step_idx += 1
        
        # Weight step
        weight_info = arbitration_result.agent_weights[agent_id]
        reasoning_trail.append(ReasoningStep(
            step_index=step_idx,
            step_type="WEIGHT_REPORT",
            content=f"Agent {agent_id} effective weight computed as {weight_info.effective_weight:.4f} ({weight_info.stated_confidence:.2f} * {weight_info.historical_accuracy:.4f} history).",
            data=weight_info.model_dump()
        ))
        meeting_log.append(MeetingLogEntry(
            step_index=step_idx,
            speaker="COORDINATOR",
            statement_type="WEIGHT_REPORT",
            content=f"Agent {agent_id}'s vote is weighted at {weight_info.effective_weight:.4f} based on historical accuracy of {weight_info.historical_accuracy:.4f}.",
            timestamp=datetime.now(timezone.utc)
        ))
        step_idx += 1
        
    # 2. Tallies
    for rec, tally in arbitration_result.recommendation_tallies.items():
        reasoning_trail.append(ReasoningStep(
            step_index=step_idx,
            step_type="TALLY",
            content=f"Recommendation '{rec}' received weighted tally of {tally:.4f}.",
            data={"recommendation": rec, "tally": tally}
        ))
        meeting_log.append(MeetingLogEntry(
            step_index=step_idx,
            speaker="COORDINATOR",
            statement_type="TALLY",
            content=f"The tally for '{rec}' is {tally:.4f}.",
            timestamp=datetime.now(timezone.utc)
        ))
        step_idx += 1
        
    # 3. Decision
    reasoning_trail.append(ReasoningStep(
        step_index=step_idx,
        step_type="DECISION",
        content=f"Selected recommendation: '{arbitration_result.winning_recommendation}'. WCS: {arbitration_result.wcs:.4f}. Decision Confidence: {arbitration_result.decision_confidence:.4f}.",
        data={"winner": arbitration_result.winning_recommendation, "wcs": arbitration_result.wcs}
    ))
    meeting_log.append(MeetingLogEntry(
        step_index=step_idx,
        speaker="COORDINATOR",
        statement_type="DECISION",
        content=f"The winning recommendation is '{arbitration_result.winning_recommendation}' with a Weighted Consensus Stability (WCS) of {arbitration_result.wcs:.4f}.",
        timestamp=datetime.now(timezone.utc)
    ))
    step_idx += 1
    
    # 4. Escalation
    reasoning_trail.append(ReasoningStep(
        step_index=step_idx,
        step_type="ESCALATION",
        content=f"Routed to {escalation_tier}: {escalation_rationale}",
        data={"tier": escalation_tier, "rationale": escalation_rationale}
    ))
    meeting_log.append(MeetingLogEntry(
        step_index=step_idx,
        speaker="COORDINATOR",
        statement_type="ESCALATION",
        content=f"Routing decision to {escalation_tier}. Reason: {escalation_rationale}",
        timestamp=datetime.now(timezone.utc)
    ))

    return reasoning_trail, meeting_log
