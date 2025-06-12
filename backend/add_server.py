import requests
import json

def add_server(url):
    """Add a server to the load balancer."""
    response = requests.post(
        "http://localhost:5000/api/loadbalancer/servers",
        json={"url": url},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    add_server("http://127.0.0.1:8000") 