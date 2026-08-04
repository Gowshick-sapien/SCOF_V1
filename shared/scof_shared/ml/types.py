"""Shared ML data structures and result types for SCOF agents."""

from dataclasses import dataclass, field
from typing import Dict, Any
import numpy as np


@dataclass
class PredictionInterval:
    """Lower and upper bound predictions for uncertainty estimation."""

    lower: np.ndarray
    upper: np.ndarray
    alpha: float = 0.1


@dataclass
class ForecastResult:
    """Output from an individual inference model."""

    point_forecast: np.ndarray
    interval: PredictionInterval
    model_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnsembleResult:
    """Combined output from an ensemble model."""

    point_forecast: np.ndarray
    interval: PredictionInterval
    agreement_score: float
    model_contributions: Dict[str, ForecastResult] = field(default_factory=dict)
