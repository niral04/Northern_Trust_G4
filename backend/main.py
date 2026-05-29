from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from database import engine, SessionLocal
import models
from routes import alerts, incidents
from websocket_manager import manager
from models import Incident
import asyncio
import json

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Incident Management System")

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routes
app.include_router(alerts.router)
app.include_router(incidents.router)

# Start escalation background job
from escalation import check_escalations
scheduler = BackgroundScheduler()
scheduler.add_job(check_escalations, 'interval', seconds=30)
scheduler.start()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Push all active incidents every 2 seconds
            db = SessionLocal()
            incidents_list = db.query(Incident).order_by(
                Incident.created_at.desc()
            ).all()

            from routes.incidents import incident_to_dict
            from routes.incidents import get_stats
            resolved_with_mttr = [i.mttr_minutes for i in incidents_list 
                      if i.status == "RESOLVED" and i.mttr_minutes is not None]
 
            data = {
                "type": "update",
                "incidents": [incident_to_dict(i) for i in incidents_list],
                
                "stats": {
                    "total":      len(incidents_list),
                    "open":       len([i for i in incidents_list if i.status == "OPEN"]),
                    "escalated":  len([i for i in incidents_list if i.status == "ESCALATED"]),
                    "resolved":   len([i for i in incidents_list if i.status == "RESOLVED"]),
                    "critical":   len([i for i in incidents_list if i.severity == "critical"]),
                    "avg_mttr":   round(sum(resolved_with_mttr) / len(resolved_with_mttr), 2)
                      if resolved_with_mttr else None
                }
            }
            db.close()

            await manager.broadcast(data)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def root():
    return {"message": "Incident Management System Running"}