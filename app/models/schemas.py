from enum import Enum
from typing import Optional

from pydantic import BaseModel


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
    service: Optional[str] = None
    metric: Optional[str] = None
    value: Optional[str] = None


class IncidentAction(BaseModel):
    actor: str = "Dashboard User"
    note: Optional[str] = None
