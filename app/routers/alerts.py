from fastapi import APIRouter
from app.models.schemas import AlertCreate
from app.services.incident_engine import ingest_alert

router = APIRouter()

@router.post("/")
def create_alert(payload: AlertCreate):

    return ingest_alert(payload)