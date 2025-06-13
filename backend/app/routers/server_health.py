from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="/api/server-health",
    tags=["server-health"]
)

@router.get("/{server_id}", response_model=List[schemas.ServerHealth])
def get_server_health(server_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    health_records = crud.get_server_health(db, server_id=server_id, skip=skip, limit=limit)
    return health_records

@router.post("/{server_id}", response_model=schemas.ServerHealth)
def create_server_health(server_id: int, health: schemas.ServerHealthCreate, db: Session = Depends(get_db)):
    return crud.create_server_health(db=db, health=health, server_id=server_id) 