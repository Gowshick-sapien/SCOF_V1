from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from .manager import manager

router = APIRouter(prefix="/ws", tags=["websocket"])
logger = logging.getLogger(__name__)

@router.websocket("/decisions/live")
async def websocket_decisions(websocket: WebSocket):
    await manager.connect(websocket, "decisions/live")
    try:
        while True:
            # We don't expect messages from client, but we must receive to handle disconnects
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "decisions/live")

@router.websocket("/agents/activity")
async def websocket_agents_activity(websocket: WebSocket):
    await manager.connect(websocket, "agents/activity")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "agents/activity")

@router.websocket("/dashboard/state")
async def websocket_dashboard_state(websocket: WebSocket):
    await manager.connect(websocket, "dashboard/state")
    try:
        from ..routers.dashboard import fetch_dashboard_state
        initial_state = await fetch_dashboard_state(websocket.app.state.redis_client)
        await websocket.send_json(initial_state)
        
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard/state")
