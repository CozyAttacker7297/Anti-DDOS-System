from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .database import Base

import datetime

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)
    severity = Column(String)
    status = Column(String, default="unread")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Server(Base):
    __tablename__ = "servers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    ip_address = Column(String)  # added ip_address here
    status = Column(String)      # you can keep or remove if ip_address is enough
    cpu = Column(Integer)
    ram = Column(Integer)
    is_active = Column(Boolean, default=True)  # added is_active to track status

class SecurityEvent(Base):
    __tablename__ = "security_events"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class BlockedIP(Base):
    __tablename__ = "blocked_ips"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True)
    reason = Column(String)
    blocked_at = Column(DateTime, default=datetime.datetime.utcnow)

class AttackLog(Base):
    __tablename__ = "attack_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    type = Column(String)
    source_ip = Column(String)
    target = Column(String)
    severity = Column(String)
    action = Column(String)
