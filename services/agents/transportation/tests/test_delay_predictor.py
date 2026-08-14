"""Unit tests for DelayPredictor, RouteScorer, and TransportEnsemble."""

import numpy as np
from services.agents.transportation.src.models.delay_predictor import DelayPredictorTrainer, DelayPredictorInference
from services.agents.transportation.src.models.route_scorer import RouteScorerInitializer, RouteScorerInference
from services.agents.transportation.src.models.ensemble import TransportEnsemble, create_trained_transport_ensemble


def test_delay_predictor_fit_and_predict():
    X = np.array([
        [0.95, 0.2, 5.0, 1000.0, 2.0, 0.5, 0.0, 0.0],
        [0.70, 2.5, 14.0, 1200.0, 2.0, 0.3, 3.0, 2.0],
        [0.98, 0.0, 2.0, 3200.0, 1.0, 0.2, 0.0, 0.0],
    ])
    y = np.array([0.2, 3.0, 0.0])

    trainer = DelayPredictorTrainer(seed=42)
    artifact = trainer.fit(X, y)
    assert artifact.model_name == "delay_predictor"

    model = DelayPredictorInference(artifact)
    preds = model.predict(X)
    assert len(preds) == 3
    assert np.all(preds >= 0.0)

    interval = model.predict_interval(X, alpha=0.1)
    assert len(interval.lower) == 3
    assert len(interval.upper) == 3
    assert np.all(interval.upper >= interval.lower)


def test_route_scorer():
    X = np.array([
        [0.95, 0.2, 5.0, 1000.0, 2.0, 0.5, 0.0, 0.0],
        [0.50, 2.5, 14.0, 1200.0, 2.0, 0.3, 4.0, 3.0],
    ])
    y = np.array([0.2, 3.0])

    init = RouteScorerInitializer()
    artifact = init.fit(X, y)
    model = RouteScorerInference(artifact)

    delays = model.predict(X)
    assert len(delays) == 2
    assert delays[1] > delays[0]  # Disrupted route should have higher delay

    interval = model.predict_interval(X)
    assert np.all(interval.upper >= interval.lower)


def test_transport_ensemble():
    X = np.array([
        [0.95, 0.2, 5.0, 1000.0, 2.0, 0.5, 0.0, 0.0],
        [0.70, 2.5, 14.0, 1200.0, 2.0, 0.3, 3.0, 2.0],
    ])
    y = np.array([0.2, 3.0])

    ensemble = create_trained_transport_ensemble(X, y, seed=42)
    res = ensemble.predict(X)

    assert len(res.point_forecast) == 2
    assert 0.0 <= res.agreement_score <= 1.0
    assert len(res.interval.lower) == 2
    assert len(res.interval.upper) == 2
    assert np.all(res.interval.upper >= res.interval.lower)
