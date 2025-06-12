from pydantic import BaseModel, Field, IPvAnyAddress
from datetime import datetime
from typing import Optional, Dict, Any

class SecurityEventBase(BaseModel):
    """Base security event schema with common attributes."""
    event_type: str = Field(..., description="Type of security event (e.g., 'DDOS', 'BRUTE_FORCE', 'SQL_INJECTION')")
    source_ip: IPvAnyAddress = Field(..., description="Source IP address of the event")
    severity: str = Field(..., description="Severity level (low/medium/high/critical)")
    description: str = Field(..., description="Description of the security event")
    status: str = Field(default="detected", description="Status of the event (detected/investigating/resolved)")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional event details")

class SecurityEventCreate(SecurityEventBase):
    """Schema for creating a new security event."""
    pass

class SecurityEventUpdate(BaseModel):
    """Schema for updating a security event."""
    event_type: Optional[str] = None
    source_ip: Optional[IPvAnyAddress] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SecurityEventResponse(SecurityEventBase):
    """Schema for security event response including database fields."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    mitigation_action: Optional[str] = Field(None, description="Action taken to mitigate the event")
    assigned_to: Optional[str] = Field(None, description="User assigned to handle the event")
    resolution_notes: Optional[str] = Field(None, description="Notes about how the event was resolved")

    class Config:
        from_attributes = True  # Enable ORM mode

class SecurityMetrics(BaseModel):
    """Schema for security metrics."""
    total_events: int
    active_events: int
    events_by_type: Dict[str, int]
    events_by_severity: Dict[str, int]
    events_by_status: Dict[str, int]
    average_resolution_time: Optional[float] = None
    top_source_ips: Dict[str, int]
    timestamp: datetime 