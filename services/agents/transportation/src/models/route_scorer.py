"""Deterministic Route Scorer for Transportation Agent.

Provides rule-based expected delay estimation from carrier performance, route transit time,
and active corridor disruptions.
"""

import pickle
from typing import Dict, Any
import numpy as np
from scof_shared.ml.base_model import BaseTrainer, BaseInferenceModel, ModelArtifact
from scof_shared.ml.types import PredictionInterval


class RouteScorerInitializer(BaseTrainer):
    """Initializes configuration and parameters for the rule-based route delay scorer."""

    def __init__(
        self,
        base_delay: float = 0.2,
        weather_factor: float = 0.8,
        port_factor: float = 0.9,
        unreliability_factor: float = 2.5,
    ):
        self.base_delay = base_delay
        self.weather_factor = weather_factor
        self.port_factor = port_factor
        self.unreliability_factor = unreliability_factor

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> ModelArtifact:
        """Stores rule configuration parameters in ModelArtifact."""
        params = {
            "base_delay": self.base_delay,
            "weather_factor": self.weather_factor,
            "port_factor": self.port_factor,
            "unreliability_factor": self.unreliability_factor,
        }
        return ModelArtifact(
            model_bytes=pickle.dumps(params),
            model_name="route_scorer",
            model_version="1.0.0",
            training_metadata={
                "n_samples": len(X_train),
                "mean_y": float(np.mean(y_train)) if len(y_train) > 0 else 0.0,
            },
        )


class RouteScorerInference(BaseInferenceModel):
    """Calculates rule-based expected transit delay in days."""

    def __init__(self, artifact: ModelArtifact):
        super().__init__(artifact)
        params = pickle.loads(artifact.model_bytes) if artifact.model_bytes else {}
        self.base_delay = params.get("base_delay", 0.2)
        self.weather_factor = params.get("weather_factor", 0.8)
        self.port_factor = params.get("port_factor", 0.9)
        self.unreliability_factor = params.get("unreliability_factor", 2.5)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Computes expected transit delay in days."""
        X_arr = np.asarray(X, dtype=float)
        on_time = X_arr[:, 0]
        weather = X_arr[:, 6]
        port = X_arr[:, 7]

        delays = (
            self.base_delay
            + (1.0 - on_time) * self.unreliability_factor
            + weather * self.weather_factor
            + port * self.port_factor
        )
        return np.maximum(0.0, delays)

    def predict_interval(self, X: np.ndarray, alpha: float = 0.1) -> PredictionInterval:
        """Returns rule-based uncertainty interval around predicted delay."""
        preds = self.predict(X)
        delta = 0.6  # Half-day nominal uncertainty band

        lower = np.maximum(0.0, preds - delta)
        upper = preds + delta

        return PredictionInterval(
            lower=lower,
            upper=upper,
            alpha=alpha,
        )
