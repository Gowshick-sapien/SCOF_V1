"""Claim collection, bounded parallel dispatch, and ClaimBundle construction."""

import time
from typing import Dict, List, Literal, Tuple
from scof_shared.protocols.a2a_client import A2AClient
from scof_shared.protocols.a2a_registry import A2ARegistry
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim


class ClaimCollector:
    """Orchestrates parallel delegation and aggregates claims into immutable ClaimBundle."""

    @staticmethod
    async def dispatch_parallel(
        client: A2AClient,
        registry: A2ARegistry,
        target_cards: List[AgentCard],
        context: ScenarioContext,
        trace_id: str,
        bundle_id: str,
        profile_version: str = "1.0.0",
    ) -> Tuple[Dict[str, StructuredClaim], Dict[str, str], Dict[str, float]]:
        """Dispatches scenario to target agents concurrently and updates registry health."""
        raw_results = await client.delegate_analyze_parallel(
            agent_cards=target_cards,
            context=context,
            trace_id=trace_id,
            bundle_id=bundle_id,
            profile_version=profile_version,
        )

        raw_claims: Dict[str, StructuredClaim] = {}
        failed_agents: Dict[str, str] = {}
        agent_latencies_ms: Dict[str, float] = {}

        for agent_id, (claim, error, latency_ms) in raw_results.items():
            agent_latencies_ms[agent_id] = round(latency_ms, 2)
            if claim is not None:
                raw_claims[agent_id] = claim
                registry.update_health(
                    agent_id=agent_id,
                    success=True,
                    latency_ms=latency_ms,
                )
            else:
                err_msg = error or "Unknown execution failure"
                failed_agents[agent_id] = err_msg
                registry.update_health(
                    agent_id=agent_id,
                    success=False,
                    latency_ms=latency_ms,
                    error_detail=err_msg,
                )

        return raw_claims, failed_agents, agent_latencies_ms

    @staticmethod
    def build_claim_bundle(
        scenario_context: ScenarioContext,
        trace_id: str,
        bundle_id: str,
        profile_name: str,
        profile_version: str,
        target_cards: List[AgentCard],
        raw_claims: Dict[str, StructuredClaim],
        failed_agents: Dict[str, str],
        agent_latencies_ms: Dict[str, float],
        start_time: float,
    ) -> ClaimBundle:
        """Constructs an immutable ClaimBundle from collected outputs."""
        total_latency_ms = round((time.time() - start_time) * 1000, 2)
        participating = [c.agent_id for c in target_cards]
        successful = list(raw_claims.keys())

        if len(successful) == len(participating) and len(participating) > 0:
            status: Literal["COMPLETE", "PARTIAL", "FAILED"] = "COMPLETE"
        elif len(successful) > 0:
            status = "PARTIAL"
        else:
            status = "FAILED"

        return ClaimBundle(
            bundle_id=bundle_id,
            scenario_id=scenario_context.scenario_id,
            trace_id=trace_id,
            profile_name=profile_name,
            profile_version=profile_version,
            status=status,
            participating_agents=participating,
            successful_agents=successful,
            failed_agents=failed_agents,
            claims=raw_claims,
            total_latency_ms=total_latency_ms,
            agent_latencies_ms=agent_latencies_ms,
            metadata={
                "disruption_type": scenario_context.disruption_type,
                "run_id": scenario_context.run_id,
            },
        )
