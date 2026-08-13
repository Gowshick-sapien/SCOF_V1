from typing import Dict, Any
from pydantic import Field, field_validator
from scof_shared.schemas.decision_record import DecisionRecord

class EvaluationDecision(DecisionRecord):
    is_comparator_only: bool = Field(default=True, frozen=True)
    baseline_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("decision_method")
    @classmethod
    def validate_baseline_method(cls, v: str) -> str:
        if v not in ("SINGLE_AGENT", "NAIVE_MAJORITY"):
            raise ValueError("EvaluationDecision must use a baseline decision_method")
        return v

