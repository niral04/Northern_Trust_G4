from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id              = Column(Integer, primary_key=True, index=True)
    incident_id     = Column(String, unique=True)  # INC-001
    alert_type      = Column(String)   # infrastructure / application
    severity        = Column(String)   # critical / high / medium / low
    status          = Column(String, default="OPEN")
    source          = Column(String)   # server-01, payment-service
    message         = Column(Text)
    assignee        = Column(String)
    notify_channel  = Column(String)   # slack / email
    escalation_level= Column(Integer, default=0)
    escalation_timeout = Column(Integer)  # minutes
    created_at      = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at     = Column(DateTime, nullable=True)
    last_escalated_at = Column(DateTime, nullable=True)
    resolution_notes= Column(Text, nullable=True)
    mttr_minutes    = Column(Integer, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"

    id          = Column(Integer, primary_key=True)
    alert_type  = Column(String)
    source      = Column(String)
    metric      = Column(String)
    value       = Column(String)
    message     = Column(Text)
    severity    = Column(String)
    received_at = Column(DateTime, default=datetime.utcnow)
    processed   = Column(String, default="false")

class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id          = Column(Integer, primary_key=True)
    incident_id = Column(String)
    event_type  = Column(String)
    description = Column(Text)
    created_at  = Column(DateTime, default=datetime.utcnow)