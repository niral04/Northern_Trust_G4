from fastapi import APIRouter

from app.core.database import get_conn

router = APIRouter()


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

    # ---------------------------------------------------
    # SEVERITY BREAKDOWN
    # ---------------------------------------------------
    c.execute("""
    SELECT severity,
           COUNT(*) as count
    FROM incidents
    GROUP BY severity
    """)

    severity_breakdown = [
        dict(row)
        for row in c.fetchall()
    ]

    # ---------------------------------------------------
    # STATUS BREAKDOWN
    # ---------------------------------------------------
    c.execute("""
    SELECT status,
           COUNT(*) as count
    FROM incidents
    GROUP BY status
    """)

    status_breakdown = [
        dict(row)
        for row in c.fetchall()
    ]

    # ---------------------------------------------------
    # PRIORITY BREAKDOWN
    # ---------------------------------------------------
    c.execute("""
    SELECT priority,
           COUNT(*) as count
    FROM incidents
    GROUP BY priority
    """)

    priority_breakdown = [
        dict(row)
        for row in c.fetchall()
    ]

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