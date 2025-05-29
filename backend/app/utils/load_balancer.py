import threading

servers = []
current = 0
lock = threading.Lock()  # To handle concurrency in multi-threaded environment

def register_server(ip: str) -> None:
    """Register a new server IP if not already present."""
    with lock:
        if ip not in servers:
            servers.append(ip)

def get_next_server() -> str | None:
    """Get the next server IP in round-robin fashion."""
    global current
    with lock:
        if not servers:
            return None
        server = servers[current]
        current = (current + 1) % len(servers)
        return server
