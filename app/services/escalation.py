import threading
import time
from datetime import datetime

from app.core.database import get_conn
from app.services.notifier import send_notification

# Severity-based timeout rules (seconds) — mirrors backend/escalation.py
SEVERITY_TIMEOUT_SECONDS = {
    "CRITICAL": 5 * 60,
    "HIGH": 10 * 60,
    "MEDIUM": 20 * 60,
    "LOW": 30 * 60,
}


def calculate_remaining_escalation_time(incident: dict) -> dict:
    """
    Compute countdown metadata for OPEN / ACKNOWLEDGED incidents (app stack).
    """
    severity = (incident.get("severity") or "MEDIUM").upper()
    timeout_seconds = SEVERITY_TIMEOUT_SECONDS.get(severity, 20 * 60)

    created_at = incident.get("created_at") or incident.get("updated_at")
    reference = datetime.fromisoformat(created_at) if created_at else datetime.utcnow()
    elapsed_seconds = max(0, int((datetime.utcnow() - reference).total_seconds()))
    remaining_seconds = max(0, timeout_seconds - elapsed_seconds)

    return {
        "incident_id": incident.get("id"),
        "escalation_level": incident.get("escalation_level", 0),
        "escalation_timeout_seconds": timeout_seconds,
        "elapsed_seconds": elapsed_seconds,
        "remaining_seconds": remaining_seconds,
    }


def auto_escalate(incident_id: int):

    def task():

        print(f"Monitoring Incident {incident_id}")

        # wait 60 seconds
        time.sleep(60)

        conn = get_conn()

        c = conn.cursor()

        # Check current incident status
        c.execute("""
        SELECT status
        FROM incidents
        WHERE id = ?
        """, (incident_id,))

        row = c.fetchone()

        if row is None:

            conn.close()

            return

        # Only escalate if still OPEN
        if row["status"] == "OPEN":

            now = datetime.utcnow().isoformat()

            c.execute("""
            UPDATE incidents
            SET status = ?,
                updated_at = ?
            WHERE id = ?
            """, (
                "ESCALATED",
                now,
                incident_id
            ))

            conn.commit()

            send_notification(
                "EMAIL",
                f"""
                INCIDENT AUTO ESCALATED

                Incident ID: {incident_id}
                """
            )

            print(f"Incident {incident_id} auto escalated")

        conn.close()

    threading.Thread(target=task).start()