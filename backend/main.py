from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from database import engine, SessionLocal, migrate_schema
import models
from routes import alerts, incidents
from websocket_manager import manager
from models import Incident
import asyncio

# Create all tables and apply lightweight migrations
models.Base.metadata.create_all(bind=engine)
migrate_schema()

app = FastAPI(title="Incident Management System")

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(alerts.router)
app.include_router(incidents.router)

# Start escalation background jobs (existing 30s job preserved)
from escalation import check_escalations, broadcast_countdown_updates

scheduler = BackgroundScheduler()
scheduler.add_job(check_escalations, "interval", seconds=30)
# Live countdown websocket broadcasts every 2 seconds
scheduler.add_job(
    lambda: broadcast_countdown_updates(escalate_expired=True),
    "interval",
    seconds=2,
)
scheduler.start()


@app.on_event("startup")
async def startup_event():
    manager.set_event_loop(asyncio.get_running_loop())


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Push all active incidents every 2 seconds (existing behavior)
            db = SessionLocal()
            incidents_list = db.query(Incident).order_by(
                Incident.created_at.desc()
            ).all()

            from routes.incidents import incident_to_dict
            from routes.incidents import get_dashboard_stats_payload

            data = {
                "type": "update",
                "event": "dashboard_stats_updated",
                "incidents": [incident_to_dict(i) for i in incidents_list],
                "stats": get_dashboard_stats_payload(db),
            }
            db.close()

            await manager.broadcast(data)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
def root():
    return {"message": "Incident Management System Running"}
