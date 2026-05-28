from collections import Counter, defaultdict
from datetime import datetime

from fastapi import APIRouter

from app.core.database import get_conn

router = APIRouter()

SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


def _title(value):
    return value.title() if value else "Unknown"


def _parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _fetch_incidents():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM incidents ORDER BY created_at DESC")
    incidents = [dict(row) for row in c.fetchall()]
    c.execute("SELECT COUNT(*) as total FROM alerts")
    total_alerts = c.fetchone()["total"]
    conn.close()
    return incidents, total_alerts


def _severity_distribution(incidents):
    counts = Counter(item["severity"] for item in incidents)
    return [
        {"name": _title(severity), "value": counts.get(severity, 0)}
        for severity in SEVERITIES
    ]


def _trend(incidents):
    buckets = {
        "00:00": {"time": "00:00", "critical": 0, "high": 0, "medium": 0, "low": 0},
        "03:00": {"time": "03:00", "critical": 0, "high": 0, "medium": 0, "low": 0},
        "06:00": {"time": "06:00", "critical": 0, "high": 0, "medium": 0, "low": 0},
        "09:00": {"time": "09:00", "critical": 0, "high": 0, "medium": 0, "low": 0},
        "12:00": {"time": "12:00", "critical": 0, "high": 0, "medium": 0, "low": 0},
        "15:00": {"time": "15:00", "critical": 0, "high": 0, "medium": 0, "low": 0},
        "18:00": {"time": "18:00", "critical": 0, "high": 0, "medium": 0, "low": 0},
        "21:00": {"time": "21:00", "critical": 0, "high": 0, "medium": 0, "low": 0},
    }
    labels = list(buckets.keys())

    for incident in incidents:
        created = _parse_datetime(incident["created_at"])
        hour = created.hour if created else 0
        label = labels[min(hour // 3, len(labels) - 1)]
        severity_key = incident["severity"].lower()
        if severity_key in buckets[label]:
            buckets[label][severity_key] += 1

    return list(buckets.values())


def _service_health(incidents):
    by_service = defaultdict(list)
    for incident in incidents:
        by_service[incident["service"] or "unknown"].append(incident)

    services = []
    for service, rows in by_service.items():
        critical_count = sum(1 for item in rows if item["severity"] == "CRITICAL")
        open_count = sum(1 for item in rows if item["status"] != "RESOLVED")
        health = max(45, 100 - critical_count * 20 - open_count * 8)
        services.append({
            "service": service,
            "health": health,
            "events": len(rows),
            "slo": max(85, 99.5 - critical_count * 3 - open_count),
        })

    return sorted(services, key=lambda item: item["health"])


def _response_times(incidents):
    by_service = defaultdict(list)
    for incident in incidents:
        by_service[incident["service"] or "unknown"].append(incident)

    response_times = []
    for service, rows in by_service.items():
        ack_minutes = []
        resolve_minutes = []

        for row in rows:
            created = _parse_datetime(row["created_at"])
            acknowledged = _parse_datetime(row["acknowledged_at"])
            resolved = _parse_datetime(row["resolved_at"])

            if created and acknowledged:
                ack_minutes.append((acknowledged - created).total_seconds() / 60)
            if created and resolved:
                resolve_minutes.append((resolved - created).total_seconds() / 60)

        response_times.append({
            "service": service,
            "detect": 1,
            "ack": round(sum(ack_minutes) / len(ack_minutes), 1) if ack_minutes else 5,
            "resolve": round(sum(resolve_minutes) / len(resolve_minutes), 1) if resolve_minutes else 30,
        })

    return response_times


def _timeline(incidents):
    return [
        {
            "time": (_parse_datetime(incident["updated_at"]) or datetime.utcnow()).strftime("%H:%M"),
            "event": f"{incident['status']} {incident['priority']} incident on {incident['service']}",
            "type": "escalation" if incident["status"] == "ESCALATED" else "mitigation" if incident["status"] == "RESOLVED" else "detection",
        }
        for incident in incidents[:6]
    ]


@router.get("/")
def analytics():
    incidents, _ = _fetch_incidents()
    severity_counts = Counter(item["severity"] for item in incidents)
    status_counts = Counter(item["status"] for item in incidents)
    priority_counts = Counter(item["priority"] for item in incidents)

    return {
        "success": True,
        "analytics": {
            "total_incidents": len(incidents),
            "severity_breakdown": [
                {"severity": severity, "count": count}
                for severity, count in severity_counts.items()
            ],
            "status_breakdown": [
                {"status": status, "count": count}
                for status, count in status_counts.items()
            ],
            "priority_breakdown": [
                {"priority": priority, "count": count}
                for priority, count in priority_counts.items()
            ],
            "trend": _trend(incidents),
            "severityDistribution": _severity_distribution(incidents),
            "responseTimes": _response_times(incidents),
            "timeline": _timeline(incidents),
            "serviceHealth": _service_health(incidents),
        },
    }


@router.get("/stats")
def analytics_stats():
    incidents, total_alerts = _fetch_incidents()
    active_statuses = {"OPEN", "ACKNOWLEDGED", "ESCALATED"}
    active_incidents = [item for item in incidents if item["status"] in active_statuses]
    critical_incidents = [item for item in incidents if item["severity"] == "CRITICAL"]
    resolved_incidents = [item for item in incidents if item["status"] == "RESOLVED"]
    automated = [item for item in incidents if item["remediation_action"]]
    mttrs = []

    for incident in resolved_incidents:
        created = _parse_datetime(incident["created_at"])
        resolved = _parse_datetime(incident["resolved_at"])
        if created and resolved:
            mttrs.append((resolved - created).total_seconds() / 60)

    within_sla = 0
    for incident in resolved_incidents:
        created = _parse_datetime(incident["created_at"])
        resolved = _parse_datetime(incident["resolved_at"])
        if created and resolved:
            minutes = (resolved - created).total_seconds() / 60
            if minutes <= (incident["sla_minutes"] or 60):
                within_sla += 1

    return {
        "activeIncidents": len(active_incidents),
        "criticalIncidents": len(critical_incidents),
        "mttrMinutes": round(sum(mttrs) / len(mttrs), 1) if mttrs else 0,
        "automationRate": round((len(automated) / len(incidents)) * 100, 1) if incidents else 0,
        "eventsPerMinute": total_alerts,
        "slaCompliance": round((within_sla / len(resolved_incidents)) * 100, 1) if resolved_incidents else 100,
    }
