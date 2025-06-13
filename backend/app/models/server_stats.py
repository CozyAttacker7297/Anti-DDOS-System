from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class ServerStats(Base):
    """Database model for server performance statistics."""
    __tablename__ = "server_stats"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Request statistics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    avg_response_time = Column(Float, nullable=True)  # in milliseconds
    
    # Traffic statistics
    bytes_sent = Column(Integer, default=0)
    bytes_received = Column(Integer, default=0)
    requests_per_second = Column(Float, default=0.0)
    
    # Error statistics
    error_count = Column(Integer, default=0)
    error_types = Column(JSON, nullable=True)
    
    # Performance metrics
    cpu_usage_avg = Column(Float, nullable=True)
    memory_usage_avg = Column(Float, nullable=True)
    disk_usage_avg = Column(Float, nullable=True)
    
    # Additional metrics
    metrics = Column(JSON, nullable=True)
    
    # Foreign keys
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    
    # Relationships
    server = relationship("Server", back_populates="stats")

    def __repr__(self):
        return f"<ServerStats(id={self.id}, server_id={self.server_id}, timestamp='{self.timestamp}', total_requests={self.total_requests})>" 