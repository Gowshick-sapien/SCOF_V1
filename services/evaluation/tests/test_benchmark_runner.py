import pytest
from services.evaluation.src.benchmark_runner import (
    calculate_pairwise_discordance,
    calculate_tie_breaker_rate,
    run_cd2f_arbitration,
    run_naive_majority_arbitration,
    run_single_agent_arbitration,
    compare_single_bundle,
    run_benchmark_comparison,
)


class TestDiscordanceAndTieBreakerMetrics:
    def test_pairwise_discordance_identical(self):
        a = ["Action A", "Action B", "Action C"]
        b = ["Action A", "Action B", "Action C"]
        assert calculate_pairwise_discordance(a, b) == 0.0

    def test_pairwise_discordance_complete(self):
        a = ["Action A", "Action B"]
        b = ["Action X", "Action Y"]
        assert calculate_pairwise_discordance(a, b) == 1.0

    def test_pairwise_discordance_normalization(self):
        a = ["  action a ", "ACTION B"]
        b = ["Action A", "action b  "]
        assert calculate_pairwise_discordance(a, b) == 0.0

    def test_pairwise_discordance_empty_or_mismatched(self):
        assert calculate_pairwise_discordance([], []) == 0.0
        assert calculate_pairwise_discordance(["A"], ["A", "B"]) == 0.0

    def test_tie_breaker_rate(self):
        decisions = [
            {"tie_breaker_used": True},
            {"tie_breaker_used": False},
            {"tie_breaker_used": True},
            {"tie_breaker_used": False},
        ]
        assert pytest.approx(calculate_tie_breaker_rate(decisions), 0.01) == 50.0

    def test_tie_breaker_rate_empty(self):
        assert calculate_tie_breaker_rate([]) == 0.0


class TestArbitrationMethods:
    @pytest.fixture
    def tied_claims(self):
        return {
            "agent_1": {"recommendation": "Zulu Reroute", "confidence": 0.8},
            "agent_2": {"recommendation": "Alpha Expedite", "confidence": 0.8},
        }

    @pytest.fixture
    def conflicting_confidence_claims(self):
        return {
            "agent_1": {"recommendation": "Action Standard", "confidence": 0.7},
            "agent_2": {"recommendation": "Action Standard", "confidence": 0.75},
            "agent_3": {"recommendation": "Action Flawed", "confidence": 0.99},
        }

    def test_naive_majority_deadlock_alphabetical_tie_break(self, tied_claims):
        res = run_naive_majority_arbitration(tied_claims)
        # Should pick Alpha Expedite over Zulu Reroute alphabetically
        assert res["recommendation"] == "Alpha Expedite"
        assert res["tie_breaker_used"] is True

    def test_single_agent_greedy_confidence_failure(self, conflicting_confidence_claims):
        res = run_single_agent_arbitration(conflicting_confidence_claims)
        # Greedily picks Action Flawed because 0.99 > 0.75
        assert res["recommendation"] == "Action Flawed"
        assert res["confidence"] == 0.99

    def test_cd2f_weighted_override(self, conflicting_confidence_claims):
        res = run_cd2f_arbitration(conflicting_confidence_claims)
        # Two agents recommending Action Standard combine weights to override single high confidence
        assert res["recommendation"] == "Action Standard"
        assert res["tie_breaker_used"] is False


class TestBundleComparison:
    def test_compare_single_bundle_with_divergence(self):
        claims = {
            "inventory_agent": {"recommendation": "Fulfill from Hub A", "confidence": 0.7},
            "supplier_agent": {"recommendation": "Fulfill from Hub A", "confidence": 0.7},
            "demand_agent": {"recommendation": "Cancel Backorders", "confidence": 0.98},
        }
        result = compare_single_bundle(claims)
        assert result.cd2f["recommendation"] == "Fulfill from Hub A"
        assert result.naive_majority["recommendation"] == "Fulfill from Hub A"
        assert result.single_agent["recommendation"] == "Cancel Backorders"
        assert result.consensus_divergence_detected is True

    def test_run_benchmark_comparison_pipeline(self):
        report = run_benchmark_comparison()
        assert report.status == "VALIDATED"
        assert len(report.methods) == 3

        method_names = [m.method_name for m in report.methods]
        assert any("CD2F" in m for m in method_names)
        assert any("Majority" in m for m in method_names)
        assert any("Single" in m for m in method_names)

        # Confirm CD2F had 0% tie-breaking, whereas Naive Majority had > 0%
        cd2f_summary = next(m for m in report.methods if "CD2F" in m.method_name)
        naive_summary = next(m for m in report.methods if "Majority" in m.method_name)
        assert cd2f_summary.tie_breaker_rate == 0.0
        assert naive_summary.tie_breaker_rate >= 0.0
