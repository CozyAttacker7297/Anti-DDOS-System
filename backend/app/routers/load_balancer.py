from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import httpx
from ..utils.load_balancer import LoadBalancer
import logging
from pydantic import BaseModel, HttpUrl

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/loadbalancer", tags=["Load Balancer"])

# Initialize load balancer
load_balancer = LoadBalancer(
    health_check_interval=30,  # seconds
    health_check_timeout=5,    # seconds
    max_failures=3            # number of failures before marking server as unhealthy
)

# Pydantic models for request validation
class ServerAdd(BaseModel):
    url: HttpUrl

class ServerRemove(BaseModel):
    url: HttpUrl

@router.on_event("startup")
async def startup_event():
    """Start the load balancer on application startup."""
    await load_balancer.start()
    logger.info("Load balancer started")

@router.on_event("shutdown")
async def shutdown_event():
    """Stop the load balancer on application shutdown."""
    await load_balancer.stop()
    logger.info("Load balancer stopped")

@router.get("/health")
async def health_check():
    """Get load balancer's health status."""
    return load_balancer.get_health()

@router.get("/stats")
async def get_stats():
    """Get current load balancer statistics."""
    return load_balancer.get_server_stats()

@router.post("/servers")
async def add_server(server: ServerAdd):
    """Add a new server to the load balancer."""
    if load_balancer.add_server(str(server.url)):
        return {"message": f"Server {server.url} added successfully"}
    raise HTTPException(status_code=400, detail="Server already exists")

@router.delete("/servers")
async def remove_server(server: ServerRemove):
    """Remove a server from the load balancer."""
    if load_balancer.remove_server(str(server.url)):
        return {"message": f"Server {server.url} removed successfully"}
    raise HTTPException(status_code=404, detail="Server not found")

@router.get("/servers")
async def list_servers():
    """List all servers in the load balancer."""
    return {
        "servers": [
            {
                "url": url,
                "status": data["status"],
                "failures": data["failures"],
                "last_check": data["last_check"],
                "stats": data["stats"]
            }
            for url, data in load_balancer.servers.items()
        ]
    }

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def forward_request(request: Request, path: str):
    """Forward requests to backend servers."""
    # Create a new request object
    body = await request.body()
    headers = dict(request.headers)
    
    # Forward the request
    response, error = await load_balancer.forward_request(
        httpx.Request(
            method=request.method,
            url=f"http://dummy/{path}",  # URL will be replaced in forward_request
            headers=headers,
            content=body
        ),
        path
    )
    
    if error:
        raise HTTPException(status_code=503, detail=error)
    
    if not response:
        raise HTTPException(status_code=503, detail="No healthy servers available")
    
    # Return the response from the backend server
    return JSONResponse(
        content=response.json(),
        status_code=response.status_code,
        headers=dict(response.headers)
    ) 