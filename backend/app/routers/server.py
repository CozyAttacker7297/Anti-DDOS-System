from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import random

from ..database import SessionLocal
from .. import models, schemas, crud

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/servers", response_model=List[schemas.ServerOut])
def list_servers(db: Session = Depends(get_db)) -> List[schemas.ServerOut]:
    return crud.get_servers(db)

@router.post("/servers", response_model=schemas.ServerOut, status_code=status.HTTP_201_CREATED)
def add_server(server: schemas.ServerBase, db: Session = Depends(get_db)) -> schemas.ServerOut:
    return crud.create_server(db, server)

@router.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_server(server_id: int, db: Session = Depends(get_db)) -> None:
    deleted = crud.delete_server(db, server_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Server not found")

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
