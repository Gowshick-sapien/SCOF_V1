import pytest
from services.evaluation.src.harness import (
    resolve_calibration_file_path,
    load_calibration_dataset,
    run_single_agent_decision,
    run_naive_majority_decision,
    run_cd2f_decision,
    evaluate_predictions,
    run_calibration_evaluation,
)


class TestHarnessDataLoader:
    def test_resolve_dataset_path(self):
        path = resolve_calibration_file_path()
        assert path is not None
        assert path.exists()

    def test_load_dataset(self):
        dataset = load_calibration_dataset()
        assert len(dataset) > 0
        first_item = dataset[0]
        assert "bundle" in first_item
        assert "ground_truth" in first_item
        assert "expected_recommendation" in first_item["ground_truth"]


class TestDecisionBaselines:
    @pytest.fixture
    def sample_claims(self):
        return {
            "demand_agent": {
                "agent_id": "demand_agent",
                "recommendation": "Expedite shipment from Supplier X",
                "confidence": 0.85,
            },
            "inventory_agent": {
                "agent_id": "inventory_agent",
                "recommendation": "Expedite shipment from Supplier X",
                "confidence": 0.92,
            },
            "supplier_agent": {
                "agent_id": "supplier_agent",
                "recommendation": "Re-route to Supplier Y",
                "confidence": 0.70,
            },
        }

    def test_single_agent_decision(self, sample_claims):
        res = run_single_agent_decision(sample_claims)
        # Should pick inventory_agent because confidence is 0.92
        assert res["recommendation"] == "Expedite shipment from Supplier X"
        assert res["confidence"] == 0.92
        assert res["tier"] == "FAST_PATH"

    def test_naive_majority_decision(self, sample_claims):
        res = run_naive_majority_decision(sample_claims)
        # 2 votes for Expedite shipment, 1 vote for Re-route
        assert res["recommendation"] == "Expedite shipment from Supplier X"
        assert pytest.approx(res["confidence"], 0.01) == 2.0 / 3.0

    def test_cd2f_decision(self, sample_claims):
        res = run_cd2f_decision(sample_claims)
        assert res["recommendation"] == "Expedite shipment from Supplier X"
        assert res["wcs"] > 0.6
        assert res["tier"] in ("FAST_PATH", "SLOW_PATH")


class TestHarnessEvaluation:
    def test_evaluate_predictions_aggregation(self):
        preds = ["Re-route A", "Expedite B"]
        gt = ["Re-route A", "Expedite B"]
        lats = [320.0, 480.0]
        tiers = ["FAST_PATH", "SLOW_PATH"]
        gt_tiers = ["FAST_PATH", "SLOW_PATH"]
        claims = [
            {"a1": {"recommendation": "Re-route A"}, "a2": {"recommendation": "Re-route A"}},
            {"a1": {"recommendation": "Expedite B"}, "a2": {"recommendation": "Expedite B"}},
        ]

        summary = evaluate_predictions(
            predictions=preds,
            ground_truth=gt,
            latencies=lats,
            escalation_tiers=tiers,
            gt_tiers=gt_tiers,
            agent_claims_list=claims,
        )

        assert summary.accuracy == 1.0
        assert summary.agreement_rate == 1.0
        assert summary.sample_count == 2
        assert summary.cohens_kappa_recommendation == 1.0
        assert summary.cohens_kappa_tier == 1.0
        assert summary.fast_path_p50_ms == 320.0
        assert summary.slow_path_p50_ms == 480.0

    def test_run_calibration_evaluation_end_to_end(self):
        result = run_calibration_evaluation()
        assert result.status == "VALIDATED"
        assert len(result.benchmark_results) == 3
        
        methods = [r.method for r in result.benchmark_results]
        assert any("CD2F" in m for m in methods)
        assert any("Majority" in m for m in methods)
        assert any("Single" in m for m in methods)

        cd2f_row = next(r for r in result.benchmark_results if "CD2F" in r.method)
        assert cd2f_row.accuracy >= 0.85
        assert cd2f_row.cohens_kappa >= 0.80
        assert result.calibration_metrics["recommendation_kappa"] >= 0.80
