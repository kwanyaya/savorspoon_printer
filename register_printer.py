#!/usr/bin/env python3
"""
Local Printer Registration Client
Runs at restaurant to register Star TSP143III with cloud server
"""

import requests
import time
import socket
import json
import sys
from datetime import datetime

# Configuration
CONFIG = {
    'CLOUD_SERVER_URL': 'http://YOUR_CLOUD_SERVER_IP:8080',  # Update with your cloud server
    'API_KEY': 'hksavorspoon-secure-print-key-2025',
    'RESTAURANT_ID': 'hk-savor-spoon-main',  # Unique ID for your restaurant
    'PRINTER_IP': '192.168.1.100',  # Your Star TSP143III IP
    'PRINTER_PORT': 9100,
    'LOCATION_NAME': 'Main Restaurant',
    'REGISTRATION_INTERVAL': 300  # Re-register every 5 minutes
}

def discover_local_printer():
    """Auto-discover Star TSP143III on local network"""
    print("🔍 Scanning for local Star TSP143III...")
    
    # Get local network range
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        ip_parts = local_ip.split('.')
        network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
        print(f"📡 Scanning network: {network_base}.x")
    except:
        network_base = "192.168.1"
    
    # Common printer IPs
    test_ips = [
        f"{network_base}.100", f"{network_base}.101", 
        f"{network_base}.200", f"{network_base}.201",
        f"{network_base}.110", f"{network_base}.111"
    ]
    
    for ip in test_ips:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, 9100))
            sock.close()
            
            if result == 0:
                print(f"✅ Found Star TSP143III at {ip}")
                CONFIG['PRINTER_IP'] = ip
                return ip
        except:
            continue
    
    print("❌ No Star TSP143III found on network")
    return None

def test_printer_connection():
    """Test if local printer is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((CONFIG['PRINTER_IP'], CONFIG['PRINTER_PORT']))
        sock.close()
        return result == 0
    except:
        return False

def register_with_cloud():
    """Register this printer with the cloud server"""
    try:
        print(f"📡 Registering with cloud server: {CONFIG['CLOUD_SERVER_URL']}")
        
        registration_data = {
            'restaurant_id': CONFIG['RESTAURANT_ID'],
            'printer_ip': CONFIG['PRINTER_IP'],
            'printer_port': CONFIG['PRINTER_PORT'],
            'location': CONFIG['LOCATION_NAME'],
            'auth_key': CONFIG['API_KEY']
        }
        
        response = requests.post(
            f"{CONFIG['CLOUD_SERVER_URL']}/printers/register",
            json=registration_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registration successful: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Registration failed: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to cloud server at {CONFIG['CLOUD_SERVER_URL']}")
        print(f"   Check: Cloud server is running and URL is correct")
        return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_cloud_print():
    """Test printing through cloud server"""
    try:
        print(f"🧪 Testing print through cloud server...")
        
        response = requests.post(
            f"{CONFIG['CLOUD_SERVER_URL']}/test/{CONFIG['RESTAURANT_ID']}",
            headers={'X-API-Key': CONFIG['API_KEY']},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Cloud print test successful!")
                print(f"📄 Check your printer for test receipt")
                return True
            else:
                print(f"❌ Cloud print test failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Cloud print test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cloud print test error: {e}")
        return False

def main():
    print("=" * 60)
    print("🏪 HK SAVOR SPOON PRINTER REGISTRATION CLIENT")
    print("=" * 60)
    print("Connects your local Star TSP143III to cloud server")
    print("Allows hksavorspoon.com to print directly to your restaurant")
    print("")
    
    # Step 1: Discover local printer
    if not test_printer_connection():
        print(f"⚠️  Configured printer {CONFIG['PRINTER_IP']} not responding")
        discovered_ip = discover_local_printer()
        if not discovered_ip:
            print("\n❌ No printer found. Please check:")
            print("   1. Star TSP143III is powered on")
            print("   2. Ethernet cable is connected")
            print("   3. Printer has valid IP address")
            sys.exit(1)
    else:
        print(f"✅ Printer ready at {CONFIG['PRINTER_IP']}:{CONFIG['PRINTER_PORT']}")
    
    # Step 2: Register with cloud
    if not register_with_cloud():
        print("\n❌ Cloud registration failed. Please check:")
        print("   1. Cloud server is running")
        print("   2. Cloud server URL is correct")
        print("   3. Internet connection is working")
        sys.exit(1)
    
    # Step 3: Test cloud printing
    if test_cloud_print():
        print("\n🎉 SUCCESS! Your printer is now connected to the cloud!")
        print(f"📝 Your website hksavorspoon.com can now print to:")
        print(f"   Restaurant ID: {CONFIG['RESTAURANT_ID']}")
        print(f"   Printer: {CONFIG['PRINTER_IP']}:{CONFIG['PRINTER_PORT']}")
        print(f"   Location: {CONFIG['LOCATION_NAME']}")
    else:
        print("\n⚠️  Registration successful but test print failed")
        print("   Check printer status and try again")
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("1. Keep this script running (or set up as service)")
    print("2. Update hksavorspoon.com to use cloud endpoint:")
    print(f"   POST {CONFIG['CLOUD_SERVER_URL']}/print")
    print("3. Include restaurant_id in print requests:")
    print(f"   {{\"restaurant_id\": \"{CONFIG['RESTAURANT_ID']}\", \"text\": \"receipt content\"}}")
    print("=" * 60)

def run_continuous():
    """Run continuous registration (for production)"""
    print("🔄 Starting continuous registration mode...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Re-register periodically
            if register_with_cloud():
                print(f"✅ Re-registered at {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"❌ Re-registration failed at {datetime.now().strftime('%H:%M:%S')}")
            
            # Wait before next registration
            time.sleep(CONFIG['REGISTRATION_INTERVAL'])
            
    except KeyboardInterrupt:
        print("\n🛑 Registration client stopped")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        # Run in continuous mode for production
        main()
        run_continuous()
    else:
        # Run one-time setup
        main()
        
        # Ask if user wants continuous mode
        response = input("\nRun in continuous mode? (y/n): ").strip().lower()
        if response == 'y':
            run_continuous()