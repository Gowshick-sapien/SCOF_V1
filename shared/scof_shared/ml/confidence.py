"""Confidence Calculator for SCOF agents.

Implements composite 40/30/30 confidence formula:
- 40% ensemble agreement score
- 30% prediction interval width score
- 30% historical error score
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ConfidenceScore:
    """Detailed confidence evaluation result."""

    score: float
    components: Dict[str, float]


class ConfidenceCalculator:
    """Auditable composite confidence calculator."""

    def __init__(
        self,
        weight_agreement: float = 0.40,
        weight_interval: float = 0.30,
        weight_historical: float = 0.30,
    ):
        total = weight_agreement + weight_interval + weight_historical
        self.w_agreement = weight_agreement / total
        self.w_interval = weight_interval / total
        self.w_historical = weight_historical / total

    def compute(
        self,
        agreement_score: float,
        interval_width: float,
        historical_error: float,
        max_interval_width: float = 100.0,
    ) -> ConfidenceScore:
        """Computes composite confidence score in range [0.0, 1.0]."""
        # Clamp input agreement to [0, 1]
        ag_score = max(0.0, min(1.0, float(agreement_score)))

        # Interval score: narrower width relative to max -> higher score
        if max_interval_width <= 0:
            int_score = 0.5
        else:
            rel_width = min(1.0, max(0.0, float(interval_width) / float(max_interval_width)))
            int_score = 1.0 - rel_width

        # Historical error score: lower error -> higher score
        hist_err_clamped = max(0.0, min(1.0, float(historical_error)))
        hist_score = 1.0 - hist_err_clamped

        raw_score = (
            self.w_agreement * ag_score
            + self.w_interval * int_score
            + self.w_historical * hist_score
        )
        clamped_score = float(max(0.0, min(1.0, raw_score)))

        return ConfidenceScore(
            score=round(clamped_score, 4),
            components={
                "agreement": round(ag_score, 4),
                "interval": round(int_score, 4),
                "historical": round(hist_score, 4),
            },
        )
