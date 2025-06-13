from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base
from ..schemas import SecurityEventCreate

class SecurityEvent(Base):
    """Database model for security events."""
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    event_type = Column(String(50), nullable=False, index=True)
    source_ip = Column(String(45), nullable=False)  # IPv6 addresses can be up to 45 chars
    severity = Column(String(20), nullable=False)
    target = Column(String(45), nullable=False)
    description = Column(String(255))
    status = Column(String(20), nullable=False, default="detected")  # detected, investigating, mitigated, resolved
    details = Column(JSON, nullable=True)
    action_taken = Column(String(255), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Mitigation information
    is_mitigated = Column(Boolean, default=False)
    mitigation_action = Column(String(50))  # block, rate_limit, etc.
    mitigation_timestamp = Column(DateTime(timezone=True), nullable=True)
    mitigation_details = Column(JSON)
    
    # Resolution information
    is_resolved = Column(Boolean, default=False)
    resolution_timestamp = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(String(255))
    
    # Foreign keys
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True)
    
    # Relationships
    server = relationship("Server", back_populates="security_events")

    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, event_type='{self.event_type}', source_ip='{self.source_ip}', severity='{self.severity}')>" 