from fastapi import APIRouter

from app.services.incident_engine import (
    get_all_incidents,
    get_incident_by_id,
    acknowledge_incident,
    resolve_incident,
    escalate_incident
)

router = APIRouter()


# ---------------------------------------------------
# GET ALL INCIDENTS
# ---------------------------------------------------
@router.get("/")
def incidents():

    return get_all_incidents()


# ---------------------------------------------------
# GET INCIDENT BY ID
# ---------------------------------------------------
@router.get("/{incident_id}")
def get_incident(incident_id: int):

    incident = get_incident_by_id(incident_id)

    if incident is None:

        return {
            "success": False,
            "message": "Incident not found"
        }

    return {
        "success": True,
        "incident": incident
    }


# ---------------------------------------------------
# ACKNOWLEDGE INCIDENT
# ---------------------------------------------------
@router.put("/{incident_id}/acknowledge")
def acknowledge(incident_id: int):

    return acknowledge_incident(incident_id)


# ---------------------------------------------------
# RESOLVE INCIDENT
# ---------------------------------------------------
@router.put("/{incident_id}/resolve")
def resolve(incident_id: int):

    return resolve_incident(incident_id)


# ---------------------------------------------------
# ESCALATE INCIDENT
# ---------------------------------------------------
@router.put("/{incident_id}/escalate")
def escalate(incident_id: int):

    return escalate_incident(incident_id)