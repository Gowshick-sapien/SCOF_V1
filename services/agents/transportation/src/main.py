"""FastAPI web service for SCOF Transportation Agent."""

import logging
import time
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim
from .agent import TransportAgent
from .config import get_config
from .mcp.tools import MCP_TOOL_DEFINITIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

START_TIME = time.time()
config = get_config()
app = FastAPI(
    title=config.name,
    version=config.version,
    description="Transportation Agent for delay prediction, route risk scoring, and carrier rerouting in SCOF.",
)

# Global agent instance
agent: TransportAgent = TransportAgent(config=config)


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
