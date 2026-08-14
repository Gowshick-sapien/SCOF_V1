"""Evidence schema for SCOF claims.

Provides machine-traceable and human-readable evidence models for structured claims.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Traceable evidence backing an agent's claim or recommendation."""

    type: Literal["historical_data", "model_output", "graph_query", "external_signal"] = Field(default= ..., description="Type of evidence source"
    )
    source: str = Field(..., description="Human-readable description of evidence origin")
    summary: str = Field(..., description="Human-readable evidence summary or finding")
    reference_id: str = Field(default= ..., description="Machine-traceable identifier (e.g. inventory_level:4567, shipment:882)"
    )
    query_hash: Optional[str] = Field(default=None, description="SHA-256 hash of the query or calculation that generated this evidence"
    )
