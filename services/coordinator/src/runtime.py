"""Coordinator persistent runtime state, discovery lifecycle, and operational metrics."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any, Dict, Optional
from scof_shared.profile.loader import DomainProfile, load_profile
from scof_shared.protocols.a2a_client import A2AClient
from scof_shared.protocols.a2a_registry import A2ARegistry


@dataclass
class CoordinatorMetrics:
    """Coordinator operational telemetry metrics."""

    orchestrations_executed: int = 0
    orchestrations_successful: int = 0
    orchestrations_partial: int = 0
    orchestrations_failed: int = 0
    total_orchestration_latency_ms: float = 0.0
    last_discovery_duration_ms: float = 0.0
    start_time: float = field(default_factory=time.time)

    @property
    def average_latency_ms(self) -> float:
        if self.orchestrations_executed == 0:
            return 0.0
        return round(self.total_orchestration_latency_ms / self.orchestrations_executed, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "orchestrations_executed": self.orchestrations_executed,
            "orchestrations_successful": self.orchestrations_successful,
            "orchestrations_partial": self.orchestrations_partial,
            "orchestrations_failed": self.orchestrations_failed,
            "total_orchestration_latency_ms": round(self.total_orchestration_latency_ms, 2),
            "average_latency_ms": self.average_latency_ms,
            "last_discovery_duration_ms": round(self.last_discovery_duration_ms, 2),
            "uptime_seconds": round(time.time() - self.start_time, 2),
        }


class CoordinatorRuntime:
    """Persistent thread-safe runtime maintaining cached registry and compiled graph."""

    def __init__(
        self,
        profile_path: Path,
        connect_timeout_sec: float = 2.0,
        read_timeout_sec: float = 8.0,
        max_retries: int = 2,
        max_concurrent_dispatch: int = 8,
        mock_mode: bool = False,
    ):
        self.profile_path = profile_path
        self.profile: Optional[DomainProfile] = None
        self.registry: A2ARegistry = A2ARegistry()
        self.a2a_client: A2AClient = A2AClient(
            connect_timeout_sec=connect_timeout_sec,
            read_timeout_sec=read_timeout_sec,
            max_retries=max_retries,
            max_concurrent_dispatch=max_concurrent_dispatch,
            mock_mode=mock_mode,
        )
        self.metrics: CoordinatorMetrics = CoordinatorMetrics()
        self.compiled_graph: Optional[Any] = None
        self.graph_metadata: Dict[str, Any] = {}

    def load_domain_profile(self) -> None:
        """Loads domain profile from path."""
        self.profile = load_profile(self.profile_path)

    def refresh_discovery(self, host_map: Optional[Dict[str, str]] = None) -> int:
        """Discovers agents and performs an atomic copy-on-write swap of the registry."""
        start_time = time.time()
        if not self.profile:
            self.load_domain_profile()

        assert self.profile is not None
        roster = self.profile.agents
        if not roster:
            raise ValueError("Domain profile does not contain an agents roster")

        # Assemble new registry snapshot out-of-band
        new_registry = A2ARegistry()
        discovered = self.a2a_client.discover_roster(roster, host_map=host_map)
        for card, endpoint in discovered:
            new_registry.register(card, endpoint)

        # Atomic copy-on-write reference swap
        self.registry = new_registry
        self.metrics.last_discovery_duration_ms = (time.time() - start_time) * 1000
        return len(new_registry)
