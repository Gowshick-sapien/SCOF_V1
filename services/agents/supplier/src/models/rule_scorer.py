"""Rule-based reliability scorer for Supplier Intelligence Agent."""

import json
from typing import Any, Dict
import numpy as np
from scof_shared.ml.base_model import BaseTrainer, BaseInferenceModel, ModelArtifact
from scof_shared.ml.types import PredictionInterval


class RuleScorerInitializer(BaseTrainer):
    """
    Initializer that captures feature statistics and threshold parameters
    for rule-based scoring. Uses BaseTrainer interface for ensemble framework consistency.
    """

    def fit(self, X_train: Any, y_train: Any, **kwargs) -> ModelArtifact:
        X_arr = np.asarray(X_train, dtype=float)

        means = np.mean(X_arr, axis=0).tolist() if len(X_arr) > 0 else [0.9, 0.5, 1.0, 0.95, 2.0, 2.0, 0.5, 0.0]
        stds = np.std(X_arr, axis=0).tolist() if len(X_arr) > 1 else [0.05] * len(means)

        params = {
            "feature_means": means,
            "feature_stds": stds,
            "weight_ontime": 0.40,
            "weight_fulfillment": 0.30,
            "weight_leadtime": 0.20,
            "weight_alternates": 0.10,
        }

        return ModelArtifact(
            model_bytes=json.dumps(params).encode("utf-8"),
            model_name="rule_scorer",
            model_version="1.0.0",
            training_metadata={
                "n_samples": len(X_arr),
                "variance": float(np.mean(stds)),
            },
        )


class RuleScorerInference(BaseInferenceModel):
    """Inference implementation of rule-based supplier reliability scorer."""

    def __init__(self, artifact: ModelArtifact):
        super().__init__(artifact)
        self.params: Dict[str, Any] = json.loads(artifact.model_bytes.decode("utf-8"))
        self.variance: float = float(artifact.training_metadata.get("variance", 0.08))

    def predict(self, X: Any) -> np.ndarray:
        """
        Computes composite rule-based reliability score in [0.0, 1.0].
        Features expected in X:
          [0]: on_time_delivery_rate
          [1]: avg_delay_days
          [2]: max_delay_days
          [3]: order_fulfillment_rate
          [4]: alternate_supplier_count
          [5]: supply_chain_hop_count
          [6]: lead_time_reliability (std dev)
          [7]: disruption_severity
        """
        X_arr = np.asarray(X, dtype=float)
        if len(X_arr.shape) == 1:
            X_arr = X_arr.reshape(1, -1)

        scores = []
        for row in X_arr:
            ontime = row[0]
            fulfillment = row[3]
            alt_count = row[4]
            lead_time_std = row[6]
            disr_sev = row[7]

            lead_time_score = max(0.0, 1.0 - (lead_time_std / 5.0))
            alt_score = min(1.0, alt_count / 3.0)

            base_score = (
                self.params.get("weight_ontime", 0.40) * ontime
                + self.params.get("weight_fulfillment", 0.30) * fulfillment
                + self.params.get("weight_leadtime", 0.20) * lead_time_score
                + self.params.get("weight_alternates", 0.10) * alt_score
            )

            # Apply disruption penalty
            if disr_sev > 0:
                penalty = min(0.60, disr_sev * 0.12)
                base_score = base_score * (1.0 - penalty)

            scores.append(np.clip(base_score, 0.0, 1.0))

        return np.array(scores, dtype=float)

    def predict_interval(self, X: Any, alpha: float = 0.1) -> PredictionInterval:
        scores = self.predict(X)
        z = 1.645 if alpha == 0.1 else 1.96
        margin = z * self.variance
        lower = np.clip(scores - margin, 0.0, 1.0)
        upper = np.clip(scores + margin, 0.0, 1.0)
        return PredictionInterval(lower=lower, upper=upper, alpha=alpha)
