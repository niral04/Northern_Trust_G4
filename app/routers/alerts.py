from fastapi import APIRouter

from app.models.schemas import AlertCreate
from app.services.incident_engine import DEMO_ALERTS, ingest_alert

router = APIRouter()


@router.post("/")
def create_alert(payload: AlertCreate):
    return ingest_alert(payload)


@router.post("/simulate")
def simulate_alerts():
    created = [ingest_alert(AlertCreate(**alert)) for alert in DEMO_ALERTS]

    return {
        "success": True,
        "created": len(created),
        "incidents": [item["incident"] for item in created],
    }
