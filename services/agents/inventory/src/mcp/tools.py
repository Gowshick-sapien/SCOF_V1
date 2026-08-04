"""MCP Tool Declarations for Inventory Agent."""

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class MCPToolDescriptor:
    """Descriptor for an MCP tool declared by the Inventory Agent."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


INVENTORY_MCP_TOOLS: List[MCPToolDescriptor] = [
    MCPToolDescriptor(
        name="read_stock_levels",
        description="Reads current and historical inventory stock levels across warehouses.",
        input_schema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "warehouse_ids": {"type": "array", "items": {"type": "string"}},
                "product_ids": {"type": "array", "items": {"type": "string"}},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "query_hash": {"type": "string"},
                "inventory_levels": {"type": "array"},
            },
        },
    ),
    MCPToolDescriptor(
        name="read_reorder_points",
        description="Reads safety stock and reorder point thresholds per product and warehouse.",
        input_schema={
            "type": "object",
            "properties": {
                "product_ids": {"type": "array", "items": {"type": "string"}},
                "warehouse_ids": {"type": "array", "items": {"type": "string"}},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "thresholds": {"type": "array"},
            },
        },
    ),
    MCPToolDescriptor(
        name="read_inbound_shipments",
        description="Reads pending shipment arrivals and in-transit inventory.",
        input_schema={
            "type": "object",
            "properties": {
                "warehouse_ids": {"type": "array", "items": {"type": "string"}},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "shipments": {"type": "array"},
            },
        },
    ),
    MCPToolDescriptor(
        name="read_inventory_disruptions",
        description="Reads active disruptions affecting supplier delivery or warehouse operations.",
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
]
