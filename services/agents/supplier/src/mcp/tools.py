"""MCP Tool Declarations for Supplier Intelligence Agent."""

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class MCPToolDescriptor:
    """Descriptor for an MCP tool declared by the Supplier Intelligence Agent."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


SUPPLIER_MCP_TOOLS: List[MCPToolDescriptor] = [
    MCPToolDescriptor(
        name="query_supplier_graph",
        description="Queries Neo4j graph for supplier upstream lineage, product supplies, and warehouse relationships.",
        input_schema={
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "query_hash": {"type": "string"},
                "lineage": {"type": "array"},
            },
        },
    ),
    MCPToolDescriptor(
        name="read_delivery_history",
        description="Reads historical purchase orders and shipment delivery performance records from PostgreSQL.",
        input_schema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "supplier_ids": {"type": "array", "items": {"type": "string"}},
                "limit_days": {"type": "integer", "default": 180},
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
        name="query_alternate_suppliers",
        description="Queries Neo4j graph for alternative suppliers supplying the same product with lead time and cost metrics.",
        input_schema={
            "type": "object",
            "properties": {
                "supplier_id": {"type": "string"},
                "product_id": {"type": "string"},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "query_hash": {"type": "string"},
                "alternates": {"type": "array"},
            },
        },
    ),
    MCPToolDescriptor(
        name="read_supplier_disruptions",
        description="Reads active disruption events impacting suppliers (e.g. supplier delay, factory shutdowns).",
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
