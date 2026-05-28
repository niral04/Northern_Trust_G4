from datetime import datetime
import json
import random
import time
import threading

from sqlalchemy.orm import Session

from models import Incident, Alert, TimelineEvent
from notifications import notify
from websocket_manager import schedule_broadcast
from lifecycle import validate_transition
from escalation import calculate_remaining_escalation_time
import audit_log

ESCALATION_CHAIN = {
    "infrastructure": {
        "critical": ["John (On-Call)", "Sarah (Senior Eng)", "Mike (Team Lead)", "Director + All"],
        "high":     ["John (On-Call)", "Sarah (Senior Eng)", "Mike (Team Lead)"]
    },
    "application": {
        "high":   ["App Support Team", "Senior Developer", "Team Lead"],
        "medium": ["App Support Team", "Senior Developer"],
        "low":    ["App Support Team"]
    }
}


def add_timeline_event(
    db: Session,
    incident_id: str,
    event_type: str,
    description: str,
    actor: str = "system",
    previous_assignee: str | None = None,
    new_assignee: str | None = None,
    escalation_level: int | None = None,
    metadata: dict | None = None,
):
    """
    Enterprise audit timeline entry with structured fields.
    Preserves legacy description text for backward compatibility.
    """
    event = TimelineEvent(
        incident_id=incident_id,
        event_type=event_type,
        description=description,
        actor=actor,
        previous_assignee=previous_assignee,
        new_assignee=new_assignee,
        escalation_level=escalation_level,
        event_metadata=json.dumps(metadata) if metadata else None,
    )
    db.add(event)
    db.commit()

    schedule_broadcast(
        "timeline_updated",
        {
            "incident_id": incident_id,
            "event_type": event_type,
            "description": description,
            "actor": actor,
            "timestamp": datetime.utcnow().isoformat(),
            "previous_assignee": previous_assignee,
            "new_assignee": new_assignee,
            "escalation_level": escalation_level,
            "metadata": metadata or {},
        },
    )


def _record_invalid_transition(
    db: Session,
    incident: Incident,
    target_status: str,
    actor: str,
    error_message: str,
):
    add_timeline_event(
        db,
        incident.incident_id,
        "INVALID_TRANSITION_ATTEMPT",
        error_message,
        actor=actor,
        metadata={"current_state": incident.status, "target_state": target_status},
    )
    audit_log.log_invalid_transition(
        incident.incident_id, incident.status, target_status, actor
    )
    schedule_broadcast(
        "invalid_transition_attempt",
        {
            "incident_id": incident.incident_id,
            "current_state": incident.status,
            "target_state": target_status,
            "message": error_message,
            "actor": actor,
        },
    )


def _enforce_transition(
    db: Session,
    incident: Incident,
    target_status: str,
    actor: str = "system",
) -> bool:
    try:
        validate_transition(incident.status, target_status)
        return True
    except ValueError as exc:
        _record_invalid_transition(db, incident, target_status, actor, str(exc))
        return False


