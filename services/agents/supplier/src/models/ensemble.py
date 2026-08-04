"""Supplier Intelligence Agent Ensemble Model."""

from typing import Dict
from scof_shared.ml.ensemble import BaseEnsemble
from scof_shared.ml.confidence import ConfidenceCalculator


class SupplierEnsemble(BaseEnsemble):
    """Ensemble combining GradientBoostingClassifier and Rule-based scorer for Supplier Agent."""

    def __init__(self, weights: Dict[str, float]):
        calc = ConfidenceCalculator(
            weight_agreement=0.40,
            weight_interval=0.30,
            weight_historical=0.30,
        )
        super().__init__(weights=weights, confidence_calculator=calc)
