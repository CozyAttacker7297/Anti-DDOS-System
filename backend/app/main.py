from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .models.base import Base
from .models.alert import Alert
from .database import SessionLocal, engine, get_db, init_db
from .schemas import AlertCreate, AlertResponse  # Import alert schemas
import psutil
import os
from dotenv import load_dotenv
import time
import logging
import datetime
from typing import List, Dict
import uvicorn
from pydantic import BaseModel
from collections import defaultdict
from sqlalchemy import func
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from .routers.load_balancer import router as load_balancer_router
from .models.attack_log import AttackLog

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

# Include router for load balancer endpoints
app.include_router(load_balancer_router)

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
        "timestamp": datetime.datetime.now().isoformat(),
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

async def get_new_alert():
    db: Session = SessionLocal()
    alert = db.query(Alert).order_by(Alert.created_at.desc()).first()
    db.close()
    if alert:
        return {
            "id": alert.id,
            "title": alert.title,
            "description": alert.description,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "status": alert.status,
            "created_at": alert.created_at.isoformat(),
            "source": alert.source,
            "details": alert.details
        }
    return {"message": "No alerts found"}

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
    logs = db.query(AttackLog).order_by(AttackLog.timestamp.desc()).all()
    return [
        {
            "timestamp": log.timestamp,
            "type": log.attack_type,
            "source_ip": log.source_ip,
            "target": log.target,
            "severity": log.severity,
            "action": log.action
        }
        for log in logs
    ]

