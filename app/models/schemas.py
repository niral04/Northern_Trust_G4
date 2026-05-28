from pydantic import BaseModel
from enum import Enum
from typing import Optional

class Severity(str, Enum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    critical = "CRITICAL"

class AlertType(str, Enum):
    infra = "INFRA"
    app = "APP"

class IncidentState(str, Enum):
    open = "OPEN"
    acknowledged = "ACKNOWLEDGED"
    escalated = "ESCALATED"
    resolved = "RESOLVED"

class AlertCreate(BaseModel):
    source: str
    type: AlertType
    severity: Severity
    message: str

class IncidentAction(BaseModel):
    actor: str
    note: Optional[str] = None