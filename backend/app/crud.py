from sqlalchemy.orm import Session
from . import models, schemas
from .models.attack_log import AttackLog

def get_servers(db: Session):
    return db.query(models.Server).filter(models.Server.is_active == True).all()

def create_server(db: Session, server: schemas.ServerBase):
    db_server = models.Server(**server.dict())
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    return db_server

def delete_server(db: Session, server_id: int):
    server = db.query(models.Server).filter(models.Server.id == server_id).first()
    if server:
        db.delete(server)
        db.commit()
    return server

def get_alerts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Alert).offset(skip).limit(limit).all()

def create_alert(db: Session, alert: schemas.AlertCreate):
    db_alert = models.Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def delete_alert(db: Session, alert_id: int):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if alert:
        db.delete(alert)
        db.commit()
    return alert

def get_blocked_ips(db: Session):
    return db.query(models.BlockedIP).all()

def create_blocked_ip(db: Session, blocked_ip: schemas.BlockedIPCreate):
    db_blocked_ip = models.BlockedIP(**blocked_ip.dict())
    db.add(db_blocked_ip)
    db.commit()
    db.refresh(db_blocked_ip)
    return db_blocked_ip

def delete_blocked_ip(db: Session, ip_id: int):
    blocked_ip = db.query(models.BlockedIP).filter(models.BlockedIP.id == ip_id).first()
    if blocked_ip:
        db.delete(blocked_ip)
        db.commit()
    return blocked_ip

def get_attack_logs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.AttackLog).offset(skip).limit(limit).all()

def create_attack_log(db: Session, attack_log: schemas.AttackLogCreate):
    db_attack_log = models.AttackLog(**attack_log.dict())
    db.add(db_attack_log)
    db.commit()
    db.refresh(db_attack_log)
    return db_attack_log

def delete_attack_log(db: Session, attack_log_id: int):
    attack_log = db.query(models.AttackLog).filter(models.AttackLog.id == attack_log_id).first()
    if attack_log:
        db.delete(attack_log)
        db.commit()
    return attack_log

def get_security_events(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.SecurityEvent).offset(skip).limit(limit).all()

def create_security_event(db: Session, event: schemas.SecurityEventCreate):
    db_event = models.SecurityEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_security_event(db: Session, event_id: int):
    return db.query(models.SecurityEvent).filter(models.SecurityEvent.id == event_id).first()

def update_security_event(db: Session, event_id: int, event: schemas.SecurityEventUpdate):
    db_event = db.query(models.SecurityEvent).filter(models.SecurityEvent.id == event_id).first()
    if db_event:
        update_data = event.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_event, key, value)
        db.commit()
        db.refresh(db_event)
    return db_event

def delete_security_event(db: Session, event_id: int):
    event = db.query(models.SecurityEvent).filter(models.SecurityEvent.id == event_id).first()
    if event:
        db.delete(event)
        db.commit()
    return event
