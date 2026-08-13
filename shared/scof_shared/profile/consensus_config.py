from typing import Dict, Literal
from pydantic import BaseModel, Field, field_validator

class FastPathConfig(BaseModel):
    confidence_threshold: float = Field(..., ge=0.0, le=1.0)
    max_impact_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

class SlowPathConfig(BaseModel):
    min_confidence: float = Field(..., ge=0.0, le=1.0)
    max_impact_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

class HumanEscalationConfig(BaseModel):
    consensus_stability_min: float = Field(..., ge=0.0, le=1.0)
    impact_level_trigger: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

class CalibrationConfig(BaseModel):
    frequency: str
    min_kappa: float = Field(..., ge=0.0, le=1.0)

class PartialBundleConfig(BaseModel):
    min_participating_agents: int = Field(default=2, ge=1)

class AccuracyConfig(BaseModel):
    default_accuracy: float = Field(default=0.50, ge=0.0, le=1.0)
    window_size: int = Field(default=50, ge=1)

class ConsensusConfig(BaseModel):
    fast_path: FastPathConfig
    slow_path: SlowPathConfig
    human_escalation: HumanEscalationConfig
    calibration: CalibrationConfig
    partial_bundle: PartialBundleConfig = Field(default_factory=PartialBundleConfig)
    accuracy: AccuracyConfig = Field(default_factory=AccuracyConfig)
    impact_mapping: Dict[str, Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]]

    @field_validator("slow_path")
    @classmethod
    def validate_confidence_thresholds(cls, v: SlowPathConfig, info) -> SlowPathConfig:
        fast_path = info.data.get("fast_path")
        if fast_path and v.min_confidence >= fast_path.confidence_threshold:
            raise ValueError("slow_path.min_confidence must be less than fast_path.confidence_threshold")
        return v
