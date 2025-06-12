from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional
from datetime import datetime

class BlockedIPBase(BaseModel):
    """Base schema for blocked IPs with common attributes."""
    ip_address: IPvAnyAddress = Field(..., description="IP address to block")
    reason: str = Field(..., description="Reason for blocking the IP")
    is_active: bool = Field(default=True, description="Whether the block is active")

class BlockedIPCreate(BlockedIPBase):
    """Schema for creating new blocked IPs."""
    pass

class BlockedIPUpdate(BaseModel):
    """Schema for updating blocked IPs."""
    reason: Optional[str] = None
    is_active: Optional[bool] = None
    unblocked_at: Optional[datetime] = None

class BlockedIPResponse(BlockedIPBase):
    """Schema for blocked IP responses including database fields."""
    id: int
    blocked_at: datetime
    unblocked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2 