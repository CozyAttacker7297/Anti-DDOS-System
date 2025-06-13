from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Server schemas
class ServerBase(BaseModel):
    name: str
    ip_address: str
    port: int
    status: str = "active"
    server_type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class ServerCreate(ServerBase):
    pass

class Server(ServerBase):
    id: int
    is_healthy: bool
    last_health_check: Optional[datetime]
    health_status: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Security Event schemas
class SecurityEventBase(BaseModel):
    event_type: str
    severity: str
    source_ip: str
    target: str
    details: Optional[Dict[str, Any]] = None
    status: str = "detected"
    action_taken: Optional[str] = None
    confidence_score: Optional[float] = None

class SecurityEventCreate(SecurityEventBase):
    pass

class SecurityEvent(SecurityEventBase):
    id: int
    timestamp: datetime
    server_id: Optional[int] = None

    class Config:
        from_attributes = True

# Attack Log schemas
class AttackLogBase(BaseModel):
    attack_type: str
    source_ip: str
    target: str
    severity: str
    action: str
    details: Optional[Dict[str, Any]] = None

class AttackLogCreate(AttackLogBase):
    pass

class AttackLog(AttackLogBase):
    id: int
    timestamp: datetime
    server_id: Optional[int] = None

    class Config:
        from_attributes = True

# Server Health schemas
class ServerHealthBase(BaseModel):
    is_healthy: bool
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    network_usage: Optional[Dict[str, int]] = None
    metrics: Optional[Dict[str, Any]] = None

class ServerHealthCreate(ServerHealthBase):
    pass

class ServerHealth(ServerHealthBase):
    id: int
    timestamp: datetime
    server_id: int

    class Config:
        from_attributes = True

# Server Stats schemas
class ServerStatsBase(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    bytes_sent: int
    bytes_received: int
    requests_per_second: float
    error_count: int
    error_types: Dict[str, int]
    cpu_usage_avg: float
    memory_usage_avg: float
    disk_usage_avg: float

class ServerStatsCreate(ServerStatsBase):
    pass

class ServerStats(ServerStatsBase):
    id: int
    timestamp: datetime
    server_id: int

    class Config:
        from_attributes = True

# Traffic Stats schemas
class TrafficStatsBase(BaseModel):
    total_requests: int
    unique_ips: int
    requests_per_second: float
    bytes_transferred: int
    top_ips: List[Dict[str, Any]]
    request_types: Dict[str, int]
    status_codes: Dict[str, int]

class TrafficStatsCreate(TrafficStatsBase):
    pass

class TrafficStats(TrafficStatsBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


