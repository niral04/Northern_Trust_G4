from datetime import datetime
from database import SessionLocal
from models import Incident
import incident_engine
import audit_log

# Severity-based escalation timeout rules (seconds)
SEVERITY_TIMEOUT_SECONDS = {
    "critical": 5 * 60,
    "high": 10 * 60,
    "medium": 20 * 60,
    "low": 30 * 60,
}


def get_escalation_timeout_seconds(incident: Incident) -> int:
    """Resolve timeout from severity; fall back to DB minutes field."""
    severity = (incident.severity or "medium").lower()
    if severity in SEVERITY_TIMEOUT_SECONDS:
        return SEVERITY_TIMEOUT_SECONDS[severity]
    if incident.escalation_timeout:
        return int(incident.escalation_timeout) * 60
    return SEVERITY_TIMEOUT_SECONDS["medium"]


def _reference_time(incident: Incident) -> datetime | None:
    """Clock start for countdown: last escalation, acknowledgement, or creation."""
    if incident.status == "ACKNOWLEDGED" and incident.acknowledged_at:
        return incident.acknowledged_at
    if incident.status == "ESCALATED" and incident.last_escalated_at:
        return incident.last_escalated_at
    return incident.created_at


def calculate_remaining_escalation_time(incident: Incident) -> dict:
    """
    Expose escalation timeout, elapsed, and remaining seconds for active incidents.
  """
    timeout_seconds = get_escalation_timeout_seconds(incident)
    reference = _reference_time(incident)

    if not reference:
        return {
            "incident_id": incident.incident_id,
            "escalation_level": incident.escalation_level or 0,
            "escalation_timeout_seconds": timeout_seconds,
            "elapsed_seconds": 0,
            "remaining_seconds": timeout_seconds,
        }

    elapsed_seconds = max(0, int((datetime.utcnow() - reference).total_seconds()))
    remaining_seconds = max(0, timeout_seconds - elapsed_seconds)

    return {
        "incident_id": incident.incident_id,
        "escalation_level": incident.escalation_level or 0,
        "escalation_timeout_seconds": timeout_seconds,
        "elapsed_seconds": elapsed_seconds,
        "remaining_seconds": remaining_seconds,
    }


def check_escalations():
    """
    Legacy scheduler hook — kept for backward compatibility.
    Runs countdown broadcast + auto-escalation pass.
    """
    broadcast_countdown_updates(escalate_expired=True)


def broadcast_countdown_updates(escalate_expired: bool = False):
    """
    Broadcast live countdown payloads for OPEN / ACKNOWLEDGED incidents.
    Called every few seconds from the scheduler.
    """
    from websocket_manager import schedule_broadcast

    db = SessionLocal()
    try:
        active_incidents = db.query(Incident).filter(
            Incident.status.in_(["OPEN", "ACKNOWLEDGED"])
        ).all()

        for incident in active_incidents:
            timing = calculate_remaining_escalation_time(incident)
            schedule_broadcast(
                "countdown_updated",
                {
                    "incident_id": timing["incident_id"],
                    "remaining_seconds": timing["remaining_seconds"],
                    "escalation_level": timing["escalation_level"],
                    "escalation_timeout_seconds": timing["escalation_timeout_seconds"],
                    "elapsed_seconds": timing["elapsed_seconds"],
                },
            )

            if escalate_expired and timing["remaining_seconds"] == 0:
                print(f"Auto-escalating {incident.incident_id} (countdown expired)")
                incident_engine.escalate_incident(
                    db,
                    incident.incident_id,
                    reason="Escalation timeout reached — no timely response",
                    actor="escalation-engine",
                    auto=True,
                )
    finally:
        db.close()
