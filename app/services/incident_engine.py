from datetime import datetime
import asyncio

from app.core.database import get_conn

from app.services.classifier import classify
from app.services.notifier import send_notification
from app.services.escalation import auto_escalate
from app.services.websocket_manager import manager


# ---------------------------------------------------
# CREATE INCIDENT FROM ALERT
# ---------------------------------------------------
def ingest_alert(payload):

    conn = get_conn()

    c = conn.cursor()

    now = datetime.utcnow().isoformat()

    # ---------------------------------------------------
    # STORE ALERT
    # ---------------------------------------------------
    c.execute("""
    INSERT INTO alerts(
        source,
        type,
        severity,
        message,
        created_at
    )
    VALUES(?,?,?,?,?)
    """, (
        payload.source,
        payload.type.value,
        payload.severity.value,
        payload.message,
        now
    ))

    alert_id = c.lastrowid

    if alert_id is None:

        conn.close()

        raise Exception("Alert creation failed")

    alert_id = int(alert_id)

    # ---------------------------------------------------
    # CLASSIFY INCIDENT
    # ---------------------------------------------------
    priority, workflow_path = classify(
        payload.type.value,
        payload.severity.value
    )

    title = f"[{payload.type.value}] {payload.message}"

    # ---------------------------------------------------
    # CREATE INCIDENT
    # ---------------------------------------------------
    c.execute("""
    INSERT INTO incidents(
        alert_id,
        title,
        alert_type,
        severity,
        priority,
        status,
        assignee,
        workflow_path,
        created_at,
        updated_at
    )
    VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (
        alert_id,
        title,
        payload.type.value,
        payload.severity.value,
        priority,
        "OPEN",
        "OnCallEngineer",
        workflow_path,
        now,
        now
    ))

    incident_id = c.lastrowid

    if incident_id is None:

        conn.close()

        raise Exception("Incident creation failed")

    incident_id = int(incident_id)

    conn.commit()

    conn.close()

    # ---------------------------------------------------
    # SEND NOTIFICATION
    # ---------------------------------------------------
    send_notification(
        "SLACK",
        f"""
        INCIDENT CREATED

        Incident ID: {incident_id}
        Severity: {payload.severity.value}
        Priority: {priority}
        Status: OPEN
        """
    )

    # ---------------------------------------------------
    # START AUTO ESCALATION TIMER
    # ---------------------------------------------------
    auto_escalate(incident_id)

    # ---------------------------------------------------
    # WEBSOCKET REALTIME EVENT
    # ---------------------------------------------------
    try:

        loop = asyncio.get_event_loop()

        loop.create_task(
            manager.broadcast({
                "event": "NEW_INCIDENT",
                "incident_id": incident_id,
                "severity": payload.severity.value,
                "priority": priority,
                "status": "OPEN"
            })
        )

    except Exception as e:

        print("WebSocket Error:", e)

    # ---------------------------------------------------
    # RESPONSE
    # ---------------------------------------------------
    return {
        "success": True,
        "incident_id": incident_id,
        "alert_id": alert_id,
        "status": "OPEN",
        "priority": priority,
        "workflow": workflow_path,
        "message": "Incident created successfully"
    }


# ---------------------------------------------------
# GET ALL INCIDENTS
# ---------------------------------------------------
def get_all_incidents():

    conn = get_conn()

    c = conn.cursor()

    c.execute("""
    SELECT * FROM incidents
    ORDER BY created_at DESC
    """)

    rows = c.fetchall()

    incidents = [dict(row) for row in rows]

    conn.close()

    return incidents


# ---------------------------------------------------
# GET INCIDENT BY ID
# ---------------------------------------------------
def get_incident_by_id(incident_id: int):

    conn = get_conn()

    c = conn.cursor()

    c.execute("""
    SELECT * FROM incidents
    WHERE id = ?
    """, (incident_id,))

    row = c.fetchone()

    conn.close()

    if row is None:

        return None

    return dict(row)


# ---------------------------------------------------
# UPDATE INCIDENT STATUS
# ---------------------------------------------------
def update_incident_status(
    incident_id: int,
    status: str
):

    conn = get_conn()

    c = conn.cursor()

    now = datetime.utcnow().isoformat()

    c.execute("""
    UPDATE incidents
    SET status = ?,
        updated_at = ?
    WHERE id = ?
    """, (
        status,
        now,
        incident_id
    ))

    conn.commit()

    c.execute("""
    SELECT * FROM incidents
    WHERE id = ?
    """, (incident_id,))

    row = c.fetchone()

    conn.close()

    if row is None:

        return {
            "success": False,
            "message": "Incident not found"
        }

    incident = dict(row)

    # ---------------------------------------------------
    # SEND NOTIFICATION
    # ---------------------------------------------------
    send_notification(
        "EMAIL",
        f"""
        INCIDENT UPDATED

        Incident ID: {incident_id}
        New Status: {status}
        """
    )

    # ---------------------------------------------------
    # WEBSOCKET STATUS UPDATE
    # ---------------------------------------------------
    try:

        loop = asyncio.get_event_loop()

        loop.create_task(
            manager.broadcast({
                "event": "INCIDENT_UPDATED",
                "incident_id": incident_id,
                "status": status
            })
        )

    except Exception as e:

        print("WebSocket Error:", e)

    return {
        "success": True,
        "incident": incident
    }


# ---------------------------------------------------
# ACKNOWLEDGE INCIDENT
# ---------------------------------------------------
def acknowledge_incident(incident_id: int):

    return update_incident_status(
        incident_id,
        "ACKNOWLEDGED"
    )


# ---------------------------------------------------
# RESOLVE INCIDENT
# ---------------------------------------------------
def resolve_incident(incident_id: int):

    return update_incident_status(
        incident_id,
        "RESOLVED"
    )


# ---------------------------------------------------
# ESCALATE INCIDENT
# ---------------------------------------------------
def escalate_incident(incident_id: int):

    return update_incident_status(
        incident_id,
        "ESCALATED"
    )