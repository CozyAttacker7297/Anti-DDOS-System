import psutil
import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Anti-DDoS Load Balancer",
    version="1.0.0",
    description="Load balancer for routing and monitoring backend servers"
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace * with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend_servers = [
    "http://192.168.1.62:5000",
    "http://192.168.1.23:5001",
    "http://192.168.1.105:5000"
]

def get_local_health(name: str = "Load Balancer"):
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    status = 100 - max(cpu, ram)
    return {
        "name": name,
        "status": status,
        "cpu": cpu,
        "ram": ram
    }

@app.get("/api/all-server-health", tags=["Health"])
def all_server_health():
    results = []

    for server in backend_servers:
        try:
            print(f"Fetching health from {server}")
            response = requests.get(f"{server}/server-health", timeout=2)
            response.raise_for_status()
            data = response.json()
            print(f"Received data: {data}")
            results.append(data)
        except Exception as e:
            print(f"[WARN] Could not fetch {server}: {e}")
            results.append({
                "name": server.split("//")[-1],
                "status": 0,
                "cpu": 0,
                "ram": 0
            })

    lb_health = get_local_health()
    print(f"Load Balancer health: {lb_health}")
    results.append(lb_health)

    print(f"Final results: {results}")
    return JSONResponse(content=results)
