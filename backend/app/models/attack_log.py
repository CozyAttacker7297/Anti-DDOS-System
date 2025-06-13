from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class AttackLog(Base):
    """Database model for attack logs."""
    __tablename__ = "attack_logs"  # Explicitly set table name to match the query

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source_ip = Column(String(45), nullable=False)  # IPv6 addresses can be up to 45 chars
    attack_type = Column(String(50), nullable=False)
    target = Column(String(255), nullable=True)  # Added target field
    severity = Column(String(20), default="medium")  # Added severity field
    action = Column(String(20), default="detected")  # Added action field
    status = Column(String(20), default="detected")  # detected, mitigated, resolved
    description = Column(String(255))
    details = Column(JSON)
    
    # Attack metrics
    request_count = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    bandwidth_used = Column(Integer, default=0)  # in bytes
    is_blocked = Column(Boolean, default=False)
    
    # Timestamps for attack lifecycle
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    mitigated_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True)
    
    # Relationships
    server = relationship("Server", back_populates="attack_logs")

    def __repr__(self):
        return f"<AttackLog(id={self.id}, attack_type='{self.attack_type}', source_ip='{self.source_ip}', status='{self.status}')>" 