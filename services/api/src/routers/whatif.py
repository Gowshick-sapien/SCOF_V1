from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime
import json

from ..events.topics import TOPIC_WHATIF_REQUESTED

def get_event_bus(request: Request):
    return request.app.state.event_bus

def get_redis(request: Request):
    return request.app.state.redis_client

router = APIRouter(prefix="/whatif", tags=["whatif"])

class WhatIfRequest(BaseModel):
    scenario_id: str
    severity_override: Optional[int] = None

@router.post("/run")
async def run_whatif(req: WhatIfRequest, request: Request, bus=Depends(get_event_bus), redis_client=Depends(get_redis)):
    whatif_id = f"wi-{uuid.uuid4().hex[:8]}"
    trace_id = request.state.trace_id
    
    # In a real impl, fetch base scenario context and apply overrides via ScenarioContextBuilder
    # For MVP, mock context
    context = {
        "scenario_id": req.scenario_id,
        "disruption_type": "whatif_simulation",
        "severity": req.severity_override or 3,
        "run_id": str(uuid.uuid4())
    }
    
    await redis_client.setex(f"whatif:{whatif_id}", 86400, "RUNNING")
    
    event_id = f"evt-{uuid.uuid4().hex}"
    
    envelope = {
        "event_id": event_id,
        "event_type": "whatif.requested",
        "schema_version": "1.0.0",
        "producer": "scof-api",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "correlation": {
            "trace_id": trace_id,
            "scenario_id": req.scenario_id,
            "profile_version": "1.0.0",
            "request_id": request.state.request_id
        },
        "payload": {
            "scenario_context": context,
            "whatif_id": whatif_id
        }
    }
    
    await redis_client.setex(f"published_events:{event_id}", 604800, json.dumps(envelope))
    await bus.publish(TOPIC_WHATIF_REQUESTED, key=whatif_id, envelope=envelope)
    
    return {"whatif_id": whatif_id, "trace_id": trace_id, "status": "RUNNING"}

@router.get("/{whatif_id}/result")
async def get_whatif_result(whatif_id: str, redis_client=Depends(get_redis)):
    status = await redis_client.get(f"whatif:{whatif_id}")
    if not status:
        raise HTTPException(status_code=404, detail="What-If simulation not found")
        
    return {"whatif_id": whatif_id, "status": status}
