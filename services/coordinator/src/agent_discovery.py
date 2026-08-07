"""Agent discovery and target resolution service for the Coordinator."""

import logging
from typing import List
from scof_shared.protocols.a2a_registry import A2ARegistry
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext

logger = logging.getLogger(__name__)


class AgentDiscoveryService:
    """Resolves target agents dynamically using registry capability and context matching."""

    @staticmethod
    def resolve_targets(registry: A2ARegistry, context: ScenarioContext) -> List[AgentCard]:
        """Resolves active specialist agents for a given scenario without concrete agent ID checks."""
        disruption_type = context.disruption_type or "none"

        # Query registry by context match
        matched_cards = registry.find_by_context(disruption_type)

        # In a comprehensive multi-agent supply chain, all healthy specialist agents contribute
        # their domain perspective unless explicitly filtered by capabilities.
        if not matched_cards:
            matched_cards = registry.get_healthy_cards()

        logger.info(
            "Resolved %d target agents for scenario '%s' (disruption_type='%s')",
            len(matched_cards),
            context.scenario_id,
            disruption_type,
        )
        return matched_cards
