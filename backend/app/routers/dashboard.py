from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.traffic_stats import TrafficStats
from ..models.attack_log import AttackLog
from sqlalchemy import func
import time
from datetime import datetime, timedelta
import random
from ..models.server import Server

router = APIRouter()

@router.get("/dashboard/stats")
async def dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    # Get total requests from traffic stats
    total_requests = db.query(func.sum(TrafficStats.clean_requests + TrafficStats.malicious_requests)).scalar() or 0
    
    # Get blocked attacks from attack logs
    blocked_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.action == "blocked"
    ).scalar() or 0
    
    # Get malicious requests from traffic stats
    malicious_requests = db.query(func.sum(TrafficStats.malicious_requests)).scalar() or 0
    
    # Get clean traffic from traffic stats
    clean_traffic = db.query(func.sum(TrafficStats.clean_requests)).scalar() or 0
    
    # Calculate uptime
    boot_time = time.time()
    uptime_seconds = int(time.time() - boot_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    return [
        {
            "title": "ATTACKS BLOCKED",
            "value": str(blocked_attacks),
            "change": "Real-time",
            "type": "danger",
            "isPositive": False
        },
        {
            "title": "MALICIOUS REQUESTS",
            "value": str(malicious_requests),
            "change": "Real-time",
            "type": "warning",
            "isPositive": True
        },
        {
            "title": "CLEAN TRAFFIC",
            "value": str(clean_traffic),
            "change": "Real-time",
            "type": "success",
            "isPositive": True
        },
        {
            "title": "UPTIME",
            "value": uptime,
            "change": "No attacks yet",
            "type": "info",
            "isPositive": True
        }
    ]

@router.get("/dashboard/attack-stats")
async def attack_stats(db: Session = Depends(get_db)):
    """Get attack statistics."""
    # Define attack types
    attack_types = ['SQLi', 'XSS', 'DDoS', 'Brute Force', 'Port Scan', 'Malware']
    
    # Get attack counts for each type in the last 24 hours
    start_time = datetime.utcnow() - timedelta(hours=24)
    attack_counts = []
    
    for attack_type in attack_types:
        count = db.query(func.count(AttackLog.id)).filter(
            AttackLog.attack_type == attack_type,
            AttackLog.timestamp >= start_time
        ).scalar() or 0
        attack_counts.append(count)
    
    # Get recent attacks for the table
    recent_attacks = db.query(AttackLog).order_by(
        AttackLog.timestamp.desc()
    ).limit(5).all()
    
    # Get total attacks in the last 24 hours
    total_attacks = db.query(func.count(AttackLog.id)).filter(
        AttackLog.timestamp >= start_time
    ).scalar() or 0
    
    return {
        "labels": attack_types,
        "data": attack_counts,
        "total_attacks": total_attacks,
        "recent_attacks": [
            {
                "timestamp": attack.timestamp.isoformat(),
                "type": attack.attack_type,
                "source_ip": attack.source_ip,
                "target": attack.target,
                "severity": attack.severity,
                "action": attack.action,
                "status": attack.status,
                "description": attack.description
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

@router.post("/dashboard/generate-test-data")
async def generate_test_data(db: Session = Depends(get_db)):
    """Generate test data for dashboard visualization"""
    try:
        # Clear old data
        db.query(TrafficStats).delete()
        db.query(AttackLog).delete()
        db.commit()

        # Create test server if not exists
        test_server = db.query(Server).filter(Server.name == "Test Server").first()
        if not test_server:
            test_server = Server(
                name="Test Server",
                ip_address="192.168.1.100",
                port=80,
                status="active",
                health_status="healthy",
                last_health_check=datetime.utcnow()
            )
            db.add(test_server)
            db.commit()
            db.refresh(test_server)

        # Generate traffic stats for the last 24 hours
        now = datetime.utcnow()
        for i in range(24):
            timestamp = now - timedelta(hours=i)
            # Make some hours have high malicious traffic
            if i % 5 == 0:
                clean = random.randint(10, 100)
                malicious = random.randint(100, 300)
            else:
                clean = random.randint(100, 1000)
                malicious = random.randint(0, 30)
            
            total = clean + malicious
            traffic_stats = TrafficStats(
                timestamp=timestamp,
                clean_requests=clean,
                malicious_requests=malicious,
                total_requests=total,
                requests_per_second=random.uniform(1.0, 10.0),
                bandwidth_usage={
                    "bytes_sent": random.randint(1000, 1000000),
                    "bytes_received": random.randint(1000, 1000000)
                },
                active_connections=random.randint(10, 100),
                error_rate=random.uniform(0.0, 5.0),
                details={
                    "source": "test_data",
                    "hour": i,
                    "peak_requests": random.randint(total, total * 2)
                }
            )
            db.add(traffic_stats)

        # Generate attack logs for the last 24 hours
        attack_types = ['SQLi', 'XSS', 'DDoS', 'Brute Force', 'Port Scan', 'Malware']
        severities = ['low', 'medium', 'high', 'critical']
        actions = ['blocked', 'monitored', 'allowed']
        statuses = ['detected', 'prevented', 'investigating']
        
        for i in range(24):
            for attack_type in attack_types:
                num_attacks = random.randint(2, 8)  # Random number of attacks per type per hour
                for _ in range(num_attacks):
                    timestamp = now - timedelta(hours=i, minutes=random.randint(0, 59), seconds=random.randint(0, 59))
                    attack_log = AttackLog(
                        timestamp=timestamp,
                        attack_type=attack_type,
                        source_ip=f"192.168.1.{random.randint(1, 255)}",
                        target=f"/api/{random.choice(['users', 'admin', 'data', 'config'])}",
                        severity=random.choice(severities),
                        action=random.choice(actions),
                        status=random.choice(statuses),
                        description=f"Test {attack_type} attack",
                        details={
                            "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
                            "headers": {"User-Agent": "Test Bot"},
                            "payload": "Test payload"
                        }
                    )
                    db.add(attack_log)

        db.commit()
        return {"status": "success", "message": "Test data generated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 