def create_incident(db: Session, alert: Alert, classification: dict):
    count    = db.query(Incident).count() + 1
    inc_id   = f"INC-{count:03d}"

    incident = Incident(
        incident_id        = inc_id,
        alert_type         = alert.alert_type,
        severity           = classification["severity"],
        status             = "OPEN",
        source             = alert.source,
        message            = alert.message,
        assignee           = classification["assignee"],
        notify_channel     = classification["notify_channel"],
        escalation_timeout = classification["escalation_timeout"],
        escalation_level   = 0
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Legacy timeline events (kept for backward compatibility)
    add_timeline_event(db, inc_id, "CREATED",
        f"Alert received from {alert.source}")
    add_timeline_event(db, inc_id, "CLASSIFIED",
        f"Classified as {classification['severity'].upper()} {alert.alert_type} incident")
    add_timeline_event(db, inc_id, "NOTIFIED",
        f"Notification sent to {classification['assignee']} via {classification['notify_channel'].upper()}")

    # Enterprise audit events
    add_timeline_event(
        db, inc_id, "INCIDENT_CREATED",
        f"Incident {inc_id} opened from alert on {alert.source}",
        actor="alert-ingestion",
        new_assignee=classification["assignee"],
        escalation_level=0,
        metadata={"alert_type": alert.alert_type, "severity": classification["severity"]},
    )

    notify(incident, "new")

    channel = (classification.get("notify_channel") or "slack").lower()
    if channel == "slack":
        add_timeline_event(
            db, inc_id, "SLACK_NOTIFICATION_SENT",
            f"Slack alert dispatched to {classification['assignee']}",
            actor="notifier",
            new_assignee=classification["assignee"],
        )
    else:
        add_timeline_event(
            db, inc_id, "EMAIL_NOTIFICATION_SENT",
            f"Email alert dispatched to {classification['assignee']}",
            actor="notifier",
            new_assignee=classification["assignee"],
        )

    timing = calculate_remaining_escalation_time(incident)
    schedule_broadcast(
        "incident_created",
        {
            "incident_id": inc_id,
            "severity": incident.severity,
            "status": incident.status,
            "assignee": incident.assignee,
            "remaining_seconds": timing["remaining_seconds"],
            "escalation_level": timing["escalation_level"],
        },
    )
    schedule_broadcast("dashboard_stats_updated", {})

    return incident


def acknowledge_incident(db: Session, incident_id: str, engineer: str):
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()

    if not incident:
        return None

    if not _enforce_transition(db, incident, "ACKNOWLEDGED", engineer):
        return incident

    if incident.status not in ("OPEN", "ESCALATED"):
        return incident

    previous_assignee = incident.assignee
    incident.status          = "ACKNOWLEDGED"
    incident.acknowledged_at = datetime.utcnow()
    incident.assignee        = engineer
    db.commit()

    add_timeline_event(
        db, incident_id, "ACKNOWLEDGED",
        f"Acknowledged by {engineer}",
        actor=engineer,
        previous_assignee=previous_assignee,
        new_assignee=engineer,
        escalation_level=incident.escalation_level,
    )

    audit_log.log_acknowledgement(
        incident_id, engineer, previous_assignee, engineer
    )
    notify(incident, "acknowledged", engineer=engineer)

    schedule_broadcast(
        "incident_acknowledged",
        {
            "incident_id": incident_id,
            "status": incident.status,
            "assignee": engineer,
            "escalation_level": incident.escalation_level,
        },
    )
    schedule_broadcast("dashboard_stats_updated", {})

    return incident


def escalate_incident(
    db: Session,
    incident_id: str,
    reason="Manual escalation",
    actor: str = "system",
    auto: bool = False,
):
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()

    if not incident:
        return None

    if incident.status not in ("OPEN", "ACKNOWLEDGED", "ESCALATED"):
        return incident

    # Validate when moving from OPEN/ACKNOWLEDGED; re-escalation from ESCALATED is allowed
    if incident.status in ("OPEN", "ACKNOWLEDGED"):
        if not _enforce_transition(db, incident, "ESCALATED", actor):
            return incident

    chain = ESCALATION_CHAIN.get(incident.alert_type, {}).get(incident.severity, [])
    next_level = incident.escalation_level + 1

    if next_level >= len(chain):
        next_level = len(chain) - 1

    previous_assignee = incident.assignee
    escalated_to             = chain[next_level] if chain else previous_assignee
    incident.escalation_level = next_level
    incident.status           = "ESCALATED"
    incident.assignee         = escalated_to
    incident.last_escalated_at = datetime.utcnow()
    db.commit()

    timing = calculate_remaining_escalation_time(incident)
    event_type = "AUTO_ESCALATED" if auto else "ESCALATED"

    add_timeline_event(db, incident_id, "ESCALATED",
        f"Escalated to {escalated_to} — Reason: {reason}")
    add_timeline_event(
        db,
        incident_id,
        event_type,
        f"Level {next_level}: {previous_assignee} → {escalated_to}. {reason}",
        actor=actor,
        previous_assignee=previous_assignee,
        new_assignee=escalated_to,
        escalation_level=next_level,
        metadata={
            "reason": reason,
            "elapsed_seconds": timing["elapsed_seconds"],
            "auto": auto,
        },
    )

    audit_log.log_escalation(
        incident_id,
        reason,
        previous_assignee,
        escalated_to,
        next_level,
        elapsed_seconds=timing["elapsed_seconds"],
        actor=actor,
    )

    notify(incident, "escalation", escalated_to=escalated_to)

    schedule_broadcast(
        "incident_escalated",
        {
            "incident_id": incident_id,
            "status": incident.status,
            "assignee": escalated_to,
            "escalation_level": next_level,
            "remaining_seconds": timing["remaining_seconds"],
            "reason": reason,
            "auto": auto,
        },
    )
    schedule_broadcast("dashboard_stats_updated", {})

    return incident


def resolve_incident(db: Session, incident_id: str, notes: str = "Resolved", actor: str = "system"):
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()

    if not incident:
        return None

    if not _enforce_transition(db, incident, "RESOLVED", actor):
        return incident

    if incident:
        incident.status          = "RESOLVED"
        incident.resolved_at     = datetime.utcnow()
        incident.resolution_notes = notes

        if incident.created_at:
            diff = datetime.utcnow() - incident.created_at
            incident.mttr_minutes = int(diff.total_seconds() / 60)

        db.commit()

        add_timeline_event(
            db,
            incident_id,
            "RESOLVED",
            f"Resolved — {notes} — MTTR: {incident.mttr_minutes} mins",
            actor=actor,
            previous_assignee=incident.assignee,
            metadata={"mttr_minutes": incident.mttr_minutes},
        )

        audit_log.log_resolution(incident_id, actor, notes, incident.mttr_minutes)
        notify(incident, "resolved", mttr=incident.mttr_minutes)

        postmortem = generate_postmortem(db, incident_id)
        add_timeline_event(db, incident_id, "POSTMORTEM_GENERATED",
            "Post-mortem report automatically generated")
        print(postmortem)

        schedule_broadcast(
            "incident_resolved",
            {
                "incident_id": incident_id,
                "status": incident.status,
                "mttr_minutes": incident.mttr_minutes,
            },
        )
        schedule_broadcast("dashboard_stats_updated", {})

    return incident


def close_incident(db: Session, incident_id: str, actor: str = "system"):
    """RESOLVED → CLOSED lifecycle step."""
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()
    if not incident:
        return None

    if not _enforce_transition(db, incident, "CLOSED", actor):
        return incident

    incident.status = "CLOSED"
    db.commit()

    add_timeline_event(
        db,
        incident_id,
        "RESOLVED",
        "Incident closed after resolution",
        actor=actor,
        metadata={"final_state": "CLOSED"},
    )
    schedule_broadcast(
        "incident_resolved",
        {"incident_id": incident_id, "status": "CLOSED"},
    )
    return incident


def generate_postmortem(db: Session, incident_id: str):
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()

    timeline = db.query(TimelineEvent).filter(
        TimelineEvent.incident_id == incident_id
    ).order_by(TimelineEvent.created_at.asc()).all()

    report = f"""
POST-MORTEM REPORT — {incident.incident_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date:        {incident.created_at.strftime('%Y-%m-%d')}
Incident ID: {incident.incident_id}
Source:      {incident.source}
Severity:    {incident.severity.upper()}
Type:        {incident.alert_type.upper()}
Assignee:    {incident.assignee}
MTTR:        {incident.mttr_minutes} minutes

TIMELINE:
"""
    for event in timeline:
        report += f"  {event.created_at.strftime('%H:%M:%S')} → {event.event_type} — {event.description}\n"

    report += f"""
Root Cause:  {incident.message}
Resolution:  {incident.resolution_notes}
SLA Status:  {'✅ Within SLA' if incident.mttr_minutes and incident.mttr_minutes < 60 else '❌ SLA Breached'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return report


AUTO_REMEDIATION_MAP = {
    "server_status":    "restart_server",
    "cpu_usage":        "kill_high_cpu_processes",
    "disk_usage":       "clear_disk_space",
    "error_rate":       "restart_application_service",
    "packet_loss":      "reset_network_interface",
    "response_time":    "restart_application_service",
    "job_failure_rate": "restart_job_scheduler",
}

REMEDIATION_DURATION = {
    "restart_server":              8,
    "kill_high_cpu_processes":     5,
    "clear_disk_space":            6,
    "restart_application_service": 7,
    "reset_network_interface":     9,
    "restart_job_scheduler":       6,
}

SUCCESS_RATE = 0.40


def _do_remediation(incident_id: str, action: str, db_factory):
    db = db_factory()
    try:
        duration = REMEDIATION_DURATION.get(action, 6)

        add_timeline_event(
            db, incident_id,
            "REMEDIATION_STARTED",
            f"Auto-remediation triggered: {action} — attempting fix..."
        )

        time.sleep(duration)

        success = random.random() < SUCCESS_RATE

        if success:
            add_timeline_event(
                db, incident_id,
                "REMEDIATION_SUCCESS",
                f"Auto-remediation successful: {action} completed — service restored"
            )
            resolve_incident(
                db, incident_id,
                notes=f"Auto-resolved by remediation engine via action: {action}"
            )
        else:
            add_timeline_event(
                db, incident_id,
                "REMEDIATION_FAILED",
                f"Auto-remediation failed: {action} unsuccessful — escalating to engineer"
            )
            escalate_incident(
                db, incident_id,
                reason=f"Auto-remediation ({action}) failed — manual intervention required",
                auto=True,
            )
    finally:
        db.close()


def attempt_remediation(incident_id: str, metric: str, db_factory):
    action = AUTO_REMEDIATION_MAP.get(metric)
    if not action:
        return None

    thread = threading.Thread(
        target=_do_remediation,
        args=(incident_id, action, db_factory),
        daemon=True
    )
    thread.start()
    return action
