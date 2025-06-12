from fastapi import FastAPI
import uvicorn
import random
import time

app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint that returns server info."""
    return {
        "message": "Hello from test server!",
        "server_id": random.randint(1000, 9999),
        "timestamp": time.time()
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint that simulates some work."""
    # Simulate some processing time
    time.sleep(random.uniform(0.1, 0.5))
    return {
        "message": "Test endpoint response",
        "server_id": random.randint(1000, 9999),
        "timestamp": time.time()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 