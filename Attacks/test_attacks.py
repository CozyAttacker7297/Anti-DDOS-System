import requests
import threading
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys

# Configuration
TARGET_URL = "http://localhost:5000"
THREADS = 20  # More threads for dramatic increases
REQUEST_DELAY = 0.001  # Much faster base requests
BATCH_SIZE = 200  # Larger batch size for dramatic increases
REQUEST_TIMEOUT = 5
TOTAL_REQUESTS = 10000

# Attack types and their weights - More aggressive distribution
ATTACK_TYPES = {
    "flood": 0.7,      # 70% flood attacks for dramatic increases
    "injection": 0.15, # 15% injection attacks
    "scan": 0.1,       # 10% scan attacks
    "brute_force": 0.05  # 5% brute force attacks
}

# Endpoints to target with weights - More focus on predict-attack
ATTACK_ENDPOINTS = [
    ("/api/predict-attack", 0.9),   # 90% of requests
    ("/api/server-health", 0.05),   # 5% of requests
    ("/api/test-connection", 0.05)   # 5% of requests
]

# Attack intensity levels with more dramatic ranges
INTENSITY_LEVELS = {
    "low": {"rate": (10000, 50000), "payload": (100000, 500000)},
    "medium": {"rate": (50000, 150000), "payload": (500000, 2000000)},
    "high": {"rate": (150000, 300000), "payload": (2000000, 5000000)},
    "extreme": {"rate": (300000, 500000), "payload": (5000000, 10000000)}
}

