from fastapi import Request

@app.get("/api/all-server-health")
@limiter.limit("5/minute")
async def all_server_health(request: Request):  # <-- Add 'request: Request' here
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
