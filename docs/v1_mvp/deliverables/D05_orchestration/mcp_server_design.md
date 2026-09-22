# Deliverable D05 -- Model Context Protocol (MCP) Server Design

## 1. Executive Overview

This document specifies the **Model Context Protocol (MCP)** server integration for specialist AI agents in Deliverable D05. Per SRS FR-5.2, all specialist agents expose standardized MCP interfaces wrapping their domain-oriented data access and calculation tools.

The MCP integration allows the Coordinator, developer tooling, and automated evaluators to:
1. Discover declared business capabilities and tool schemas at runtime (`POST /mcp/tools/list`).
2. Execute domain-specific calculation and query tools with schema validation (`POST /mcp/tools/call`).
3. Maintain domain encapsulation: agents expose **business-level tools** (e.g. `read_historical_demand`, `query_supplier_reliability`, `estimate_delay`), strictly avoiding exposure of low-level generic database queries (`query_postgres`, `cypher_query`).

---

## 2. Standard MCP Protocol Endpoints

Each specialist agent mounts a standard MCP router (`shared/scof_shared/protocols/mcp_server.py`) with the following two endpoints:

### 2.1 Tool Discovery: `POST /mcp/tools/list`

- **Request**: Empty payload or optional capability filter.
- **Response**: List of tool descriptors conforming to MCP schema specification.

```json
{
  "tools": [
    {
      "name": "read_historical_demand",
      "description": "Reads historical sales and order demand time-series for specified products.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "run_id": {"type": "string", "description": "Simulation run identifier"},
          "product_ids": {"type": "array", "items": {"type": "string"}},
          "limit_days": {"type": "integer", "default": 365}
        },
        "required": ["run_id", "product_ids"]
      },
      "outputSchema": {
        "type": "object",
        "properties": {
          "query_hash": {"type": "string"},
          "rows": {"type": "array"}
        }
      }
    }
  ]
}
```

### 2.2 Tool Invocation: `POST /mcp/tools/call`

- **Request Contract**:
```json
{
  "name": "read_historical_demand",
  "arguments": {
    "run_id": "run-001",
    "product_ids": ["PROD-001", "PROD-002"],
    "limit_days": 90
  }
}
```

- **Response Contract (Success)**:
```json
{
  "content": [
    {
      "type": "json",
      "data": {
        "query_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "record_count": 90,
        "rows": [
          {"order_date": "2026-05-01", "quantity": 120, "product_id": "PROD-001"}
        ]
      }
    }
  ],
  "isError": false
}
```

- **Response Contract (Error)**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Tool 'unknown_tool' is not registered on this agent."
    }
  ],
  "isError": true
}
```

---

## 3. Domain Business Tools per Agent

Each specialist agent declares domain-oriented business tools matching its profile definition in [profiles/mvp-electronics/agents.yaml](file:///d:/projects/SCOF_V1/SCOF/profiles/mvp-electronics/agents.yaml):

### 3.1 Demand Forecast Agent (`demand-agent`, port 8011)

| Tool Name | Description | Required Arguments |
|:---|:---|:---|
| `read_historical_demand` | Retrieves historical order demand time-series | `run_id`, `product_ids` |
| `read_demand_disruptions` | Retrieves active demand spike / surge events | `run_id`, `scenario_id` |
| `read_product_catalog` | Retrieves SKU definitions and category metadata | `product_ids` |

### 3.2 Inventory Agent (`inventory-agent`, port 8012)

| Tool Name | Description | Required Arguments |
|:---|:---|:---|
| `read_stock_levels` | Retrieves current on-hand and safety stock | `run_id`, `product_ids` |
| `read_reorder_points` | Retrieves configured min/max reorder thresholds | `product_ids` |
| `read_inbound_shipments` | Retrieves scheduled inbound purchase orders | `run_id`, `product_ids` |
| `read_inventory_disruptions` | Retrieves warehouse stock loss / spoilage events | `run_id`, `scenario_id` |

### 3.3 Supplier Intelligence Agent (`supplier-agent`, port 8013)

| Tool Name | Description | Required Arguments |
|:---|:---|:---|
| `query_supplier_graph` | Queries Neo4j for supplier lineage and products | `supplier_id`, `product_id` |
| `read_delivery_history` | Retrieves historical purchase order fulfillment | `run_id`, `supplier_ids` |
| `query_alternate_suppliers` | Queries Neo4j for certified alternate vendors | `supplier_id`, `product_id` |
| `read_supplier_disruptions` | Retrieves supplier delay and shutdown events | `run_id`, `scenario_id` |

### 3.4 Transportation Agent (`transport-agent`, port 8014)

| Tool Name | Description | Required Arguments |
|:---|:---|:---|
| `query_route_network` | Queries Neo4j for transit route segments | `origin_id`, `destination_id` |
| `estimate_delay` | Computes ML + rule transit delay magnitude | `route_id`, `carrier_id` |
| `query_alternative_routes` | Queries Neo4j for shortest path detour routes | `origin_id`, `destination_id` |
| `read_transport_disruptions` | Retrieves port congestion / weather events | `run_id`, `scenario_id` |

---

## 4. MCP Server Implementation Architecture

The reusable MCP server router in `shared/scof_shared/protocols/mcp_server.py` wraps an agent's registered tool descriptors and execution callbacks:

```python
from typing import Any, Callable, Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


class MCPToolCallRequest(BaseModel):
    name: str = Field(..., description="Tool name to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments for tool execution")


class MCPToolResponseContent(BaseModel):
    type: str = "json"
    data: Optional[Any] = None
    text: Optional[str] = None


class MCPToolCallResponse(BaseModel):
    content: List[MCPToolResponseContent]
    isError: bool = False


def create_mcp_router(
    tools: List[Any],
    execution_handlers: Dict[str, Callable[[Dict[str, Any]], Any]],
) -> APIRouter:
    router = APIRouter(prefix="/mcp", tags=["MCP"])

    @router.post("/tools/list")
    def list_tools():
        return {"tools": [t.to_mcp_schema() for t in tools]}

    @router.post("/tools/call", response_model=MCPToolCallResponse)
    def call_tool(request: MCPToolCallRequest):
        handler = execution_handlers.get(request.name)
        if not handler:
            return MCPToolCallResponse(
                content=[MCPToolResponseContent(type="text", text=f"Tool '{request.name}' not found.")],
                isError=True,
            )
        try:
            result = handler(request.arguments)
            return MCPToolCallResponse(
                content=[MCPToolResponseContent(type="json", data=result)],
                isError=False,
            )
        except Exception as e:
            return MCPToolCallResponse(
                content=[MCPToolResponseContent(type="text", text=str(e))],
                isError=True,
            )

    return router
```

---

## 5. Security & Isolation Invariants

1. **Read-Only Data Access**: MCP tools in D05 execute read-only queries against PostgreSQL and Neo4j. No state mutation or synthetic data generation occurs via MCP.
2. **Schema Validation**: Arguments are validated against the declared JSON Schema before dispatch to internal data access handlers.
3. **Traceability**: All MCP responses include cryptographic `query_hash` identifiers linking back to PostgreSQL or Neo4j data records.
