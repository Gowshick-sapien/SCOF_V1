from typing import Dict, List, Literal, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from scof_shared.schemas.meeting_log import MeetingLogEntry


class AgentWeightBreakdown(BaseModel):
    stated_confidence: float
    historical_accuracy: float
    effective_weight: float

class ReasoningStep(BaseModel):
    step_index: int
    step_type: Literal["CLAIM", "WEIGHT_REPORT", "TALLY", "ESCALATION", "DECISION"]
    content: str
    data: Optional[Dict[str, Any]] = None


class DecisionRecord(BaseModel):
    decision_id: str
    scenario_id: str
    consensus_bundle_id: str
    source_bundle_id: str
    decision_method: Literal["CD2F", "SINGLE_AGENT", "NAIVE_MAJORITY"]
    final_recommendation: Optional[str]
    decision_confidence: float = Field(..., ge=0.0, le=1.0)
    weighted_consensus_stability: float = Field(..., ge=0.0, le=1.0)
    escalation_tier: Literal["FAST_PATH", "SLOW_PATH", "HUMAN_ESCALATION"]
    escalation_rationale: str
    agent_weights: Dict[str, AgentWeightBreakdown]
    recommendation_tallies: Dict[str, float]
    reasoning_trail: List[ReasoningStep]
    meeting_log_entries: List[MeetingLogEntry]
    timestamp: datetime
    profile_name: str
    profile_version: str
    engine_version: str
