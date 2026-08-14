"""Unit and integration tests for TransportAgent."""

from scof_shared.schemas.scenario_context import ScenarioContext
from services.agents.transportation.src.agent import TransportAgent


def test_transport_agent_card():
    agent = TransportAgent()
    card = agent.get_agent_card()

    assert card.agent_id == "transport-agent"
    assert "delay_prediction" in card.capabilities
    assert "port_congestion" in card.supported_contexts
    assert card.output_schema == "StructuredClaim"


def test_transport_rank_alternates():
    agent = TransportAgent()
    alts = [
        {"alt_route_id": "r1", "alt_carrier": "c1", "alt_mode": "ocean", "alt_reliability_rating": 0.85, "alt_transit_time_days": 15.0, "alt_cost": 1200.0, "hop_count": 2},
        {"alt_route_id": "r2", "alt_carrier": "c2", "alt_mode": "air", "alt_reliability_rating": 0.98, "alt_transit_time_days": 2.0, "alt_cost": 3200.0, "hop_count": 1},
        {"alt_route_id": "r3", "alt_carrier": "c3", "alt_mode": "rail", "alt_reliability_rating": 0.92, "alt_transit_time_days": 5.0, "alt_cost": 950.0, "hop_count": 2},
    ]

    ranked = agent.rank_alternate_routes(alts)
    assert len(ranked) == 3
    assert all("composite_rank_score" in r for r in ranked)
    assert ranked[0]["composite_rank_score"] >= ranked[1]["composite_rank_score"]


def test_transport_agent_analyze_baseline():
    agent = TransportAgent()
    ctx = ScenarioContext(
        scenario_id="scen-base",
        run_id="run-001",
        target_entity_type="route",
        target_entity_id="route-sea-01",
    )

    claim = agent.analyze(ctx)

    assert claim.agent_id == "transport-agent"
    assert claim.scenario_id == "scen-base"
    assert claim.priority in ["LOW", "MEDIUM"]
    assert 0.0 <= claim.confidence <= 1.0
    assert len(claim.evidence) >= 2
    for ev in claim.evidence:
        if ev.type in ["historical_data", "graph_query"]:
            assert ev.query_hash is not None and len(ev.query_hash) == 64


def test_transport_agent_analyze_disruption():
    agent = TransportAgent()
    ctx = ScenarioContext(
        scenario_id="scen-disrupt",
        run_id="run-002",
        target_entity_type="route",
        target_entity_id="route-sea-01",
        disruption_type="port_congestion",
        severity=4,
    )

    claim = agent.analyze(ctx)

    assert claim.agent_id == "transport-agent"
    assert claim.scenario_id == "scen-disrupt"
    assert claim.priority in ["HIGH", "MEDIUM"]
    assert "Reroute" in claim.recommendation or "congestion" in claim.reasoning.lower() or "delay" in claim.reasoning.lower()
    assert 0.0 <= claim.confidence <= 1.0


def test_transport_agent_determinism():
    agent1 = TransportAgent()
    agent2 = TransportAgent()

    ctx = ScenarioContext(
        scenario_id="scen-det",
        run_id="run-det",
        target_entity_type="route",
        target_entity_id="route-sea-01",
        disruption_type="weather_delay",
        severity=3,
    )

    claim1 = agent1.analyze(ctx)
    claim2 = agent2.analyze(ctx)

    assert claim1.confidence == claim2.confidence
    assert claim1.priority == claim2.priority
    assert claim1.recommendation == claim2.recommendation
    assert claim1.reasoning == claim2.reasoning
