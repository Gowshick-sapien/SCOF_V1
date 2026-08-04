"""Claim Builder utility for SCOF agents.

Assembles StructuredClaim Pydantic objects from model outputs and evidence items.
Enforces the rule that computed confidence is never clamped or inflated. If confidence
falls below confidence_floor, low_confidence=True is set.
"""

from typing import List, Literal, Optional
from scof_shared.schemas.evidence import EvidenceItem
from scof_shared.schemas.structured_claim import StructuredClaim


class ClaimBuilder:
    """Fluent builder for constructing StructuredClaim objects safely."""

    def __init__(self, agent_id: str, scenario_id: str):
        self.agent_id = agent_id
        self.scenario_id = scenario_id
        self.recommendation: str = ""
        self.reasoning: str = ""
        self.confidence: float = 0.5
        self.priority: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
        self.impact: str = ""
        self.evidence: List[EvidenceItem] = []

    def set_recommendation(self, recommendation: str) -> "ClaimBuilder":
        self.recommendation = recommendation
        return self

    def set_reasoning(self, reasoning: str) -> "ClaimBuilder":
        self.reasoning = reasoning
        return self

    def set_confidence(self, score: float) -> "ClaimBuilder":
        self.confidence = max(0.0, min(1.0, float(score)))
        return self

    def set_priority(self, priority: Literal["HIGH", "MEDIUM", "LOW"]) -> "ClaimBuilder":
        self.priority = priority
        return self

    def set_impact(self, impact: str) -> "ClaimBuilder":
        self.impact = impact
        return self

    def add_evidence(
        self,
        type: Literal["historical_data", "model_output", "graph_query", "external_signal"],
        source: str,
        summary: str,
        reference_id: str,
        query_hash: Optional[str] = None,
    ) -> "ClaimBuilder":
        item = EvidenceItem(
            type=type,
            source=source,
            summary=summary,
            reference_id=reference_id,
            query_hash=query_hash,
        )
        self.evidence.append(item)
        return self

    def build(self, confidence_floor: float = 0.60) -> StructuredClaim:
        """Finalizes and returns a StructuredClaim.

        Sets low_confidence=True if self.confidence < confidence_floor,
        but NEVER alters the raw computed confidence score.
        """
        is_low_confidence = self.confidence < confidence_floor

        return StructuredClaim(
            agent_id=self.agent_id,
            scenario_id=self.scenario_id,
            recommendation=self.recommendation,
            reasoning=self.reasoning,
            confidence=self.confidence,
            low_confidence=is_low_confidence,
            priority=self.priority,
            impact=self.impact,
            evidence=self.evidence,
        )
