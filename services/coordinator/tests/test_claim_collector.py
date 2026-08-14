"""Unit tests for ClaimCollector dispatch and bundle assembly."""

import time
import pytest
from scof_shared.protocols.a2a_client import A2AClient
from scof_shared.protocols.a2a_registry import A2ARegistry
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.evidence import EvidenceItem
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim
from services.coordinator.src.claim_collector import ClaimCollector


@pytest.mark.asyncio
async def test_claim_collector_parallel_mock():
    """Tests bounded parallel dispatch in mock mode."""
    client = A2AClient(mock_mode=True, max_concurrent_dispatch=4)
    registry = A2ARegistry()

    cards = [
        AgentCard(
            agent_id=f"agent-{i}",
            name=f"Agent {i}",
            description="Specialist",
            version="1.0.0",
            capabilities=["test"],
            tags=["mock"],
            supported_contexts=["all"],
            endpoint=f"http://localhost:801{i}",
        )
        for i in range(1, 5)
    ]
    for c in cards:
        registry.register(c, c.endpoint)

    context = ScenarioContext(
        scenario_id="scen-mock-01",
        run_id="run-01",
        tick=5,
        disruption_type="none",
    )

    raw_claims, failed, latencies = await ClaimCollector.dispatch_parallel(
        client=client,
        registry=registry,
        target_cards=cards,
        context=context,
        trace_id="trace-01",
        bundle_id="bundle-01",
    )

    assert len(raw_claims) == 4
    assert len(failed) == 0
    assert len(latencies) == 4

    bundle = ClaimCollector.build_claim_bundle(
        scenario_context=context,
        trace_id="trace-01",
        bundle_id="bundle-01",
        profile_name="mvp-electronics",
        profile_version="1.0.0",
        target_cards=cards,
        raw_claims=raw_claims,
        failed_agents=failed,
        agent_latencies_ms=latencies,
        start_time=time.time() - 0.1,
    )

    assert bundle.status == "COMPLETE"
    assert len(bundle.successful_agents) == 4
    assert bundle.scenario_id == "scen-mock-01"


def test_claim_bundle_partial_status():
    """Tests status resolution when one or more agents fail."""
    context = ScenarioContext(
        scenario_id="scen-02",
        run_id="run-02",
        tick=1,
        disruption_type="supplier_delay",
    )
    cards = [
        AgentCard(
            agent_id="agent-1",
            name="A1",
            description="",
            version="1.0.0",
            capabilities=[],
            tags=[],
            supported_contexts=["all"],
            endpoint="http://localhost:8011",
        ),
        AgentCard(
            agent_id="agent-2",
            name="A2",
            description="",
            version="1.0.0",
            capabilities=[],
            tags=[],
            supported_contexts=["all"],
            endpoint="http://localhost:8012",
        ),
    ]

    mock_claim = StructuredClaim(
        agent_id="agent-1",
        scenario_id="scen-02",
        recommendation="R1",
        reasoning="Reasoning 1",
        confidence=0.9,
        priority="LOW",
        impact="Impact 1",
        evidence=[
            EvidenceItem(
                type="historical_data",
                source="test-source",
                summary="test-summary",
                reference_id="ref:1",
            )
        ],
    )

    # Partial success
    bundle_partial = ClaimCollector.build_claim_bundle(
        scenario_context=context,
        trace_id="t1",
        bundle_id="b1",
        profile_name="test",
        profile_version="1.0.0",
        target_cards=cards,
        raw_claims={"agent-1": mock_claim},
        failed_agents={"agent-2": "Connection timed out"},
        agent_latencies_ms={"agent-1": 50.0, "agent-2": 2000.0},
        start_time=time.time(),
    )
    assert bundle_partial.status == "PARTIAL"
    assert "agent-2" in bundle_partial.failed_agents

    # Complete failure
    bundle_failed = ClaimCollector.build_claim_bundle(
        scenario_context=context,
        trace_id="t2",
        bundle_id="b2",
        profile_name="test",
        profile_version="1.0.0",
        target_cards=cards,
        raw_claims={},
        failed_agents={"agent-1": "500 error", "agent-2": "500 error"},
        agent_latencies_ms={},
        start_time=time.time(),
    )
    assert bundle_failed.status == "FAILED"
