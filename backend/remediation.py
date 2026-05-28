
import time
import random
import threading
from datetime import datetime

from sqlalchemy.orm import Session

from database import SessionLocal
from models import Incident, TimelineEvent
from notifications import send_slack_notification


REMEDIATION_ACTIONS = {
    "server_status": "Restarting server",
    "cpu_usage": "Restarting application service",
    "packet_loss": "Restarting network adapter",
    "disk_usage": "Clearing temporary storage",
    "error_rate": "Restarting application container"
}


def add_timeline_event(db: Session, incident_id: str, event: str):
    timeline = TimelineEvent(
        incident_id=incident_id,
        event=event,
        timestamp=datetime.utcnow()
    )

    db.add(timeline)
    db.commit()


def auto_resolve_incident(db: Session, incident: Incident):
    incident.status = "RESOLVED"
    incident.resolved_at = datetime.utcnow()

    mttr_seconds = (
        incident.resolved_at - incident.created_at
    ).total_seconds()

    incident.mttr = round(mttr_seconds, 2)

    db.commit()

    add_timeline_event(
        db,
        incident.id,
        f"Incident auto-resolved in {incident.mttr} seconds"
    )

    send_slack_notification(
        f"✅ AUTO REMEDIATION SUCCESS\n"
        f"Incident {incident.id} resolved automatically\n"
        f"Source: {incident.source}\n"
        f"MTTR: {incident.mttr} seconds"
    )


def remediation_failed(db: Session, incident: Incident):
    add_timeline_event(
        db,
        incident.id,
        "Auto remediation failed"
    )

    send_slack_notification(
        f"⚠️ AUTO REMEDIATION FAILED\n"
        f"Incident {incident.id} requires manual intervention"
    )


def attempt_remediation(incident_id: str):
    db = SessionLocal()

    try:
        incident = db.query(Incident).filter(
            Incident.id == incident_id
        ).first()

        if not incident:
            return

        if incident.status != "OPEN":
            return

        action = REMEDIATION_ACTIONS.get(
            incident.metric,
            "Restarting service"
        )

        add_timeline_event(
            db,
            incident.id,
            f"Auto remediation started: {action}"
        )

        # simulate remediation time
        time.sleep(10)

        # 70% success rate
        success = random.random() < 0.7

        if success:
            add_timeline_event(
                db,
                incident.id,
                f"Auto remediation successful: {action}"
            )

            auto_resolve_incident(db, incident)

        else:
            remediation_failed(db, incident)

    except Exception as e:
        print("Remediation Error:", e)

    finally:
        db.close()


def start_auto_remediation(incident_id: str):
    remediation_thread = threading.Thread(
        target=attempt_remediation,
        args=(incident_id,)
    )

    remediation_thread.daemon = True
    remediation_thread.start()

