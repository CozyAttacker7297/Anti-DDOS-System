from fastapi import APIRouter
from ..utils import block_ip, unblock_ip

router = APIRouter()

@router.post("/ipblock/block")
def block_ip_route(ip: str):
    block_ip(ip)
    return {"status": "blocked", "ip": ip}

@router.post("/ipblock/unblock")
def unblock_ip_route(ip: str):
    unblock_ip(ip)
    return {"status": "unblocked", "ip": ip} 