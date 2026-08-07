"""Unit tests for Coordinator execution state and ClaimBundle immutability."""

import pytest
from pydantic import ValidationError
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.evidence import EvidenceItem
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim


def test_claim_bundle_immutability():
    """Validates that ClaimBundle is frozen and cannot be mutated after creation."""
    context = ScenarioContext(
        scenario_id="scen-001",
        run_id="run-001",
        tick=10,
        disruption_type="none",
        parameters={},
    )
    claim = StructuredClaim(
        agent_id="demand-agent",
        scenario_id="scen-001",
        recommendation="Maintain safety stock.",
        reasoning="Normal demand forecast.",
        confidence=0.9,
        priority="LOW",
        impact="Low impact.",
        evidence=[
            EvidenceItem(
                type="historical_data",
                source="Historical Demand Service",
                summary="Demand is within normal bounds",
                reference_id="product:prod-001",
                query_hash="a" * 64,
            )
        ],
    )

    bundle = ClaimBundle(
        bundle_id="bundle-001",
        scenario_id="scen-001",
        trace_id="trace-001",
        profile_name="mvp-electronics",
        profile_version="1.0.0",
        status="COMPLETE",
        participating_agents=["demand-agent"],
        successful_agents=["demand-agent"],
        failed_agents={},
        claims={"demand-agent": claim},
        total_latency_ms=120.5,
        agent_latencies_ms={"demand-agent": 120.5},
    )

    assert bundle.bundle_id == "bundle-001"
    assert bundle.status == "COMPLETE"
    assert "demand-agent" in bundle.claims

    # Attempt mutation should raise ValidationError (frozen model)
    with pytest.raises(ValidationError):
        bundle.status = "FAILED"

    with pytest.raises(ValidationError):
        bundle.profile_version = "2.0.0"
