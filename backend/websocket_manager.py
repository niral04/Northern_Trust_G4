from fastapi import WebSocket
from typing import List
import asyncio
import json
import audit_log


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._loop = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        """Original broadcast — unchanged for backward compatibility."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(data))
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_event(self, event: str, payload: dict | None = None):
        """
        Structured enterprise event envelope:
        { "event": "<name>", ...payload }
        """
        message = {"event": event}
        if payload:
            message.update(payload)
        audit_log.log_websocket_broadcast(event, message)
        await self.broadcast(message)

    def set_event_loop(self, loop):
        self._loop = loop

    def schedule_broadcast(self, event: str, payload: dict | None = None):
        """Thread-safe helper for sync code (scheduler, incident engine)."""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.broadcast_event(event, payload), self._loop
            )
            return

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.broadcast_event(event, payload))
        except RuntimeError:
            asyncio.run(self.broadcast_event(event, payload))


manager = WebSocketManager()


def schedule_broadcast(event: str, payload: dict | None = None):
    manager.schedule_broadcast(event, payload)
