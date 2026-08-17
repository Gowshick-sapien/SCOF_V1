from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import uuid
import datetime
import json

from ..events.topics import TOPIC_DISRUPTIONS_TRIGGERED

# We need to get the event_bus and redis_client. We can import them from main but that causes circular dependency.
# Instead, we can attach them to request.app.state in main.py
def get_event_bus(request: Request):
    return request.app.state.event_bus

def get_redis(request: Request):
    return request.app.state.redis_client

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

class TriggerRequest(BaseModel):
    scenario_id: str

class ReplayRequest(BaseModel):
    event_id: str

@router.get("")
async def list_scenarios():
    # Placeholder for list of scenarios. Ideally from db or static.
    return {"scenarios": []}

@router.post("/trigger")
async def trigger_scenario(req: TriggerRequest, request: Request, bus=Depends(get_event_bus)):
    # 1. Fetch scenario context (Mocked for MVP, normally from DB)
    context = {
        "scenario_id": req.scenario_id,
        "disruption_type": "supplier_delay",
        "severity": 3,
        "run_id": str(uuid.uuid4())
    }
    
    trace_id = request.state.trace_id
    event_id = f"evt-{uuid.uuid4().hex}"
    
    envelope = {
        "event_id": event_id,
        "event_type": "disruption.triggered",
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
            "scenario_context": context
        }
    }
    
    redis_client = get_redis(request)
    await redis_client.setex(f"published_events:{event_id}", 604800, json.dumps(envelope))
    
    await bus.publish(TOPIC_DISRUPTIONS_TRIGGERED, key=req.scenario_id, envelope=envelope)
    
    return {"event_id": event_id, "trace_id": trace_id, "status": "TRIGGERED"}

@router.post("/replay")
async def replay_scenario(req: ReplayRequest, request: Request, bus=Depends(get_event_bus), redis_client=Depends(get_redis)):
    original_event_str = await redis_client.get(f"published_events:{req.event_id}")
    if not original_event_str:
        raise HTTPException(status_code=404, detail="Original event not found or expired")
        
    original_event = json.loads(original_event_str)
    
    new_event_id = f"evt-{uuid.uuid4().hex}"
    new_trace_id = request.state.trace_id
    
    new_envelope = {
        "event_id": new_event_id,
        "original_event_id": req.event_id,
        "event_type": original_event.get("event_type", "disruption.triggered"),
        "schema_version": "1.0.0",
        "producer": "scof-api",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "correlation": {
            "trace_id": new_trace_id,
            "scenario_id": original_event.get("correlation", {}).get("scenario_id", ""),
            "profile_version": original_event.get("correlation", {}).get("profile_version", "1.0.0"),
            "request_id": request.state.request_id
        },
        "payload": original_event.get("payload", {})
    }
    
    await redis_client.setex(f"published_events:{new_event_id}", 604800, json.dumps(new_envelope))
    
    topic = TOPIC_DISRUPTIONS_TRIGGERED # Or deduce from event_type
    key = new_envelope["correlation"]["scenario_id"]
    await bus.publish(topic, key=key, envelope=new_envelope)
    
    return {"event_id": new_event_id, "trace_id": new_trace_id, "status": "REPLAY_TRIGGERED"}
