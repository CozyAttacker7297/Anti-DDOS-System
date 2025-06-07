from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .. import models, crud, schemas
from ..database import get_db
from datetime import datetime
from fastapi import HTTPException
router = APIRouter()

@router.get("/attack-logs")
def get_attack_logs(db: Session = Depends(get_db)):
    return crud.get_attack_logs(db)

@router.post("/add-sample", status_code=status.HTTP_201_CREATED)
def add_sample_attack_log(db: Session = Depends(get_db)):
    sample = schemas.AttackLogBase(
        type="DDoS",
        source_ip="192.168.1.100",
        target="webserver-1",
        severity="high",
        action="blocked"
    )
    attack_log = models.AttackLog(
        type=sample.type,
        source_ip=sample.source_ip,
        target=sample.target,
        severity=sample.severity,
        action=sample.action,
        timestamp=datetime.utcnow()
    )
    db.add(attack_log)
    db.commit()
    db.refresh(attack_log)
    return {"message": "Sample attack log added", "attack_log_id": attack_log.id}

@router.delete("/attack-logs/{log_id}", status_code=204)
def delete_attack_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.AttackLog).filter(models.AttackLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Attack log not found")
    db.delete(log)
    db.commit()
    return