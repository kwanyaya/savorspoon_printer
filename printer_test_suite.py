# -*- coding: utf-8 -*-
"""
HK Savor Spoon Printer Test & Diagnostic Tool
=============================================
Consolidated testing and diagnostic utilities
"""

import urllib.request
import json
import time
import win32print

class PrinterTester:
    """Comprehensive printer testing"""
    
    def __init__(self, server_url="http://localhost:8080", api_key="hksavorspoon-secure-print-key-2025"):
        self.server_url = server_url
        self.api_key = api_key
    
    def test_server_status(self):
        """Test server status endpoint"""
        print("1. TESTING SERVER STATUS")
        print("-" * 30)
        
        try:
            req = urllib.request.Request(f'{self.server_url}/status')
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                print(f"✅ Server Status: {data.get('status')}")
                print(f"   Version: {data.get('version')}")
                print(f"   Computer: {data.get('computer')}")
                print(f"   Printer: {data.get('default_printer')}")
                return True
                
        except Exception as e:
            print(f"❌ Server status failed: {e}")
            return False
    
    def test_api_authentication(self):
        """Test API key authentication"""
        print("\n2. TESTING API AUTHENTICATION")
        print("-" * 30)
        
        # Test with correct API key
        try:
            test_data = {"text": f"API Test - {time.strftime('%H:%M:%S')}"}
            data = json.dumps(test_data, ensure_ascii=False).encode('utf-8')
            
            req = urllib.request.Request(f'{self.server_url}/print', data=data)
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            req.add_header('X-API-Key', self.api_key)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('success'):
                    print(f"✅ API Authentication: SUCCESS")
                    print(f"   Message: {result.get('message')}")
                    return True
                else:
                    print(f"❌ API Authentication failed: {result.get('error')}")
                    return False
                    
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"❌ API Authentication: 401 Unauthorized")
            else:
                print(f"❌ API Authentication: HTTP {e.code}")
            return False
        except Exception as e:
            print(f"❌ API Authentication error: {e}")
            return False
    
    def test_chinese_printing(self):
        """Test Chinese character printing"""
        print("\n3. TESTING CHINESE PRINTING")
        print("-" * 30)
        
        chinese_text = f"""
HK SAVOR SPOON 測試
==================
時間: {time.strftime('%Y-%m-%d %H:%M:%S')}

繁體中文測試: 香港美味湯匙
Traditional Chinese Test

項目清單:
- 叉燒包 x2  $15.00
- 蝦餃 x3   $18.00  
- 奶茶 x1   $8.00
總計: $41.00

謝謝光臨！
==================
"""
        
        try:
            test_data = {"text": chinese_text}
            data = json.dumps(test_data, ensure_ascii=False).encode('utf-8')
            
            req = urllib.request.Request(f'{self.server_url}/print', data=data)
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            req.add_header('X-API-Key', self.api_key)
            
            print("   Sending Chinese text...")
            start_time = time.time()
            
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                elapsed = time.time() - start_time
                
                if result.get('success'):
                    print(f"✅ Chinese printing: SUCCESS ({elapsed:.2f}s)")
                    print(f"   Message: {result.get('message')}")
                    return True
                else:
                    print(f"❌ Chinese printing failed: {result.get('error')}")
                    return False
                    
        except Exception as e:
            print(f"❌ Chinese printing error: {e}")
            return False
    
    def diagnose_printer_hardware(self):
        """Diagnose physical printer issues"""
        print("\n4. PRINTER HARDWARE DIAGNOSIS")
        print("-" * 30)
        
        printer_name = "Star TSP100 Cutter (TSP143)"
        
        try:
            # Check if printer exists
            printers = [p[2] for p in win32print.EnumPrinters(2)]
            if printer_name not in printers:
                print(f"❌ Printer '{printer_name}' not found")
                print("   Available printers:")
                for p in printers:
                    print(f"     - {p}")
                return False
            
            # Check printer status
            handle = win32print.OpenPrinter(printer_name)
            info = win32print.GetPrinter(handle, 2)
            
            status = info['Status']
            port = info['pPortName']
            
            print(f"✅ Printer found: {printer_name}")
            print(f"   Port: {port}")
            print(f"   Status: {status}")
            
            if status == 0:
                print("   ✅ Printer status: Normal")
            else:
                print("   ⚠️ Printer has issues:")
                if status & 0x80:
                    print("     - OFFLINE")
                if status & 0x10:
                    print("     - PAPER OUT")
                if status & 0x08:
                    print("     - PAPER JAM")
                if status & 0x01:
                    print("     - PAUSED")
            
            # Check queue
            jobs = win32print.EnumJobs(handle, 0, -1, 1)
            print(f"   Jobs in queue: {len(jobs)}")
            
            win32print.ClosePrinter(handle)
            return True
            
        except Exception as e:
            print(f"❌ Hardware diagnosis failed: {e}")
            return False
    
    def run_full_test(self):
        """Run complete test suite"""
        print("HK SAVOR SPOON PRINTER TEST SUITE")
        print("=" * 50)
        
        results = {
            'server_status': self.test_server_status(),
            'api_auth': self.test_api_authentication(),
            'chinese_print': self.test_chinese_printing(),
            'hardware': self.diagnose_printer_hardware()
        }
        
        print(f"\n📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = sum(results.values())
        total = len(results)
        
        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test.replace('_', ' ').title():<20} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Printer system is working correctly!")
        else:
            print("⚠️ Some tests failed - Check the results above")
        
        return results

def printer_self_test_guide():
    """Guide for running printer self-test"""
    print("\nPRINTER SELF-TEST GUIDE")
    print("=" * 30)
    print("If software tests fail, try this hardware test:")
    print()
    print("1. Turn OFF the Star TSP100 printer")
    print("2. Hold down the FEED button (on the printer)")
    print("3. While holding FEED, turn the printer ON")
    print("4. Keep holding FEED for 3 seconds")
    print("5. Release the FEED button")
    print()
    print("Expected: Printer should print a configuration page")
    print("If this fails → Hardware/power/paper issue")
    print("If this works → Driver/software issue")

if __name__ == "__main__":
    # Run the test suite
    tester = PrinterTester()
    results = tester.run_full_test()
    
    # Show self-test guide if needed
    if not all(results.values()):
        printer_self_test_guide()
