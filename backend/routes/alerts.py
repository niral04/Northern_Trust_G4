import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, SessionLocal          # ← ADD SessionLocal here
from models import Alert
from classifer import classify_alert
import incident_engine
from pydantic import BaseModel

router = APIRouter()

class AlertInput(BaseModel):
    alert_type: str
    source:     str
    metric:     str
    value:      str
    message:    str
    severity:   str = "medium"

@router.post("/api/alerts")
def ingest_alert(alert_input: AlertInput, db: Session = Depends(get_db)):

    # Save raw alert
    alert = Alert(
        alert_type = alert_input.alert_type,
        source     = alert_input.source,
        metric     = alert_input.metric,
        value      = alert_input.value,
        message    = alert_input.message,
        severity   = alert_input.severity,
        processed  = "false"
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Classify
    classification = classify_alert(
        alert_input.alert_type,
        alert_input.metric,
        alert_input.value,
        alert_input.message
    )

    # Create incident
    incident = incident_engine.create_incident(db, alert, classification)

    # ← ADD THIS: trigger auto-remediation in background thread
    action = incident_engine.attempt_remediation(
        incident.incident_id,
        alert_input.metric,
        SessionLocal
    )

    # Mark alert processed
    alert.processed = "true"
    db.commit()

    return {
        "status":      "incident_created",
        "incident_id": incident.incident_id,
        "severity":    incident.severity,
        "assignee":    incident.assignee,
        "remediation": action if action else "no_action_available"   # ← ADD this line
    }

@router.get("/api/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.received_at.desc()).limit(50).all()
    return alerts