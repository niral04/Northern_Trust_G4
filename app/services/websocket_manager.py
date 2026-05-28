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
        """Structured event envelope for enterprise real-time updates."""
        message = {"event": event}
        if payload:
            message.update(payload)
        await self.broadcast(message)

    def schedule_broadcast(self, event: str, payload: dict | None = None):
        import asyncio

        message = {"event": event, **(payload or {})}
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.broadcast_event(event, payload))
        except RuntimeError:
            asyncio.run(self.broadcast_event(event, payload))


manager = ConnectionManager()