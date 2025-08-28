#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick External Access Test
Test if your print server is reachable from the internet
"""

import requests
import time

def test_external_access():
    """Test if external access is working"""
    
    print("🌐 Testing External Access to Print Server")
    print("=" * 50)
    print("URL: http://58.153.166.26:5000")
    print()
    
    print("1️⃣ Testing connection...")
    try:
        # Test with a longer timeout
        response = requests.get(
            "http://58.153.166.26:5000/status", 
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS! External access is working!")
            data = response.json()
            print(f"   Server: {data.get('server', 'Unknown')}")
            print(f"   Printer: {data.get('default_printer', 'Unknown')}")
            print(f"   Current IP: {data.get('local_ip', 'Unknown')}")
            print()
            print("🎉 Your HK Savor Spoon website should now be able to print!")
            return True
        else:
            print(f"❌ Server responded with error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - This is the same error your website is getting")
        print("   The print server is not accessible from the internet")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION FAILED - Port forwarding is not working")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    success = test_external_access()
    
    if not success:
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("=" * 50)
        print("1. Run fix_firewall.ps1 as Administrator")
        print("2. Check your router port forwarding:")
        print("   - External Port: 5000")
        print("   - Internal IP: (check what the server shows)")
        print("   - Internal Port: 5000")
        print("3. Restart your router")
        print("4. Wait 5 minutes for changes to take effect")
        print("5. Test again")
        print()
        print("💡 If still not working, try using port 8080 instead of 5000")
        print("   Some ISPs block port 5000")

if __name__ == "__main__":
    main()
