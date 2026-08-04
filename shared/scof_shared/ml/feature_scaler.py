"""Feature Scaler for ML models with serialization support."""

from pathlib import Path
import pickle
from typing import Any
import numpy as np


class FeatureScaler:
    """Serializable StandardScaler wrapper."""

    def __init__(self):
        self.mean_: np.ndarray = None
        self.scale_: np.ndarray = None

    def fit(self, X: Any) -> "FeatureScaler":
        arr = np.asarray(X, dtype=float)
        self.mean_ = np.mean(arr, axis=0)
        self.scale_ = np.std(arr, axis=0)
        self.scale_[self.scale_ == 0] = 1.0
        return self

    def transform(self, X: Any) -> np.ndarray:
        if self.mean_ is None or self.scale_ is None:
            raise ValueError("FeatureScaler is not fitted yet.")
        arr = np.asarray(X, dtype=float)
        return (arr - self.mean_) / self.scale_

    def fit_transform(self, X: Any) -> np.ndarray:
        return self.fit(X).transform(X)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Path) -> "FeatureScaler":
        with open(path, "rb") as f:
            return pickle.load(f)
