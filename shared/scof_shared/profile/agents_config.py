"""Profile Agent Roster configuration models and loader helper."""

from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml
from pydantic import BaseModel, Field


class AgentConfigModel(BaseModel):
    """Configuration model for a single agent from agents.yaml."""

    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent display name")
    port: int = Field(..., description="HTTP server port")
    confidence_floor: float = Field(0.50, description="Minimum acceptable confidence threshold")
    ensemble_weights: Optional[Dict[str, float]] = Field(
        None, description="Weights assigned to ensemble sub-models"
    )
    forecast_horizon_days: Optional[int] = Field(
        14, description="Forecast horizon window in days"
    )
    mcp_tools: Optional[List[str]] = Field(
        default_factory=list, description="List of MCP tool names declared by agent"
    )


class AgentsRosterModel(BaseModel):
    """Container for active agents roster."""

    active_agents: List[AgentConfigModel]


def load_agents_config(profile_path: Union[str, Path]) -> AgentsRosterModel:
    """Loads agents.yaml from the given profile directory."""
    path = Path(profile_path)
    agents_file = path / "agents.yaml"
    if not agents_file.exists():
        raise FileNotFoundError(f"agents.yaml not found at {agents_file}")

    with open(agents_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return AgentsRosterModel(**data)


def get_agent_config(
    roster: AgentsRosterModel, agent_id: str
) -> Optional[AgentConfigModel]:
    """Finds an agent configuration by ID within a roster."""
    for agent in roster.active_agents:
        if agent.id == agent_id:
            return agent
    return None
