"""A2A Registry and Agent Registration tracking for SCOF agent discovery.

Maintains in-memory agent discovery metadata, capabilities matching, and
deterministic operational health-state tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import copy
from typing import Any, Dict, List, Literal, Optional
from scof_shared.schemas.agent_card import AgentCard

HealthStatus = Literal["UNKNOWN", "HEALTHY", "DEGRADED", "UNHEALTHY"]


@dataclass
class AgentRegistration:
    """Registered specialist agent entry with operational health telemetry."""

    card: AgentCard
    endpoint_url: str
    health_status: HealthStatus = "UNKNOWN"
    last_seen: Optional[datetime] = None
    consecutive_failures: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_latency_ms: float = 0.0
    last_error: Optional[str] = None

    @property
    def average_latency_ms(self) -> float:
        """Returns average response latency across successful calls."""
        if self.success_count == 0:
            return 0.0
        return round(self.total_latency_ms / self.success_count, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.card.agent_id,
            "name": self.card.name,
            "endpoint_url": self.endpoint_url,
            "health_status": self.health_status,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "consecutive_failures": self.consecutive_failures,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "average_latency_ms": self.average_latency_ms,
            "last_error": self.last_error,
            "capabilities": self.card.capabilities,
            "supported_contexts": self.card.supported_contexts,
        }


class A2ARegistry:
    """In-memory agent registry supporting dynamic discovery and copy-on-write swaps."""

    def __init__(self, entries: Optional[Dict[str, AgentRegistration]] = None):
        self._entries: Dict[str, AgentRegistration] = entries or {}

    def register(self, card: AgentCard, endpoint_url: str) -> None:
        """Registers or updates an agent in the registry."""
        existing = self._entries.get(card.agent_id)
        if existing:
            existing.card = card
            existing.endpoint_url = endpoint_url
        else:
            self._entries[card.agent_id] = AgentRegistration(
                card=card,
                endpoint_url=endpoint_url,
                health_status="UNKNOWN",
            )

    def unregister(self, agent_id: str) -> bool:
        """Removes an agent from the registry."""
        if agent_id in self._entries:
            del self._entries[agent_id]
            return True
        return False

    def update_health(
        self,
        agent_id: str,
        success: bool,
        latency_ms: float = 0.0,
        error_detail: Optional[str] = None,
    ) -> None:
        """Updates health status and metrics based on invocation outcome.

        Deterministic Health State Transitions:
        - Success: consecutive_failures = 0, health = HEALTHY (or DEGRADED if latency > 5000ms).
        - Failure: consecutive_failures += 1.
          - consecutive_failures in [2, 4] -> DEGRADED
          - consecutive_failures >= 5 -> UNHEALTHY
        """
        entry = self._entries.get(agent_id)
        if not entry:
            return

        now = datetime.now(timezone.utc)
        if success:
            entry.last_seen = now
            entry.consecutive_failures = 0
            entry.success_count += 1
            entry.total_latency_ms += latency_ms
            entry.last_error = None
            if latency_ms > 5000.0:
                entry.health_status = "DEGRADED"
            else:
                entry.health_status = "HEALTHY"
        else:
            entry.consecutive_failures += 1
            entry.failure_count += 1
            entry.last_error = error_detail
            if entry.consecutive_failures >= 5:
                entry.health_status = "UNHEALTHY"
            elif entry.consecutive_failures >= 2:
                entry.health_status = "DEGRADED"

    def get(self, agent_id: str) -> Optional[AgentRegistration]:
        """Returns registration entry by agent ID."""
        return self._entries.get(agent_id)

    def get_card(self, agent_id: str) -> Optional[AgentCard]:
        """Returns AgentCard by agent ID."""
        entry = self._entries.get(agent_id)
        return entry.card if entry else None

    def get_all(self) -> List[AgentRegistration]:
        """Returns all registered agent entries."""
        return list(self._entries.values())

    def get_healthy_cards(self) -> List[AgentCard]:
        """Returns AgentCards for all non-unhealthy registered agents."""
        return [
            entry.card
            for entry in self._entries.values()
            if entry.health_status != "UNHEALTHY"
        ]

    def find_by_capability(self, capability: str) -> List[AgentCard]:
        """Finds active agents declaring a specific capability."""
        return [
            entry.card
            for entry in self._entries.values()
            if capability in entry.card.capabilities and entry.health_status != "UNHEALTHY"
        ]

    def find_by_context(self, disruption_type: str) -> List[AgentCard]:
        """Finds active agents supporting a specific disruption context."""
        matches = [
            entry.card
            for entry in self._entries.values()
            if (
                disruption_type in entry.card.supported_contexts
                or "all" in entry.card.supported_contexts
                or not entry.card.supported_contexts
            )
            and entry.health_status != "UNHEALTHY"
        ]
        return matches

    def clone(self) -> "A2ARegistry":
        """Creates an independent clone for atomic copy-on-write snapshot replacement."""
        cloned_entries = {
            agent_id: copy.deepcopy(reg)
            for agent_id, reg in self._entries.items()
        }
        return A2ARegistry(cloned_entries)

    def __len__(self) -> int:
        return len(self._entries)
