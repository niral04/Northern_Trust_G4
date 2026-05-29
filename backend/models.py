from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime, timezone, timedelta
from database import Base

# IST timezone
IST = timezone(timedelta(hours=5, minutes=30))

def ist_now():
    return datetime.now(IST).replace(tzinfo=None)

class Incident(Base):
    __tablename__ = "incidents"

    id                 = Column(Integer, primary_key=True, index=True)
    incident_id        = Column(String, unique=True)
    alert_type         = Column(String)
    severity           = Column(String)
    status             = Column(String, default="OPEN")
    source             = Column(String)
    message            = Column(Text)
    assignee           = Column(String)
    notify_channel     = Column(String)
    escalation_level   = Column(Integer, default=0)
    escalation_timeout = Column(Integer)
    created_at         = Column(DateTime, default=ist_now)       # ✅ fixed
    acknowledged_at    = Column(DateTime, nullable=True)
    resolved_at        = Column(DateTime, nullable=True)
    last_escalated_at  = Column(DateTime, nullable=True)
    resolution_notes   = Column(Text, nullable=True)
    mttr_minutes       = Column(Float, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"

    id          = Column(Integer, primary_key=True)
    alert_type  = Column(String)
    source      = Column(String)
    metric      = Column(String)
    value       = Column(String)
    message     = Column(Text)
    severity    = Column(String)
    received_at = Column(DateTime, default=ist_now)              # ✅ fixed
    processed   = Column(String, default="false")

class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id          = Column(Integer, primary_key=True)
    incident_id = Column(String)
    event_type  = Column(String)
    description = Column(Text)
    created_at  = Column(DateTime, default=ist_now)              # ✅ fixed