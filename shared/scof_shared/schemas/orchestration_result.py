from typing import Optional
from pydantic import BaseModel
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.decision_record import DecisionRecord

class OrchestrationResult(BaseModel):
    claim_bundle: ClaimBundle
    decision_record: Optional[DecisionRecord] = None