# Route to add a new alert into the database
@app.post("/add_alert/")
async def add_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Add a new alert and broadcast it to all connected clients."""
    try:
        # Create alert in database
        db_alert = Alert(
            title=alert.title,
            description=alert.description,
            alert_type=alert.alert_type,
            severity=alert.severity,
            source=alert.source,
            details=alert.details,
            status="new"
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)

        # Broadcast alert to all connected clients
        await broadcast_new_alert(db_alert)

        return AlertResponse(
            id=db_alert.id,
            title=db_alert.title,
            description=db_alert.description,
            alert_type=db_alert.alert_type,
            severity=db_alert.severity,
            status=db_alert.status,
            created_at=db_alert.created_at,
            source=db_alert.source,
            details=db_alert.details
        )
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating alert")

# Function to broadcast the new alert to all WebSocket clients
async def broadcast_new_alert(alert: Alert):
    """Broadcast a new alert to all connected WebSocket clients."""
    if not connected_clients:
        logger.info("No connected clients to broadcast alert to")
        return

    alert_data = {
        "id": alert.id,
        "title": alert.title,
        "description": alert.description,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "status": alert.status,
        "created_at": alert.created_at.isoformat(),
        "source": alert.source,
        "details": alert.details
    }

    disconnected_clients = []
    for client in connected_clients:
        try:
            await client.send_json({
                "type": "alert",
                "data": alert_data
            })
            logger.info(f"Alert broadcasted to client: {id(client)}")
        except WebSocketDisconnect:
            disconnected_clients.append(client)
            logger.info(f"Client disconnected during broadcast: {id(client)}")
        except Exception as e:
            logger.error(f"Error broadcasting alert to client {id(client)}: {e}")
            disconnected_clients.append(client)

    # Clean up disconnected clients
    for client in disconnected_clients:
        if client in connected_clients:
            connected_clients.remove(client)
            logger.info(f"Removed disconnected client: {id(client)}")

# Route to fetch current server health (CPU/RAM)
@app.get("/api/server-health")
async def server_health():
    health_data = await get_server_health()
    return health_data

# Test connection to verify that the backend is connected
@app.get("/api/test-connection")
async def test_connection():
    return {
        "status": "success",
        "message": "Backend is connected!",
        "timestamp": time.time()
    }

# Function to update traffic stats in database asynchronously
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
                error_rate=0.0
            )
            db.add(latest_stats)
        
        # Update stats
        if is_malicious:
            latest_stats.malicious_requests += 1
        else:
            latest_stats.clean_requests += 1
        
        latest_stats.total_requests = latest_stats.clean_requests + latest_stats.malicious_requests
        
        # Calculate requests per second (simple moving average)
        time_diff = datetime.datetime.utcnow() - latest_stats.timestamp
        if time_diff.total_seconds() > 0:
            latest_stats.requests_per_second = latest_stats.total_requests / time_diff.total_seconds()
        
        db.commit()
        return latest_stats
    except Exception as e:
        logger.error(f"Error updating traffic stats in database: {e}")
        db.rollback()
        return None

def cleanup_request_counts():
    current_time = time.time()
    stale_keys = [k for k, v in request_counts.items() if (current_time - v["last_request"]) > 30]
    for k in stale_keys:
        del request_counts[k]

@app.middleware("http")
async def track_traffic_middleware(request: Request, call_next):
    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"
    
    # Cleanup old request counts
    cleanup_request_counts()
    
    # Read request body once
    body_content = await request.body()
    
    # Check for malicious indicators
    is_malicious = False
    attack_type = None
    
    # Get headers and body as strings for checking
    headers_str = str(request.headers)
    body_str = body_content.decode() if body_content else ""
    
    # Check user agent
    user_agent = request.headers.get("user-agent", "").lower()
    if any(bot in user_agent for bot in ["botnet", "sql", "scan", "injection", "bruteforce"]):
        is_malicious = True
        attack_type = "bot"
    
    # Check attack type headers
    if request.headers.get("x-attack-type"):
        is_malicious = True
        attack_type = request.headers.get("x-attack-type")
    
    # Check content type for SQL injection
    if "application/x-www-form-urlencoded" in request.headers.get("content-type", ""):
        if any(inj in body_str.lower() for inj in ["'or'1'='1", "union select", "drop table"]):
            is_malicious = True
            attack_type = "injection"
    
    # Check for suspicious paths
    if any(path in request.url.path for path in ["/admin", "/config", "/settings"]):
        if "bot" in user_agent:
            is_malicious = True
            attack_type = "scan"
    
    # Check rate limit
    current_time = time.time()
    if client_host in request_counts:
        if current_time - request_counts[client_host]["last_request"] < 0.1:  # 100ms threshold
            request_counts[client_host]["count"] += 1
            if request_counts[client_host]["count"] > 10:  # More than 10 requests per 100ms
                is_malicious = True
                attack_type = "flood"
        else:
            request_counts[client_host] = {"count": 1, "last_request": current_time}
    else:
        request_counts[client_host] = {"count": 1, "last_request": current_time}
    
    # Update traffic stats in database
    db = next(get_db())
    try:
        stats = await update_traffic_stats_db(db, is_malicious)
        
        # If malicious, save to attack logs
        if is_malicious:
            attack_log = AttackLog(
                timestamp=datetime.datetime.utcnow(),
                source_ip=client_host,
                attack_type=attack_type or "unknown",
                target=request.url.path,
                severity="high",
                action="blocked",
                headers=dict(request.headers),
                body=body_str
            )
            db.add(attack_log)
            db.commit()
            
            logger.warning(f"Potential attack detected from {client_host}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving attack log: {str(e)}")
    finally:
        db.close()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate request duration
    duration = time.time() - start_time
    
    # Log the request
    logger.info(f"Request: {request.method} {request.url.path} - Duration: {duration:.3f}s")
    
    return response

# Error handling middleware for catching exceptions
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
@app.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info("WebSocket connection established")

        while True:
            message = await websocket.receive_text()
            if message == "get_stats":
                stats_data = await get_stats_data()
                await websocket.send_json(stats_data)
            else:
                await websocket.send_text(f"Unknown command: {message}")
    except Exception as e:
        logger.error(f"Error in WebSocket: {str(e)}")
    finally:
        logger.info("WebSocket connection closed")
        await websocket.close()



# Function to generate stats (this can be dynamic based on DB, etc.)
async def get_stats_data():
    return [
        {
            "title": "ATTACKS BLOCKED",
            "value": "0",
            "change": "12% from yesterday",
            "type": "danger",
            "isPositive": False
        },
        {
            "title": "MALICIOUS REQUESTS",
            "value": "5,732",
            "change": "8% from yesterday",
            "type": "warning",
            "isPositive": True
        },
        {
            "title": "CLEAN TRAFFIC",
            "value": "2.1M",
            "change": "3% from yesterday",
            "type": "success",
            "isPositive": True
        },
        {
            "title": "UPTIME",
            "value": "99.98%",
            "change": "All systems normal",
            "type": "info",
            "isPositive": True
        }
    ]

class AttackPrediction(BaseModel):
    source_ip: str
    target: str
    request_rate: int
    payload_size: int
    request_type: str
    user_agent: str

@app.post("/api/predict-attack")
async def predict_attack(attack_data: AttackPrediction):
    try:
        # Log the attack attempt
        logger.warning(f"Potential attack detected from {attack_data.source_ip}")
        
        # Analyze the request
        is_attack = False
        attack_type = None
        
        # Check for flood attack
        if attack_data.request_rate > 500:
            is_attack = True
            attack_type = "flood"
        
        # Check for large payload
        if attack_data.payload_size > 10000:
            is_attack = True
            attack_type = "payload"
        
        # Check for suspicious user agent
        if "BotNet" in attack_data.user_agent:
            is_attack = True
            attack_type = "botnet"
        
        # Record the attack in the database
        if is_attack:
            new_attack = AttackLog(
                source_ip=attack_data.source_ip,
                target=attack_data.target,
                type=attack_type,
                severity="high" if attack_data.request_rate > 1000 else "medium",
                action="blocked"
            )
            db = SessionLocal()
            db.add(new_attack)
            db.commit()
            db.refresh(new_attack)
            db.close()
            
            # Broadcast the attack via WebSocket
            await broadcast_new_alert(new_attack)
        
        return {
            "is_attack": is_attack,
            "attack_type": attack_type,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error processing attack prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Update the stats endpoint to include historical data
@app.get("/api/dashboard/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get current traffic statistics."""
    try:
        # Get latest traffic stats
        latest_stats = db.query(TrafficStats).order_by(TrafficStats.timestamp.desc()).first()
        
        if not latest_stats:
            latest_stats = TrafficStats(
                clean_requests=0,
                malicious_requests=0,
                total_requests=0,
                requests_per_second=0.0,
                bandwidth_usage={"bytes_sent": 0, "bytes_received": 0},
                active_connections=0,
                error_rate=0.0
            )
            db.add(latest_stats)
            db.commit()
        
        # Get total attacks and latest attack timestamp
        latest_attack = db.query(AttackLog).order_by(AttackLog.timestamp.desc()).first()
        total_attacks = db.query(AttackLog).count()
        
        # Calculate uptime based on latest attack
        uptime_seconds = 0
        if latest_attack:
            uptime_seconds = (datetime.datetime.utcnow() - latest_attack.timestamp).total_seconds()
        
        return {
            "traffic_stats": {
                "clean_requests": latest_stats.clean_requests,
                "malicious_requests": latest_stats.malicious_requests,
                "total_requests": latest_stats.total_requests,
                "requests_per_second": latest_stats.requests_per_second,
                "bandwidth_usage": latest_stats.bandwidth_usage,
                "active_connections": latest_stats.active_connections,
                "error_rate": latest_stats.error_rate
            },
            "attack_stats": {
                "total_attacks": total_attacks,
                "latest_attack": latest_attack.timestamp if latest_attack else None,
                "uptime_seconds": uptime_seconds
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

@app.get("/api/dashboard/attack-stats")
async def get_attack_stats(db: Session = Depends(get_db)):
    try:
        # Get attack counts by type for the last 24 hours
        one_day_ago = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        
        # Query attack logs grouped by type
        attack_stats = db.query(
            AttackLog.attack_type,
            func.count(AttackLog.id).label('count')
        ).filter(
            AttackLog.timestamp >= one_day_ago
        ).group_by(
            AttackLog.attack_type
        ).all()
        
        # Create a dictionary of attack types with their counts
        attack_counts = {
            'SQLi': 0,
            'XSS': 0,
            'DDoS': 0,
            'Brute Force': 0,
            'Port Scan': 0,
            'Malware': 0
        }
        
        # Update counts from database
        for attack_type, count in attack_stats:
            # Map database attack types to our categories
            if attack_type:
                attack_type = attack_type.lower()
                if 'sql' in attack_type:
                    attack_counts['SQLi'] += count
                elif 'xss' in attack_type:
                    attack_counts['XSS'] += count
                elif 'ddos' in attack_type or 'flood' in attack_type:
                    attack_counts['DDoS'] += count
                elif 'brute' in attack_type:
                    attack_counts['Brute Force'] += count
                elif 'port' in attack_type or 'scan' in attack_type:
                    attack_counts['Port Scan'] += count
                elif 'malware' in attack_type or 'botnet' in attack_type:
                    attack_counts['Malware'] += count
        
        return {
            'labels': list(attack_counts.keys()),
            'data': list(attack_counts.values())
        }
    except Exception as e:
        logger.error(f"Error getting attack stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving attack statistics")

# Add this at the bottom of the file
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        workers=4,  # Increase number of workers
        timeout_keep_alive=120,  # Increase keep-alive timeout
        limit_concurrency=1000,  # Increase concurrent connection limit
        backlog=2048  # Increase connection backlog
    )
