from typing import Literal
from datetime import datetime
from pydantic import BaseModel

class MeetingLogEntry(BaseModel):
    step_index: int
    speaker: str
    statement_type: Literal["CLAIM", "WEIGHT_REPORT", "TALLY", "ESCALATION", "DECISION"]
    content: str
    timestamp: datetime
