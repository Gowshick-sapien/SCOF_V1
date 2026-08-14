"""Unit tests for CoordinatorOrchestrator LangGraph pipeline."""

import pytest
from scof_shared.protocols.a2a_client import A2AClient
from scof_shared.protocols.a2a_registry import A2ARegistry
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from services.coordinator.src.orchestrator import CoordinatorOrchestrator


@pytest.mark.asyncio
async def test_coordinator_orchestrator_pipeline():
    """Validates end-to-end execution through the LangGraph StateGraph pipeline."""
    registry = A2ARegistry()
    client = A2AClient(mock_mode=True)

    # Register 4 specialist agents
    for name, port in [
        ("demand-agent", 8011),
        ("inventory-agent", 8012),
        ("supplier-agent", 8013),
        ("transport-agent", 8014),
    ]:
        card = AgentCard(
            agent_id=name,
            name=name.replace("-", " ").title(),
            description=f"Specialist agent for {name}",
            version="1.0.0",
            capabilities=["analyze"],
            tags=["specialist"],
            supported_contexts=["all", "baseline_assessment", "demand_spike"],
            endpoint=f"http://localhost:{port}",
        )
        registry.register(card, card.endpoint)

    orchestrator = CoordinatorOrchestrator(
        registry=registry,
        client=client,
        profile_name="mvp-electronics",
        profile_version="1.0.0",
    )

    # Verify graph metadata & hash
    assert len(orchestrator.graph_hash) == 64
    mermaid = orchestrator.get_mermaid_diagram()
    assert "initialize_context" in mermaid
    assert "dispatch_parallel" in mermaid

    meta = orchestrator.get_metadata()
    assert len(meta["nodes"]) == 4
    assert meta["graph_hash"] == orchestrator.graph_hash

    # Execute orchestration
    context = ScenarioContext(
        scenario_id="scen-eval-001",
        run_id="run-eval-01",
        tick=1,
        disruption_type="demand_spike",
        parameters={"spike_factor": 2.5},
    )

    bundle = await orchestrator.orchestrate(context)

    assert bundle.scenario_id == "scen-eval-001"
    assert bundle.status == "COMPLETE"
    assert len(bundle.successful_agents) == 4
    assert "demand-agent" in bundle.claims
    assert "supplier-agent" in bundle.claims
    assert bundle.total_latency_ms >= 0.0
