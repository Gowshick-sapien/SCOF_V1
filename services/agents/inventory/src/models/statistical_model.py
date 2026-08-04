"""Statistical baseline model implementation for Inventory Agent forecasting.

Decomposes stock depletion into linear trend and depletion rate projections.
"""

import pickle
from typing import Any
import numpy as np
from scof_shared.ml.base_model import BaseTrainer, BaseInferenceModel, ModelArtifact
from scof_shared.ml.types import PredictionInterval


class InventoryStatisticalTrainer(BaseTrainer):
    """Trainer for statistical inventory depletion model."""

    def fit(self, X_train: Any, y_train: Any, **kwargs) -> ModelArtifact:
        y_arr = np.asarray(y_train, dtype=float)
        n = len(y_arr)

        if n <= 1:
            slope = -5.0
            intercept = float(y_arr[0]) if n == 1 else 500.0
            residual_std = 5.0
        else:
            t = np.arange(n)
            slope, intercept = np.polyfit(t, y_arr, 1)
            preds = slope * t + intercept
            residual_std = float(np.std(y_arr - preds))

        params = {
            "slope": float(slope),
            "intercept": float(intercept),
            "residual_std": float(residual_std),
        }

        model_bytes = pickle.dumps(params)

        return ModelArtifact(
            model_bytes=model_bytes,
            model_name="statistical",
            model_version="1.0.0",
            training_metadata=params,
        )


class InventoryStatisticalInference(BaseInferenceModel):
    """Inference wrapper for trained statistical inventory model."""

    def __init__(self, artifact: ModelArtifact):
        super().__init__(artifact)
        self.params = pickle.loads(artifact.model_bytes)
        self.slope = float(self.params["slope"])
        self.intercept = float(self.params["intercept"])
        self.residual_std = float(self.params["residual_std"])

    def predict(self, X: Any) -> np.ndarray:
        X_arr = np.asarray(X, dtype=float)
        n = len(X_arr)
        if n == 0:
            return np.array([])

        current_stock = X_arr[:, 0]
        depletion_rate = X_arr[:, 1]

        # Project 7-day future stock level
        projected = current_stock - (depletion_rate * 7.0)

        # Apply disruption acceleration if present (column index 5)
        if X_arr.shape[1] > 5:
            disr = X_arr[:, 5]
            projected -= disr * 15.0

        return np.maximum(0.0, projected)

    def predict_interval(self, X: Any, alpha: float = 0.1) -> PredictionInterval:
        preds = self.predict(X)
        z = 1.645 if alpha == 0.1 else 1.96
        margin = z * max(5.0, self.residual_std)
        lower = np.maximum(0.0, preds - margin)
        upper = preds + margin
        return PredictionInterval(lower=lower, upper=upper, alpha=alpha)
