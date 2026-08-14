"""Unit tests for Supplier Agent Reliability Models."""

import numpy as np
from services.agents.supplier.src.models.reliability_scorer import ReliabilityScorerInference, ReliabilityScorerTrainer
from services.agents.supplier.src.models.rule_scorer import RuleScorerInference, RuleScorerInitializer
from services.agents.supplier.src.models.ensemble import SupplierEnsemble


def test_reliability_scorer_fit_and_predict():
    X = np.array([
        [0.95, 0.2, 1.0, 0.98, 2.0, 2.0, 0.5, 0.0],
        [0.60, 4.5, 8.0, 0.70, 1.0, 3.0, 2.5, 4.0],
        [0.90, 0.4, 2.0, 0.95, 2.0, 2.0, 0.8, 0.0],
        [0.50, 6.0, 10.0, 0.60, 0.0, 4.0, 3.0, 5.0],
    ])
    y = np.array([0, 1, 0, 1])

    trainer = ReliabilityScorerTrainer(seed=42)
    artifact = trainer.fit(X, y)

    assert artifact.model_name == "reliability_scorer"
    assert "residual_std" in artifact.training_metadata

    infer = ReliabilityScorerInference(artifact)
    preds = infer.predict(X)

    assert len(preds) == 4
    assert np.all(preds >= 0.0) and np.all(preds <= 1.0)
    # Healthy supplier score should exceed disrupted supplier score
    assert preds[0] > preds[1]

    interval = infer.predict_interval(X, alpha=0.1)
    assert len(interval.lower) == 4
    assert len(interval.upper) == 4
    assert np.all(interval.lower <= interval.upper)
    assert np.all(interval.lower >= 0.0) and np.all(interval.upper <= 1.0)


def test_rule_scorer():
    X = np.array([
        [0.95, 0.2, 1.0, 0.98, 2.0, 2.0, 0.5, 0.0],
        [0.60, 4.5, 8.0, 0.70, 1.0, 3.0, 2.5, 4.0],
    ])
    y = np.array([0, 1])

    trainer = RuleScorerInitializer()
    artifact = trainer.fit(X, y)

    infer = RuleScorerInference(artifact)
    preds = infer.predict(X)

    assert len(preds) == 2
    assert preds[0] > preds[1]
    assert np.all(preds >= 0.0) and np.all(preds <= 1.0)


def test_supplier_ensemble():
    X = np.array([
        [0.95, 0.2, 1.0, 0.98, 2.0, 2.0, 0.5, 0.0],
        [0.60, 4.5, 8.0, 0.70, 1.0, 3.0, 2.5, 4.0],
    ])
    y = np.array([0, 1])

    ensemble = SupplierEnsemble(weights={"reliability_scorer": 0.6, "rule_scorer": 0.4})

    ml_trainer = ReliabilityScorerTrainer(seed=42)
    ml_art = ml_trainer.fit(X, y)
    ensemble.register_model("reliability_scorer", ReliabilityScorerInference(ml_art))

    rule_trainer = RuleScorerInitializer()
    rule_art = rule_trainer.fit(X, y)
    ensemble.register_model("rule_scorer", RuleScorerInference(rule_art))

    result = ensemble.predict(X)

    assert len(result.point_forecast) == 2
    assert 0.0 <= result.agreement_score <= 1.0
    assert len(result.model_contributions) == 2

    interval_width = float(np.mean(result.interval.upper - result.interval.lower))
    conf = ensemble.confidence_calculator.compute(
        agreement_score=result.agreement_score,
        interval_width=interval_width,
        historical_error=0.10,
        max_interval_width=1.0,
    )
    assert 0.0 <= conf.score <= 1.0
