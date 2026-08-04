"""MCP Tool Declarations for Demand Agent."""

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class MCPToolDescriptor:
    """Descriptor for an MCP tool declared by the Demand Agent."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


DEMAND_MCP_TOOLS: List[MCPToolDescriptor] = [
    MCPToolDescriptor(
        name="read_historical_demand",
        description="Reads historical sales and order demand time-series for specified products.",
        input_schema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "product_ids": {"type": "array", "items": {"type": "string"}},
                "limit_days": {"type": "integer", "default": 365},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "query_hash": {"type": "string"},
                "rows": {"type": "array"},
            },
        },
    ),
    MCPToolDescriptor(
        name="read_demand_disruptions",
        description="Reads active disruption events impacting demand (e.g. demand spikes).",
        input_schema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "scenario_id": {"type": "string"},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "query_hash": {"type": "string"},
                "disruptions": {"type": "array"},
            },
        },
    ),
    MCPToolDescriptor(
        name="read_product_catalog",
        description="Reads product metadata and SKU definitions.",
        input_schema={
            "type": "object",
            "properties": {
                "product_ids": {"type": "array", "items": {"type": "string"}},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "products": {"type": "array"},
            },
        },
    ),
]
