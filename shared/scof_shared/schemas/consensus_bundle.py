from typing import Dict, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field

class NormalizedClaim(BaseModel):
    agent_id: str
    recommendation: str
    stated_confidence: float = Field(..., ge=0.0, le=1.0)
    parsed_impact_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    evidence_count: int
    original_impact_text: str

class ConsensusBundle(BaseModel):
    consensus_bundle_id: str
    source_bundle_id: str
    scenario_id: str
    profile_name: str
    profile_version: str
    participating_agents: List[str]
    successful_agents: List[str]
    failed_agents: Dict[str, str]
    normalized_claims: Dict[str, NormalizedClaim]
    excluded_claims: Dict[str, str]
    engine_version: str
    config_fingerprint: str
    timestamp: datetime
