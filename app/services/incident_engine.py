from datetime import datetime

from app.core.database import get_conn
from app.services.classifier import classify
from app.services.notifier import send_notification


def utc_now():
    return datetime.utcnow().isoformat()


def _row_to_dict(row):
    return dict(row) if row else None


def _add_timeline_event(cursor, incident_id: int, stage: str, event_type: str, description: str, actor: str):
    cursor.execute("""
    INSERT INTO timeline_events(
        incident_id,
        stage,
        event_type,
        description,
        actor,
        created_at
    )
    VALUES(?,?,?,?,?,?)
    """, (
        incident_id,
        stage,
        event_type,
        description,
        actor,
        utc_now(),
    ))


def _get_timeline(cursor, incident_id: int):
    cursor.execute("""
    SELECT * FROM timeline_events
    WHERE incident_id = ?
    ORDER BY created_at ASC, id ASC
    """, (incident_id,))
    return [dict(row) for row in cursor.fetchall()]


def _get_notifications(cursor, incident_id: int):
    cursor.execute("""
    SELECT * FROM notifications
    WHERE incident_id = ?
    ORDER BY created_at ASC, id ASC
    """, (incident_id,))
    return [dict(row) for row in cursor.fetchall()]


def _hydrate_incident(cursor, incident):
    if incident is None:
        return None

    hydrated = dict(incident)
    incident_id = hydrated["id"]
    hydrated["timeline"] = _get_timeline(cursor, incident_id)
    hydrated["notifications"] = _get_notifications(cursor, incident_id)
    hydrated["postmortem"] = build_postmortem(hydrated, hydrated["timeline"])
    return hydrated


def _fetch_incident(cursor, incident_id: int):
    cursor.execute("""
    SELECT * FROM incidents
    WHERE id = ?
    """, (incident_id,))
    return _row_to_dict(cursor.fetchone())


def _notification_targets(incident):
    channel = incident["notification_channel"] or "Email"
    assignee = incident["assignee"] or "On-call"

    if "SMS" in channel:
        return [("SMS", assignee), ("Slack", "#infra-incidents")]
    if "Slack" in channel:
        return [("Slack", "#incident-response"), ("Email", assignee)]
    return [("Email", assignee)]


def _notify_incident(incident_id: int, subject: str, message: str):
    conn = get_conn()
    c = conn.cursor()
    incident = _fetch_incident(c, incident_id)
    conn.close()

    if not incident:
        return []

    notifications = []
    for channel, recipient in _notification_targets(incident):
        notifications.append(
            send_notification(
                incident_id,
                channel,
                recipient,
                f"{subject}: {message}",
            )
        )
    return notifications


def ingest_alert(payload):
    now = utc_now()
    alert_type = payload.type.value
    severity = payload.severity.value
    service = payload.service or ("edge-network" if alert_type == "INFRA" else "checkout-api")
    route = classify(alert_type, severity, service)
    title = f"[{alert_type}] {payload.message}"

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO alerts(
        source,
        type,
        severity,
        service,
        metric,
        value,
        message,
        created_at
    )
    VALUES(?,?,?,?,?,?,?,?)
    """, (
        payload.source,
        alert_type,
        severity,
        service,
        payload.metric,
        payload.value,
        payload.message,
        now,
    ))
    alert_id = c.lastrowid

    c.execute("""
    INSERT INTO incidents(
        alert_id,
        title,
        description,
        alert_type,
        severity,
        priority,
        status,
        service,
        assignee,
        workflow_path,
        notification_channel,
        escalation_level,
        sla_minutes,
        remediation_action,
        created_at,
        updated_at
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        alert_id,
        title,
        payload.message,
        alert_type,
        severity,
        route["priority"],
        "OPEN",
        service,
        route["assignee"],
        route["workflow_path"],
        route["notification_channel"],
        0,
        route["sla_minutes"],
        route["remediation_action"],
        now,
        now,
    ))
    incident_id = c.lastrowid

    _add_timeline_event(
        c,
        incident_id,
        "detection",
        "ALERT_INGESTED",
        f"Alert from {payload.source} for {service}: {payload.message}",
        "Monitoring",
    )
    _add_timeline_event(
        c,
        incident_id,
        "triage",
        "CLASSIFIED",
        f"Classified as {severity} {alert_type}; routed to {route['workflow_path']} with {route['priority']} priority",
        "Classifier",
    )
    _add_timeline_event(
        c,
        incident_id,
        "remediation",
        "RUNBOOK_ATTACHED",
        route["remediation_action"],
        "Workflow Engine",
    )

    conn.commit()
    incident = _hydrate_incident(c, _fetch_incident(c, incident_id))
    conn.close()

    _notify_incident(
        incident_id,
        "Incident created",
        f"{title} | Priority {route['priority']} | Owner {route['assignee']}",
    )

    return {
        "success": True,
        "incident_id": incident_id,
        "alert_id": alert_id,
        "status": "OPEN",
        "priority": route["priority"],
        "workflow": route["workflow_path"],
        "incident": get_incident_by_id(incident_id),
        "message": "Incident created successfully",
    }


