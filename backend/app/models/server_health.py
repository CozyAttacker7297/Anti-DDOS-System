from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class ServerHealth(Base):
    """Database model for server health checks."""
    __tablename__ = "server_health"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_healthy = Column(Boolean, default=True)
    response_time = Column(Float, nullable=True)  # in milliseconds
    status_code = Column(Integer, nullable=True)
    error_message = Column(String(255), nullable=True)
    
    # System metrics
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    disk_usage = Column(Float, nullable=True)
    network_usage = Column(JSON, nullable=True)
    
    # Additional metrics
    metrics = Column(JSON, nullable=True)
    
    # Foreign keys
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    
    # Relationships
    server = relationship("Server", back_populates="health_checks")

    def __repr__(self):
        return f"<ServerHealth(id={self.id}, server_id={self.server_id}, is_healthy={self.is_healthy}, timestamp='{self.timestamp}')>" 