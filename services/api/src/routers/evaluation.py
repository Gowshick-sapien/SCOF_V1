from fastapi import APIRouter, HTTPException
from fastapi import APIRouter

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

@router.get("/benchmark")
async def get_benchmark():
    # Proxy to observability or mock for MVP
    return {"benchmark": "baseline_01", "accuracy": 0.95}

@router.get("/calibration")
async def get_calibration():
    # Proxy to observability or mock for MVP
    return {"calibration_runs": []}
