from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Server(Base):
    """Database model for servers."""
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)  # IPv6 addresses can be up to 45 chars
    port = Column(Integer, nullable=False)
    status = Column(String(20), default="active")  # active, inactive, maintenance
    server_type = Column(String(50))  # web, database, cache, etc.
    location = Column(String(100))
    description = Column(String(255))
    
    # Health monitoring
    is_healthy = Column(Boolean, default=True)
    last_health_check = Column(DateTime(timezone=True), nullable=True)
    health_status = Column(JSON, default={"status": "unknown", "last_check": None})
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    disk_usage = Column(Float, nullable=True)
    uptime_seconds = Column(Float, nullable=True)
    is_responding = Column(Boolean, default=True)
    response_time_ms = Column(Float, nullable=True)
    
    # Load balancer integration
    is_load_balanced = Column(Boolean, default=False)
    weight = Column(Integer, default=1)
    max_connections = Column(Integer, default=1000)
    current_connections = Column(Integer, default=0)
    
    # ZeroTier integration
    zerotier_node_id = Column(String(10))
    zerotier_ip = Column(String(45))
    zerotier_status = Column(String(20), default="disconnected")
    
    # Security settings
    security_status = Column(JSON, nullable=True)
    last_attack = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    maintenance_schedule = Column(JSON, nullable=True)

    # Relationships
    health_checks = relationship("ServerHealth", back_populates="server")
    stats = relationship("ServerStats", back_populates="server")
    attack_logs = relationship("AttackLog", back_populates="server")
    security_events = relationship("SecurityEvent", back_populates="server")

    def __repr__(self):
        return f"<Server(id={self.id}, name='{self.name}', ip='{self.ip_address}', status='{self.status}')>"

class ServerHealth(Base):
    """Database model for server health checks."""
    __tablename__ = "server_health"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    status = Column(String, nullable=False)
    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    disk_usage = Column(Float, nullable=False)
    uptime_seconds = Column(Float, nullable=False)
    is_responding = Column(Boolean, default=True)
    response_time_ms = Column(Float, nullable=True)
    error_message = Column(String, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    server = relationship("Server", back_populates="health_checks")

    def __repr__(self):
        return f"<ServerHealth(server_id={self.server_id}, status='{self.status}', checked_at='{self.checked_at}')>"

class ServerStats(Base):
    """Database model for server statistics."""
    __tablename__ = "server_stats"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    total_requests = Column(Integer, default=0)
    active_connections = Column(Integer, default=0)
    requests_per_second = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    bandwidth_usage = Column(JSON, nullable=False)  # bytes_sent, bytes_received
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    server = relationship("Server", back_populates="stats")

    def __repr__(self):
        return f"<ServerStats(server_id={self.server_id}, requests_per_second={self.requests_per_second}, recorded_at='{self.recorded_at}')>" 