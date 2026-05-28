from fastapi import APIRouter

from app.core.database import get_conn

router = APIRouter()


def _fetch_breakdown(cursor, column):

    cursor.execute(f"""
    SELECT {column},
           COUNT(*) as count
    FROM incidents
    GROUP BY {column}
    """)

    return [
        dict(row)
        for row in cursor.fetchall()
    ]


# ---------------------------------------------------
# ANALYTICS DASHBOARD API
# ---------------------------------------------------
@router.get("/")
def analytics():

    conn = get_conn()

    c = conn.cursor()

    # ---------------------------------------------------
    # TOTAL INCIDENTS
    # ---------------------------------------------------
    c.execute("""
    SELECT COUNT(*) as total
    FROM incidents
    """)

    total_incidents = c.fetchone()["total"]

    severity_breakdown = _fetch_breakdown(c, "severity")
    status_breakdown = _fetch_breakdown(c, "status")
    priority_breakdown = _fetch_breakdown(c, "priority")

    conn.close()

    # ---------------------------------------------------
    # FINAL RESPONSE
    # ---------------------------------------------------
    return {

        "success": True,

        "analytics": {

            "total_incidents": total_incidents,

            "severity_breakdown": severity_breakdown,

            "status_breakdown": status_breakdown,

            "priority_breakdown": priority_breakdown
        }
    }


@router.get("/stats")
def analytics_stats():

    conn = get_conn()

    c = conn.cursor()

    c.execute("""
    SELECT status,
           severity,
           COUNT(*) as count
    FROM incidents
    GROUP BY status, severity
    """)

    rows = [dict(row) for row in c.fetchall()]

    c.execute("""
    SELECT COUNT(*) as total
    FROM alerts
    """)

    total_alerts = c.fetchone()["total"]

    conn.close()

    active_statuses = {"OPEN", "ACKNOWLEDGED", "ESCALATED"}
    active_incidents = sum(
        row["count"]
        for row in rows
        if row["status"] in active_statuses
    )
    critical_incidents = sum(
        row["count"]
        for row in rows
        if row["severity"] == "CRITICAL"
    )
    resolved_incidents = sum(
        row["count"]
        for row in rows
        if row["status"] == "RESOLVED"
    )
    total_incidents = sum(row["count"] for row in rows)

    return {
        "activeIncidents": active_incidents,
        "criticalIncidents": critical_incidents,
        "mttrMinutes": 0,
        "automationRate": 100 if total_incidents else 0,
        "eventsPerMinute": total_alerts,
        "slaCompliance": 100 if not total_incidents else round((resolved_incidents / total_incidents) * 100, 1),
    }
