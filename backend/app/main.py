from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .models.base import Base
from .models.traffic_stats import TrafficStats
from .database import SessionLocal, engine, get_db, init_db
from .routers import dashboard, load_balancer, server_health
import psutil
import os
from dotenv import load_dotenv
import time
import logging
from typing import List, Dict
import uvicorn
from pydantic import BaseModel
from collections import defaultdict
from sqlalchemy import func
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from .models.attack_log import AttackLog
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter with higher limits
limiter = Limiter(key_func=get_remote_address)

# Initialize WebSocket clients list
connected_clients: List[WebSocket] = []

# Traffic tracking with thread-safe counters
traffic_stats = {
    "clean_requests": 0,
    "malicious_requests": 0,
    "last_update": time.time()
}

# Create thread pool for database operations
db_executor = ThreadPoolExecutor(max_workers=20)

# Create an instance of the FastAPI app
app = FastAPI(
    title="Anti-DDOS System API",
    description="Backend API for the Anti-DDOS System Dashboard",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router, prefix="/api")
app.include_router(load_balancer.router, prefix="/api")
app.include_router(server_health.router, prefix="/api")

# Initialize request tracking
request_counts = {}  # Track request counts per IP

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")

# Configure CORS
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware
TRUSTED_HOSTS = os.getenv(
    "TRUSTED_HOSTS",
    "localhost,127.0.0.1"
).split(",")

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=TRUSTED_HOSTS
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the application."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws/server-health")
async def websocket_server_health(websocket: WebSocket):
    await websocket.accept()
    try:
        connected_clients.append(websocket)
        logger.info(f"Client connected. Total clients: {len(connected_clients)}")
        
        while True:
            try:
                message = await websocket.receive_text()
                if message == "get_health":
                    health_data = await health_check()
                    await websocket.send_json(health_data)
                elif message == "get_stats":
                    stats_data = await get_stats_data()
                    await websocket.send_json(stats_data)
                else:
                    await websocket.send_json({"error": f"Unknown command: {message}"})
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_json({"error": "Internal server error"})
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
            logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")

# Helper functions to interact with the database using SQLAlchemy
async def get_server_health():
    loop = asyncio.get_event_loop()
    cpu = await loop.run_in_executor(None, lambda: psutil.cpu_percent(interval=1))
    ram = psutil.virtual_memory().percent
    return {"cpu": cpu, "ram": ram}

async def get_recent_attack_logs():
    db: Session = SessionLocal()
    attack_logs = db.query(AttackLog).order_by(AttackLog.timestamp.desc()).limit(5).all()
    db.close()
    logs = []
    for log in attack_logs:
        logs.append({
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "type": log.attack_type,
            "source_ip": log.source_ip,
            "target": log.target,
            "severity": log.severity,
            "action": log.action
        })
    return logs

# Route to fetch attack logs via HTTP request
@app.get("/api/get-attack-logs")
async def get_attack_logs(db: Session = Depends(get_db)):
    """Get recent attack logs."""
    try:
        # Get the last 50 attack logs, ordered by most recent
        logs = db.query(AttackLog).order_by(AttackLog.timestamp.desc()).limit(50).all()
        
        return [
            {
                "timestamp": log.timestamp,
                "type": log.attack_type,
                "source_ip": log.source_ip,
                "target": log.target if hasattr(log, 'target') else "Unknown",
                "severity": log.severity if hasattr(log, 'severity') else "medium",
                "action": log.action if hasattr(log, 'action') else "detected"
            }
            for log in logs
        ]
    except Exception as e:
        logger.error(f"Error getting attack logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving attack logs")

@app.get("/api/server-health")
async def server_health():
    """Get server health metrics."""
    return await get_server_health()

@app.get("/api/test-connection")
async def test_connection():
    """Test endpoint to verify API connectivity."""
    return {"status": "connected", "message": "API is reachable"}

