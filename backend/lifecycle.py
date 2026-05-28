"""
Centralized incident lifecycle validation.
Valid transitions are enforced before any status mutation.
"""

# Allowed state transitions (uppercase status values)
VALID_TRANSITIONS = {
    "OPEN": ["ACKNOWLEDGED", "ESCALATED"],
    "ACKNOWLEDGED": ["RESOLVED"],
    "ESCALATED": ["ACKNOWLEDGED", "RESOLVED"],
    "RESOLVED": ["CLOSED"],
    "CLOSED": [],
}


def validate_transition(current_state: str, target_state: str) -> None:
    """
    Raise ValueError when a lifecycle transition is not permitted.
    """
    current = (current_state or "").upper()
    target = (target_state or "").upper()

    allowed = VALID_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise ValueError(
            f"Invalid transition: {current} → {target}. "
            f"Allowed from {current}: {', '.join(allowed) or 'none'}"
        )
