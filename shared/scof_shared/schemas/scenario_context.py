"""Scenario Context schema for agent invocation.

Common payload format sent by Coordinator to specialist agents.
"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class ScenarioContext(BaseModel):
    """Input payload context passed to specialist agents for analysis."""

    scenario_id: str = Field(..., description="Unique scenario identifier")
    run_id: Optional[str] = Field(None, description="Simulation run identifier")
    disruption_id: Optional[str] = Field(None, description="Disruption event ID if applicable")
    disruption_type: Optional[str] = Field(
        None, description="Type of disruption (e.g. demand_spike, supplier_delay)"
    )
    target_entity_type: Optional[str] = Field(
        None, description="Target entity category (e.g. product, supplier, warehouse)"
    )
    target_entity_id: Optional[str] = Field(
        None, description="Target entity ID affected by disruption"
    )
    severity: Optional[int] = Field(None, description="Disruption severity level")
    start_date: Optional[date] = Field(None, description="Analysis window start date")
    end_date: Optional[date] = Field(None, description="Analysis window end date")
    product_ids: Optional[List[str]] = Field(
        None, description="Filter list of product IDs to analyze"
    )
    warehouse_ids: Optional[List[str]] = Field(
        None, description="Filter list of warehouse IDs to analyze"
    )
