from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import subprocess
import logging
from ..database import get_db
from .. import models
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

def _run_iptables_command(command: list) -> bool:
    """Run an iptables command and return success status."""
    try:
        result = subprocess.run(
            ["iptables"] + command,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"iptables command failed: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("iptables command not found")
        return False

def block_ip(ip: str) -> bool:
    """Block an IP address using iptables."""
    # Add rule to block IP
    if not _run_iptables_command(["-A", "INPUT", "-s", ip, "-j", "DROP"]):
        return False
    
    # Save rules
    if not _run_iptables_command(["-S"]):
        return False
    
    return True

def unblock_ip(ip: str) -> bool:
    """Unblock an IP address using iptables."""
    # Remove rule to block IP
    if not _run_iptables_command(["-D", "INPUT", "-s", ip, "-j", "DROP"]):
        return False
    
    # Save rules
    if not _run_iptables_command(["-S"]):
        return False
    
    return True

@router.post("/ipblock/block")
async def block_ip_route(ip: str, db: Session = Depends(get_db)):
    """Block an IP address and log it in the database."""
    if not block_ip(ip):
        raise HTTPException(status_code=500, detail="Failed to block IP")
    
    # Log the blocked IP in the database
    blocked_ip = models.BlockedIP(
        ip_address=ip,
        reason="Manual block",
        blocked_at=datetime.utcnow()
    )
    db.add(blocked_ip)
    db.commit()
    
    return {
        "status": "blocked",
        "ip": ip,
        "timestamp": blocked_ip.blocked_at
    }

@router.post("/ipblock/unblock")
async def unblock_ip_route(ip: str, db: Session = Depends(get_db)):
    """Unblock an IP address and update the database."""
    if not unblock_ip(ip):
        raise HTTPException(status_code=500, detail="Failed to unblock IP")
    
    # Update the blocked IP record in the database
    blocked_ip = db.query(models.BlockedIP).filter(
        models.BlockedIP.ip_address == ip,
        models.BlockedIP.unblocked_at == None
    ).first()
    
    if blocked_ip:
        blocked_ip.unblocked_at = datetime.utcnow()
        db.commit()
    
    return {
        "status": "unblocked",
        "ip": ip,
        "timestamp": datetime.utcnow()
    }

@router.get("/ipblock/list")
async def list_blocked_ips(db: Session = Depends(get_db)):
    """List all blocked IPs."""
    blocked_ips = db.query(models.BlockedIP).filter(
        models.BlockedIP.unblocked_at == None
    ).all()
    
    return [
        {
            "ip": ip.ip_address,
            "reason": ip.reason,
            "blocked_at": ip.blocked_at,
            "unblocked_at": ip.unblocked_at
        }
        for ip in blocked_ips
    ] 