import asyncio
import logging
import time
import json
import os
from typing import Dict, List, Optional, Tuple
import httpx
from datetime import datetime
import psutil

logger = logging.getLogger(__name__)

class LoadBalancer:
    def __init__(
        self,
        health_check_interval: int = 30,
        health_check_timeout: int = 5,
        max_failures: int = 3
    ):
        self.health_check_interval = health_check_interval
        self.health_check_timeout = health_check_timeout
        self.max_failures = max_failures
        
        # Server state tracking
        self.servers: Dict[str, Dict] = {}  # server_url -> {status, failures, last_check, stats}
        self.current_index = 0
        self._health_check_task = None
        
        # Load persisted servers if they exist
        self._load_servers()
        
    def _load_servers(self):
        """Load persisted server list from file."""
        try:
            if os.path.exists('servers.json'):
                with open('servers.json', 'r') as f:
                    data = json.load(f)
                    self.servers = {
                        url: {
                            "status": "unknown",  # Reset status on load
                            "failures": 0,
                            "last_check": 0,
                            "added_time": 0,  # Track when server was added
                            "stats": {
                                "cpu_usage": 0,
                                "memory_usage": 0,
                                "response_time": 0,
                                "uptime": 0
                            }
                        }
                        for url in data.get('servers', [])
                    }
                    logger.info(f"Loaded {len(self.servers)} servers from persistence")
        except Exception as e:
            logger.error(f"Error loading persisted servers: {e}")
            
    def _save_servers(self):
        """Save server list to file."""
        try:
            with open('servers.json', 'w') as f:
                json.dump({'servers': list(self.servers.keys())}, f)
            logger.info(f"Saved {len(self.servers)} servers to persistence")
        except Exception as e:
            logger.error(f"Error saving servers to persistence: {e}")

    async def start(self):
        """Start the load balancer and health check loop."""
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Load balancer started")
        
    async def stop(self):
        """Stop the load balancer and health check loop."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("Load balancer stopped")

    def add_server(self, server_url: str) -> bool:
        """Add a new server to the load balancer."""
        if not server_url.startswith(('http://', 'https://')):
            server_url = f"http://{server_url}"
            
        if server_url in self.servers:
            return False
            
        self.servers[server_url] = {
            "status": "unknown",
            "failures": 0,
            "last_check": time.time(),  # Set initial check time to now
            "added_time": time.time(),  # Track when server was added
            "stats": {
                "cpu_usage": 0,
                "memory_usage": 0,
                "response_time": 0,
                "uptime": 0
            }
        }
        logger.info(f"Added server: {server_url}")
        self._save_servers()  # Save after adding
        return True

    def remove_server(self, server_url: str) -> bool:
        """Remove a server from the load balancer."""
        if server_url in self.servers:
            del self.servers[server_url]
            logger.info(f"Removed server: {server_url}")
            self._save_servers()  # Save after removing
            return True
        return False

    async def _health_check_loop(self):
        """Background task to periodically check server health."""
        while True:
            try:
                logger.info(f"Starting health check loop. Current servers: {list(self.servers.keys())}")
                async with httpx.AsyncClient(timeout=self.health_check_timeout) as client:
                    for server_url in list(self.servers.keys()):
                        try:
                            logger.info(f"Checking health of server: {server_url}")
                            start_time = time.time()
                            response = await client.get(f"{server_url}/health")
                            response_time = (time.time() - start_time) * 1000  # Convert to ms
                            
                            if response.status_code == 200:
                                data = response.json()
                                logger.info(f"Server {server_url} is healthy. Response: {data}")
                                self.servers[server_url].update({
                                    "status": "healthy",
                                    "failures": 0,
                                    "last_check": time.time(),
                                    "stats": {
                                        "cpu_usage": data.get("cpu_usage", 0),
                                        "memory_usage": data.get("memory_usage", 0),
                                        "response_time": response_time,
                                        "uptime": data.get("uptime", 0)
                                    }
                                })
                                self._save_servers()  # Save after successful health check
                            else:
                                logger.warning(f"Server {server_url} returned status code {response.status_code}")
                                self._handle_server_failure(server_url)
                        except Exception as e:
                            logger.warning(f"Health check failed for {server_url}: {str(e)}")
                            self._handle_server_failure(server_url)
                
                # Remove servers that haven't been seen
                current_time = time.time()
                for server_url in list(self.servers.keys()):
                    server_data = self.servers[server_url]
                    last_check = server_data["last_check"]
                    added_time = server_data.get("added_time", last_check)  # Fallback to last_check for backward compatibility
                    time_since_last_check = current_time - last_check
                    time_since_added = current_time - added_time
                    
                    # Only remove if server has been added for more than 2 intervals and hasn't been checked
                    if time_since_added > self.health_check_interval * 2 and time_since_last_check > self.health_check_interval * 2:
                        logger.info(f"Removing inactive server: {server_url} (no check for {time_since_last_check}s, added {time_since_added}s ago)")
                        del self.servers[server_url]
                        self._save_servers()  # Save after removing server
                    else:
                        logger.info(f"Server {server_url} last check: {last_check}, time since: {time_since_last_check}s, added {time_since_added}s ago")
                
                logger.info(f"Health check loop completed. Current servers: {self.get_server_stats()}")
            except Exception as e:
                logger.error(f"Error in health check loop: {str(e)}")
            
            await asyncio.sleep(self.health_check_interval)
    
    def _handle_server_failure(self, server_url: str):
        """Handle a server health check failure."""
        self.servers[server_url]["failures"] += 1
        if self.servers[server_url]["failures"] >= self.max_failures:
            self.servers[server_url]["status"] = "unhealthy"
            logger.warning(f"Server {server_url} marked as unhealthy after {self.max_failures} failures")
    
    def get_next_server(self) -> Optional[str]:
        """Get the next healthy server using round-robin selection."""
        healthy_servers = [
            url for url, data in self.servers.items()
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
                url = f"{server}/{path}"
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
                url: {
                    "status": data["status"],
                    "failures": data["failures"],
                    "last_check": data["last_check"],
                    "stats": data["stats"]
                }
                for url, data in self.servers.items()
            }
        }

    def get_health(self) -> Dict:
        """Get load balancer's own health status."""
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "cpu_usage": cpu_usage,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "uptime": time.time() - psutil.boot_time(),
            "server_count": len(self.servers),
            "healthy_server_count": len([s for s in self.servers.values() if s["status"] == "healthy"])
        }
