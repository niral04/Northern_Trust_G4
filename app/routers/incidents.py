from fastapi import APIRouter

from app.models.schemas import IncidentAction
from app.services.incident_engine import (
    acknowledge_incident,
    escalate_incident,
    get_all_incidents,
    get_incident_by_id,
    resolve_incident,
)

router = APIRouter()


@router.get("/")
def incidents():
    return get_all_incidents()


@router.get("/{incident_id}")
def get_incident(incident_id: int):
    incident = get_incident_by_id(incident_id)

    if incident is None:
        return {"success": False, "message": "Incident not found"}

    return {"success": True, "incident": incident}


@router.put("/{incident_id}/acknowledge")
def acknowledge(incident_id: int, body: IncidentAction | None = None):
    body = body or IncidentAction()
    return acknowledge_incident(incident_id, body.actor, body.note)


@router.put("/{incident_id}/resolve")
def resolve(incident_id: int, body: IncidentAction | None = None):
    body = body or IncidentAction()
    return resolve_incident(incident_id, body.actor, body.note)


@router.put("/{incident_id}/escalate")
def escalate(incident_id: int, body: IncidentAction | None = None):
    body = body or IncidentAction()
    return escalate_incident(incident_id, body.actor, body.note)


@router.get("/{incident_id}/postmortem")
def postmortem(incident_id: int):
    incident = get_incident_by_id(incident_id)

    if incident is None:
        return {"success": False, "message": "Incident not found"}

    return {"success": True, "postmortem": incident["postmortem"]}