async def update_traffic_stats_db(db: Session, is_malicious: bool):
    """Update traffic statistics in the database."""
    try:
        # Get the latest stats record
        latest_stats = db.query(TrafficStats).order_by(TrafficStats.timestamp.desc()).first()
        
        if not latest_stats:
            # Create new stats record if none exists
            latest_stats = TrafficStats(
                clean_requests=0,
                malicious_requests=0,
                total_requests=0,
                requests_per_second=0.0,
                bandwidth_usage={"bytes_sent": 0, "bytes_received": 0},
                active_connections=0,
                error_rate=0.0,
                timestamp=datetime.now()
            )
            db.add(latest_stats)
        
        # Update stats
        if is_malicious:
            latest_stats.malicious_requests += 1
        else:
            latest_stats.clean_requests += 1
        latest_stats.total_requests = latest_stats.clean_requests + latest_stats.malicious_requests
        
        # Calculate requests per second (simple moving average)
        current_time = datetime.now()
        if latest_stats.timestamp:
            time_diff = current_time - latest_stats.timestamp
            if time_diff.total_seconds() > 0:
                latest_stats.requests_per_second = latest_stats.total_requests / time_diff.total_seconds()
        
        # Update timestamp
        latest_stats.timestamp = current_time
        
        db.commit()
        return latest_stats
    except Exception as e:
        logger.error(f"Error updating traffic stats: {e}")
        db.rollback()
        return None

def cleanup_request_counts():
    """Clean up old request counts periodically."""
    current_time = time.time()
    for ip in list(request_counts.keys()):
        if current_time - request_counts[ip]["last_request"] > 3600:  # 1 hour
            del request_counts[ip]

@app.middleware("http")
async def track_traffic_middleware(request: Request, call_next):
    """Middleware to track traffic and detect suspicious activity."""
    try:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Initialize or update request count for this IP
        if client_ip not in request_counts:
            request_counts[client_ip] = {"count": 0, "last_request": time.time()}
        
        request_counts[client_ip]["count"] += 1
        request_counts[client_ip]["last_request"] = time.time()
        
        # Check for suspicious activity
        if request_counts[client_ip]["count"] > 100:  # More than 100 requests per minute
            logger.warning(f"Suspicious activity detected from IP: {client_ip}")
            # Update traffic stats to mark this as malicious
            db = SessionLocal()
            try:
                await update_traffic_stats_db(db, True)
                traffic_stats["malicious_requests"] += 1
            finally:
                db.close()
        
        # Process the request
        response = await call_next(request)
        
        # Update clean traffic stats for successful requests
        if response.status_code == 200:
            db = SessionLocal()
            try:
                await update_traffic_stats_db(db, False)
                traffic_stats["clean_requests"] += 1
            finally:
                db.close()
        
        return response
        
    except Exception as e:
        logger.error(f"Error in track_traffic_middleware: {e}")
        return await call_next(request)

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """Middleware to handle errors and provide consistent error responses."""
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

@app.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    """WebSocket endpoint for real-time traffic statistics."""
    await websocket.accept()
    try:
        connected_clients.append(websocket)
        while True:
            try:
                message = await websocket.receive_text()
                if message == "get_stats":
                    stats = await get_stats_data()
                    await websocket.send_json(stats)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket stats: {e}")
                await websocket.send_json({"error": "Internal server error"})
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def get_stats_data():
    """Get current traffic statistics."""
    try:
        # Get database session
        db = SessionLocal()
        
        # Get traffic stats from database
        recent_stats = db.query(TrafficStats).order_by(
            TrafficStats.timestamp.desc()
        ).limit(100).all()
        
        # Calculate statistics
        total_requests = len(recent_stats)
        malicious_requests = sum(1 for stat in recent_stats if stat.is_malicious)
        clean_requests = total_requests - malicious_requests
        
        # Get attack logs
        attack_logs = db.query(AttackLog).order_by(
            AttackLog.timestamp.desc()
        ).limit(10).all()
        
        # Format attack logs
        formatted_logs = [
            {
                "timestamp": log.timestamp.isoformat(),
                "type": log.attack_type,
                "source_ip": log.source_ip,
                "target": log.target if hasattr(log, 'target') else "Unknown",
                "severity": log.severity if hasattr(log, 'severity') else "medium",
                "action": log.action if hasattr(log, 'action') else "detected"
            }
            for log in attack_logs
        ]
        
        # Get server health
        health = await get_server_health()
        
        return {
            "traffic_stats": {
                "total_requests": total_requests,
                "malicious_requests": malicious_requests,
                "clean_requests": clean_requests,
                "last_update": datetime.now().isoformat()
            },
            "attack_logs": formatted_logs,
            "server_health": health
        }
    except Exception as e:
        logger.error(f"Error getting stats data: {e}")
        return {
            "error": "Failed to get statistics",
            "details": str(e)
        }
    finally:
        db.close()

