import os
import json
import subprocess
import logging
import ctypes
import sys
from typing import List, Dict, Optional
import requests
from pathlib import Path
from app.config.zerotier_config import ZEROTIER_NETWORK_ID, NETWORK_MEMBERS

logger = logging.getLogger(__name__)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ZeroTierManager:
    def __init__(self, api_token: str = None):
        self.network_id = ZEROTIER_NETWORK_ID
        self.api_token = api_token or self._get_authtoken()
        self.api_base = "http://localhost:9993"
        self.members: Dict[str, Dict] = {}
        self.known_members = NETWORK_MEMBERS
        self.zerotier_cli_path = self._find_zerotier_cli()
        
        if not self.api_token:
            logger.warning("No ZeroTier API token found. Some functionality may be limited.")
            if not is_admin():
                logger.warning("Running without admin privileges. Try running the application as administrator.")
        
    def _get_authtoken(self) -> str:
        """Get the ZeroTier authtoken from the secret file."""
        # Common locations for authtoken.secret on Windows
        possible_paths = [
            r"C:\ProgramData\ZeroTier\One\authtoken.secret",
            os.path.expandvars(r"%ProgramData%\ZeroTier\One\authtoken.secret"),
            os.path.expandvars(r"%LocalAppData%\ZeroTier\One\authtoken.secret"),
            os.path.expandvars(r"%AppData%\ZeroTier\One\authtoken.secret")
        ]
        
        # First try to get token from environment variable
        token = os.getenv("ZEROTIER_API_TOKEN")
        if token:
            logger.info("Found ZeroTier API token in environment variable")
            return token
            
        # Then try to read from file
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    # Try to read with elevated permissions if needed
                    if not is_admin():
                        logger.warning(f"Attempting to read {path} without admin privileges")
                    
                    with open(path, 'r') as f:
                        token = f.read().strip()
                        if token:
                            logger.info(f"Found ZeroTier authtoken at {path}")
                            return token
                        else:
                            logger.warning(f"Found empty authtoken file at {path}")
            except PermissionError:
                logger.warning(f"Permission denied reading {path}. Try running as administrator.")
            except Exception as e:
                logger.debug(f"Error reading authtoken from {path}: {e}")
                continue
                
        # If we still don't have a token, try to get it from zerotier-cli
        try:
            result = subprocess.run(
                [self.zerotier_cli_path, "info"],
                capture_output=True,
                text=True,
                check=False,
                shell=True
            )
            if result.returncode == 0 and "authtoken=" in result.stdout:
                token = result.stdout.split("authtoken=")[1].split()[0]
                logger.info("Found ZeroTier authtoken from zerotier-cli")
                return token
        except Exception as e:
            logger.debug(f"Error getting authtoken from zerotier-cli: {e}")
                
        logger.warning("Could not find ZeroTier authtoken file")
        return ""

    def _find_zerotier_cli(self) -> str:
        """Find the zerotier-cli executable path."""
        # Common locations for zerotier-cli on Windows
        possible_paths = [
            "zerotier-cli",  # If it's in PATH
            r"C:\Program Files\ZeroTier\One\zerotier-cli.exe",
            r"C:\Program Files (x86)\ZeroTier\One\zerotier-cli.exe",
            os.path.expandvars(r"%ProgramFiles%\ZeroTier\One\zerotier-cli.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\ZeroTier\One\zerotier-cli.exe"),
            os.path.expandvars(r"%LocalAppData%\Programs\ZeroTier\One\zerotier-cli.exe"),
            "/usr/bin/zerotier-cli",
            "/usr/local/bin/zerotier-cli"
        ]
        
        # Log the current PATH for debugging
        logger.info(f"Current PATH: {os.environ.get('PATH', '')}")
        
        for path in possible_paths:
            try:
                logger.info(f"Trying to find zerotier-cli at: {path}")
                result = subprocess.run(
                    [path, "info"],
                    capture_output=True,
                    text=True,
                    check=False,
                    shell=True  # Use shell=True for Windows
                )
                if result.returncode == 0:
                    logger.info(f"Found zerotier-cli at: {path}")
                    return path
                else:
                    logger.debug(f"zerotier-cli not found at {path}: {result.stderr}")
            except Exception as e:
                logger.debug(f"Error checking {path}: {e}")
                continue
                
        # Try using 'where' command on Windows to find zerotier-cli
        try:
            result = subprocess.run(
                ["where", "zerotier-cli"],
                capture_output=True,
                text=True,
                check=False,
                shell=True
            )
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                logger.info(f"Found zerotier-cli using 'where' command: {path}")
                return path
        except Exception as e:
            logger.debug(f"Error using 'where' command: {e}")
                
        logger.warning("zerotier-cli not found in common locations. Will try using 'zerotier-cli' from PATH")
        return "zerotier-cli"
        
    def _run_zerotier_cli(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a zerotier-cli command with proper error handling."""
        try:
            # Ensure we're using the full path and shell=True for Windows
            cmd = [self.zerotier_cli_path] + command
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            # Try running with elevated privileges if needed
            if not is_admin():
                logger.warning("Running zerotier-cli without admin privileges")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                shell=True
            )
            
            if result.returncode != 0:
                logger.error(f"ZeroTier CLI error: {result.stderr}")
                if "authtoken.secret not found or readable" in result.stderr:
                    logger.error("Permission denied accessing authtoken.secret. Try running as administrator.")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running zerotier-cli: {e}")
            if check:
                raise
            return subprocess.CompletedProcess(cmd, 1, "", str(e))

    def join_network(self) -> bool:
        """Join the ZeroTier network."""
        try:
            # Check if already joined
            result = self._run_zerotier_cli(["listnetworks"])
            if result.returncode == 0 and self.network_id in result.stdout:
                logger.info(f"Already joined network {self.network_id}")
                return True
                
            result = self._run_zerotier_cli(["join", self.network_id])
            if result.returncode == 0:
                logger.info(f"Successfully joined network {self.network_id}")
                return True
            else:
                logger.error(f"Failed to join network: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to join network: {e}")
            return False

    def leave_network(self) -> bool:
        """Leave the ZeroTier network."""
        try:
            result = self._run_zerotier_cli(["leave", self.network_id])
            if result.returncode == 0:
                logger.info(f"Successfully left network {self.network_id}")
                return True
            else:
                logger.error(f"Failed to leave network: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to leave network: {e}")
            return False

    def get_network_members(self) -> List[Dict]:
        """Get all members in the network."""
        try:
            response = requests.get(
                f"{self.api_base}/network/{self.network_id}/member",
                headers={"X-ZT1-Auth": self.api_token}
            )
            response.raise_for_status()
            members = response.json()
            
            # Enrich member data with known information
            for member in members:
                node_id = member["nodeId"]
                if node_id in self.known_members:
                    member.update(self.known_members[node_id])
            
            self.members = {m["nodeId"]: m for m in members}
            return members
        except Exception as e:
            logger.error(f"Failed to get network members: {e}")
            return []

    def get_member_ip(self, node_id: str) -> Optional[str]:
        """Get the IP address of a network member."""
        if node_id in self.known_members:
            return self.known_members[node_id]["ip"]
        if node_id in self.members:
            member = self.members[node_id]
            if "ipAssignments" in member and member["ipAssignments"]:
                return member["ipAssignments"][0]
        return None

    def authorize_member(self, node_id: str) -> bool:
        """Authorize a member in the network."""
        try:
            response = requests.post(
                f"{self.api_base}/network/{self.network_id}/member/{node_id}",
                headers={"X-ZT1-Auth": self.api_token},
                json={"authorized": True}
            )
            response.raise_for_status()
            logger.info(f"Authorized member {node_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to authorize member {node_id}: {e}")
            return False

    def get_my_node_id(self) -> Optional[str]:
        """Get the local node's ZeroTier ID."""
        try:
            return self._run_zerotier_cli(["info"]).stdout.split()[2]
        except Exception as e:
            logger.error(f"Failed to get node ID: {e}")
            return None

    def get_my_ip(self) -> Optional[str]:
        """Get the local node's IP in the ZeroTier network."""
        node_id = self.get_my_node_id()
        if node_id:
            return self.get_member_ip(node_id)
        return None
        
    def get_member_status(self, node_id: str) -> Dict:
        """Get detailed status of a network member."""
        if node_id in self.members:
            member = self.members[node_id]
            return {
                "node_id": node_id,
                "name": member.get("name", "Unknown"),
                "ip": self.get_member_ip(node_id),
                "authorized": member.get("authorized", False),
                "last_seen": member.get("lastSeen", 0),
                "physical_ip": member.get("physicalIp", "Unknown"),
                "version": member.get("version", "Unknown")
            }
        return {
            "node_id": node_id,
            "status": "unknown",
            "error": "Member not found"
        } 