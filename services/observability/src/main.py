import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, status
from pydantic import BaseModel

from scof_shared.schemas.decision_record import DecisionRecord
from .models import CalibrationMetricsPayload, DecisionSearchRequest
from .database import init_db_pool, close_db_pool, get_db
from .decision_repo import DecisionRepository
from .calibration_repo import CalibrationRepository
import psycopg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Observability Backend, initializing DB pool...")
    await init_db_pool()
    yield
    logger.info("Shutting down Observability Backend, closing DB pool...")
    await close_db_pool()

app = FastAPI(
    title="SCOF Observability & Explainability Backend",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/decisions", status_code=status.HTTP_201_CREATED)
async def ingest_decision(
    decision: DecisionRecord,
    x_trace_id: str = Header(default="unknown"),
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """
    Ingest a new DecisionRecord from the CD2F engine.
    Idempotent operation using decision_id as primary key.
    """
    repo = DecisionRepository(db)
    try:
        await repo.save_decision(decision, x_trace_id)
        return {"status": "success", "decision_id": decision.decision_id}
    except Exception as e:
        logger.error(f"Failed to persist decision {decision.decision_id}: {e}")
        raise HTTPException(status_code=500, detail="Database persistence failed")

@app.get("/decisions")
async def list_decisions(
    limit: int = 50,
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """List recent decision records."""
    repo = DecisionRepository(db)
    return await repo.list_decisions(limit)

@app.get("/decisions/{decision_id}")
async def get_decision_trace(
    decision_id: str,
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """Fetch decision provenance and reasoning trail for replay."""
    repo = DecisionRepository(db)
    record = await repo.get_decision(decision_id)
    if not record:
        raise HTTPException(status_code=404, detail="Decision not found")
    return record

@app.get("/scenarios/{scenario_id}/decisions")
async def get_scenario_decisions(
    scenario_id: str,
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """Fetch all decisions for a given scenario."""
    repo = DecisionRepository(db)
    return await repo.get_decisions_by_scenario(scenario_id)

@app.post("/decisions/search")
async def search_similar_decisions(
    req: DecisionSearchRequest,
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """Semantic search for similar past decisions."""
    repo = DecisionRepository(db)
    return await repo.search_similar_decisions(req.query_text, req.limit)

@app.post("/calibration", status_code=status.HTTP_201_CREATED)
async def ingest_calibration(
    payload: CalibrationMetricsPayload,
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """Ingest complete calibration report."""
    repo = CalibrationRepository(db)
    try:
        await repo.save_calibration(payload)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to persist calibration: {e}")
        raise HTTPException(status_code=500, detail="Database persistence failed")

@app.get("/calibration/history")
async def get_calibration_history(
    limit: int = 10,
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """Retrieve calibration scores over time."""
    repo = CalibrationRepository(db)
    return await repo.get_calibration_history(limit)
