"""GradientBoostingClassifier reliability scoring model for Supplier Intelligence Agent."""

import pickle
from typing import Any, Dict, Optional
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from scof_shared.ml.base_model import BaseTrainer, BaseInferenceModel, ModelArtifact
from scof_shared.ml.types import PredictionInterval


class ReliabilityScorerTrainer(BaseTrainer):
    """Trainer for GradientBoosting supplier reliability scoring model."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def fit(self, X_train: Any, y_train: Any, **kwargs) -> ModelArtifact:
        X_arr = np.asarray(X_train, dtype=float)
        y_arr = np.asarray(y_train, dtype=int)

        # Ensure at least two classes exist for classifier fit
        if len(np.unique(y_arr)) < 2:
            # Augment with synthetic opposing class sample
            synthetic_x = np.array([X_arr[0] * 0.5])
            synthetic_y = np.array([1 if y_arr[0] == 0 else 0])
            X_arr = np.vstack([X_arr, synthetic_x])
            y_arr = np.concatenate([y_arr, synthetic_y])

        model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=self.seed,
        )
        model.fit(X_arr, y_arr)

        model_bytes = pickle.dumps(model)

        # Residual std for probability calibration intervals
        proba = model.predict_proba(X_arr)
        # Class 1 is failure probability
        fail_proba = proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]
        residual_std = float(np.std(y_arr - fail_proba)) if len(y_arr) > 1 else 0.10

        return ModelArtifact(
            model_bytes=model_bytes,
            model_name="reliability_scorer",
            model_version="1.0.0",
            training_metadata={
                "seed": self.seed,
                "n_samples": len(X_arr),
                "residual_std": residual_std,
            },
        )


class ReliabilityScorerInference(BaseInferenceModel):
    """Inference wrapper for trained GradientBoosting supplier reliability model."""

    def __init__(self, artifact: ModelArtifact):
        super().__init__(artifact)
        self.model: GradientBoostingClassifier = pickle.loads(artifact.model_bytes)
        self.residual_std: float = float(artifact.training_metadata.get("residual_std", 0.10))

    def predict(self, X: Any) -> np.ndarray:
        """
        Predicts supplier reliability score in range [0.0, 1.0].
        Score = 1.0 - failure_probability.
        """
        X_arr = np.asarray(X, dtype=float)
        if len(X_arr.shape) == 1:
            X_arr = X_arr.reshape(1, -1)

        proba = self.model.predict_proba(X_arr)
        if proba.shape[1] > 1:
            failure_prob = proba[:, 1]
        else:
            failure_prob = proba[:, 0]

        reliability_score = 1.0 - failure_prob
        return np.clip(reliability_score, 0.0, 1.0)

    def predict_interval(self, X: Any, alpha: float = 0.1) -> PredictionInterval:
        """
        Residual-calibrated prediction intervals for reliability scores.
        """
        scores = self.predict(X)
        z = 1.645 if alpha == 0.1 else 1.96
        margin = z * self.residual_std
        lower = np.clip(scores - margin, 0.0, 1.0)
        upper = np.clip(scores + margin, 0.0, 1.0)
        return PredictionInterval(lower=lower, upper=upper, alpha=alpha)
