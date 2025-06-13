from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Optional, List
import httpx
from app.utils.zerotier_load_balancer import ZeroTierLoadBalancer
from app.utils.zerotier_manager import ZeroTierManager, is_admin
from app.config.zerotier_config import NETWORK_MEMBERS, HEALTH_CHECK_INTERVAL, HEALTH_CHECK_TIMEOUT, MAX_FAILURES, BACKEND_PORT, ZEROTIER_NETWORK_ID
import os
from dotenv import load_dotenv
import time
import logging
from sqlalchemy.orm import Session
from app.database import get_db

load_dotenv()

router = APIRouter(prefix="/api/loadbalancer", tags=["Load Balancer"])

# Initialize ZeroTier manager and load balancer
zerotier_manager = ZeroTierManager()  # Will automatically find the authtoken

load_balancer = ZeroTierLoadBalancer(
    zerotier_manager,
    health_check_interval=HEALTH_CHECK_INTERVAL,
    health_check_timeout=HEALTH_CHECK_TIMEOUT,
    max_failures=MAX_FAILURES
)

logger = logging.getLogger(__name__)

@router.on_event("startup")
async def startup_event():
    """Initialize ZeroTier connection on startup."""
    try:
        if not is_admin():
            logger.warning("Running without admin privileges. Some ZeroTier functionality may be limited.")
            logger.warning("For full functionality, please run the application as administrator.")
        
        # Try to join the network
        if not zerotier_manager.join_network():
            logger.warning("Failed to join ZeroTier network - continuing without ZeroTier functionality")
            return
            
        # Start the load balancer
        load_balancer.start()
        
        # Log startup information
        logger.info("Load Balancer started:")
        logger.info(f"Node ID: {zerotier_manager.get_node_id()}")
        logger.info(f"ZeroTier IP: {zerotier_manager.get_zerotier_ip()}")
        logger.info(f"Network ID: {ZEROTIER_NETWORK_ID}")
        logger.info(f"Known members: {len(NETWORK_MEMBERS)}")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        logger.warning("Failed to join ZeroTier network - continuing without ZeroTier functionality")

@router.on_event("shutdown")
async def shutdown_event():
    """Stop the load balancer on application shutdown."""
    await load_balancer.stop()
    zerotier_manager.leave_network()

@router.get("/health")
async def health_check():
    """Health check endpoint for the load balancer."""
    node_id = zerotier_manager.get_node_id()
    my_ip = zerotier_manager.get_zerotier_ip()
    stats = load_balancer.get_server_stats()
    
    return {
        "status": "healthy",
        "node_id": node_id,
        "zerotier_ip": my_ip,
        "network_id": ZEROTIER_NETWORK_ID,
        "stats": stats
    }

@router.get("/stats")
async def get_stats():
    """Get current load balancer statistics."""
    return load_balancer.get_server_stats()

@router.get("/members")
async def get_members():
    """Get all ZeroTier network members with detailed status."""
    members = zerotier_manager.get_network_members()
    return {
        "total_members": len(members),
        "active_members": len([m for m in members if m.get("authorized", False)]),
        "members": [
            {
                "node_id": member["nodeId"],
                "name": member.get("name", "Unknown"),
                "ip": zerotier_manager.get_member_ip(member["nodeId"]),
                "authorized": member.get("authorized", False),
                "last_seen": member.get("lastSeen", 0),
                "physical_ip": member.get("physicalIp", "Unknown"),
                "version": member.get("version", "Unknown"),
                "status": "active" if time.time() - member.get("lastSeen", 0) < 300 else "inactive"
            }
            for member in members
        ]
    }

@router.get("/members/{node_id}")
async def get_member_status(node_id: str):
    """Get detailed status of a specific network member."""
    return zerotier_manager.get_member_status(node_id)

@router.post("/authorize/{node_id}")
async def authorize_member(node_id: str):
    """Authorize a ZeroTier network member."""
    if node_id not in NETWORK_MEMBERS:
        raise HTTPException(status_code=404, detail="Member not found in known network members")
        
    if zerotier_manager.authorize_member(node_id):
        return {
            "status": "success",
            "message": f"Authorized member {node_id}",
            "member": zerotier_manager.get_member_status(node_id)
        }
    raise HTTPException(status_code=400, detail="Failed to authorize member")

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