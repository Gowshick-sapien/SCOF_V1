from typing import Dict, List
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # channel_name -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info(f"Client connected to {channel}. Total clients: {len(self.active_connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            try:
                self.active_connections[channel].remove(websocket)
                logger.info(f"Client disconnected from {channel}. Remaining clients: {len(self.active_connections[channel])}")
            except ValueError:
                pass

    async def broadcast(self, message: dict, channel: str):
        if channel not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to client on {channel}: {e}")
                disconnected.append(connection)
                
        for connection in disconnected:
            self.disconnect(connection, channel)

manager = ConnectionManager()
