"""Agent Card schema for SCOF agent discovery and A2A integration.

Represents self-describing metadata published by each agent service.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AgentCard(BaseModel):
    """Agent Card contract for discovery, capabilities declaration, and protocol binding."""

    agent_id: str = Field(..., description="Unique ID of the agent")
    name: str = Field(..., description="Human-readable agent display name")
    description: str = Field(..., description="Detailed functional description of the agent")
    version: str = Field("1.0.0", description="Semantic version string")
    capabilities: List[str] = Field(default_factory=list, description="List of capability names")
    tags: List[str] = Field(default_factory=list, description="Classification tags")
    supported_contexts: List[str] = Field(
        default_factory=list, description="Disruption types this agent processes"
    )
    dependencies: List[str] = Field(
        default_factory=list, description="Services or data stores this agent depends on"
    )
    input_schema: Dict[str, str] = Field(
        default_factory=lambda: {"context": "ScenarioContext"},
        description="Input contract name or schema",
    )
    output_schema: str = Field(
        "StructuredClaim", description="Output contract name produced by agent"
    )
    protocol: str = Field("A2A/1.0", description="Supported protocol standard")
    endpoint: str = Field(..., description="Base HTTP URL for agent service")