class AttackPrediction(BaseModel):
    source_ip: str
    target: str
    request_rate: int
    payload_size: int
    request_type: str
    user_agent: str

@app.post("/api/predict-attack")
async def predict_attack(
    request: Request,
    db: Session = Depends(get_db)
):
    """Predict if a request is malicious and update stats."""
    try:
        # Get request data
        data = await request.json()
        logger.info(f"Received predict-attack request with data: {data}")
        
        # Extract data with defaults
        source_ip = data.get("source_ip", "unknown")
        target = data.get("target", "unknown")
        request_rate = int(data.get("request_rate", 0))
        payload_size = int(data.get("payload_size", 0))
        request_type = data.get("request_type", "GET")
        user_agent = data.get("user_agent", "unknown")

        # Simple attack detection logic
        is_malicious = False
        attack_type = None
        severity = "low"
        action = "monitored"

        # Check for suspicious patterns
        if request_rate > 1000:  # High request rate
            is_malicious = True
            attack_type = "DDoS"
            severity = "high"
            action = "blocked"
        elif payload_size > 1000000:  # Large payload
            is_malicious = True
            attack_type = "Payload Attack"
            severity = "medium"
            action = "blocked"
        elif "sql" in user_agent.lower() or "injection" in user_agent.lower():
            is_malicious = True
            attack_type = "SQL Injection"
            severity = "high"
            action = "blocked"
        elif "scan" in user_agent.lower():
            is_malicious = True
            attack_type = "Port Scan"
            severity = "medium"
            action = "monitored"

        # Update traffic stats in database
        try:
            await update_traffic_stats_db(db, is_malicious)
            logger.info(f"Updated traffic stats - malicious: {is_malicious}")
        except Exception as e:
            logger.error(f"Error updating traffic stats: {e}")

        # If malicious, log the attack
        if is_malicious:
            try:
                attack_log = AttackLog(
                    timestamp=datetime.now(),
                    attack_type=attack_type,
                    source_ip=source_ip,
                    target=target,
                    severity=severity,
                    action=action,
                    status="detected",
                    description=f"Detected {attack_type} attack",
                    details={
                        "request_rate": request_rate,
                        "payload_size": payload_size,
                        "request_type": request_type,
                        "user_agent": user_agent
                    }
                )
                db.add(attack_log)
                db.commit()
                logger.info(f"Logged attack: {attack_type} from {source_ip}")
            except Exception as e:
                logger.error(f"Error logging attack: {e}")
                db.rollback()

        # Update in-memory stats
        if is_malicious:
            traffic_stats["malicious_requests"] += 1
        else:
            traffic_stats["clean_requests"] += 1
        traffic_stats["last_update"] = time.time()

        response_data = {
            "is_malicious": is_malicious,
            "attack_type": attack_type,
            "severity": severity,
            "action": action,
            "message": f"Request {'blocked' if is_malicious else 'allowed'}"
        }
        logger.info(f"Sending response: {response_data}")
        return response_data

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        logger.error(f"Request body: {await request.body()}")
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON data"}
        )
    except Exception as e:
        logger.error(f"Error in predict_attack: {str(e)}")
        logger.error(f"Request body: {await request.body()}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error processing request: {str(e)}"}
        )

