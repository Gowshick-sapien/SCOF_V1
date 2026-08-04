"""XGBoost model implementation for Inventory Agent forecasting."""

import pickle
from typing import Any
import numpy as np
from xgboost import XGBRegressor
from scof_shared.ml.base_model import BaseTrainer, BaseInferenceModel, ModelArtifact
from scof_shared.ml.types import PredictionInterval


class InventoryXGBoostTrainer(BaseTrainer):
    """Trainer for XGBoost inventory stock forecasting model."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def fit(self, X_train: Any, y_train: Any, **kwargs) -> ModelArtifact:
        X_arr = np.asarray(X_train, dtype=float)
        y_arr = np.asarray(y_train, dtype=float)

        model = XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.08,
            random_state=self.seed,
            n_jobs=1,
        )
        model.fit(X_arr, y_arr)

        model_bytes = pickle.dumps(model)

        preds = model.predict(X_arr)
        residual_std = float(np.std(y_arr - preds)) if len(y_arr) > 1 else 10.0

        return ModelArtifact(
            model_bytes=model_bytes,
            model_name="xgboost",
            model_version="1.0.0",
            training_metadata={
                "seed": self.seed,
                "n_samples": len(X_arr),
                "residual_std": residual_std,
            },
        )


class InventoryXGBoostInference(BaseInferenceModel):
    """Inference wrapper for trained XGBoost inventory model."""

    def __init__(self, artifact: ModelArtifact):
        super().__init__(artifact)
        self.model: XGBRegressor = pickle.loads(artifact.model_bytes)
        self.residual_std: float = float(artifact.training_metadata.get("residual_std", 10.0))

    def predict(self, X: Any) -> np.ndarray:
        X_arr = np.asarray(X, dtype=float)
        return self.model.predict(X_arr)

    def predict_interval(self, X: Any, alpha: float = 0.1) -> PredictionInterval:
        preds = self.predict(X)
        z = 1.645 if alpha == 0.1 else 1.96
        margin = z * self.residual_std
        lower = np.maximum(0.0, preds - margin)
        upper = preds + margin
        return PredictionInterval(lower=lower, upper=upper, alpha=alpha)
