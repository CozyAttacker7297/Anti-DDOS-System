from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="/api/security",
    tags=["security"]
)

@router.get("/events", response_model=List[schemas.SecurityEvent])
def get_security_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_security_events(db, skip=skip, limit=limit)
    return events

@router.post("/events", response_model=schemas.SecurityEvent)
def create_security_event(event: schemas.SecurityEventCreate, db: Session = Depends(get_db)):
    return crud.create_security_event(db=db, event=event)

@router.get("/attack-logs", response_model=List[schemas.AttackLog])
def get_attack_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = crud.get_attack_logs(db, skip=skip, limit=limit)
    return logs

@router.post("/attack-logs", response_model=schemas.AttackLog)
def create_attack_log(log: schemas.AttackLogCreate, db: Session = Depends(get_db)):
    return crud.create_attack_log(db=db, log=log) 