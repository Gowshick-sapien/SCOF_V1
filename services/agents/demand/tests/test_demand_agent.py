"""Unit tests for Demand Agent."""

import sys
from pathlib import Path

pkg_root = Path(__file__).resolve().parents[1]
workspace_root = Path(__file__).resolve().parents[4]
if str(workspace_root / "shared") not in sys.path:
    sys.path.insert(0, str(workspace_root / "shared"))
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from scof_shared.schemas.scenario_context import ScenarioContext
from src.agent import DemandAgent
from src.config import SCOF_PROFILE_PATH


def test_demand_agent_analysis():
    agent = DemandAgent(profile_path=SCOF_PROFILE_PATH)
    ctx = ScenarioContext(scenario_id="scen-test-01", run_id="run-01", product_ids=["prod-101"])

    claim = agent.analyze(ctx)

    assert claim.agent_id == "demand-agent"
    assert claim.scenario_id == "scen-test-01"
    assert len(claim.recommendation) > 0
    assert len(claim.reasoning) > 0
    assert 0.0 <= claim.confidence <= 1.0
    assert len(claim.evidence) > 0
    assert claim.evidence[0].reference_id != ""


def test_demand_agent_card():
    agent = DemandAgent(profile_path=SCOF_PROFILE_PATH)
    card = agent.get_agent_card()

    assert card.agent_id == "demand-agent"
    assert card.version == "1.0.0"
    assert "demand_forecasting" in card.capabilities
