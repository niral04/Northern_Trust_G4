from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Incident, TimelineEvent
import incident_engine
from escalation import calculate_remaining_escalation_time
from pydantic import BaseModel
import json

router = APIRouter()

class AckInput(BaseModel):
    engineer: str = "On-Call Engineer"

class ResolveInput(BaseModel):
    notes: str = "Issue resolved"

@router.get("/api/incidents")
def get_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(
        Incident.created_at.desc()
    ).all()
    return [incident_to_dict(i) for i in incidents]

@router.get("/api/incidents/active")
def get_active_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).filter(
        Incident.status.in_(["OPEN", "ACKNOWLEDGED", "ESCALATED"])
    ).order_by(Incident.created_at.desc()).all()
    return [incident_to_dict(i) for i in incidents]

@router.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()
    return incident_to_dict(incident)

@router.get("/api/incidents/{incident_id}/timeline")
def get_timeline(incident_id: str, db: Session = Depends(get_db)):
    events = db.query(TimelineEvent).filter(
        TimelineEvent.incident_id == incident_id
    ).order_by(TimelineEvent.created_at.asc()).all()
    return [timeline_to_dict(event) for event in events]

@router.put("/api/incidents/{incident_id}/acknowledge")
def acknowledge(incident_id: str, body: AckInput, db: Session = Depends(get_db)):
    incident = incident_engine.acknowledge_incident(db, incident_id, body.engineer)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident_to_dict(incident)

@router.put("/api/incidents/{incident_id}/escalate")
def escalate(incident_id: str, db: Session = Depends(get_db)):
    incident = incident_engine.escalate_incident(db, incident_id, "Manual escalation")
    return incident_to_dict(incident)

@router.put("/api/incidents/{incident_id}/resolve")
def resolve(incident_id: str, body: ResolveInput, db: Session = Depends(get_db)):
    incident = incident_engine.resolve_incident(db, incident_id, body.notes)
    return incident_to_dict(incident)

@router.get("/api/dashboard/stats")
def get_stats(db: Session = Depends(get_db)):
    return get_dashboard_stats_payload(db)


def get_dashboard_stats_payload(db: Session):
    all_incidents = db.query(Incident).all()
    resolved = [i for i in all_incidents if i.status == "RESOLVED"]
    mttr_list = [i.mttr_minutes for i in resolved if i.mttr_minutes]

    return {
        "total":        len(all_incidents),
        "open":         len([i for i in all_incidents if i.status == "OPEN"]),
        "acknowledged": len([i for i in all_incidents if i.status == "ACKNOWLEDGED"]),
        "escalated":    len([i for i in all_incidents if i.status == "ESCALATED"]),
        "resolved":     len(resolved),
        "critical":     len([i for i in all_incidents if i.severity == "critical"]),
        "high":         len([i for i in all_incidents if i.severity == "high"]),
        "medium":       len([i for i in all_incidents if i.severity == "medium"]),
        "avg_mttr":     round(sum(mttr_list) / len(mttr_list), 1) if mttr_list else 0,
        # Frontend KPI compatibility fields
        "activeIncidents": len([i for i in all_incidents if i.status in ("OPEN", "ACKNOWLEDGED", "ESCALATED")]),
        "criticalIncidents": len([i for i in all_incidents if i.severity == "critical"]),
        "mttrMinutes": round(sum(mttr_list) / len(mttr_list), 1) if mttr_list else 0,
        "automationRate": 72,
        "eventsPerMinute": 18,
        "slaCompliance": 94,
    }


def timeline_to_dict(event: TimelineEvent):
    metadata = {}
    if event.event_metadata:
        try:
            metadata = json.loads(event.event_metadata)
        except json.JSONDecodeError:
            metadata = {"raw": event.event_metadata}

    return {
        "id": event.id,
        "incident_id": event.incident_id,
        "event_type": event.event_type,
        "description": event.description,
        "actor": event.actor or "system",
        "timestamp": (event.created_at.isoformat() + "Z") if event.created_at else None,
        "time": event.created_at.strftime("%H:%M:%S") if event.created_at else None,
        "previous_assignee": event.previous_assignee,
        "new_assignee": event.new_assignee,
        "escalation_level": event.escalation_level,
        "metadata": metadata,
        # Legacy detail-page fields
        "action": event.description,
        "user": event.actor or "system",
        "type": _timeline_ui_type(event.event_type),
        "event": event.description,
    }