def get_all_incidents():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    SELECT * FROM incidents
    ORDER BY
      CASE priority
        WHEN 'P1' THEN 1
        WHEN 'P2' THEN 2
        WHEN 'P3' THEN 3
        ELSE 4
      END,
      created_at DESC
    """)
    incidents = [_hydrate_incident(c, row) for row in c.fetchall()]
    conn.close()
    return incidents


def get_incident_by_id(incident_id: int):
    conn = get_conn()
    c = conn.cursor()
    incident = _hydrate_incident(c, _fetch_incident(c, incident_id))
    conn.close()
    return incident


def update_incident_status(incident_id: int, status: str, actor: str = "Dashboard User", note: str | None = None):
    status = status.upper()
    now = utc_now()
    conn = get_conn()
    c = conn.cursor()

    incident = _fetch_incident(c, incident_id)
    if incident is None:
        conn.close()
        return {"success": False, "message": "Incident not found"}

    updates = ["status = ?", "updated_at = ?"]
    params = [status, now]

    if status == "ACKNOWLEDGED":
        updates.append("acknowledged_at = COALESCE(acknowledged_at, ?)")
        params.append(now)
    if status == "RESOLVED":
        updates.append("resolved_at = COALESCE(resolved_at, ?)")
        updates.append("resolution_notes = ?")
        params.extend([now, note or "Resolved from dashboard"])

    params.append(incident_id)
    c.execute(f"""
    UPDATE incidents
    SET {', '.join(updates)}
    WHERE id = ?
    """, params)

    stage = "resolution" if status == "RESOLVED" else "triage"
    _add_timeline_event(
        c,
        incident_id,
        stage,
        status,
        note or f"Incident marked {status}",
        actor,
    )

    conn.commit()
    updated = _hydrate_incident(c, _fetch_incident(c, incident_id))
    conn.close()

    _notify_incident(incident_id, f"Incident {status.lower()}", note or f"Incident {incident_id} is now {status}")

    return {"success": True, "incident": get_incident_by_id(incident_id)}


def acknowledge_incident(incident_id: int, actor: str = "On-call Engineer", note: str | None = None):
    return update_incident_status(incident_id, "ACKNOWLEDGED", actor, note or "Owner acknowledged the incident")


def resolve_incident(incident_id: int, actor: str = "On-call Engineer", note: str | None = None):
    return update_incident_status(incident_id, "RESOLVED", actor, note or "Service restored and validation completed")


def escalate_incident(incident_id: int, actor: str = "Escalation Engine", note: str | None = None):
    now = utc_now()
    conn = get_conn()
    c = conn.cursor()

    incident = _fetch_incident(c, incident_id)
    if incident is None:
        conn.close()
        return {"success": False, "message": "Incident not found"}

    next_level = int(incident.get("escalation_level") or 0) + 1
    assignee = "Senior Infrastructure Engineer" if incident["alert_type"] == "INFRA" else "Application Support Lead"

    c.execute("""
    UPDATE incidents
    SET status = 'ESCALATED',
        escalation_level = ?,
        assignee = ?,
        updated_at = ?
    WHERE id = ?
    """, (next_level, assignee, now, incident_id))

    _add_timeline_event(
        c,
        incident_id,
        "escalation",
        "ESCALATED",
        note or f"Escalated to level {next_level}: {assignee}",
        actor,
    )

    conn.commit()
    conn.close()

    _notify_incident(incident_id, "Incident escalated", f"Incident {incident_id} escalated to {assignee}")

    return {"success": True, "incident": get_incident_by_id(incident_id)}


def build_postmortem(incident, timeline):
    created = incident.get("created_at")
    resolved = incident.get("resolved_at")
    mttr_minutes = None

    if created and resolved:
        try:
            mttr_minutes = round((datetime.fromisoformat(resolved) - datetime.fromisoformat(created)).total_seconds() / 60, 1)
        except ValueError:
            mttr_minutes = None

    return {
        "incident_id": incident.get("id"),
        "service": incident.get("service"),
        "severity": incident.get("severity"),
        "priority": incident.get("priority"),
        "owner": incident.get("assignee"),
        "root_cause": incident.get("description"),
        "resolution": incident.get("resolution_notes") or "Pending resolution",
        "mttr_minutes": mttr_minutes,
        "sla_status": "Pending" if mttr_minutes is None else ("Within SLA" if mttr_minutes <= (incident.get("sla_minutes") or 60) else "SLA Breached"),
        "timeline": timeline,
    }


DEMO_ALERTS = [
    {
        "source": "Prometheus",
        "type": "INFRA",
        "severity": "CRITICAL",
        "service": "payments-db-primary",
        "metric": "host_up",
        "value": "0",
        "message": "Primary payments database host is unreachable",
    },
    {
        "source": "CloudWatch",
        "type": "INFRA",
        "severity": "HIGH",
        "service": "edge-network",
        "metric": "packet_loss",
        "value": "35%",
        "message": "Packet loss above threshold on edge network",
    },
    {
        "source": "Sentry",
        "type": "APP",
        "severity": "HIGH",
        "service": "checkout-api",
        "metric": "error_rate",
        "value": "18%",
        "message": "Checkout API error rate spike detected",
    },
    {
        "source": "Grafana",
        "type": "APP",
        "severity": "MEDIUM",
        "service": "login-service",
        "metric": "latency_p95",
        "value": "2200ms",
        "message": "Login service latency is above baseline",
    },
]
