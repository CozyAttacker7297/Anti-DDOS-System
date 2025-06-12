from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AttackBase(BaseModel):
    """Base attack schema with common attributes."""
    source_ip: str = Field(..., description="Source IP address of the attack")
    attack_type: str = Field(..., description="Type of attack (e.g., 'DDOS', 'BRUTE_FORCE', etc.)")
    request_count: int = Field(..., description="Number of requests in the attack")
    duration_seconds: float = Field(..., description="Duration of the attack in seconds")
    status: str = Field(default="detected", description="Status of the attack (detected/blocked/resolved)")

class AttackCreate(AttackBase):
    """Schema for creating a new attack record."""
    pass

class AttackResponse(AttackBase):
    """Schema for attack response including database fields."""
    id: int
    detected_at: datetime
    blocked_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enable ORM mode 