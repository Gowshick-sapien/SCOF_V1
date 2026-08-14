from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

class CalibrationMetricsPayload(BaseModel):
    id: str
    timestamp: datetime
    recommendation_kappa: Optional[float]
    escalation_tier_kappa: Optional[float]
    exact_match_rate: float
    confusion_breakdown: Dict[str, Any]
    sample_size: int
    pass_status: bool
    warnings: List[str]

class DecisionSearchRequest(BaseModel):
    query_text: str
    limit: int = 5
