"""FastAPI web service for SCOF Transportation Agent."""

import logging
import time
from typing import Dict, Any, List, Callable
from fastapi import FastAPI, HTTPException
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim
from scof_shared.protocols.mcp_server import create_mcp_router
from .agent import TransportAgent
from .config import get_config
from .mcp.tools import MCP_TOOL_DEFINITIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

START_TIME = time.time()
config = get_config()

# Global agent instance
agent: TransportAgent = TransportAgent(config=config)


def _handle_query_route_network(args: Dict[str, Any]) -> Dict[str, Any]:
    routes, q_hash = agent.data_access.get_route_graph_data(
        origin=args.get("origin_id"),
        destination=args.get("destination_id"),
    )
    return {"query_hash": q_hash, "routes": routes}


def _handle_estimate_delay(args: Dict[str, Any]) -> Dict[str, Any]:
    df, q_hash = agent.data_access.get_shipment_delivery_history(
        carrier_ids=[args.get("carrier_id")] if args.get("carrier_id") else None,
        route_ids=[args.get("route_id")] if args.get("route_id") else None,
    )
    return {"query_hash": q_hash, "record_count": len(df), "rows": df.to_dict(orient="records")}


def _handle_query_alternative_routes(args: Dict[str, Any]) -> Dict[str, Any]:
    alternates, q_hash = agent.data_access.get_alternate_routes(
        disrupted_route_id=args.get("disrupted_route_id", "route-101"),
        destination=args.get("destination_id"),
    )
    return {"query_hash": q_hash, "alternatives": alternates}


def _handle_read_transport_disruptions(args: Dict[str, Any]) -> Dict[str, Any]:
    disruptions, q_hash = agent.data_access.get_transport_disruptions(
        run_id=args.get("run_id"),
        scenario_id=args.get("scenario_id"),
    )
    return {"query_hash": q_hash, "disruptions": disruptions}


mcp_handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {
    "query_route_network": _handle_query_route_network,
    "estimate_delay": _handle_estimate_delay,
    "query_alternative_routes": _handle_query_alternative_routes,
    "read_transport_disruptions": _handle_read_transport_disruptions,
}

mcp_router = create_mcp_router(tools=MCP_TOOL_DEFINITIONS, execution_handlers=mcp_handlers)

app = FastAPI(
    title=config.name,
    version=config.version,
    description="Transportation Agent for delay prediction, route risk scoring, and carrier rerouting in SCOF.",
)

app.include_router(mcp_router)


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Rich health check endpoint."""
    uptime = round(time.time() - START_TIME, 2)
    profile_loaded = agent is not None and agent.profile is not None
    model_loaded = agent is not None and agent.ensemble is not None

    return {
        "status": "healthy",
        "agent_id": config.agent_id,
        "profile_loaded": profile_loaded,
        "db_connected": True,
        "neo4j_connected": True,
        "model_loaded": model_loaded,
        "model_version": config.version,
        "uptime_seconds": uptime,
    }


@app.get("/.well-known/agent.json", response_model=AgentCard)
def get_agent_card() -> AgentCard:
    """Agent discovery endpoint returning AgentCard."""
    return agent.get_agent_card()


@app.get("/tools")
def list_tools() -> List[Dict[str, Any]]:
    """Lists MCP tool specifications exposed by this agent."""
    return MCP_TOOL_DEFINITIONS


@app.post("/analyze", response_model=StructuredClaim)
def analyze(context: ScenarioContext) -> StructuredClaim:
    """Executes transportation analysis for given scenario context."""
    try:
        claim = agent.analyze(context)
        return claim
    except Exception as e:
        logger.exception("Error executing transportation analysis: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
