# -*- coding: utf-8 -*-
"""
HK SAVOR SPOON PRINT SERVER - SECURITY MONITOR
==============================================
Real-time security monitoring dashboard
"""

import requests
import time
import json
import os
import sys
from datetime import datetime
import threading

API_KEY = "hksavorspoon-secure-print-key-2025"
SERVER_URL = "http://localhost:8080"

class SecurityMonitor:
    def __init__(self):
        self.headers = {"X-API-Key": API_KEY}
        self.running = True
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def get_security_status(self):
        try:
            response = requests.get(f"{SERVER_URL}/security-status", 
                                  headers=self.headers, timeout=5)
            return response.json() if response.status_code == 200 else None
        except:
            return None
            
    def get_server_status(self):
        try:
            response = requests.get(f"{SERVER_URL}/status", 
                                  headers=self.headers, timeout=5)
            return response.json() if response.status_code == 200 else None
        except:
            return None
            
    def get_queue_status(self):
        try:
            response = requests.get(f"{SERVER_URL}/queue", 
                                  headers=self.headers, timeout=5)
            return response.json() if response.status_code == 200 else None
        except:
            return None
            
    def display_dashboard(self):
        self.clear_screen()
        
        print("=" * 70)
        print("🛡️  HK SAVOR SPOON PRINT SERVER - SECURITY MONITOR")
        print("=" * 70)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Server Status
        server_status = self.get_server_status()
        if server_status:
            print("🟢 SERVER STATUS: ONLINE")
            print(f"   Version: {server_status.get('version', 'Unknown')}")
            print(f"   Printer: {server_status.get('printer', 'Not configured')}")
        else:
            print("🔴 SERVER STATUS: OFFLINE or UNREACHABLE")
            print()
            return
            
        print()
        
        # Security Status
        security_status = self.get_security_status()
        if security_status:
            print("🛡️  SECURITY STATUS:")
            print(f"   🚫 Blocked IPs: {security_status.get('blocked_ips', 0)}")
            print(f"   ⚡ Rate Limited IPs: {security_status.get('rate_limited_ips', 0)}")
            
            if security_status.get('blocked_list'):
                print("   🔒 Currently Blocked:")
                for ip in security_status['blocked_list'][:5]:  # Show max 5
                    print(f"      • {ip}")
                if len(security_status['blocked_list']) > 5:
                    print(f"      ... and {len(security_status['blocked_list']) - 5} more")
        else:
            print("🛡️  SECURITY STATUS: Unable to retrieve")
            
        print()
        
        # Queue and Circuit Breaker
        queue_status = self.get_queue_status()
        if queue_status:
            cb = queue_status.get('circuit_breaker', {})
            state = cb.get('state', 'UNKNOWN')
            
            if state == 'CLOSED':
                print("🟢 CIRCUIT BREAKER: CLOSED (Normal Operation)")
            elif state == 'OPEN':
                print("🔴 CIRCUIT BREAKER: OPEN (Service Protection Active)")
            elif state == 'HALF_OPEN':
                print("🟡 CIRCUIT BREAKER: HALF_OPEN (Testing Recovery)")
            else:
                print(f"⚪ CIRCUIT BREAKER: {state}")
                
            print(f"   Failures: {cb.get('failures', 0)}")
            print(f"   Queue Size: {queue_status.get('queue_size', 0)}")
        else:
            print("🔄 CIRCUIT BREAKER: Unable to retrieve status")
            
        print()
        
        # Recent Attacks/Events
        if os.path.exists('print_server_secure.log'):
            print("🚨 RECENT SECURITY EVENTS:")
            try:
                with open('print_server_secure.log', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # Get last 20 lines and filter for security events
                recent_lines = lines[-20:] if len(lines) > 20 else lines
                security_events = []
                
                for line in recent_lines:
                    if any(marker in line for marker in ['🚫', '🔍', '⚡', '🚨', '🔑']):
                        security_events.append(line.strip())
                        
                if security_events:
                    for event in security_events[-5:]:  # Show last 5 events
                        # Extract timestamp and event
                        parts = event.split(' - ', 2)
                        if len(parts) >= 3:
                            timestamp = parts[0]
                            level = parts[1]
                            message = parts[2]
                            
                            # Color coding based on severity
                            if '🚨' in message or '🚫' in message:
                                print(f"   🔴 {timestamp[-8:]} {message}")
                            elif '🔍' in message or '⚡' in message:
                                print(f"   🟡 {timestamp[-8:]} {message}")
                            elif '🔑' in message:
                                print(f"   🟠 {timestamp[-8:]} {message}")
                            else:
                                print(f"   ⚪ {timestamp[-8:]} {message}")
                else:
                    print("   ✅ No recent security events")
                    
            except Exception as e:
                print(f"   ❌ Error reading log: {e}")
        else:
            print("🚨 RECENT SECURITY EVENTS: No log file found")
            
        print()
        print("=" * 70)
        print("Press Ctrl+C to exit | Refreshing every 5 seconds...")
        print("=" * 70)
        
    def run(self):
        print("Starting Security Monitor...")
        print("Connecting to server...")
        
        try:
            while self.running:
                self.display_dashboard()
                time.sleep(5)  # Refresh every 5 seconds
                
        except KeyboardInterrupt:
            print("\n\n🛑 Security Monitor stopped by user")
            self.running = False

if __name__ == "__main__":
    try:
        monitor = SecurityMonitor()
        monitor.run()
    except Exception as e:
        print(f"❌ Monitor error: {e}")
        sys.exit(1)
