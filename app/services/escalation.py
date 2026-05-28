from datetime import datetime

from app.core.database import get_conn


def find_sla_breaches():
    """Return open incidents whose age is beyond their configured SLA window."""

    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    SELECT * FROM incidents
    WHERE status IN ('OPEN', 'ACKNOWLEDGED', 'ESCALATED')
    """)
    rows = [dict(row) for row in c.fetchall()]
    conn.close()

    breached = []
    now = datetime.utcnow()

    for incident in rows:
        try:
            created_at = datetime.fromisoformat(incident["created_at"])
        except (TypeError, ValueError):
            continue

        age_minutes = (now - created_at).total_seconds() / 60
        if age_minutes > (incident.get("sla_minutes") or 60):
            breached.append(incident)

    return breached
