from fastapi import APIRouter, Request, Depends
import json

def get_redis(request: Request):
    return request.app.state.redis_client

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

async def fetch_dashboard_state(redis_client):
    state = await redis_client.get("dashboard:state")
    if state:
        return json.loads(state)
        
    decisions = await redis_client.lrange("dashboard:recent_decisions", 0, 9)
    parsed_decisions = [json.loads(d) for d in decisions] if decisions else []
    
    mock_state = {
        "active_alerts": [],
        "system_health": "nominal",
        "recent_decisions": parsed_decisions,
        "active_disruptions": len(parsed_decisions)
    }
    await redis_client.setex("dashboard:state", 5, json.dumps(mock_state))
    return mock_state

@router.get("/state")
async def get_dashboard_state(redis_client=Depends(get_redis)):
    return await fetch_dashboard_state(redis_client)
