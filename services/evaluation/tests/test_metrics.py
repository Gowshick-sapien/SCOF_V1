import pytest
from services.evaluation.src.metrics import (
    calculate_decision_accuracy,
    calculate_wcs_stability,
    calculate_agreement_rate,
    calculate_cohens_kappa,
    calculate_latency_percentiles,
    calculate_stockout_risk_reduction,
    calculate_fill_rate_delta,
)


class TestDecisionAccuracy:
    def test_perfect_accuracy(self):
        preds = ["Re-route to Backup", "Expedite shipment", "Hold production"]
        gt = ["Re-route to Backup", "Expedite shipment", "Hold production"]
        assert calculate_decision_accuracy(preds, gt) == 1.0

    def test_partial_accuracy(self):
        preds = ["Re-route to Backup", "Wrong action", "Hold production"]
        gt = ["Re-route to Backup", "Expedite shipment", "Hold production"]
        assert pytest.approx(calculate_decision_accuracy(preds, gt), 0.001) == 2.0 / 3.0

    def test_normalized_casing_and_whitespace(self):
        preds = ["  re-route to backup  ", "EXPEDITE SHIPMENT", "Hold production"]
        gt = ["Re-route to Backup", "expedite shipment", "hold production "]
        assert calculate_decision_accuracy(preds, gt, normalized=True) == 1.0
        assert calculate_decision_accuracy(preds, gt, normalized=False) < 1.0

    def test_empty_or_mismatched(self):
        assert calculate_decision_accuracy([], []) == 0.0
        assert calculate_decision_accuracy(["A"], ["A", "B"]) == 0.0


class TestWCSStability:
    def test_unanimous_stability(self):
        weights = {"a1": 0.8, "a2": 0.9, "a3": 0.85}
        winning = ["a1", "a2", "a3"]
        assert pytest.approx(calculate_wcs_stability(weights, winning), 0.001) == 1.0

    def test_partial_consensus_stability(self):
        weights = {"a1": 1.0, "a2": 1.0, "a3": 1.0, "a4": 1.0}
        winning = ["a1", "a2"]
        assert pytest.approx(calculate_wcs_stability(weights, winning), 0.001) == 0.5

    def test_empty_or_zero_weights(self):
        assert calculate_wcs_stability({}, ["a1"]) == 1.0
        assert calculate_wcs_stability({"a1": 0.0}, ["a1"]) == 0.0


class TestAgreementRate:
    def test_unanimous_agreement(self):
        claims = [
            {"recommendation": "Expedite PO"},
            {"recommendation": "Expedite PO"},
            {"recommendation": "Expedite PO"},
        ]
        assert calculate_agreement_rate(claims) == 1.0

    def test_complete_divergence(self):
        claims = [
            {"recommendation": "Action A"},
            {"recommendation": "Action B"},
            {"recommendation": "Action C"},
        ]
        assert calculate_agreement_rate(claims) == 0.0

    def test_dict_of_claims_and_action_key(self):
        claims_dict = {
            "a1": {"action": "Re-route"},
            "a2": {"action": "Re-route"},
            "a3": {"action": "Cancel"},
        }
        # 3 pairs: (a1, a2) -> match, (a1, a3) -> no, (a2, a3) -> no -> 1/3 = 0.333
        assert pytest.approx(calculate_agreement_rate(claims_dict), 0.01) == 1.0 / 3.0

    def test_single_or_empty_claim(self):
        assert calculate_agreement_rate([]) == 1.0
        assert calculate_agreement_rate([{"recommendation": "Sole claim"}]) == 1.0


class TestCohensKappa:
    def test_perfect_calibration(self):
        a = ["FAST_PATH", "SLOW_PATH", "HUMAN_ESCALATION", "FAST_PATH"]
        b = ["FAST_PATH", "SLOW_PATH", "HUMAN_ESCALATION", "FAST_PATH"]
        assert calculate_cohens_kappa(a, b) == 1.0

    def test_single_class_identical(self):
        a = ["FAST_PATH", "FAST_PATH", "FAST_PATH"]
        b = ["FAST_PATH", "FAST_PATH", "FAST_PATH"]
        assert calculate_cohens_kappa(a, b) == 1.0

    def test_disagreement_lower_kappa(self):
        a = ["FAST_PATH", "SLOW_PATH", "FAST_PATH", "SLOW_PATH"]
        b = ["SLOW_PATH", "FAST_PATH", "SLOW_PATH", "FAST_PATH"]
        assert calculate_cohens_kappa(a, b) < 0.0

    def test_empty_or_mismatched(self):
        assert calculate_cohens_kappa([], []) == 0.0
        assert calculate_cohens_kappa(["A"], ["A", "B"]) == 0.0


class TestLatencyPercentiles:
    def test_percentile_calculation(self):
        lats = [100.0, 200.0, 300.0, 400.0, 500.0]
        res = calculate_latency_percentiles(lats)
        assert res["p50"] == 300.0
        assert res["mean"] == 300.0
        assert res["p90"] == 500.0
        assert res["p99"] == 500.0

    def test_empty_latencies(self):
        res = calculate_latency_percentiles([])
        assert res["p50"] == 0.0
        assert res["mean"] == 0.0


class TestOperationalRiskEstimators:
    def test_stockout_risk_reduction(self):
        assert pytest.approx(calculate_stockout_risk_reduction(0.40, 0.10), 0.01) == 75.0
        assert calculate_stockout_risk_reduction(0.0, 0.10) == 0.0
        assert calculate_stockout_risk_reduction(0.40, 0.50) == 0.0

    def test_fill_rate_delta(self):
        assert pytest.approx(calculate_fill_rate_delta(0.85, 0.95), 0.001) == 0.10
