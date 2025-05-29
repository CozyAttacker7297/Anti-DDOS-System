# load_balancer.py
from flask import Flask, request
import requests

app = Flask(__name__)

# Start with your own server
backend_servers = [
    "http://192.168.193.224:5000"  # Only Shivam for now
]


current = 0

@app.route('/')
def load_balance():
    global current
    backend = backend_servers[current]
    current = (current + 1) % len(backend_servers)
    
    try:
        response = requests.get(backend)
        return response.text
    except Exception as e:
        return f"Error contacting backend: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
