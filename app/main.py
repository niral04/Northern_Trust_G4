from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db

from fastapi import WebSocket
from app.services.websocket_manager import manager

from app.routers import alerts
from app.routers import incidents
from app.routers import analytics

app = FastAPI(title="Incident Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["Alerts"]
)

app.include_router(
    incidents.router,
    prefix="/incidents",
    tags=["Incidents"]
)

app.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

@app.get("/")
def home():

    return {
        "message": "IMS Backend Running"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await manager.connect(websocket)

    try:

        while True:

            data = await websocket.receive_text()

            print("Received:", data)

    except Exception as e:

        print("WebSocket Error:", e)

        manager.disconnect(websocket)