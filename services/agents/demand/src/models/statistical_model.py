"""Statistical baseline model implementation for Demand Agent forecasting.

Decomposes demand time-series into linear trend and weekly seasonality components.
"""

import pickle
from typing import Any
import numpy as np
from scof_shared.ml.base_model import BaseTrainer, BaseInferenceModel, ModelArtifact
from scof_shared.ml.types import PredictionInterval


class DemandStatisticalTrainer(BaseTrainer):
    """Trainer for statistical trend + seasonality demand model."""

    def fit(self, X_train: Any, y_train: Any, **kwargs) -> ModelArtifact:
        y_arr = np.asarray(y_train, dtype=float)
        n = len(y_arr)

        if n <= 1:
            slope = 0.0
            intercept = float(y_arr[0]) if n == 1 else 100.0
            seasonality = np.zeros(7)
            residual_std = 5.0
        else:
            t = np.arange(n)
            slope, intercept = np.polyfit(t, y_arr, 1)
            trend = slope * t + intercept
            residuals = y_arr - trend

            # Day of week seasonality
            seasonality = np.zeros(7)
            for dow in range(7):
                idx = np.where(t % 7 == dow)[0]
                if len(idx) > 0:
                    seasonality[dow] = np.mean(residuals[idx])

            total_preds = trend + seasonality[t % 7]
            residual_std = float(np.std(y_arr - total_preds))

        params = {
            "slope": float(slope),
            "intercept": float(intercept),
            "seasonality": seasonality.tolist(),
            "residual_std": float(residual_std),
        }

        model_bytes = pickle.dumps(params)

        return ModelArtifact(
            model_bytes=model_bytes,
            model_name="statistical",
            model_version="1.0.0",
            training_metadata=params,
        )


class DemandStatisticalInference(BaseInferenceModel):
    """Inference wrapper for trained statistical demand model."""

    def __init__(self, artifact: ModelArtifact):
        super().__init__(artifact)
        self.params = pickle.loads(artifact.model_bytes)
        self.slope = float(self.params["slope"])
        self.intercept = float(self.params["intercept"])
        self.seasonality = np.array(self.params["seasonality"])
        self.residual_std = float(self.params["residual_std"])

    def predict(self, X: Any) -> np.ndarray:
        X_arr = np.asarray(X, dtype=float)
        n = len(X_arr)
        if n == 0:
            return np.array([])

        dow_col = X_arr[:, 0].astype(int) % 7
        t_indices = np.arange(n)

        trend = self.slope * t_indices + self.intercept
        season = self.seasonality[dow_col]
        preds = np.maximum(0.0, trend + season)

        # Apply exogenous disruption adjustment if present (column index 6)
        if X_arr.shape[1] > 6:
            disr = X_arr[:, 6]
            preds += disr * 10.0

        return preds

    def predict_interval(self, X: Any, alpha: float = 0.1) -> PredictionInterval:
        preds = self.predict(X)
        z = 1.645 if alpha == 0.1 else 1.96
        margin = z * max(5.0, self.residual_std)
        lower = np.maximum(0.0, preds - margin)
        upper = preds + margin
        return PredictionInterval(lower=lower, upper=upper, alpha=alpha)
