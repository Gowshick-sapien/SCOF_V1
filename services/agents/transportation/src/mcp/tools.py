"""MCP Tool specifications and handler stubs for Transportation Agent."""

from typing import Dict, Any, List


MCP_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "get_route_details",
        "description": "Queries Neo4j knowledge graph for route topology, transit time, cost, and carrier.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Origin node ID (e.g., sup-01, port-la)"},
                "destination": {"type": "string", "description": "Destination node ID (e.g., wh-01)"},
                "transport_mode": {"type": "string", "description": "Transport mode filter (ocean, road, rail, air)"},
            },
        },
    },
    {
        "name": "get_carrier_performance",
        "description": "Queries PostgreSQL shipment history for carrier delivery metrics and on-time performance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "carrier_id": {"type": "string", "description": "Carrier ID or name (e.g., carrier-01, PacificFreight)"},
                "days_back": {"type": "integer", "description": "Number of days of history to query", "default": 90},
            },
            "required": ["carrier_id"],
        },
    },
    {
        "name": "predict_shipment_delay",
        "description": "Runs Transportation ML ensemble to predict transit delay in days for a route given active conditions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "route_id": {"type": "string", "description": "Route ID (e.g., route-101)"},
                "carrier_id": {"type": "string", "description": "Carrier ID (e.g., carrier-01)"},
                "weather_severity": {"type": "integer", "description": "Weather disruption severity 0-5", "default": 0},
            },
            "required": ["route_id"],
        },
    },
    {
        "name": "recommend_alternate_route",
        "description": "Finds and ranks alternate transport routes/modes avoiding a disrupted corridor.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "disrupted_route_id": {"type": "string", "description": "ID of the disrupted transport route"},
                "destination": {"type": "string", "description": "Target destination node ID (e.g., wh-01)"},
            },
            "required": ["disrupted_route_id"],
        },
    },
]
