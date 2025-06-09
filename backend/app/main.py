from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from . import models
from .database import SessionLocal, engine
import psutil
import os
from dotenv import load_dotenv
import time
import logging
import datetime
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create an instance of the FastAPI app
app = FastAPI(
    title="Anti-DDOS System API",
    description="Backend API for the Anti-DDOS System Dashboard",
    version="1.0.0"
)

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

# Database models and session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# WebSocket to listen for real-time updates
@app.websocket("/ws/server-health")
async def websocket_server_health(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()

            if message == "get_health":
                health_data = await get_server_health()
                await websocket.send_json(health_data)

            elif message == "new_alert":
                alert_data = await get_new_alert()
                await websocket.send_json(alert_data)

            elif message == "get_attack_logs":
                attack_logs = await get_recent_attack_logs()
                await websocket.send_json(attack_logs)

            else:
                await websocket.send_text(f"Unknown command: {message}")

    except WebSocketDisconnect:
        logger.info("Client disconnected")

# Helper functions to interact with the database using SQLAlchemy
async def get_server_health():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    return {"cpu": cpu, "ram": ram}

async def get_new_alert():
    db: Session = SessionLocal()
    alert = db.query(models.Alert).order_by(models.Alert.created_at.desc()).first()
    db.close()
    if alert:
        return {
            "id": alert.id,
            "message": alert.message,
            "severity": alert.severity,
            "status": alert.status,
            "created_at": alert.created_at.isoformat()
        }
    return {"message": "No alerts found"}

async def get_recent_attack_logs():
    db: Session = SessionLocal()
    attack_logs = db.query(models.AttackLog).order_by(models.AttackLog.timestamp.desc()).limit(5).all()
    db.close()
    logs = []
    for log in attack_logs:
        logs.append({
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "type": log.type,
            "source_ip": log.source_ip,
            "target": log.target,
            "severity": log.severity,
            "action": log.action
        })
    return logs

# Route to fetch attack logs via HTTP request
@app.get("/api/get-attack-logs")
async def get_attack_logs(db: Session = Depends(get_db)):
    return await get_recent_attack_logs()

# Route to add a new alert into the database
@app.post("/add_alert/")
async def add_alert(message: str, severity: str, db: Session = Depends(get_db)):
    new_alert = models.Alert(message=message, severity=severity)
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    # Broadcast the new alert to connected WebSocket clients
    await broadcast_new_alert(new_alert)
    
    return {"message": f"Alert '{message}' added with severity '{severity}'!"}

# Function to broadcast the new alert to all WebSocket clients
async def broadcast_new_alert(new_alert: models.Alert):
    # Placeholder: Ideally, you would have an in-memory store like Redis or a WebSocket manager to broadcast
    logger.info(f"Broadcasting new alert: {new_alert.message}")

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