@app.get("/api/dashboard/stats")
async def get_stats():
    """Get dashboard statistics."""
    return await get_stats_data()

@app.get("/api/dashboard/attack-stats")
async def get_attack_stats(db: Session = Depends(get_db)):
    """Get attack statistics for the dashboard."""
    try:
        # Get recent attack logs
        recent_attacks = db.query(AttackLog).order_by(
            AttackLog.timestamp.desc()
        ).limit(100).all()
        
        # Calculate statistics
        total_attacks = len(recent_attacks)
        attack_types = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for attack in recent_attacks:
            attack_types[attack.attack_type] += 1
            severity_counts[attack.severity] += 1
        
        # Get top attacking IPs
        top_attackers = db.query(
            AttackLog.source_ip,
            func.count(AttackLog.id).label('attack_count')
        ).group_by(AttackLog.source_ip).order_by(
            func.count(AttackLog.id).desc()
        ).limit(5).all()
        
        return {
            "total_attacks": total_attacks,
            "attack_types": dict(attack_types),
            "severity_distribution": dict(severity_counts),
            "top_attackers": [
                {"ip": ip, "count": count}
                for ip, count in top_attackers
            ],
            "recent_attacks": [
                {
                    "timestamp": attack.timestamp.isoformat(),
                    "type": attack.attack_type,
                    "source_ip": attack.source_ip,
                    "target": attack.target if hasattr(attack, 'target') else "Unknown",
                    "severity": attack.severity if hasattr(attack, 'severity') else "medium",
                    "action": attack.action if hasattr(attack, 'action') else "detected"
                }
                for attack in recent_attacks[:10]  # Last 10 attacks
            ]
        }
    except Exception as e:
        logger.error(f"Error getting attack stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-traffic")
async def test_traffic(db: Session = Depends(get_db)):
    """Test endpoint to generate traffic for testing."""
    try:
        # Create a test traffic stats record
        stats = TrafficStats(
            timestamp=datetime.now(),
            is_malicious=False,
            request_count=1
        )
        db.add(stats)
        db.commit()
        
        return {
            "status": "success",
            "message": "Test traffic recorded",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error recording test traffic: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test-attack")
async def test_attack(db: Session = Depends(get_db)):
    """Test endpoint to simulate an attack and update stats."""
    try:
        # Create a test attack log
        attack_log = AttackLog(
            timestamp=datetime.now(),
            attack_type="DDoS",
            source_ip="192.168.1.100",
            target="/api/admin",
            severity="high",
            action="blocked",
            status="detected",
            description="Test DDoS attack",
            details={
                "method": "POST",
                "headers": {"User-Agent": "Test Bot"},
                "payload": "Test payload"
            }
        )
        db.add(attack_log)
        
        # Update traffic stats
        latest_stats = db.query(TrafficStats).order_by(TrafficStats.timestamp.desc()).first()
        if not latest_stats:
            latest_stats = TrafficStats(
                clean_requests=0,
                malicious_requests=0,
                total_requests=0,
                requests_per_second=0.0,
                bandwidth_usage={"bytes_sent": 0, "bytes_received": 0},
                active_connections=0,
                error_rate=0.0,
                timestamp=datetime.now()
            )
            db.add(latest_stats)
        
        # Increment malicious requests
        latest_stats.malicious_requests += 1
        latest_stats.total_requests += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Test attack simulated",
            "attack": {
                "type": "DDoS",
                "source_ip": "192.168.1.100",
                "target": "/api/admin",
                "severity": "high",
                "action": "blocked"
            }
        }
    except Exception as e:
        logger.error(f"Error simulating attack: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Add this at the bottom of the file
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        workers=2,  # Reduced number of workers
        timeout_keep_alive=30,  # Reduced keep-alive timeout
        limit_concurrency=100,  # Reduced concurrent connection limit
        backlog=128,  # Reduced connection backlog
        loop="uvloop",  # Use uvloop for better performance
        http="httptools",  # Use httptools for better performance
        log_level="info"
    )