def _timeline_ui_type(event_type: str) -> str:
    event_type = (event_type or "").upper()
    if event_type in ("ESCALATED", "AUTO_ESCALATED"):
        return "escalation"
    if event_type in ("RESOLVED", "REMEDIATION_SUCCESS"):
        return "mitigation"
    if event_type == "ACKNOWLEDGED":
        return "acknowledgement"
    if event_type == "INVALID_TRANSITION_ATTEMPT":
        return "invalid"
    return "detection"


def _severity_label(severity: str) -> str:
    return (severity or "medium").capitalize()


def _status_label(status: str) -> str:
    return (status or "OPEN").lower()


def incident_to_dict(incident):
    if not incident:
        return None

    timing = calculate_remaining_escalation_time(incident)

    return {
        "id":                incident.incident_id,
        "incident_id":       incident.incident_id,
        "alert_type":        incident.alert_type,
        "severity":          _severity_label(incident.severity),
        "status":            _status_label(incident.status),
        "source":            incident.source,
        "message":           incident.message,
        "title":             incident.message,
        "service":           incident.source,
        "assignee":          incident.assignee,
        "owner":             incident.assignee,
        "notify_channel":    incident.notify_channel,
        "escalation_level":  incident.escalation_level,
        "escalation_timeout": incident.escalation_timeout,
        "escalation_timeout_seconds": timing["escalation_timeout_seconds"],
        "elapsed_seconds":   timing["elapsed_seconds"],
        "remaining_seconds": timing["remaining_seconds"],
        "created_at":        (incident.created_at.isoformat() + "Z") if incident.created_at else None,
        "createdAt":         (incident.created_at.isoformat() + "Z") if incident.created_at else None,
        "acknowledged_at":   (incident.acknowledged_at.isoformat() + "Z") if incident.acknowledged_at else None,
        "resolved_at":       (incident.resolved_at.isoformat() + "Z") if incident.resolved_at else None,
        "mttr_minutes":      incident.mttr_minutes,
    }


def _frontend_analytics_payload(db: Session):
    all_incidents = db.query(Incident).all()
    severity_counts = {}
    for incident in all_incidents:
        label = _severity_label(incident.severity)
        severity_counts[label] = severity_counts.get(label, 0) + 1

    severity_distribution = [
        {"name": name, "value": count}
        for name, count in severity_counts.items()
    ]

    recent_events = (
        db.query(TimelineEvent)
        .order_by(TimelineEvent.created_at.desc())
        .limit(12)
        .all()
    )
    timeline = [timeline_to_dict(event) for event in reversed(recent_events)]

    return {
        "severityDistribution": severity_distribution,
        "timeline": timeline,
        "serviceHealth": [
            {"service": "payment-api", "health": 82, "events": 14, "slo": 97},
            {"service": "auth-service", "health": 91, "events": 6, "slo": 99},
            {"service": "inventory-api", "health": 76, "events": 21, "slo": 95},
        ],
        "trend": [],
        "responseTimes": [],
    }


# ── Frontend compatibility routes (existing /api routes unchanged) ──

@router.get("/incidents")
def get_incidents_compat(db: Session = Depends(get_db)):
    return get_incidents(db)


@router.get("/incidents/{incident_id}")
def get_incident_compat(incident_id: str, db: Session = Depends(get_db)):
    return get_incident(incident_id, db)


@router.get("/incidents/{incident_id}/timeline")
def get_timeline_compat(incident_id: str, db: Session = Depends(get_db)):
    return get_timeline(incident_id, db)


@router.get("/analytics")
def get_analytics_compat(db: Session = Depends(get_db)):
    return {
        "success": True,
        "analytics": _frontend_analytics_payload(db),
    }


@router.get("/analytics/stats")
def get_analytics_stats_compat(db: Session = Depends(get_db)):
    return get_dashboard_stats_payload(db)
@router.get("/api/incidents/{incident_id}/postmortem")
def get_postmortem(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(
        Incident.incident_id == incident_id
    ).first()

    timeline = db.query(TimelineEvent).filter(
        TimelineEvent.incident_id == incident_id
    ).order_by(TimelineEvent.created_at.asc()).all()

    return {
        "incident_id":   incident.incident_id,
        "date":          str(incident.created_at.strftime('%Y-%m-%d')),
        "source":        incident.source,
        "severity":      incident.severity.upper(),
        "type":          incident.alert_type.upper(),
        "assignee":      incident.assignee,
        "mttr_minutes":  incident.mttr_minutes,
        "root_cause":    incident.message,
        "resolution":    incident.resolution_notes,
        "sla_status":    "Within SLA" if incident.mttr_minutes and incident.mttr_minutes < 60 else "SLA Breached",
        "timeline": [
            {
                "time":        event.created_at.strftime('%H:%M:%S'),
                "event_type":  event.event_type,
                "description": event.description
            }
            for event in timeline
        ]
    }