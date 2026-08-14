"""Unit tests for AgentDiscoveryService and A2ARegistry."""

from scof_shared.protocols.a2a_registry import A2ARegistry, HealthStatus
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from services.coordinator.src.agent_discovery import AgentDiscoveryService


def test_agent_discovery_context_matching():
    """Tests dynamic discovery and context matching without concrete agent ID checks."""
    registry = A2ARegistry()

    card1 = AgentCard(
        agent_id="demand-agent",
        name="Demand Agent",
        description="Forecasts demand",
        version="1.0.0",
        capabilities=["read_historical_demand"],
        tags=["demand"],
        supported_contexts=["demand_spike", "baseline_assessment"],
        endpoint="http://localhost:8011",
    )
    card2 = AgentCard(
        agent_id="supplier-agent",
        name="Supplier Intelligence Agent",
        description="Supplier risk",
        version="1.0.0",
        capabilities=["query_supplier_graph"],
        tags=["supplier"],
        supported_contexts=["supplier_delay", "baseline_assessment"],
        endpoint="http://localhost:8013",
    )

    registry.register(card1, "http://localhost:8011")
    registry.register(card2, "http://localhost:8013")

    # Scenario matching specific disruption
    ctx_supplier = ScenarioContext(
        scenario_id="scen-sup-01",
        run_id="run-01",
        tick=1,
        disruption_type="supplier_delay",
    )
    targets = AgentDiscoveryService.resolve_targets(registry, ctx_supplier)
    assert len(targets) == 1
    assert targets[0].agent_id == "supplier-agent"

    # Baseline scenario matches all healthy agents
    ctx_baseline = ScenarioContext(
        scenario_id="scen-base-01",
        run_id="run-01",
        tick=1,
        disruption_type="baseline_assessment",
    )
    targets_all = AgentDiscoveryService.resolve_targets(registry, ctx_baseline)
    assert len(targets_all) == 2


def test_health_state_transitions():
    """Tests health state threshold progression: HEALTHY -> DEGRADED -> UNHEALTHY."""
    registry = A2ARegistry()
    card = AgentCard(
        agent_id="test-agent",
        name="Test Agent",
        description="Test",
        version="1.0.0",
        capabilities=[],
        tags=[],
        supported_contexts=["all"],
        endpoint="http://localhost:8099",
    )
    registry.register(card, "http://localhost:8099")

    # Initial state should be UNKNOWN
    reg = registry.get("test-agent")
    assert reg is not None
    assert reg.health_status == "UNKNOWN"

    # Successful call -> HEALTHY
    registry.update_health("test-agent", success=True, latency_ms=150.0)
    assert reg.health_status == "HEALTHY"
    assert reg.average_latency_ms == 150.0

    # 1 failure -> still HEALTHY (threshold is 2)
    registry.update_health("test-agent", success=False, error_detail="503 timeout")
    assert reg.health_status == "HEALTHY"
    assert reg.consecutive_failures == 1

    # 2 consecutive failures -> DEGRADED
    registry.update_health("test-agent", success=False, error_detail="503 timeout")
    assert reg.health_status == "DEGRADED"
    assert reg.consecutive_failures == 2

    # 5 consecutive failures -> UNHEALTHY
    for _ in range(3):
        registry.update_health("test-agent", success=False, error_detail="500 crash")
    assert reg.health_status == "UNHEALTHY"
    assert reg.consecutive_failures == 5

    # Successful recovery -> immediately HEALTHY
    registry.update_health("test-agent", success=True, latency_ms=80.0)
    assert reg.health_status == "HEALTHY"
    assert reg.consecutive_failures == 0

