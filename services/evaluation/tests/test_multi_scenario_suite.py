import pytest
from pathlib import Path
from services.evaluation.src.harness import (
    resolve_benchmark_suite_path,
    evaluate_category_breakdown,
    CategoryBenchmarkResponse,
)


class TestMultiScenarioSuiteStructure:
    def test_resolve_suite_path(self):
        suite_path = resolve_benchmark_suite_path()
        assert suite_path is not None
        assert suite_path.exists()
        assert suite_path.name in ("benchmark_suite.json", "calibration_set.json")

    def test_benchmark_suite_categories_distribution(self):
        suite_path = resolve_benchmark_suite_path()
        import json
        with open(suite_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if suite_path.name == "benchmark_suite.json":
            assert len(data) == 20
            categories = [item.get("bundle", {}).get("disruption_category") for item in data]
            
            assert categories.count("SUPPLIER_DELAY") == 5
            assert categories.count("TRANSPORTATION_FAILURE") == 5
            assert categories.count("DEMAND_SPIKE") == 5
            assert categories.count("ADVERSE_WEATHER") == 5


class TestCategoryMetricsEvaluation:
    def test_evaluate_category_breakdown(self):
        res = evaluate_category_breakdown()
        assert isinstance(res, CategoryBenchmarkResponse)
        assert res.status == "VALIDATED"
        assert len(res.categories) == 4

        cat_names = [c.category for c in res.categories]
        assert "SUPPLIER_DELAY" in cat_names
        assert "TRANSPORTATION_FAILURE" in cat_names
        assert "DEMAND_SPIKE" in cat_names
        assert "ADVERSE_WEATHER" in cat_names

        for c in res.categories:
            assert c.accuracy >= 0.80
            assert 0.0 <= c.wcs_stability <= 1.0
            assert c.latency_p50_ms > 0.0
            assert 0.0 <= c.conflict_intensity <= 1.0
            assert 0.0 <= c.fast_path_pct <= 100.0
            assert 0.0 <= c.human_escalation_pct <= 100.0
