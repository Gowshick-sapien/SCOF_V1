"""FastAPI application entry point for Supplier Intelligence Agent microservice."""

import time
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim

from scof_shared.protocols.mcp_server import create_mcp_router
from src.agent import SupplierAgent
from src.mcp.tools import SUPPLIER_MCP_TOOLS
from src.config import (
    AGENT_ID,
    NEO4J_URI,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PORT,
    SCOF_PROFILE_PATH,
)

START_TIME = time.time()
agent_instance: Optional[SupplierAgent] = None


def _handle_query_supplier_graph(args: dict) -> dict:
    if not agent_instance:
        raise RuntimeError("Supplier agent not initialized")
    lineage, q_hash = agent_instance.data_access.get_supplier_graph_data(
        product_id=args.get("product_id")
    )
    return {"query_hash": q_hash, "lineage": lineage}


def _handle_read_delivery_history(args: dict) -> dict:
    if not agent_instance:
        raise RuntimeError("Supplier agent not initialized")
    df, q_hash = agent_instance.data_access.get_supplier_delivery_history(
        run_id=args.get("run_id"),
        supplier_ids=args.get("supplier_ids"),
        limit_days=args.get("limit_days", 180),
    )
    return {"query_hash": q_hash, "record_count": len(df), "rows": df.to_dict(orient="records")}


def _handle_query_alternate_suppliers(args: dict) -> dict:
    if not agent_instance:
        raise RuntimeError("Supplier agent not initialized")
    alternates, q_hash = agent_instance.data_access.get_alternate_suppliers(
        supplier_id=args.get("supplier_id", "SUP-001"),
        product_id=args.get("product_id"),
    )
    return {"query_hash": q_hash, "alternates": alternates}


def _handle_read_supplier_disruptions(args: dict) -> dict:
    if not agent_instance:
        raise RuntimeError("Supplier agent not initialized")
    disruptions, q_hash = agent_instance.data_access.get_supplier_disruptions(
        run_id=args.get("run_id"),
        scenario_id=args.get("scenario_id"),
    )
    return {"query_hash": q_hash, "disruptions": disruptions}


mcp_handlers = {
    "query_supplier_graph": _handle_query_supplier_graph,
    "read_delivery_history": _handle_read_delivery_history,
    "query_alternate_suppliers": _handle_query_alternate_suppliers,
    "read_supplier_disruptions": _handle_read_supplier_disruptions,
}

mcp_router = create_mcp_router(tools=SUPPLIER_MCP_TOOLS, execution_handlers=mcp_handlers)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_instance
    agent_instance = SupplierAgent(
        profile_path=SCOF_PROFILE_PATH,
        db_config={
            "host": POSTGRES_HOST,
            "port": POSTGRES_PORT,
            "dbname": POSTGRES_DB,
        },
    )
    yield


app = FastAPI(
    title="SCOF Supplier Intelligence Agent Service",
    version="1.0.0",
    description="Microservice providing supplier reliability assessment and backup vendor recommendations.",
    lifespan=lifespan,
)

app.include_router(mcp_router)


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
    """Invokes Supplier Agent analysis pipeline."""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent instance not initialized")
    try:
        return agent_instance.analyze(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
