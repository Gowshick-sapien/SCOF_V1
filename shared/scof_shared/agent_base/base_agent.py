"""Abstract Base Agent for all SCOF specialist agents."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from scof_shared.profile.loader import DomainProfile, ProfileLoader
from scof_shared.profile.agents_config import get_agent_config, AgentConfigModel
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim


class BaseAgent(ABC):
    """Abstract base class defining life cycle and contract for SCOF specialist agents."""

    def __init__(
        self,
        agent_id: str,
        profile_path: Optional[str] = None,
        graph_client: Optional[Any] = None,
        vector_client: Optional[Any] = None,
    ):
        self.agent_id = agent_id
        self.profile: Optional[DomainProfile] = None
        self.config: Optional[AgentConfigModel] = None
        self.graph_client = graph_client
        self.vector_client = vector_client

        if profile_path:
            self.load_profile_config(profile_path)

    def load_profile_config(self, profile_path: str) -> None:
        """Loads domain profile and agent configuration from agents.yaml."""
        self.profile = ProfileLoader.load_profile(profile_path)
        if self.profile and self.profile.agents:
            self.config = get_agent_config(self.profile.agents, self.agent_id)

    @property
    def confidence_floor(self) -> float:
        """Returns configured confidence floor or default 0.50."""
        if self.config:
            return self.config.confidence_floor
        return 0.50

    @abstractmethod
    def get_agent_card(self, endpoint_url: str = "") -> AgentCard:
        """Returns self-describing A2A Agent Card."""
        pass

    @abstractmethod
    def analyze(self, context: ScenarioContext) -> StructuredClaim:
        """Executes agent analysis pipeline and returns StructuredClaim."""
        pass
