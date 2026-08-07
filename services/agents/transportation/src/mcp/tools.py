"""MCP Tool specifications and definitions for Transportation Agent."""

from typing import Dict, Any, List


MCP_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "query_route_network",
        "description": "Queries Neo4j knowledge graph for route topology, transit time, cost, and carrier.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "origin_id": {"type": "string", "description": "Origin node ID (e.g., sup-01, port-la)"},
                "destination_id": {"type": "string", "description": "Destination node ID (e.g., wh-01)"},
                "transport_mode": {"type": "string", "description": "Transport mode filter (ocean, road, rail, air)"},
            },
        },
    },
    {
        "name": "estimate_delay",
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
        "name": "query_alternative_routes",
        "description": "Finds and ranks alternate transport routes/modes avoiding a disrupted corridor.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "disrupted_route_id": {"type": "string", "description": "ID of the disrupted transport route"},
                "destination_id": {"type": "string", "description": "Target destination node ID (e.g., wh-01)"},
            },
            "required": ["disrupted_route_id"],
        },
    },
    {
        "name": "read_transport_disruptions",
        "description": "Reads active disruption events impacting routes, ports, or carriers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "scenario_id": {"type": "string"},
            },
        },
    },
]
