from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class AlertType(str, Enum):
    SYSTEM = "system"
    SECURITY = "security"
    NETWORK = "network"
    SERVER = "server"
    ZEROTIER = "zerotier"

class AlertBase(BaseModel):
    """Base schema for alerts with common attributes."""
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Detailed alert description")
    alert_type: AlertType = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    source: str = Field(..., description="Source of the alert")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional alert details")

class AlertCreate(AlertBase):
    """Schema for creating new alerts."""
    pass

class AlertUpdate(BaseModel):
    """Schema for updating existing alerts."""
    title: Optional[str] = None
    description: Optional[str] = None
    alert_type: Optional[AlertType] = None
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    details: Optional[Dict[str, Any]] = None
    resolution_notes: Optional[str] = None

class AlertResponse(AlertBase):
    """Schema for alert responses including database fields."""
    id: int
    status: AlertStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True) 