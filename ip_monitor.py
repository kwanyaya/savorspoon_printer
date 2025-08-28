#!/usr/bin/env python3
"""
HK Savor Spoon - IP Monitor & DDNS Update Script
Monitors IP changes and updates your print server configuration
"""

import requests
import time
import json
import logging
from datetime import datetime

# Configuration
CHECK_INTERVAL = 300  # Check every 5 minutes
LOG_FILE = "ip_monitor.log"
CONFIG_FILE = "current_ip.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_external_ip():
    """Get current external IP address"""
    services = [
        "http://ifconfig.me/ip",
        "http://ipinfo.io/ip", 
        "http://api.ipify.org",
        "http://checkip.amazonaws.com"
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=10)
            if response.status_code == 200:
                ip = response.text.strip()
                logger.info(f"Got IP {ip} from {service}")
                return ip
        except Exception as e:
            logger.warning(f"Failed to get IP from {service}: {e}")
            continue
    
    return None

def load_config():
    """Load current IP configuration"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_ip": None, "last_update": None}

def save_config(ip):
    """Save current IP configuration"""
    config = {
        "last_ip": ip,
        "last_update": datetime.now().isoformat(),
        "print_server_url": f"http://{ip}:8080"
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def notify_ip_change(old_ip, new_ip):
    """Notify about IP change"""
    print("\n" + "="*50)
    print("🚨 IP ADDRESS CHANGED!")
    print("="*50)
    print(f"Old IP: {old_ip}")
    print(f"New IP: {new_ip}")
    print(f"New Print Server URL: http://{new_ip}:8080")
    print("\n⚠️  IMPORTANT: Update your website configuration!")
    print("Change WINDOWS_PRINT_SERVER_URL to:")
    print(f"http://{new_ip}:8080")
    print("="*50)
    
    # Log to file
    logger.warning(f"IP changed from {old_ip} to {new_ip}")

def main():
    """Main monitoring loop"""
    logger.info("Starting IP Monitor for HK Savor Spoon Print Server")
    
    config = load_config()
    last_ip = config.get("last_ip")
    
    print("🔍 HK Savor Spoon IP Monitor Started")
    print(f"📊 Checking every {CHECK_INTERVAL//60} minutes")
    print(f"📝 Logs saved to: {LOG_FILE}")
    
    if last_ip:
        print(f"🌐 Last known IP: {last_ip}")
        print(f"🔗 Current URL: http://{last_ip}:8080")
    
    try:
        while True:
            current_ip = get_external_ip()
            
            if current_ip:
                if current_ip != last_ip:
                    notify_ip_change(last_ip, current_ip)
                    save_config(current_ip)
                    last_ip = current_ip
                else:
                    logger.info(f"IP unchanged: {current_ip}")
            else:
                logger.error("Failed to get external IP from all services")
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("IP Monitor stopped by user")
        print("\n👋 IP Monitor stopped")

if __name__ == "__main__":
    main()
