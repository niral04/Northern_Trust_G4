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
    """
    Resolve escalation timeout from severity.
    Falls back to DB-configured timeout if needed.
    """
    severity = (incident.severity or "medium").lower()

    if severity in SEVERITY_TIMEOUT_SECONDS:
        return SEVERITY_TIMEOUT_SECONDS[severity]

    if incident.escalation_timeout:
        return int(incident.escalation_timeout) * 60

    return SEVERITY_TIMEOUT_SECONDS["medium"]


def _reference_time(incident: Incident) -> datetime | None:
    """
    Determine the clock reference point for escalation countdown.
    """

    if incident.status == "ESCALATED" and incident.last_escalated_at:
        return incident.last_escalated_at

    if incident.status == "ACKNOWLEDGED" and incident.acknowledged_at:
        return incident.acknowledged_at

    return incident.created_at


def calculate_remaining_escalation_time(incident: Incident) -> dict:
    """
    Calculate escalation countdown metadata for active incidents.
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

    elapsed_seconds = int(
        max(
            0,
            (datetime.utcnow() - reference).total_seconds()
        )
    )

    remaining_seconds = int(
        max(
            0,
            timeout_seconds - elapsed_seconds
        )
    )

    return {
        "incident_id": incident.incident_id,
        "escalation_level": incident.escalation_level or 0,
        "escalation_timeout_seconds": timeout_seconds,
        "elapsed_seconds": elapsed_seconds,
        "remaining_seconds": remaining_seconds,
    }


def check_escalations():
    """
    Legacy scheduler hook.
    Runs countdown broadcast + auto escalation checks.
    """
    broadcast_countdown_updates(escalate_expired=True)


def broadcast_countdown_updates(escalate_expired: bool = False):
    """
    Broadcast live countdown updates for active incidents.

    Also triggers automatic escalation when timeout expires.
    """

    from websocket_manager import schedule_broadcast

    db = SessionLocal()

    try:
        active_incidents = db.query(Incident).filter(
            Incident.status.in_(["OPEN", "ACKNOWLEDGED"])
        ).all()

        for incident in active_incidents:

            timing = calculate_remaining_escalation_time(incident)

            # Broadcast live countdown update
            schedule_broadcast(
                "countdown_updated",
                {
                    "incident_id": timing["incident_id"],
                    "remaining_seconds": timing["remaining_seconds"],
                    "escalation_level": timing["escalation_level"],
                    "timeout_seconds": timing["escalation_timeout_seconds"],
                    "elapsed_seconds": timing["elapsed_seconds"],
                    "status": incident.status,
                },
            )

            # Auto escalation
            if (
                escalate_expired
                and timing["remaining_seconds"] <= 0
                and incident.status in ["OPEN", "ACKNOWLEDGED"]
            ):

                print(
                    f"[ESCALATION ENGINE] Auto escalating incident {incident.incident_id}"
                )

                audit_log.log_event(
                    "AUTO_ESCALATION_TRIGGERED",
                    {
                        "incident_id": incident.incident_id,
                        "severity": incident.severity,
                        "escalation_level": incident.escalation_level,
                    },
                )

                try:
                    incident_engine.escalate_incident(
                        db=db,
                        incident_id=incident.incident_id,
                        reason="Escalation timeout reached — no timely response",
                        actor="escalation-engine",
                        auto=True,
                    )

                    schedule_broadcast(
                        "incident_escalated",
                        {
                            "incident_id": incident.incident_id,
                            "message": "Incident auto escalated",
                        },
                    )

                except Exception as escalation_error:
                    print(
                        f"[ESCALATION ERROR] {incident.incident_id}: {str(escalation_error)}"
                    )

    finally:
        db.close()