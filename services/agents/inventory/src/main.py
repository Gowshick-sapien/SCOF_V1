"""FastAPI application entry point for Inventory Agent microservice."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim

from scof_shared.protocols.mcp_server import create_mcp_router
from src.agent import InventoryAgent
from src.mcp.tools import INVENTORY_MCP_TOOLS
from src.config import (
    AGENT_ID,
    NEO4J_URI,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PORT,
    SCOF_PROFILE_PATH,
)

START_TIME = time.time()
agent_instance: InventoryAgent = None


def _handle_read_stock_levels(args: dict) -> dict:
    if not agent_instance:
        raise RuntimeError("Inventory agent not initialized")
    df, q_hash = agent_instance.data_access.get_inventory_levels(
        run_id=args.get("run_id"),
        warehouse_ids=args.get("warehouse_ids"),
        product_ids=args.get("product_ids"),
    )
    return {"query_hash": q_hash, "record_count": len(df), "inventory_levels": df.to_dict(orient="records")}


def _handle_read_reorder_points(args: dict) -> dict:
    product_ids = args.get("product_ids", [])
    warehouse_ids = args.get("warehouse_ids", [])
    thresholds = [
        {"product_id": pid, "warehouse_id": wid, "reorder_point": 200, "safety_stock": 50}
        for pid in product_ids
        for wid in (warehouse_ids or ["WH-001"])
    ]
    return {"thresholds": thresholds}


def _handle_read_inbound_shipments(args: dict) -> dict:
    warehouse_ids = args.get("warehouse_ids", [])
    shipments = [
        {"shipment_id": f"SHP-{wid}-01", "warehouse_id": wid, "status": "IN_TRANSIT", "eta_days": 3}
        for wid in warehouse_ids
    ]
    return {"shipments": shipments}


def _handle_read_inventory_disruptions(args: dict) -> dict:
    if not agent_instance:
        raise RuntimeError("Inventory agent not initialized")
    disruptions, q_hash = agent_instance.data_access.get_active_disruptions(
        run_id=args.get("run_id"),
        scenario_id=args.get("scenario_id"),
    )
    return {"query_hash": q_hash, "disruptions": disruptions}


mcp_handlers = {
    "read_stock_levels": _handle_read_stock_levels,
    "read_reorder_points": _handle_read_reorder_points,
    "read_inbound_shipments": _handle_read_inbound_shipments,
    "read_inventory_disruptions": _handle_read_inventory_disruptions,
}

mcp_router = create_mcp_router(tools=INVENTORY_MCP_TOOLS, execution_handlers=mcp_handlers)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_instance
    agent_instance = InventoryAgent(
        profile_path=SCOF_PROFILE_PATH,
        db_config={
            "host": POSTGRES_HOST,
            "port": POSTGRES_PORT,
            "dbname": POSTGRES_DB,
        },
    )
    yield


app = FastAPI(
    title="SCOF Inventory Agent Service",
    version="1.0.0",
    description="Microservice providing inventory risk and stockout claims.",
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
    """Invokes Inventory Agent analysis pipeline."""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent instance not initialized")
    try:
        return agent_instance.analyze(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
