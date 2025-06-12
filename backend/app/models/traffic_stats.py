from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.sql import func
from .base import Base

class TrafficStats(Base):
    """Database model for traffic statistics."""
    __tablename__ = "traffic_stats"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    clean_requests = Column(Integer, default=0)
    malicious_requests = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    requests_per_second = Column(Float, default=0.0)
    bandwidth_usage = Column(JSON, default={"bytes_sent": 0, "bytes_received": 0})
    active_connections = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)
    details = Column(JSON, nullable=True)  # Additional statistics

    def __repr__(self):
        return f"<TrafficStats(id={self.id}, total_requests={self.total_requests}, timestamp={self.timestamp})>" 