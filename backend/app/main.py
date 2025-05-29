from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .routers import dashboard_router, iptable_router, server_router, loadbalancer_router
import psutil
import os
from dotenv import load_dotenv
import time
from typing import Callable
import logging
import httpx  # async HTTP client
import itertools

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

app = FastAPI(
    title="Anti-DDOS System API",
    description="Backend API for the Anti-DDOS System Dashboard",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Get allowed origins from environment variable, fallback to development default
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

# Get trusted hosts from environment variable
TRUSTED_HOSTS = os.getenv(
    "TRUSTED_HOSTS",
    "localhost,127.0.0.1"
).split(",")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "X-Content-Range"],
    max_age=3600,
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=TRUSTED_HOSTS
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next: Callable):
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next: Callable):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Include routers
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
app.include_router(iptable_router, prefix="/api", tags=["iptable"])
app.include_router(server_router, prefix="/api", tags=["servers"])
app.include_router(loadbalancer_router, prefix="/api", tags=["loadbalancer"])

@app.get("/api/test-connection")
async def test_connection():
    return {
        "status": "success",
        "message": "Backend is connected!",
        "timestamp": time.time()
    }

@app.get("/api/server-health")
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def server_health(request: Request) -> dict:
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        return {
            "name": "Web Server 1",
            "status": 100 - ram,
            "cpu": cpu,
            "ram": ram
        }
    except Exception as e:
        logger.error(f"Error getting server health: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error retrieving server health metrics"
        )

# List your backend Flask servers here
backend_servers = [
    "http://192.168.1.62:5000",
    "http://192.168.1.23:5001",
    "http://192.168.1.105:5000"
]

@app.get("/api/all-server-health")
@limiter.limit("5/minute")
async def all_server_health(request: Request):
    results = []
    async with httpx.AsyncClient(timeout=2) as client:
        for server_url in backend_servers:
            try:
                resp = await client.get(f"{server_url}/server-health")
                resp.raise_for_status()
                results.append(resp.json())
            except Exception as e:
                logger.warning(f"Could not fetch health from {server_url}: {e}")
                results.append({
                    "name": server_url,
                    "status": 0,
                    "cpu": 0,
                    "ram": 0
                })

    # Add load balancer health info at the end
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    load_balancer_health = {
        "name": "Load Balancer",
        "status": 100 - max(cpu, ram),
        "cpu": cpu,
        "ram": ram
    }
    results.append(load_balancer_health)

    return results

# Round-robin cycle for backend servers
server_cycle = itertools.cycle(backend_servers)

# Proxy fallback route for load balancing
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_request(full_path: str, request: Request):
    backend_url = next(server_cycle)
    url = f"{backend_url}/{full_path}"

    headers = dict(request.headers)
    body = await request.body()
    method = request.method

    async with httpx.AsyncClient() as client:
        try:
            backend_response = await client.request(
                method, url, headers=headers, content=body, timeout=10
            )
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to backend server {backend_url}: {e}")
            return JSONResponse(
                status_code=502,
                content={"error": f"Failed to connect to backend server {backend_url}: {str(e)}"},
            )

    return Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=dict(backend_response.headers),
        media_type=backend_response.headers.get("content-type"),
    )
