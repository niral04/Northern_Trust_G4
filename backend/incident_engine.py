from datetime import datetime
from sqlalchemy.orm import Session
from models import Incident, Alert, TimelineEvent
from notifications import notify
from websocket_manager import manager
import asyncio
import random

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

def acknowledge_incident(db: Session, incident_id: str, engineer: str):
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()

    if incident and incident.status == "OPEN" or incident.status == "ESCALATED":
        incident.status          = "ACKNOWLEDGED"
        incident.acknowledged_at = datetime.utcnow()
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

    escalated_to             = chain[next_level]
    incident.escalation_level = next_level
    incident.status           = "ESCALATED"
    incident.assignee         = escalated_to
    incident.last_escalated_at = datetime.utcnow()
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
        incident.status          = "RESOLVED"
        incident.resolved_at     = datetime.utcnow()
        incident.resolution_notes = notes

        if incident.created_at:
            diff = datetime.utcnow() - incident.created_at
            incident.mttr_minutes = int(diff.total_seconds() / 60)

        db.commit()

        # RESOLVED timeline first
        add_timeline_event(db, incident_id, "RESOLVED",
            f"Resolved — {notes} — MTTR: {incident.mttr_minutes} mins")

        notify(incident, "resolved", mttr=incident.mttr_minutes)

        # POSTMORTEM after resolved
        postmortem = generate_postmortem(db, incident_id)
        add_timeline_event(db, incident_id, "POSTMORTEM_GENERATED",
            "Post-mortem report automatically generated")
        print(postmortem)

        add_timeline_event(db, incident_id, "RESOLVED",
            f"Resolved — {notes} — MTTR: {incident.mttr_minutes} mins")

        notify(incident, "resolved", mttr=incident.mttr_minutes)
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