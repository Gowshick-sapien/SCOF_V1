import logging
import httpx
from typing import Optional
from ..config import COORDINATOR_URL
from .topics import TOPIC_DECISIONS_COMPLETED, TOPIC_ORCHESTRATION_FAILED
from .bus import EventBus
from ..websocket.manager import ConnectionManager
import redis.asyncio as redis
import uuid
import datetime

logger = logging.getLogger(__name__)

async def handle_disruption_triggered(envelope: dict, bus: EventBus):
    """Execution Consumer: calls D05 orchestrate/full"""
    payload = envelope.get("payload", {})
    context = payload.get("scenario_context")
    correlation = envelope.get("correlation", {})
    trace_id = correlation.get("trace_id", str(uuid.uuid4()))
    
    if not context:
        raise ValueError("Missing scenario_context in payload")
        
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{COORDINATOR_URL}/orchestrate/full",
                json=context,
                headers={"X-Trace-ID": trace_id},
                timeout=30.0
            )
            resp.raise_for_status()
            result = resp.json()
            
            # Publish success to decisions.completed
            out_envelope = {
                "event_id": f"evt-{uuid.uuid4().hex}",
                "event_type": "decision.completed",
                "schema_version": "1.0.0",
                "producer": "scof-api",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "correlation": correlation,
                "payload": result
            }
            await bus.publish(TOPIC_DECISIONS_COMPLETED, key=result.get("claim_bundle", {}).get("scenario_id", ""), envelope=out_envelope)
            
        except Exception as e:
            logger.error(f"Failed to orchestrate disruption: {e}")
            out_envelope = {
                "event_id": f"evt-{uuid.uuid4().hex}",
                "event_type": "orchestration.failed",
                "schema_version": "1.0.0",
                "producer": "scof-api",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "correlation": correlation,
                "payload": {"status": "FAILED", "error": str(e), "scenario_context": context}
            }
            await bus.publish(TOPIC_ORCHESTRATION_FAILED, key=context.get("scenario_id", ""), envelope=out_envelope)

async def handle_whatif_requested(envelope: dict, bus: EventBus, redis_client: redis.Redis):
    """Execution Consumer: calls D05 orchestrate/full for whatif"""
    payload = envelope.get("payload", {})
    context = payload.get("scenario_context")
    whatif_id = payload.get("whatif_id")
    correlation = envelope.get("correlation", {})
    trace_id = correlation.get("trace_id", str(uuid.uuid4()))
    
    if not context or not whatif_id:
        raise ValueError("Missing scenario_context or whatif_id in payload")
        
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{COORDINATOR_URL}/orchestrate/full",
                json=context,
                headers={"X-Trace-ID": trace_id},
                timeout=30.0
            )
            resp.raise_for_status()
            result = resp.json()
            
            await redis_client.setex(f"whatif:{whatif_id}", 86400, "COMPLETED")
            
            out_envelope = {
                "event_id": f"evt-{uuid.uuid4().hex}",
                "event_type": "decision.completed",
                "schema_version": "1.0.0",
                "producer": "scof-api",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "correlation": correlation,
                "payload": result
            }
            await bus.publish(TOPIC_DECISIONS_COMPLETED, key=result.get("claim_bundle", {}).get("scenario_id", ""), envelope=out_envelope)
            
        except Exception as e:
            logger.error(f"Failed to orchestrate whatif: {e}")
            await redis_client.setex(f"whatif:{whatif_id}", 86400, "FAILED")
            out_envelope = {
                "event_id": f"evt-{uuid.uuid4().hex}",
                "event_type": "orchestration.failed",
                "schema_version": "1.0.0",
                "producer": "scof-api",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "correlation": correlation,
                "payload": {"status": "FAILED", "error": str(e), "scenario_context": context}
            }
            await bus.publish(TOPIC_ORCHESTRATION_FAILED, key=context.get("scenario_id", ""), envelope=out_envelope)

async def handle_decision_completed(envelope: dict, ws_manager: ConnectionManager, redis_client: redis.Redis):
    """Notification Consumer: broadcast decision"""
    await ws_manager.broadcast(envelope, "decisions/live")
    
    # Invalidate dashboard cache
    await redis_client.delete("dashboard:state")
    
    # Assembly logic should ideally fetch components and broadcast
    # Prepend this decision to recent decisions
    decision = envelope.get("payload", {}).get("decision_record", {})
    if decision:
        import json
        await redis_client.lpush("dashboard:recent_decisions", json.dumps(decision))
        await redis_client.ltrim("dashboard:recent_decisions", 0, 9)
    
    from ..routers.dashboard import fetch_dashboard_state
    fresh_state = await fetch_dashboard_state(redis_client)
    await ws_manager.broadcast(fresh_state, "dashboard/state")

async def handle_agent_activity(envelope: dict, ws_manager: ConnectionManager):
    """Notification Consumer: broadcast agent activity"""
    await ws_manager.broadcast(envelope, "agents/activity")

async def handle_orchestration_failed(envelope: dict, ws_manager: ConnectionManager):
    """Notification Consumer: broadcast failure"""
    # Send failure alert on decisions channel
    await ws_manager.broadcast(envelope, "decisions/live")
