"""Ensemble model for Transportation Agent combining ML Regressor and Rule-based Scorer."""

from typing import Dict, Any, Optional
from scof_shared.ml.ensemble import BaseEnsemble
from scof_shared.ml.confidence import ConfidenceCalculator
from .delay_predictor import DelayPredictorTrainer, DelayPredictorInference
from .route_scorer import RouteScorerInitializer, RouteScorerInference


class TransportEnsemble(BaseEnsemble):
    """Combines GradientBoostingRegressor delay prediction with deterministic route scoring."""

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        confidence_calculator: Optional[ConfidenceCalculator] = None,
    ):
        model_weights = weights or {
            "delay_predictor": 0.65,
            "route_scorer": 0.35,
        }
        conf_calc = confidence_calculator or ConfidenceCalculator(
            weight_agreement=0.40,
            weight_interval=0.30,
            weight_historical=0.30,
        )
        super().__init__(
            weights=model_weights,
            confidence_calculator=conf_calc,
        )


def create_trained_transport_ensemble(
    X_train,
    y_train,
    seed: int = 42,
    weights: Optional[Dict[str, float]] = None,
) -> TransportEnsemble:
    """Convenience factory: trains models on synthetic/historical data and returns ready ensemble."""
    # 1. Delay Predictor
    delay_trainer = DelayPredictorTrainer(seed=seed)
    delay_artifact = delay_trainer.fit(X_train, y_train)
    delay_model = DelayPredictorInference(delay_artifact)

    # 2. Route Scorer
    route_init = RouteScorerInitializer()
    route_artifact = route_init.fit(X_train, y_train)
    route_model = RouteScorerInference(route_artifact)

    # 3. Ensemble
    ensemble = TransportEnsemble(weights=weights)
    ensemble.register_model("delay_predictor", delay_model)
    ensemble.register_model("route_scorer", route_model)

    return ensemble
