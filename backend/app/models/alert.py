from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Alert(Base):
    """Database model for system alerts."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    alert_type = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=False)
    source = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Status tracking
    status = Column(String, nullable=False, default="active")
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True)
    server = relationship("Server", backref="alerts")
    security_event_id = Column(Integer, ForeignKey("security_events.id"), nullable=True)
    security_event = relationship("SecurityEvent", backref="alerts")

    def __repr__(self):
        return f"<Alert(title='{self.title}', alert_type='{self.alert_type}', severity='{self.severity}')>" 