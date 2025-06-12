import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple
import httpx
from app.utils.zerotier_manager import ZeroTierManager

logger = logging.getLogger(__name__)

class ZeroTierLoadBalancer:
    def __init__(
        self,
        zerotier_manager: ZeroTierManager,
        health_check_interval: int = 30,
        health_check_timeout: int = 5,
        max_failures: int = 3
    ):
        self.zerotier_manager = zerotier_manager
        self.health_check_interval = health_check_interval
        self.health_check_timeout = health_check_timeout
        self.max_failures = max_failures
        
        # Server state tracking
        self.servers: Dict[str, Dict] = {}  # IP -> {status, failures, last_check}
        self.current_index = 0
        self._health_check_task = None
        
    async def start(self):
        """Start the load balancer and health check loop."""
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("ZeroTier load balancer started")
        
    async def stop(self):
        """Stop the load balancer and health check loop."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("ZeroTier load balancer stopped")
        
    async def _health_check_loop(self):
        """Background task to periodically check server health."""
        while True:
            try:
                # Get current network members
                members = self.zerotier_manager.get_network_members()
                
                # Update server list
                for member in members:
                    ip = self.zerotier_manager.get_member_ip(member["nodeId"])
                    if ip and member["authorized"]:
                        if ip not in self.servers:
                            self.servers[ip] = {
                                "status": "unknown",
                                "failures": 0,
                                "last_check": 0
                            }
                
                # Check health of each server
                async with httpx.AsyncClient(timeout=self.health_check_timeout) as client:
                    for ip in list(self.servers.keys()):
                        try:
                            response = await client.get(f"http://{ip}:5000/health")
                            if response.status_code == 200:
                                self.servers[ip]["status"] = "healthy"
                                self.servers[ip]["failures"] = 0
                            else:
                                self._handle_server_failure(ip)
                        except Exception as e:
                            logger.warning(f"Health check failed for {ip}: {e}")
                            self._handle_server_failure(ip)
                        self.servers[ip]["last_check"] = time.time()
                
                # Remove servers that haven't been seen
                current_time = time.time()
                for ip in list(self.servers.keys()):
                    if current_time - self.servers[ip]["last_check"] > self.health_check_interval * 2:
                        del self.servers[ip]
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
            
            await asyncio.sleep(self.health_check_interval)
    
    def _handle_server_failure(self, ip: str):
        """Handle a server health check failure."""
        self.servers[ip]["failures"] += 1
        if self.servers[ip]["failures"] >= self.max_failures:
            self.servers[ip]["status"] = "unhealthy"
            logger.warning(f"Server {ip} marked as unhealthy after {self.max_failures} failures")
    
    def get_next_server(self) -> Optional[str]:
        """Get the next healthy server using round-robin selection."""
        healthy_servers = [
            ip for ip, data in self.servers.items()
            if data["status"] == "healthy"
        ]
        
        if not healthy_servers:
            return None
            
        server = healthy_servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(healthy_servers)
        return server
    
    async def forward_request(self, request: httpx.Request, path: str) -> Tuple[Optional[httpx.Response], Optional[str]]:
        """Forward a request to the next available server."""
        server = self.get_next_server()
        if not server:
            return None, "No healthy servers available"
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"http://{server}:5000/{path}"
                response = await client.request(
                    method=request.method,
                    url=url,
                    headers=dict(request.headers),
                    content=await request.body()
                )
                return response, None
        except Exception as e:
            logger.error(f"Error forwarding request to {server}: {e}")
            self._handle_server_failure(server)
            return None, str(e)
    
    def get_server_stats(self) -> Dict:
        """Get current server statistics."""
        return {
            "total_servers": len(self.servers),
            "healthy_servers": len([s for s in self.servers.values() if s["status"] == "healthy"]),
            "unhealthy_servers": len([s for s in self.servers.values() if s["status"] == "unhealthy"]),
            "servers": {
                ip: {
                    "status": data["status"],
                    "failures": data["failures"],
                    "last_check": data["last_check"]
                }
                for ip, data in self.servers.items()
            }
        } 