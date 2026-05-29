from models import Incident, Alert, TimelineEvent, ist_now
from datetime import datetime
from sqlalchemy.orm import Session
from models import Incident, Alert, TimelineEvent
from notifications import notify
from websocket_manager import manager
import asyncio
import random

import time
import threading

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

def add_timeline_event(db: Session, incident_id: str, event_type: str, description: str):
    event = TimelineEvent(
        incident_id=incident_id,
        event_type=event_type,
        description=description
    )
    db.add(event)
    db.commit()

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

    add_timeline_event(db, inc_id, "CREATED",
        f"Alert received from {alert.source}")
    add_timeline_event(db, inc_id, "CLASSIFIED",
        f"Classified as {classification['severity'].upper()} {alert.alert_type} incident")
    add_timeline_event(db, inc_id, "NOTIFIED",
        f"Notification sent to {classification['assignee']} via {classification['notify_channel'].upper()}")

    notify(incident, "new")
    return incident

from models import Incident, Alert, TimelineEvent, ist_now

def acknowledge_incident(db: Session, incident_id: str, engineer: str):
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()

    if incident and incident.status in ["OPEN", "ESCALATED"]:
        incident.status          = "ACKNOWLEDGED"
        incident.acknowledged_at = ist_now()              # ← changed
        incident.assignee        = engineer
        db.commit()

        add_timeline_event(db, incident_id, "ACKNOWLEDGED",
            f"Acknowledged by {engineer}")
    return incident

def escalate_incident(db: Session, incident_id: str, reason="Manual escalation"):
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()

    if not incident:
        return None

    chain = ESCALATION_CHAIN.get(incident.alert_type, {}).get(incident.severity, [])
    next_level = incident.escalation_level + 1

    if next_level >= len(chain):
        next_level = len(chain) - 1

    escalated_to               = chain[next_level]
    incident.escalation_level  = next_level
    incident.status            = "ESCALATED"
    incident.assignee          = escalated_to
    incident.last_escalated_at = ist_now()                # ← changed
    db.commit()

    add_timeline_event(db, incident_id, "ESCALATED",
        f"Escalated to {escalated_to} — Reason: {reason}")

    notify(incident, "escalation", escalated_to=escalated_to)
    return incident

def resolve_incident(db: Session, incident_id: str, notes: str = "Resolved"):
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()

    if incident:
        incident.status           = "RESOLVED"
        incident.resolved_at      = ist_now()             # ← changed
        incident.resolution_notes = notes

        if incident.created_at:
            diff = ist_now() - incident.created_at        # ← changed
            incident.mttr_minutes = round(
                diff.total_seconds() / 60, 2
            )

        db.commit()

        add_timeline_event(db, incident_id, "RESOLVED",
            f"Resolved — {notes} — MTTR: {incident.mttr_minutes} mins")

        notify(incident, "resolved", mttr=incident.mttr_minutes)

        postmortem = generate_postmortem(db, incident_id)
        add_timeline_event(db, incident_id, "POSTMORTEM_GENERATED",
            "Post-mortem report automatically generated")
        print(postmortem)

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




# Maps each metric to a remediation action name
AUTO_REMEDIATION_MAP = {
    "server_status":    "restart_server",
    "cpu_usage":        "kill_high_cpu_processes",
    "disk_usage":       "clear_disk_space",
    "error_rate":       "restart_application_service",
    "packet_loss":      "reset_network_interface",
    "response_time":    "restart_application_service",
    "job_failure_rate": "restart_job_scheduler",
}

# How long (seconds) to simulate the fix taking
REMEDIATION_DURATION = {
    "restart_server":              8,
    "kill_high_cpu_processes":     5,
    "clear_disk_space":            6,
    "restart_application_service": 7,
    "reset_network_interface":     9,
    "restart_job_scheduler":       6,
}

# 70 % success rate for demo realism
SUCCESS_RATE = 0.35


def _do_remediation(incident_id: str, action: str, db_factory):
    """
    Runs in a background thread.
    db_factory is a callable that returns a fresh DB session (use SessionLocal).
    """
    db = db_factory()
    try:
        duration = REMEDIATION_DURATION.get(action, 6)

        # Log: remediation started
        add_timeline_event(
            db, incident_id,
            "REMEDIATION_STARTED",
            f"Auto-remediation triggered: {action} — attempting fix..."
        )

        time.sleep(duration)      # simulate the fix running

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
                reason=f"Auto-remediation ({action}) failed — manual intervention required"
            )
    finally:
        db.close()


def attempt_remediation(incident_id: str, metric: str, db_factory):
    """
    Call this right after create_incident().
    Looks up the right action for the metric and starts a background thread.
    Returns the action name if triggered, or None.
    """
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