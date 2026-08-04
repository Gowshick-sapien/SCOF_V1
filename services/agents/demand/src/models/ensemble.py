"""Demand Agent Ensemble Model."""

from typing import Dict
from scof_shared.ml.ensemble import BaseEnsemble
from scof_shared.ml.confidence import ConfidenceCalculator


class DemandEnsemble(BaseEnsemble):
    """Ensemble combining XGBoost and Statistical baseline models for Demand Agent."""

    def __init__(self, weights: Dict[str, float]):
        calc = ConfidenceCalculator(
            weight_agreement=0.40,
            weight_interval=0.30,
            weight_historical=0.30,
        )
        super().__init__(weights=weights, confidence_calculator=calc)
