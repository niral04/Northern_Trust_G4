from datetime import timedelta
from database import SessionLocal
from models import Incident, ist_now                      # ← add ist_now
import incident_engine

def check_escalations():
    db = SessionLocal()
    try:
        open_incidents = db.query(Incident).filter(
            Incident.status.in_(["OPEN", "ESCALATED"])
        ).all()

        for incident in open_incidents:
            timeout_mins   = incident.escalation_timeout
            reference_time = incident.last_escalated_at or incident.created_at

            if not reference_time:
                continue

            elapsed      = ist_now() - reference_time     # ← changed
            elapsed_mins = elapsed.total_seconds() / 60

            if elapsed_mins >= timeout_mins:
                print(f"Auto-escalating {incident.incident_id}")
                incident_engine.escalate_incident(
                    db,
                    incident.incident_id,
                    reason=f"No acknowledgement in {timeout_mins} minutes"
                )
    finally:
        db.close()