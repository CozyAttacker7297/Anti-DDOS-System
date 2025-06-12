import itertools
import httpx
from fastapi import Request

# Render server URLs from your friends
backend_servers = [
    "https://friend1-backend.onrender.com",
    "https://friend2-backend.onrender.com"
]

# Round-robin iterator
server_pool = itertools.cycle(backend_servers)

async def forward_request(request: Request, path: str):
    backend_url = next(server_pool)
    full_url = f"{backend_url}/{path}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=full_url,
                headers=request.headers.raw,
                content=await request.body()
            )
            return {
                "from_backend": backend_url,
                "status_code": response.status_code,
                "response": response.json()
            }
        except Exception as e:
            return {"error": "Server unreachable", "details": str(e)}
