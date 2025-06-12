import os
import psutil
import requests
import itertools
import httpx
from fastapi import FastAPI, APIRouter, Request, HTTPException
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

# Define a router for load balancer endpoints
router = APIRouter()

# Define backend servers list – using localhost and a Render server
backend_servers = os.getenv("BACKEND_SERVERS", "http://localhost:5000").split(",")

# Define a round-robin iterator
server_pool = itertools.cycle(backend_servers)

# Define a helper function to get local health (CPU/RAM) for the load balancer
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

# Define endpoint /server-health (GET) to return local health
@router.get("/server-health", tags=["Health"])
def server_health():
    return get_local_health()

# Define endpoint /all-server-health (GET) to poll health from backend servers and return a JSON list
@router.get("/all-server-health", tags=["Health"])
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

# Define a helper function to forward a request
async def forward_request(request: Request, path: str):
    backend_url = next(server_pool)
    full_url = f"{backend_url}/{path}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method=request.method, url=full_url, headers=request.headers.raw, content=await request.body())
            return {"from_backend": backend_url, "status_code": response.status_code, "response": response.json()}
        except Exception as e:
            return {"error": "Server unreachable", "details": str(e)}

# Define endpoint /forward (POST) to forward a request
@router.post("/forward")
async def forward(request: Request, path: str = "data"):
    return await forward_request(request, path)
