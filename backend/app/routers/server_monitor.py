from fastapi import APIRouter
import psutil
import requests

router = APIRouter()

# Replace these with your backend IPs or render URLs
backend_servers = [
    "http://192.168.56.1:8000",
    "http://192.168.1.101:8000",
    "http://192.168.1.102:8000",
]

@router.get("/server-health")
def server_health():
    """Health of Load Balancer itself."""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    status = 100 - max(cpu, ram)
    return {
        "name": "Load Balancer",
        "status": status,
        "cpu": cpu,
        "ram": ram
    }

@router.get("/all-server-health")
def all_server_health():
    """Fetch health of all backend servers + load balancer itself."""
    data = []
    for server in backend_servers:
        try:
            res = requests.get(f"{server}/api/server-health", timeout=2)
            res.raise_for_status()
            data.append(res.json())
        except Exception as e:
            print(f"Error fetching {server}: {e}")
            data.append({
                "name": server,
                "status": 0,
                "cpu": 0,
                "ram": 0
            })

    # Add load balancer health
    lb_cpu = psutil.cpu_percent(interval=None)
    lb_ram = psutil.virtual_memory().percent
    lb_status = 100 - max(lb_cpu, lb_ram)
    data.append({
        "name": "Load Balancer",
        "status": lb_status,
        "cpu": lb_cpu,
        "ram": lb_ram
    })
    return data
