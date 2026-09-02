import argparse
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

from scof_shared.profile.loader import load_profile
from scof_shared.schemas.claim_bundle import ClaimBundle
from scof_shared.schemas.decision_record import DecisionRecord
from services.consensus.src.config import SCOF_PROFILE_PATH, ACCURACY_STORE_PATH, logger
from services.consensus.src.accuracy_tracker import AccuracyTracker
from services.consensus.src.engine import run_consensus

app = FastAPI(title="SCOF CD2F Consensus Engine")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "scof-consensus"}

# Global instances initialized on startup
profile = None
accuracy_tracker = None

@app.on_event("startup")
async def startup_event():
    global profile, accuracy_tracker
    logger.info(f"Loading domain profile from {SCOF_PROFILE_PATH}")
    profile = load_profile(SCOF_PROFILE_PATH)
    if not profile.consensus:
        raise ValueError("Profile does not contain consensus configuration.")
        
    logger.info(f"Initializing accuracy tracker at {ACCURACY_STORE_PATH}")
    accuracy_tracker = AccuracyTracker(
        store_path=ACCURACY_STORE_PATH,
        window_size=profile.consensus.accuracy.window_size,
        default_accuracy=profile.consensus.accuracy.default_accuracy
    )

class ArbitrationRequest(BaseModel):
    bundle: ClaimBundle

@app.post("/arbitrate", response_model=DecisionRecord)
async def arbitrate(request: ArbitrationRequest):
    if not profile or not accuracy_tracker:
        raise HTTPException(status_code=503, detail="Service not fully initialized.")
        
    try:
        decision = run_consensus(request.bundle, profile.consensus, accuracy_tracker)
        return decision
    except Exception as e:
        logger.error(f"Arbitration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def run_cli(fixture_path: str):
    logger.info(f"Running CLI against fixture {fixture_path}")
    prof = load_profile(SCOF_PROFILE_PATH)
    if not prof.consensus:
        logger.error("No consensus config found in profile.")
        return
        
    tracker = AccuracyTracker(
        store_path=ACCURACY_STORE_PATH,
        window_size=prof.consensus.accuracy.window_size,
        default_accuracy=prof.consensus.accuracy.default_accuracy
    )
    
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    bundle = ClaimBundle(**data)
    decision = run_consensus(bundle, prof.consensus, tracker)
    
    print(decision.model_dump_json(indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CD2F Consensus Engine")
    parser.add_argument("--fixture", type=str, help="Path to a fixture JSON file to arbitrate via CLI")
    args = parser.parse_args()
    
    if args.fixture:
        run_cli(args.fixture)
    else:
        uvicorn.run("services.consensus.src.main:app", host="0.0.0.0", port=8020, reload=True)
