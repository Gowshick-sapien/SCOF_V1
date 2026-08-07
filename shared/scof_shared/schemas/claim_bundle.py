"""Claim Bundle schema for SCOF multi-agent orchestration.

Defines the immutable contract aggregating raw structured claims produced by all
participating specialist agents for a given scenario evaluation.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from scof_shared.schemas.structured_claim import StructuredClaim


class ClaimBundle(BaseModel):
    """Immutable collection of structured claims returned by specialist agents."""

    model_config = ConfigDict(frozen=True)

    bundle_id: str = Field(..., description="Unique UUID identifier for this claim bundle")
    scenario_id: str = Field(..., description="Target scenario identifier context")
    trace_id: str = Field(..., description="Distributed correlation trace identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when bundle was assembled",
    )
    profile_name: str = Field(
        "mvp-electronics", description="Name of the active Domain Profile"
    )
    profile_version: str = Field(
        "1.0.0", description="Semantic version of the active Domain Profile"
    )
    status: Literal["COMPLETE", "PARTIAL", "FAILED"] = Field(
        "COMPLETE", description="Overall bundle aggregation status"
    )
    participating_agents: List[str] = Field(
        default_factory=list,
        description="List of agent IDs to which tasks were delegated",
    )
    successful_agents: List[str] = Field(
        default_factory=list,
        description="List of agent IDs that successfully returned valid claims",
    )
    failed_agents: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of agent ID to error description for failed delegations",
    )
    claims: Dict[str, StructuredClaim] = Field(
        default_factory=dict,
        description="Mapping of agent ID to its returned StructuredClaim",
    )
    total_latency_ms: float = Field(
        0.0, description="End-to-end orchestration latency in milliseconds"
    )
    agent_latencies_ms: Dict[str, float] = Field(
        default_factory=dict,
        description="Roundtrip latency in milliseconds for each participating agent",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional orchestration metadata or execution flags",
    )

    def get_claim(self, agent_id: str) -> Optional[StructuredClaim]:
        """Retrieves structured claim for a specific agent if present."""
        return self.claims.get(agent_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize claim bundle to dictionary."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClaimBundle":
        """Deserialize claim bundle from dictionary."""
        return cls(**data)
