from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from sqlalchemy import func

router = APIRouter()

@router.get("/dashboard/stats")
async def dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    # Get total requests
    total_requests = db.query(func.count(models.AttackLog.id)).scalar() or 0
    
    # Get blocked IPs
    blocked_ips = db.query(func.count(models.BlockedIP.id)).scalar() or 0
    
    # Get active alerts
    active_alerts = db.query(func.count(models.Alert.id)).filter(
        models.Alert.status == "active"
    ).scalar() or 0
    
    # Get recent attacks
    recent_attacks = db.query(models.AttackLog).order_by(
        models.AttackLog.timestamp.desc()
    ).limit(5).all()
    
    return {
        "total_requests": total_requests,
        "blocked_ips": blocked_ips,
        "active_alerts": active_alerts,
        "recent_attacks": [
            {
                "timestamp": attack.timestamp,
                "type": attack.attack_type,
                "source_ip": attack.source_ip,
                "target": attack.target,
                "severity": attack.severity,
                "action": attack.action
            }
            for attack in recent_attacks
        ]
    }

@router.get("/dashboard/uptime")
async def dashboard_uptime():
    """Get system uptime."""
    import psutil
    import time
    
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    
    days = int(uptime_seconds // (24 * 3600))
    hours = int((uptime_seconds % (24 * 3600)) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    
    return {
        "uptime": {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        },
        "boot_time": boot_time,
        "total_seconds": uptime_seconds
    } 