"""State definitions for LangGraph multi-agent orchestration."""

from typing import Dict, List, Optional, TypedDict
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim


class CoordinatorExecutionState(TypedDict):
    """Ephemeral state schema passed through LangGraph nodes for a single orchestration run."""

    scenario_context: ScenarioContext
    trace_id: str
    bundle_id: str
    profile_name: str
    profile_version: str

    target_agent_cards: List[AgentCard]

    raw_claims: Dict[str, StructuredClaim]
    failed_agents: Dict[str, str]
    agent_latencies_ms: Dict[str, float]

    claim_bundle: Optional[ClaimBundle]

    execution_log: List[str]
    status: str
    start_time: float
    end_time: float
