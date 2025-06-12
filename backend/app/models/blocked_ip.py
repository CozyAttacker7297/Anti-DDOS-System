from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.sql import func
from ..database import Base

class BlockedIP(Base):
    """Database model for blocked IP addresses."""
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)  # IPv6 addresses can be up to 45 chars
    reason = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    blocked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    unblocked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<BlockedIP(ip_address='{self.ip_address}', reason='{self.reason}', is_active={self.is_active})>" 