#!/usr/bin/env python3
"""
Test script for HK Savor Spoon Windows Print Server
"""

import requests
import json
import sys

# Configuration
SERVER_URL = "http://localhost:5000"
API_KEY = "hksavorspoon-secure-print-key-2025"  # Match your server API key

def test_server_status():
    """Test server status endpoint"""
    try:
        print("Testing server status...")
        response = requests.get(f"{SERVER_URL}/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running!")
            print(f"   Computer: {data.get('computer', 'Unknown')}")
            print(f"   Local IP: {data.get('local_ip', 'Unknown')}")
            print(f"   Default Printer: {data.get('default_printer', 'None')}")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing status: {e}")
        return False

def test_printers_list():
    """Test printers list endpoint"""
    try:
        print("\nTesting printers list...")
        headers = {"X-API-Key": API_KEY}
        response = requests.get(f"{SERVER_URL}/printers", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            printers = data.get('printers', [])
            print(f"✅ Found {len(printers)} printer(s):")
            
            for printer in printers:
                status = "DEFAULT" if printer.get('is_default') else ""
                print(f"   - {printer.get('name')} {status}")
            
            return len(printers) > 0
        elif response.status_code == 401:
            print("❌ Unauthorized - Check API key")
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing printers: {e}")
        return False

def test_simple_print():
    """Test simple text printing"""
    try:
        print("\nTesting simple print...")
        headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": f"""
================================
    HK SAVOR SPOON TEST PRINT
================================
This is a test print from the
Python test script.

If you see this, your printer
server is working correctly!

Timestamp: {requests.get(f"{SERVER_URL}/status").json().get('timestamp', 'Unknown')}
================================
""",
            "job_name": "Python Test Print"
        }
        
        response = requests.post(f"{SERVER_URL}/print", 
                               headers=headers, 
                               json=data, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Print job sent successfully!")
            print(f"   Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Print failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing print: {e}")
        return False

def test_receipt_print():
    """Test receipt printing"""
    try:
        print("\nTesting receipt print...")
        headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "receipt_data": {
                "order_id": "TEST001",
                "customer_name": "Test Customer",
                "items": [
                    {
                        "name": "Chicken Rice",
                        "quantity": 2,
                        "price": 15.50
                    },
                    {
                        "name": "Wonton Soup",
                        "quantity": 1,
                        "price": 8.00
                    }
                ],
                "total": "39.00",
                "payment_method": "Cash",
                "order_time": "2025-08-26 10:30:00"
            },
            "job_name": "Test Receipt"
        }
        
        response = requests.post(f"{SERVER_URL}/print", 
                               headers=headers, 
                               json=data, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Receipt printed successfully!")
            print(f"   Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Receipt print failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing receipt: {e}")
        return False

def main():
    """Run all tests"""
    print("="*50)
    print("HK Savor Spoon Print Server Test Suite")
    print("="*50)
    
    tests = [
        test_server_status,
        test_printers_list,
        test_simple_print,
        test_receipt_print
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests
    
    print("="*50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your print server is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("="*50)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
