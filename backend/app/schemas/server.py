from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ServerType(str, Enum):
    WEB = "web"
    DATABASE = "database"
    LOAD_BALANCER = "load_balancer"
    PROXY = "proxy"
    OTHER = "other"

class ServerStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class ServerBase(BaseModel):
    """Base schema for servers with common attributes."""
    name: str = Field(..., description="Server name")
    ip_address: IPvAnyAddress = Field(..., description="Server IP address")
    port: int = Field(..., ge=1, le=65535, description="Server port")
    status: ServerStatus = Field(default=ServerStatus.ACTIVE, description="Server status")
    server_type: ServerType = Field(..., description="Type of server")
    location: Optional[str] = Field(None, description="Server location")
    description: Optional[str] = Field(None, description="Server description")

class ServerCreate(ServerBase):
    """Schema for creating new servers."""
    pass

class ServerUpdate(BaseModel):
    """Schema for updating servers."""
    name: Optional[str] = None
    ip_address: Optional[IPvAnyAddress] = None
    port: Optional[int] = None
    status: Optional[ServerStatus] = None
    server_type: Optional[ServerType] = None
    location: Optional[str] = None
    description: Optional[str] = None

class ServerHealth(BaseModel):
    """Schema for server health information."""
    status: ServerStatus
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    uptime_seconds: float
    last_check: datetime
    is_responding: bool
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None

class ServerStats(BaseModel):
    """Schema for server statistics."""
    total_requests: int
    active_connections: int
    requests_per_second: float
    error_rate: float
    bandwidth_usage: Dict[str, float]  # bytes_sent, bytes_received
    timestamp: datetime

class ServerResponse(ServerBase):
    """Schema for server responses including database fields."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    health: Optional[ServerHealth] = None
    stats: Optional[ServerStats] = None

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2

class ServerOut(ServerResponse):
    """Extended server response schema for detailed server information."""
    zerotier_address: Optional[str] = None
    zerotier_status: Optional[str] = None
    load_balancer_status: Optional[str] = None
    security_status: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    last_attack: Optional[Dict[str, Any]] = None
    maintenance_schedule: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2 