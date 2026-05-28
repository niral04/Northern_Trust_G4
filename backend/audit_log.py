"""
Structured audit logging for incident operations.
"""
import json
import logging

logger = logging.getLogger("ims.audit")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def log_escalation(
    incident_id: str,
    reason: str,
    previous_assignee: str,
    new_assignee: str,
    escalation_level: int,
    elapsed_seconds: int | None = None,
    actor: str = "system",
):
    logger.info(
        json.dumps(
            {
                "action": "escalation",
                "incident_id": incident_id,
                "reason": reason,
                "previous_assignee": previous_assignee,
                "new_assignee": new_assignee,
                "escalation_level": escalation_level,
                "elapsed_escalation_seconds": elapsed_seconds,
                "actor": actor,
            }
        )
    )


def log_acknowledgement(
    incident_id: str,
    actor: str,
    previous_assignee: str,
    new_assignee: str,
):
    logger.info(
        json.dumps(
            {
                "action": "acknowledgement",
                "incident_id": incident_id,
                "actor": actor,
                "previous_assignee": previous_assignee,
                "new_assignee": new_assignee,
            }
        )
    )


def log_resolution(incident_id: str, actor: str, notes: str, mttr_minutes: int | None):
    logger.info(
        json.dumps(
            {
                "action": "resolution",
                "incident_id": incident_id,
                "actor": actor,
                "notes": notes,
                "mttr_minutes": mttr_minutes,
            }
        )
    )


def log_websocket_broadcast(event: str, payload: dict):
    logger.info(
        json.dumps({"action": "websocket_broadcast", "event": event, "payload": payload})
    )


def log_invalid_transition(
    incident_id: str,
    current_state: str,
    target_state: str,
    actor: str = "system",
):
    logger.warning(
        json.dumps(
            {
                "action": "invalid_transition",
                "incident_id": incident_id,
                "current_state": current_state,
                "target_state": target_state,
                "actor": actor,
            }
        )
    )