# Burst attack patterns with more dramatic sizes
BURST_PATTERNS = {
    "sudden_spike": {"probability": 0.4, "size": (500, 1000)},
    "gradual_increase": {"probability": 0.2, "size": (300, 800)},
    "wave": {"probability": 0.3, "size": (400, 900)},
    "constant_high": {"probability": 0.1, "size": (800, 1500)}
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

def get_random_headers(source_ip, attack_type, intensity="medium"):
    """Generate random headers based on attack type and intensity."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.277",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Vivaldi/4.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Brave/1.24.85"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "X-Forwarded-For": source_ip,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "X-Request-ID": f"{random.randint(1000000, 9999999)}-{random.randint(1000, 9999)}",
        "X-Attack-Intensity": intensity,
        "X-Timestamp": str(int(time.time() * 1000))
    }
    
    # Add attack-specific headers with varying intensity
    if attack_type == "injection":
        headers.update({
            "X-SQL-Injection": "1' OR '1'='1",
            "X-XSS-Attack": "<script>alert('xss')</script>",
            "X-Command-Injection": "& cat /etc/passwd",
            "X-Path-Injection": "' or '1'='1",
            "X-NoSQL-Injection": '{"$gt": ""}',
            "X-Template-Injection": "${7*7}",
            "X-LDAP-Injection": "*)(uid=*))(|(uid=*"
        })
    elif attack_type == "scan":
        headers.update({
            "X-Scan": "true",
            "X-Port-Scan": "true",
            "X-Vulnerability-Scan": "true",
            "X-Directory-Scan": "true",
            "X-Security-Scan": "true",
            "X-Network-Scan": "true",
            "X-Web-Scan": "true"
        })
    elif attack_type == "brute_force":
        headers.update({
            "X-Brute-Force": "true",
            "X-Auth-Attempt": "true",
            "X-Credential-Spray": "true",
            "X-Password-Guess": "true",
            "X-Login-Attempt": "true",
            "X-Account-Enumeration": "true"
        })
    elif attack_type == "flood":
        rate_range = INTENSITY_LEVELS[intensity]["rate"]
        headers.update({
            "X-Flood-Attack": "true",
            "X-Request-Rate": str(random.randint(*rate_range)),
            "X-Burst-Size": str(random.randint(100, 1000)),
            "X-Flood-Type": random.choice(["burst", "sustained", "pulse"]),
            "X-Attack-Pattern": random.choice(["random", "sequential", "burst"]),
            "X-Connection-Type": random.choice(["keep-alive", "close"]),
            "X-Request-Method": random.choice(["GET", "POST", "PUT", "DELETE"])
        })
    
    return headers

def send_clean_traffic(session):
    for endpoint in NORMAL_ENDPOINTS:
        headers = get_random_headers("127.0.0.1", "clean")
        send_request(session, "GET", f"{TARGET_URL}{endpoint}", headers)

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
    # Determine burst pattern
    burst_pattern = random.choices(
        list(BURST_PATTERNS.keys()),
        weights=[p["probability"] for p in BURST_PATTERNS.values()]
    )[0]
    
    # Calculate burst size based on pattern
    burst_size = random.randint(*BURST_PATTERNS[burst_pattern]["size"])
    
    for _ in range(burst_size):
        attack_type = random.choices(list(ATTACK_TYPES.keys()), weights=list(ATTACK_TYPES.values()))[0]
        fake_ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
        
        # Randomly select attack intensity with bias towards higher intensities
        intensity = random.choices(
            ["low", "medium", "high", "extreme"],
            weights=[0.1, 0.2, 0.4, 0.3]  # More weight on high and extreme
        )[0]
        
        headers = get_random_headers(fake_ip, attack_type, intensity)
        
        # Select endpoint based on weights
        endpoint = random.choices([e[0] for e in ATTACK_ENDPOINTS], weights=[e[1] for e in ATTACK_ENDPOINTS])[0]
        
        # Use GET for server-health and test-connection, POST for predict-attack
        if endpoint in ["/api/server-health", "/api/test-connection"]:
            method = "GET"
            data = None
        else:
            method = "POST"
            # Get rate and payload ranges based on intensity
            rate_range = INTENSITY_LEVELS[intensity]["rate"]
            payload_range = INTENSITY_LEVELS[intensity]["payload"]
            
            # Prepare data for predict-attack with intensity-based values
            data = {
                "source_ip": fake_ip,
                "target": endpoint,
                "request_rate": random.randint(*rate_range),
                "payload_size": random.randint(*payload_range),
                "request_type": method,
                "user_agent": headers["User-Agent"],
                "attack_intensity": intensity,
                "timestamp": int(time.time() * 1000),
                "burst_pattern": burst_pattern
            }
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
        
        try:
            if method == "POST":
                response = session.post(
                    f"{TARGET_URL}{endpoint}",
                    headers=headers,
                    json=data,
                    timeout=REQUEST_TIMEOUT
                )
            else:
                response = session.get(
                    f"{TARGET_URL}{endpoint}",
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
            
            if response.status_code == 200:
                print(f"✅ {method} Request: {TARGET_URL}{endpoint} - Status: {response.status_code} - Intensity: {intensity} - Pattern: {burst_pattern}")
            else:
                print(f"❌ {method} Request failed: {TARGET_URL}{endpoint} - Status: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            if data:
                print(f"Request data: {data}")
        
        # Add very small random delay between requests
        time.sleep(random.uniform(0.0001, 0.001))

def attack_worker():
    """Worker function for each thread."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    })
    
    # Add retry mechanism
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    while True:
        try:
            send_malicious_traffic(session)
            # Random delay between attack batches
            time.sleep(random.uniform(0.0001, 0.001))
        except Exception as e:
            print(f"Worker error: {str(e)}")
            time.sleep(1)  # Wait a bit before retrying

def main():
    print(f"🚀 Starting ULTRA-REALISTIC attack simulation with {TOTAL_REQUESTS} total requests")
    print(f"📊 Attack distribution: {ATTACK_TYPES}")
    print(f"👥 Using {THREADS} concurrent threads")
    print(f"🎯 Target: {TARGET_URL}")
    print(f"⚡ Base request delay: {REQUEST_DELAY} seconds")
    print(f"🌊 Batch size: {BATCH_SIZE}")
    print(f"💥 Attack intensity levels: {list(INTENSITY_LEVELS.keys())}")
    print(f"🌪️ Burst patterns: {list(BURST_PATTERNS.keys())}")
    print(f"🛡️ Evasion techniques: Enabled")
    print(f"⏱️ Timeout handling: Optimized")
    print(f"💾 Resource usage: Optimized")
    
    # Start attack threads
    threads = []
    for _ in range(THREADS):
        thread = threading.Thread(target=attack_worker)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Attack simulation stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
