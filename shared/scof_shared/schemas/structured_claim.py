"""Structured Claim schema for SCOF agents.

Defines the primary contract returned by all specialist agents to the coordinator.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from scof_shared.schemas.evidence import EvidenceItem


class StructuredClaim(BaseModel):
    """Structured claim output representing an agent's assessment and recommendation."""

    agent_id: str = Field(..., description="Unique identifier of the issuing agent")
    scenario_id: str = Field(..., description="Scenario identifier context")
    recommendation: str = Field(..., description="Proposed mitigation or operational action")
    reasoning: str = Field(
        ..., description="Concise rationale summarizing why this recommendation was made"
    )
    confidence: float = Field(
        ..., description="Model computed confidence score in range [0.0, 1.0]"
    )
    low_confidence: bool = Field(
        False, description="True if confidence is below the agent confidence floor"
    )
    priority: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        "MEDIUM", description="Urgency level of the claim"
    )
    impact: str = Field(..., description="Estimated operational or financial impact")
    evidence: List[EvidenceItem] = Field(
        default_factory=list, description="Traceable evidence items supporting the claim"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when claim was generated",
    )

    @field_validator("confidence")
    @classmethod
    def validate_confidence_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {v}")
        return float(v)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize claim to dictionary."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuredClaim":
        """Deserialize claim from dictionary."""
        return cls(**data)
