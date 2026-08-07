"""A2A HTTP Client for dynamic agent discovery, bounded parallel delegation, and retries."""

import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple
import httpx
from scof_shared.profile.agents_config import AgentsRosterModel
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.evidence import EvidenceItem
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim


class A2AClient:
    """Client for discovering and communicating with specialist agents over A2A protocol."""

    def __init__(
        self,
        connect_timeout_sec: float = 2.0,
        read_timeout_sec: float = 8.0,
        max_retries: int = 2,
        max_concurrent_dispatch: int = 8,
        mock_mode: bool = False,
    ):
        self.connect_timeout_sec = connect_timeout_sec
        self.read_timeout_sec = read_timeout_sec
        self.max_retries = max_retries
        self.max_concurrent_dispatch = max_concurrent_dispatch
        self.mock_mode = mock_mode

    def _get_timeout(self) -> httpx.Timeout:
        return httpx.Timeout(
            connect=self.connect_timeout_sec,
            read=self.read_timeout_sec,
            write=self.read_timeout_sec,
            pool=self.connect_timeout_sec,
        )

    def discover_agent(self, endpoint_url: str) -> Optional[AgentCard]:
        """Synchronously discovers an agent by querying its .well-known/agent.json endpoint."""
        if self.mock_mode:
            return self._generate_mock_agent_card(endpoint_url)

        url = f"{endpoint_url.rstrip('/')}/.well-known/agent.json"
        try:
            with httpx.Client(timeout=self._get_timeout()) as client:
                response = client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    # Ensure endpoint is recorded accurately
                    if not data.get("endpoint"):
                        data["endpoint"] = endpoint_url
                    return AgentCard(**data)
        except Exception:
            return None
        return None

    async def discover_agent_async(self, endpoint_url: str) -> Optional[AgentCard]:
        """Asynchronously discovers an agent by querying its .well-known/agent.json endpoint."""
        if self.mock_mode:
            return self._generate_mock_agent_card(endpoint_url)

        url = f"{endpoint_url.rstrip('/')}/.well-known/agent.json"
        try:
            async with httpx.AsyncClient(timeout=self._get_timeout()) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if not data.get("endpoint"):
                        data["endpoint"] = endpoint_url
                    return AgentCard(**data)
        except Exception:
            return None
        return None

    def discover_roster(
        self,
        roster: AgentsRosterModel,
        host_map: Optional[Dict[str, str]] = None,
    ) -> List[Tuple[AgentCard, str]]:
        """Discovers all active agents defined in the profile roster."""
        host_map = host_map or {}
        discovered: List[Tuple[AgentCard, str]] = []

        for agent_cfg in roster.active_agents:
            host = host_map.get(agent_cfg.id, "localhost")
            endpoint = f"http://{host}:{agent_cfg.port}"
            if self.mock_mode:
                card = self._create_card_from_config(agent_cfg, endpoint)
                discovered.append((card, endpoint))
            else:
                card = self.discover_agent(endpoint)
                if card:
                    discovered.append((card, endpoint))


        return discovered

    async def delegate_analyze(
        self,
        agent_card: AgentCard,
        context: ScenarioContext,
        trace_id: str,
        bundle_id: str,
        profile_version: str = "1.0.0",
    ) -> Tuple[Optional[StructuredClaim], Optional[str], float]:
        """Delegates a scenario analysis to an agent with retries and timeout handling."""
        start_time = time.time()
        agent_id = agent_card.agent_id

        if self.mock_mode:
            await asyncio.sleep(0.01)  # Simulate brief asynchronous latency
            latency = (time.time() - start_time) * 1000
            claim = self._generate_mock_claim(agent_card, context)
            return claim, None, latency

        endpoint = agent_card.endpoint.rstrip("/")
        url = f"{endpoint}/analyze"
        headers = {
            "Content-Type": "application/json",
            "X-Scenario-ID": context.scenario_id,
            "X-Bundle-ID": bundle_id,
            "X-Trace-ID": trace_id,
            "X-Profile-Version": profile_version,
            "X-Agent-ID": agent_id,
        }
        payload = context.to_dict()

        last_error: Optional[str] = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self._get_timeout()) as client:
                    response = await client.post(url, json=payload, headers=headers)

                    # 4xx client errors should not be retried
                    if 400 <= response.status_code < 500:
                        latency = (time.time() - start_time) * 1000
                        return (
                            None,
                            f"HTTP {response.status_code}: {response.text}",
                            latency,
                        )

                    if response.status_code == 200:
                        claim_data = response.json()
                        claim = StructuredClaim(**claim_data)
                        latency = (time.time() - start_time) * 1000
                        return claim, None, latency

                    # 5xx server error
                    last_error = f"HTTP {response.status_code}: {response.text}"

            except httpx.TimeoutException as e:
                last_error = f"Timeout error: {str(e)}"
            except Exception as e:
                last_error = f"Network error: {str(e)}"

            if attempt < self.max_retries:
                # Exponential backoff
                await asyncio.sleep(0.2 * (2**attempt))

        latency = (time.time() - start_time) * 1000
        return None, last_error or "Unknown failure", latency

    async def delegate_analyze_parallel(
        self,
        agent_cards: List[AgentCard],
        context: ScenarioContext,
        trace_id: str,
        bundle_id: str,
        profile_version: str = "1.0.0",
    ) -> Dict[str, Tuple[Optional[StructuredClaim], Optional[str], float]]:
        """Delegates analysis to multiple agents in parallel with bounded concurrency."""
        semaphore = asyncio.Semaphore(self.max_concurrent_dispatch)

        async def _bounded_call(card: AgentCard):
            async with semaphore:
                return card.agent_id, await self.delegate_analyze(
                    card, context, trace_id, bundle_id, profile_version
                )

        tasks = [_bounded_call(card) for card in agent_cards]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return {agent_id: res for agent_id, res in results}

    def _generate_mock_agent_card(self, endpoint_url: str) -> AgentCard:
        """Generates fallback synthetic AgentCard for mock testing."""
        return AgentCard(
            agent_id="mock-agent",
            name="Mock Specialist Agent",
            description="Synthetic mock agent for offline testing",
            version="1.0.0",
            capabilities=["mock_capability"],
            tags=["mock"],
            supported_contexts=["baseline_assessment", "supplier_delay", "demand_spike"],
            endpoint=endpoint_url,
        )

    def _create_card_from_config(self, agent_cfg: Any, endpoint_url: str) -> AgentCard:
        return AgentCard(
            agent_id=agent_cfg.id,
            name=agent_cfg.name,
            description=f"Automated service for {agent_cfg.name}",
            version="1.0.0",
            capabilities=[tool for tool in (agent_cfg.mcp_tools or [])],
            tags=["specialist"],
            supported_contexts=["baseline_assessment", "supplier_delay", "transport_failure", "demand_spike"],
            endpoint=endpoint_url,
        )

    def _generate_mock_claim(
        self, agent_card: AgentCard, context: ScenarioContext
    ) -> StructuredClaim:
        """Generates realistic synthetic StructuredClaim for mock testing."""
        is_disruption = context.disruption_type != "none"
        priority = "HIGH" if is_disruption else "LOW"
        confidence = 0.88 if is_disruption else 0.95

        return StructuredClaim(
            agent_id=agent_card.agent_id,
            scenario_id=context.scenario_id,
            recommendation=f"Operational recommendation from {agent_card.name} for context {context.disruption_type}.",
            reasoning=f"Analyzed simulation run {context.run_id} under disruption type {context.disruption_type}.",
            confidence=confidence,
            low_confidence=False,
            priority=priority,
            impact=f"Estimated operational impact assessed by {agent_card.agent_id}.",
            evidence=[
                EvidenceItem(
                    type="historical_data",
                    source=f"{agent_card.name} telemetry stream",
                    summary=f"Analyzed simulation run {context.run_id} under disruption {context.disruption_type}",
                    reference_id=f"scenario:{context.scenario_id}",
                    query_hash="a" * 64,
                )
            ],
        )

