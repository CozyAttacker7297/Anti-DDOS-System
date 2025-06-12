import subprocess
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.blocked_ip import BlockedIP
from ..schemas.security import SecurityEventCreate
from ..crud import create_security_event

logger = logging.getLogger(__name__)

def _run_iptables_command(command: List[str]) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error(f"iptables command failed: {result.stderr}")
        return result
    except Exception as e:
        logger.error(f"Error running iptables command: {e}")
        raise

def block_ip(ip: str, db: Session, reason: str = "Suspicious activity") -> bool:
    from . import crud
    if get_blocked_ips(db, ip=ip):
        logger.info(f"IP {ip} is already blocked")
        return True

    result = _run_iptables_command(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    if result.returncode == 0:
        blocked_ip = BlockedIP(ip_address=ip, reason=reason, blocked_at=datetime.utcnow())
        db.add(blocked_ip)
        event = SecurityEventCreate(
            event_type="IP_BLOCK",
            source_ip=ip,
            severity="high",
            description=f"IP {ip} blocked: {reason}",
            status="resolved",
            details={"action": "blocked", "reason": reason}
        )
        create_security_event(db, event)
        db.commit()
        logger.info(f"Successfully blocked IP {ip}")
        return True
    else:
        logger.error(f"Failed to block IP {ip}: {result.stderr}")
        return False

def unblock_ip(ip: str, db: Session) -> bool:
    from . import crud
    result = _run_iptables_command(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"])
    if result.returncode == 0:
        blocked_ip = db.query(BlockedIP).filter(BlockedIP.ip_address == ip).first()
        if blocked_ip:
            blocked_ip.unblocked_at = datetime.utcnow()
            blocked_ip.is_active = False
            event = SecurityEventCreate(
                event_type="IP_UNBLOCK",
                source_ip=ip,
                severity="low",
                description=f"IP {ip} unblocked",
                status="resolved",
                details={"action": "unblocked"}
            )
            create_security_event(db, event)
            db.commit()
            logger.info(f"Successfully unblocked IP {ip}")
            return True
    else:
        logger.error(f"Failed to unblock IP {ip}: {result.stderr}")
        return False

def get_blocked_ips(db: Session, ip: Optional[str] = None) -> List[Dict]:
    try:
        query = db.query(BlockedIP).filter(BlockedIP.is_active == True)
        if ip:
            query = query.filter(BlockedIP.ip_address == ip)
        return [
            {
                "ip_address": ip.ip_address,
                "reason": ip.reason,
                "blocked_at": ip.blocked_at,
                "unblocked_at": ip.unblocked_at,
                "is_active": ip.is_active
            }
            for ip in query.all()
        ]
    except Exception as e:
        logger.error(f"Error getting blocked IPs: {e}")
        return []
