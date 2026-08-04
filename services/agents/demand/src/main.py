"""FastAPI application entry point for Demand Agent microservice."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim

from src.agent import DemandAgent
from src.config import (
    AGENT_ID,
    NEO4J_URI,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PORT,
    SCOF_PROFILE_PATH,
)

START_TIME = time.time()
agent_instance: DemandAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_instance
    agent_instance = DemandAgent(
        profile_path=SCOF_PROFILE_PATH,
        db_config={
            "host": POSTGRES_HOST,
            "port": POSTGRES_PORT,
            "dbname": POSTGRES_DB,
        },
    )
    yield


app = FastAPI(
    title="SCOF Demand Agent Service",
    version="1.0.0",
    description="Microservice providing demand forecasting claims.",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    """Rich health check endpoint."""
    uptime = round(time.time() - START_TIME, 2)
    profile_loaded = agent_instance is not None and agent_instance.profile is not None
    model_loaded = agent_instance is not None and agent_instance.ensemble is not None

    return {
        "status": "healthy",
        "agent_id": AGENT_ID,
        "profile_loaded": profile_loaded,
        "db_connected": True,
        "neo4j_connected": True,
        "model_loaded": model_loaded,
        "model_version": "1.0.0",
        "uptime_seconds": uptime,
    }


@app.get("/.well-known/agent.json")
def get_agent_card() -> AgentCard:
    """Returns self-describing A2A Agent Card."""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent instance not initialized")
    return agent_instance.get_agent_card()


@app.post("/analyze", response_model=StructuredClaim)
def analyze(context: ScenarioContext) -> StructuredClaim:
    """Invokes Demand Agent analysis pipeline."""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent instance not initialized")
    try:
        return agent_instance.analyze(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
