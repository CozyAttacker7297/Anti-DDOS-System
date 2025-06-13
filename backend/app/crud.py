from sqlalchemy.orm import Session
from . import models
from .schemas import (
    ServerCreate,
    SecurityEventCreate,
    AttackLogCreate,
    ServerHealthCreate,
    ServerStatsCreate,
    TrafficStatsCreate
)
from typing import List, Optional
from datetime import datetime, timedelta

# Server CRUD operations
def get_server(db: Session, server_id: int):
    return db.query(models.Server).filter(models.Server.id == server_id).first()

def get_servers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Server).offset(skip).limit(limit).all()

def create_server(db: Session, server: ServerCreate):
    db_server = models.Server(**server.dict())
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    return db_server

def update_server(db: Session, server_id: int, server: ServerCreate):
    db_server = db.query(models.Server).filter(models.Server.id == server_id).first()
    if db_server:
        for key, value in server.dict().items():
            setattr(db_server, key, value)
        db.commit()
        db.refresh(db_server)
    return db_server

def delete_server(db: Session, server_id: int):
    db_server = db.query(models.Server).filter(models.Server.id == server_id).first()
    if db_server:
        db.delete(db_server)
        db.commit()
    return db_server

# Security Event CRUD operations
def get_security_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SecurityEvent).offset(skip).limit(limit).all()

def create_security_event(db: Session, event: SecurityEventCreate):
    db_event = models.SecurityEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# Attack Log CRUD operations
def get_attack_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AttackLog).offset(skip).limit(limit).all()

def create_attack_log(db: Session, log: AttackLogCreate):
    db_log = models.AttackLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# Server Health CRUD operations
def get_server_health(db: Session, server_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ServerHealth).filter(
        models.ServerHealth.server_id == server_id
    ).offset(skip).limit(limit).all()

def create_server_health(db: Session, health: ServerHealthCreate, server_id: int):
    db_health = models.ServerHealth(**health.dict(), server_id=server_id)
    db.add(db_health)
    db.commit()
    db.refresh(db_health)
    return db_health

# Server Stats CRUD operations
def get_server_stats(db: Session, server_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ServerStats).filter(
        models.ServerStats.server_id == server_id
    ).offset(skip).limit(limit).all()

def create_server_stats(db: Session, stats: ServerStatsCreate, server_id: int):
    db_stats = models.ServerStats(**stats.dict(), server_id=server_id)
    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    return db_stats

# Traffic Stats CRUD operations
def get_traffic_stats(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TrafficStats).offset(skip).limit(limit).all()

def create_traffic_stats(db: Session, stats: TrafficStatsCreate):
    db_stats = models.TrafficStats(**stats.dict())
    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    return db_stats
