import threading
import time
from datetime import datetime

from app.core.database import get_conn
from app.services.notifier import send_notification


def auto_escalate(incident_id: int):

    def task():

        print(f"Monitoring Incident {incident_id}")

        # wait 60 seconds
        time.sleep(60)

        conn = get_conn()

        c = conn.cursor()

        # Check current incident status
        c.execute("""
        SELECT status
        FROM incidents
        WHERE id = ?
        """, (incident_id,))

        row = c.fetchone()

        if row is None:

            conn.close()

            return

        # Only escalate if still OPEN
        if row["status"] == "OPEN":

            now = datetime.utcnow().isoformat()

            c.execute("""
            UPDATE incidents
            SET status = ?,
                updated_at = ?
            WHERE id = ?
            """, (
                "ESCALATED",
                now,
                incident_id
            ))

            conn.commit()

            send_notification(
                "EMAIL",
                f"""
                INCIDENT AUTO ESCALATED

                Incident ID: {incident_id}
                """
            )

            print(f"Incident {incident_id} auto escalated")

        conn.close()

    threading.Thread(target=task).start()