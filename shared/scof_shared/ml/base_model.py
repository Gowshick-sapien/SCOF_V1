"""Base interfaces for ML model training and inference in SCOF agents.

Enforces clear separation between Trainer (fit/save) and InferenceModel (predict).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import pickle
import numpy as np
from scof_shared.ml.types import PredictionInterval


@dataclass
class ModelArtifact:
    """Serializable container for model weights and training metadata."""

    model_bytes: bytes
    model_name: str
    model_version: str
    training_metadata: Dict[str, Any]
    created_at: datetime = datetime.now(timezone.utc)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Path) -> "ModelArtifact":
        if not path.exists():
            raise FileNotFoundError(f"Model artifact not found at {path}")
        with open(path, "rb") as f:
            return pickle.load(f)


class BaseTrainer(ABC):
    """Abstract base trainer class."""

    @abstractmethod
    def fit(self, X_train: Any, y_train: Any, **kwargs) -> ModelArtifact:
        """Trains the model and returns a serializable artifact."""
        pass


class BaseInferenceModel(ABC):
    """Abstract base inference model class initialized from trained artifact."""

    def __init__(self, artifact: ModelArtifact):
        self.artifact = artifact
        self.model_name = artifact.model_name
        self.model_version = artifact.model_version

    @abstractmethod
    def predict(self, X: Any) -> np.ndarray:
        """Generates point forecasts."""
        pass

    @abstractmethod
    def predict_interval(self, X: Any, alpha: float = 0.1) -> PredictionInterval:
        """Generates prediction intervals."""
        pass
