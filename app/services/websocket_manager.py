from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("WebSocket connected")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("WebSocket disconnected")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

    async def broadcast_event(self, event: str, payload: dict | None = None):
        """
        Structured event envelope for real-time updates.
        Example:
        {
            "event": "incident_created",
            "incident_id": 1
        }
        """
        message = {"event": event}

        if payload:
            message.update(payload)

        await self.broadcast(message)


manager = ConnectionManager()