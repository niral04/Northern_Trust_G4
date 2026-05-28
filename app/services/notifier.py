from datetime import datetime

from app.core.database import get_conn


def record_notification(incident_id: int, channel: str, recipient: str, message: str):
    now = datetime.utcnow().isoformat()
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO notifications(
        incident_id,
        channel,
        recipient,
        status,
        message,
        created_at
    )
    VALUES(?,?,?,?,?,?)
    """, (
        incident_id,
        channel,
        recipient,
        "SENT_SIMULATED",
        message,
        now,
    ))

    conn.commit()
    notification_id = c.lastrowid
    conn.close()

    return {
        "id": notification_id,
        "incident_id": incident_id,
        "channel": channel,
        "recipient": recipient,
        "status": "SENT_SIMULATED",
        "message": message,
        "created_at": now,
    }


def send_notification(incident_id: int, channel: str, recipient: str, message: str):
    """Simulate external notifications for demo readiness without real credentials."""

    notification = record_notification(incident_id, channel, recipient, message)
    print(f"[{channel}] to {recipient}: {message}")
    return notification
