# Test models
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional, Any
from datetime import datetime

class AnalyticalCapabilityContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    capability_name: str
    domain: str
    input_parameters: dict[str, Any]
    timeout_ms: int = 500
    is_deterministic: bool = True

class ForecastEnsembleOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    sku_id: str
    location_id: str
    horizon_days: int
    point_forecast: float
    p10_forecast: float
    p50_forecast: float
    p90_forecast: float
    component_models: dict[str, float]
    model_agreement: float
    computed_at: datetime
    execution_time_ms: float

class TriggerThreshold(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    metric_name: str
    domain: str
    warning_threshold: float
    critical_threshold: float
    evaluation_window_minutes: int
    min_consecutive_breaches: int = 2

class DomainSignal(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    signal_id: str
    domain: str
    metric_name: str
    observed_value: float
    baseline_value: float
    variance_pct: float
    severity: Literal['INFO', 'WARNING', 'CRITICAL']
    detected_at: datetime

class IssueProposal(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    issue_id: str
    originating_agent_id: str
    domain: str
    primary_signal: DomainSignal
    impacted_entities: list[str]
    proposed_scope: list[str]
    created_at: datetime
