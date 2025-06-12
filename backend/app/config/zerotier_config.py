"""
ZeroTier Network Configuration
"""

# Network Configuration
ZEROTIER_NETWORK_ID = "fada62b0151d1338"

# Known members in the network
NETWORK_MEMBERS = {
    "2ad627e8b0": {
        "name": "Server 1",
        "ip": "192.168.193.171",
        "physical_ip": "152.58.32.116"
    },
    "45e975c763": {
        "name": "Server 2",
        "ip": "192.168.193.198",
        "physical_ip": "103.97.104.197"
    },
    "abc7b56b84": {
        "name": "Server 3",
        "ip": "192.168.193.119",
        "physical_ip": "103.53.234.44"
    },
    "d59c362dcb": {
        "name": "Server 4",
        "ip": "192.168.193.230",
        "physical_ip": "223.233.86.193"
    },
    "f840236d82": {
        "name": "Server 5",
        "ip": "192.168.193.224",
        "physical_ip": "58.84.60.11"
    }
}

# Load Balancer Configuration
HEALTH_CHECK_INTERVAL = 30  # seconds
HEALTH_CHECK_TIMEOUT = 5    # seconds
MAX_FAILURES = 3            # number of failures before marking server as unhealthy
BACKEND_PORT = 5000         # port where backend servers are running 