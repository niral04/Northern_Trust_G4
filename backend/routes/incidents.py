from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Incident, TimelineEvent
import incident_engine
from pydantic import BaseModel

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
    return events

@router.put("/api/incidents/{incident_id}/acknowledge")
def acknowledge(incident_id: str, body: AckInput, db: Session = Depends(get_db)):
    incident = incident_engine.acknowledge_incident(db, incident_id, body.engineer)
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
        "avg_mttr":     round(sum(mttr_list) / len(mttr_list), 1) if mttr_list else 0
    }

def incident_to_dict(incident):
    if not incident:
        return None
    return {
        "id":                incident.id,
        "incident_id":       incident.incident_id,
        "alert_type":        incident.alert_type,
        "severity":          incident.severity,
        "status":            incident.status,
        "source":            incident.source,
        "message":           incident.message,
        "assignee":          incident.assignee,
        "notify_channel":    incident.notify_channel,
        "escalation_level":  incident.escalation_level,
        "escalation_timeout":incident.escalation_timeout,
        "created_at":        str(incident.created_at),
        "acknowledged_at":   str(incident.acknowledged_at) if incident.acknowledged_at else None,
        "resolved_at":       str(incident.resolved_at) if incident.resolved_at else None,
        "mttr_minutes":      incident.mttr_minutes
        
    }
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