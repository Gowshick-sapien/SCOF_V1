"""Unit tests for Demand Ensemble."""

import sys
from pathlib import Path

pkg_root = Path(__file__).resolve().parents[1]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

import numpy as np
from src.models.ensemble import DemandEnsemble
from src.models.xgboost_model import DemandXGBoostTrainer, DemandXGBoostInference
from src.models.statistical_model import DemandStatisticalTrainer, DemandStatisticalInference


def test_demand_ensemble_prediction():
    X = np.random.randn(20, 7)
    y = np.full(20, 100.0) + np.random.randn(20) * 5.0

    xgb_trainer = DemandXGBoostTrainer(seed=42)
    xgb_art = xgb_trainer.fit(X, y)

    stat_trainer = DemandStatisticalTrainer()
    stat_art = stat_trainer.fit(X, y)

    ensemble = DemandEnsemble(weights={"xgboost": 0.6, "statistical": 0.4})
    ensemble.register_model("xgboost", DemandXGBoostInference(xgb_art))
    ensemble.register_model("statistical", DemandStatisticalInference(stat_art))

    res = ensemble.predict(X)

    assert len(res.point_forecast) == 20
    assert 0.0 <= res.agreement_score <= 1.0
    assert len(res.interval.lower) == 20
    assert len(res.interval.upper) == 20
