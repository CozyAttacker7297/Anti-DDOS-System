from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AttackType(str, Enum):
    DDOS = "ddos"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    OTHER = "other"

class AttackStatus(str, Enum):
    DETECTED = "detected"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    FAILED = "failed"

class AttackLogBase(BaseModel):
    """Base schema for attack logs with common attributes."""
    source_ip: IPvAnyAddress = Field(..., description="Source IP address of the attack")
    attack_type: AttackType = Field(..., description="Type of attack")
    status: AttackStatus = Field(default=AttackStatus.DETECTED, description="Status of the attack")
    description: str = Field(..., description="Description of the attack")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional attack details")
    request_count: int = Field(default=1, description="Number of requests in the attack")
    duration_seconds: float = Field(..., description="Duration of the attack in seconds")
    is_blocked: bool = Field(default=False, description="Whether the source IP was blocked")

class AttackLogCreate(AttackLogBase):
    """Schema for creating new attack logs."""
    pass

class AttackLogUpdate(BaseModel):
    """Schema for updating attack logs."""
    status: Optional[AttackStatus] = None
    description: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    request_count: Optional[int] = None
    duration_seconds: Optional[float] = None
    is_blocked: Optional[bool] = None
    mitigation_notes: Optional[str] = None

class AttackLogResponse(AttackLogBase):
    """Schema for attack log responses including database fields."""
    id: int
    detected_at: datetime
    mitigated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    mitigation_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2 