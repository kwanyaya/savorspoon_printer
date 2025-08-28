#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
External Access Test for HK Savor Spoon Print Server
Test from any external computer or online service
"""

import requests
import time
import json

# Your public print server details
PUBLIC_URL = "http://58.153.166.26:5000"
API_KEY = "hksavorspoon-secure-print-key-2025"

def test_external_access():
    """Test external access to the print server"""
    
    print("🌐 Testing External Access to HK Savor Spoon Print Server")
    print("=" * 60)
    print(f"Public URL: {PUBLIC_URL}")
    print(f"Testing from external perspective...")
    print()
    
    # Test 1: Basic connectivity
    print("1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(f"{PUBLIC_URL}/status", timeout=20)
        
        if response.status_code == 200:
            print("✅ SUCCESS! External access is working!")
            data = response.json()
            print(f"   Server: {data.get('server', 'Unknown')}")
            print(f"   Computer: {data.get('computer', 'Unknown')}")
            print(f"   Printer: {data.get('default_printer', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - server may not be accessible externally")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - port forwarding may not be working")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_external_printing():
    """Test external printing functionality"""
    
    print("\n2️⃣ Testing external printing...")
    
    test_receipt = """🌐 External Access Test
========================================
         港式美味湯匙
         HK SAVOR SPOON  
========================================
訂單編號: EXT001
測試時間: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """

外部訪問測試成功！
External access test successful!

謝謝！ Thank you!
========================================"""

    try:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        data = {
            "text": test_receipt,
            "font_size": "large",
            "job_name": "External_Access_Test"
        }
        
        response = requests.post(
            f"{PUBLIC_URL}/print",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ External printing successful!")
            print(f"   Message: {result.get('message', 'No message')}")
            print("   🖨️ Check your Star TSP100 printer for output!")
            return True
        else:
            print(f"❌ Print request failed with status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Print test failed: {e}")
        return False

def main():
    """Main test function"""
    
    # Test basic access
    access_works = test_external_access()
    
    if access_works:
        # Test printing if access works
        print_works = test_external_printing()
        
        print("\n🎉 External Access Test Results:")
        print("================================")
        print("✅ Status endpoint: Working")
        print("✅ Print endpoint: Working" if print_works else "❌ Print endpoint: Failed")
        print("\n🚀 Your HK Savor Spoon website can now:")
        print("   • Check print server status")
        print("   • Send print jobs to your restaurant")
        print("   • Print receipts on your Star TSP100")
        
        print(f"\n📋 Integration URLs for your website:")
        print(f"   Status: {PUBLIC_URL}/status")
        print(f"   Print: {PUBLIC_URL}/print")
        print(f"   API Key: {API_KEY}")
        
    else:
        print("\n❌ External access is not working yet.")
        print("\n🔧 Troubleshooting steps:")
        print("1. Wait 2-5 minutes for router changes to take effect")
        print("2. Restart your router if needed")
        print("3. Check Windows Firewall (run as Administrator):")
        print("   netsh advfirewall firewall add rule name=\"HK Savor Spoon\" dir=in action=allow protocol=TCP localport=5000")
        print("4. Verify port forwarding settings:")
        print("   External Port: 5000 → Internal IP: 192.168.0.184:5000")
        print("5. Some ISPs block port 5000 - try port 8080 instead")

if __name__ == "__main__":
    main()
