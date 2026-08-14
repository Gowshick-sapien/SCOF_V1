"""Unit tests for Scenario and Disruption Event Generator."""

from datetime import date
from pathlib import Path
# type: ignore
from scof_shared.profile.loader import ProfileLoader
# type: ignore
from services.simulation.src.disruption_generator import DisruptionGenerator
# type: ignore
from services.simulation.src.entity_generator import EntityGenerator

PROFILE_PATH = Path("profiles/mvp-electronics")


def test_disruption_generator():
    profile = ProfileLoader.load_profile(PROFILE_PATH)
    entity_gen = EntityGenerator(profile)
    master_entities = entity_gen.generate_all()

    gen = DisruptionGenerator(
        run_id="run-test-001",
        profile=profile,
        master_entities=master_entities,
        random_seed=42,
    )
    result = gen.generate_all(start_date=date(2026, 1, 1), history_days=180)

    scenarios = result["scenarios"]
    disruptions = result["disruption_events"]

    assert len(scenarios) == 2
    assert scenarios[0]["scenario_id"].startswith("scen-")

    assert len(disruptions) > 0
    for d in disruptions:
        assert d["id"].startswith("disrupt-")
        assert 1 <= d["severity"] <= 5
        assert d["run_id"] == "run-test-001"
        assert d["target_entity_type"] in ("supplier", "route", "product")
