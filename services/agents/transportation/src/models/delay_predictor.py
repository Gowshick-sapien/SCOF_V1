"""Gradient Boosting Delay Predictor for Transportation Agent.

Predicts shipment transit delay in days from carrier history, route parameters,
and disruption events with residual-calibrated prediction intervals.
"""

import pickle
from typing import Dict, Any, Optional
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from scof_shared.ml.base_model import BaseTrainer, BaseInferenceModel, ModelArtifact
from scof_shared.ml.types import PredictionInterval


class DelayPredictorTrainer(BaseTrainer):
    """Trains GradientBoostingRegressor to predict transit delay in days."""

    def __init__(self, seed: int = 42, n_estimators: int = 50, max_depth: int = 3):
        self.seed = seed
        self.n_estimators = n_estimators
        self.max_depth = max_depth

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> ModelArtifact:
        """Fits regressor and calculates empirical residual standard deviation."""
        X_arr = np.asarray(X_train, dtype=float)
        y_arr = np.asarray(y_train, dtype=float)

        model = GradientBoostingRegressor(
            random_state=self.seed,
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
        )
        model.fit(X_arr, y_arr)

        train_preds = model.predict(X_arr)
        residuals = y_arr - train_preds
        residual_std = float(np.std(residuals)) if len(residuals) > 1 else 0.5
        residual_std = max(0.2, residual_std)  # Floor at 0.2 days

        return ModelArtifact(
            model_bytes=pickle.dumps(model),
            model_name="delay_predictor",
            model_version="1.0.0",
            training_metadata={
                "seed": self.seed,
                "n_samples": len(X_arr),
                "residual_std": residual_std,
                "mean_train_delay": float(np.mean(y_arr)),
            },
        )


class DelayPredictorInference(BaseInferenceModel):
    """Runs inference with residual-calibrated prediction intervals."""

    def __init__(self, artifact: ModelArtifact):
        super().__init__(artifact)
        self.model: GradientBoostingRegressor = pickle.loads(artifact.model_bytes)
        self.residual_std = float(artifact.training_metadata.get("residual_std", 0.5))

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predicts transit delay in days (non-negative)."""
        X_arr = np.asarray(X, dtype=float)
        preds = self.model.predict(X_arr)
        return np.maximum(0.0, preds)

    def predict_interval(self, X: np.ndarray, alpha: float = 0.1) -> PredictionInterval:
        """Calculates prediction intervals using calibrated residual standard error."""
        preds = self.predict(X)
        z = 1.645 if abs(alpha - 0.1) < 0.01 else 1.96
        margin = z * self.residual_std

        lower = np.maximum(0.0, preds - margin)
        upper = preds + margin

        return PredictionInterval(
            lower=lower,
            upper=upper,
            alpha=alpha,
        )
