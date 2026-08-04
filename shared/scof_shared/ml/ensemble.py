"""Base Ensemble framework for SCOF agents.

Combines predictions from multiple registered BaseInferenceModel instances using weighted averaging
and computes agreement metrics.
"""

from typing import Dict, Any
import numpy as np
from scof_shared.ml.base_model import BaseInferenceModel
from scof_shared.ml.confidence import ConfidenceCalculator
from scof_shared.ml.types import EnsembleResult, ForecastResult, PredictionInterval


class BaseEnsemble:
    """Pluggable ensemble engine combining multiple inference models."""

    def __init__(
        self,
        weights: Dict[str, float],
        confidence_calculator: ConfidenceCalculator,
    ):
        self.weights = weights
        self.confidence_calculator = confidence_calculator
        self.models: Dict[str, BaseInferenceModel] = {}

    def register_model(self, name: str, model: BaseInferenceModel) -> None:
        """Registers a trained inference model."""
        self.models[name] = model

    def compute_agreement(self, results: Dict[str, ForecastResult]) -> float:
        """Computes normalized agreement score between registered model predictions.

        Returns 1.0 if identical or single model, decreases as predictions diverge.
        """
        if len(results) <= 1:
            return 1.0

        forecasts = [res.point_forecast for res in results.values()]
        # Mean pairwise relative difference
        total_diff = 0.0
        pairs = 0
        for i in range(len(forecasts)):
            for j in range(i + 1, len(forecasts)):
                f1 = np.asarray(forecasts[i], dtype=float)
                f2 = np.asarray(forecasts[j], dtype=float)
                denom = np.maximum(np.abs(f1) + np.abs(f2), 1e-5)
                rel_diff = np.mean(2.0 * np.abs(f1 - f2) / denom)
                total_diff += rel_diff
                pairs += 1

        avg_rel_diff = total_diff / max(1, pairs)
        agreement = max(0.0, 1.0 - avg_rel_diff)
        return float(agreement)

    def predict(self, X: Any, alpha: float = 0.1) -> EnsembleResult:
        """Predicts using weighted ensemble of all registered models."""
        if not self.models:
            raise ValueError("No models registered in ensemble.")

        contributions: Dict[str, ForecastResult] = {}
        total_weight = 0.0
        weighted_points = None
        weighted_lowers = None
        weighted_uppers = None

        for name, model in self.models.items():
            w = float(self.weights.get(name, 1.0))
            point = model.predict(X)
            interval = model.predict_interval(X, alpha=alpha)

            contributions[name] = ForecastResult(
                point_forecast=point,
                interval=interval,
                model_name=name,
                metadata={"weight": w},
            )

            if weighted_points is None:
                weighted_points = w * point
                weighted_lowers = w * interval.lower
                weighted_uppers = w * interval.upper
            else:
                weighted_points += w * point
                weighted_lowers += w * interval.lower
                weighted_uppers += w * interval.upper

            total_weight += w

        if total_weight <= 0:
            total_weight = 1.0

        final_point = weighted_points / total_weight
        final_lower = weighted_lowers / total_weight
        final_upper = weighted_uppers / total_weight

        agreement = self.compute_agreement(contributions)

        return EnsembleResult(
            point_forecast=final_point,
            interval=PredictionInterval(lower=final_lower, upper=final_upper, alpha=alpha),
            agreement_score=agreement,
            model_contributions=contributions,
        )
