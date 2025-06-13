from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import random

from ..database import SessionLocal
from .. import models, schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="/api/servers",
    tags=["servers"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Server])
def get_servers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    servers = crud.get_servers(db, skip=skip, limit=limit)
    return servers

@router.post("/", response_model=schemas.Server)
def create_server(server: schemas.ServerCreate, db: Session = Depends(get_db)):
    return crud.create_server(db=db, server=server)

@router.get("/{server_id}", response_model=schemas.Server)
def get_server(server_id: int, db: Session = Depends(get_db)):
    db_server = crud.get_server(db, server_id=server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server

@router.put("/{server_id}", response_model=schemas.Server)
def update_server(server_id: int, server: schemas.ServerCreate, db: Session = Depends(get_db)):
    db_server = crud.update_server(db, server_id=server_id, server=server)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server

@router.delete("/{server_id}")
def delete_server(server_id: int, db: Session = Depends(get_db)):
    db_server = crud.delete_server(db, server_id=server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return {"message": "Server deleted successfully"}

from pydantic import BaseModel

class ServerHealth(BaseModel):
    id: int
    name: str
    status: str

@router.get("/all-server-health", response_model=List[ServerHealth])
def all_server_health(db: Session = Depends(get_db)) -> List[ServerHealth]:
    servers = crud.get_servers(db)
    possible_statuses = ["healthy", "degraded", "offline"]
    servers_with_status = [
        ServerHealth(id=server.id, name=server.name, status=random.choice(possible_statuses))
        for server in servers
    ]
    return servers_with_status
