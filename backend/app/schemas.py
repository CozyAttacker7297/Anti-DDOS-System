from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# -------------------- Alert Schemas --------------------

class AlertBase(BaseModel):
    message: str
    severity: str
    status: Optional[str] = "unread"

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# -------------------- Legacy Server Schemas --------------------

class LegacyServerBase(BaseModel):
    name: str
    status: str
    cpu: int
    ram: int

class LegacyServer(LegacyServerBase):
    id: int

    class Config:
        from_attributes = True

# -------------------- Security Event Schemas --------------------

class SecurityEventBase(BaseModel):
    event_type: str
    description: str

class SecurityEvent(SecurityEventBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# -------------------- Blocked IP Schemas --------------------

class BlockedIPBase(BaseModel):
    ip: str
    reason: str

class BlockedIP(BlockedIPBase):
    id: int
    blocked_at: datetime

    class Config:
        from_attributes = True

# -------------------- Attack Log Schemas --------------------

class AttackLogBase(BaseModel):
    type: str
    source_ip: str
    target: str
    severity: str
    action: str

class AttackLog(AttackLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# -------------------- Updated Server Schemas --------------------

class ServerBase(BaseModel):
    name: str
    ip_address: str

class ServerCreate(ServerBase):
    pass

class ServerOut(ServerBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


