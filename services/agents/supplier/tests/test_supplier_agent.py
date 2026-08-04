"""Unit tests for Supplier Intelligence Agent."""

from scof_shared.schemas.scenario_context import ScenarioContext
from src.agent import SupplierAgent


def test_supplier_agent_card():
    agent = SupplierAgent()
    card = agent.get_agent_card()

    assert card.agent_id == "supplier-agent"
    assert card.name == "Supplier Intelligence Agent"
    assert "supplier_reliability_scoring" in card.capabilities
    assert "alternate_supplier_recommendation" in card.capabilities
    assert "supplier_delay" in card.supported_contexts


def test_supplier_rank_alternates():
    agent = SupplierAgent()
    alternates = [
        {
            "alt_supplier_id": "sup-01",
            "alt_supplier_name": "Semico Components",
            "alt_lead_time_days": 7,
            "alt_unit_cost": 24.50,
        },
        {
            "alt_supplier_id": "sup-03",
            "alt_supplier_name": "Apex Microdevices",
            "alt_lead_time_days": 5,
            "alt_unit_cost": 26.00,
        },
    ]
    reliabilities = {"sup-01": 0.95, "sup-03": 0.92}
    hops = {"sup-01": 2, "sup-03": 2}

    ranked = agent.rank_alternate_suppliers(alternates, reliabilities, hops)
    assert len(ranked) == 2
    assert "composite_rank_score" in ranked[0]
    assert ranked[0]["composite_rank_score"] >= ranked[1]["composite_rank_score"]


def test_supplier_agent_analyze_baseline():
    agent = SupplierAgent()
    ctx = ScenarioContext(
        scenario_id="scen-baseline",
        run_id="run-001",
        target_entity_type="supplier",
        target_entity_id="sup-01",
        product_ids=["prod-101"],
    )

    claim = agent.analyze(ctx)

    assert claim.agent_id == "supplier-agent"
    assert claim.scenario_id == "scen-baseline"
    assert claim.priority in ["LOW", "MEDIUM"]
    assert 0.0 <= claim.confidence <= 1.0
    assert len(claim.evidence) >= 2
    # Check query hashes in evidence
    for ev in claim.evidence:
        if ev.type in ["graph_query", "historical_data"]:
            assert ev.query_hash is not None and len(ev.query_hash) == 64


def test_supplier_agent_analyze_disruption():
    agent = SupplierAgent()
    ctx = ScenarioContext(
        scenario_id="scen-disruption",
        run_id="run-002",
        target_entity_type="supplier",
        target_entity_id="sup-02",
        disruption_type="supplier_delay",
        severity=4,
        product_ids=["prod-101"],
    )

    claim = agent.analyze(ctx)

    assert claim.agent_id == "supplier-agent"
    assert claim.priority == "HIGH"
    assert "Reroute" in claim.recommendation or "alternate" in claim.recommendation.lower()
    assert "sup-02" in claim.reasoning or "disruption" in claim.reasoning.lower()


def test_supplier_agent_determinism():
    agent = SupplierAgent()
    ctx = ScenarioContext(
        scenario_id="scen-det",
        run_id="run-003",
        target_entity_type="supplier",
        target_entity_id="sup-02",
        disruption_type="supplier_delay",
        severity=3,
        product_ids=["prod-101"],
    )

    claim1 = agent.analyze(ctx)
    claim2 = agent.analyze(ctx)

    assert claim1.confidence == claim2.confidence
    assert claim1.recommendation == claim2.recommendation
    assert claim1.priority == claim2.priority
