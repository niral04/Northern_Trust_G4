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


manager = ConnectionManager()