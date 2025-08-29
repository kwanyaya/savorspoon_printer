#!/usr/bin/env python3
"""
Comprehensive Test Suite for HK Savor Spoon Windows Print Server
Tests all functionality including Chinese character support and external access
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:5000"
API_KEY = "hksavorspoon-secure-print-key-2025"  # Match your server API key

class PrintServerTester:
    """Comprehensive test suite for the print server"""
    
    def __init__(self, server_url=SERVER_URL, api_key=API_KEY):
        self.server_url = server_url
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        self.passed_tests = 0
        self.total_tests = 0
    
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}")
            if message:
                print(f"   {message}")
        else:
            print(f"❌ {test_name}")
            print(f"   {message}")
        print()
    
    def test_server_status(self):
        """Test if server is running and responding"""
        try:
            response = requests.get(f"{self.server_url}/status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                message = f"Server: {data.get('server', 'Unknown')}"
                message += f" | Computer: {data.get('computer', 'Unknown')}"
                message += f" | IP: {data.get('local_ip', 'Unknown')}"
                message += f" | Printer: {data.get('default_printer', 'None')}"
                
                self.log_test("Server Status Check", True, message)
                return True
            else:
                self.log_test("Server Status Check", False, f"HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test("Server Status Check", False, "Cannot connect - server not running")
            return False
        except Exception as e:
            self.log_test("Server Status Check", False, str(e))
            return False
    
    def test_api_authentication(self):
        """Test API key authentication"""
        try:
            # Test with valid API key
            response = requests.get(f"{self.server_url}/printers", headers=self.headers, timeout=5)
            if response.status_code != 200 and response.status_code != 401:
                # If we get something other than 200 or 401, there might be another issue
                self.log_test("API Authentication", False, f"Unexpected response: {response.status_code}")
                return False
            
            # Test with invalid API key
            bad_headers = {"X-API-Key": "invalid-key", "Content-Type": "application/json"}
            response = requests.get(f"{self.server_url}/printers", headers=bad_headers, timeout=5)
            
            if response.status_code == 401:
                self.log_test("API Authentication", True, "API key validation working correctly")
                return True
            else:
                self.log_test("API Authentication", False, "Invalid API key was accepted")
                return False
                
        except Exception as e:
            self.log_test("API Authentication", False, str(e))
            return False
    
    def test_printer_detection(self):
        """Test printer detection and listing"""
        try:
            response = requests.get(f"{self.server_url}/printers", headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                printers = data.get('printers', [])
                default_printer = data.get('default_printer')
                
                if len(printers) > 0:
                    message = f"Found {len(printers)} printer(s) | Default: {default_printer or 'None'}"
                    self.log_test("Printer Detection", True, message)
                    return True
                else:
                    self.log_test("Printer Detection", False, "No printers found")
                    return False
            else:
                self.log_test("Printer Detection", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Printer Detection", False, str(e))
            return False
    
    def test_simple_print(self):
        """Test simple text printing"""
        try:
            test_text = f"""
================================
    SIMPLE TEXT PRINT TEST
================================
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a basic text printing test.
If you see this printout, the basic
printing functionality is working.

English characters: ABCDEFG
Numbers: 1234567890
Symbols: !@#$%^&*()
================================
"""
            
            data = {
                "text": test_text,
                "job_name": "Simple Text Test"
            }
            
            response = requests.post(f"{self.server_url}/print", 
                                   headers=self.headers, 
                                   json=data, 
                                   timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                message = f"Print job sent: {result.get('message', 'No details')}"
                self.log_test("Simple Text Print", True, message)
                return True
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', f"HTTP {response.status_code}")
                self.log_test("Simple Text Print", False, error_msg)
                return False
                
        except Exception as e:
            self.log_test("Simple Text Print", False, str(e))
            return False
    
    def test_chinese_characters(self):
        """Test Chinese character printing (both Simplified and Traditional)"""
        try:
            chinese_text = f"""
================================
      中文字符测试 (Chinese Test)
================================
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

简体中文测试：
你好世界！这是简体中文测试。
欢迎光临香港美食勺餐厅！

繁體中文測試：
你好世界！這是繁體中文測試。
歡迎光臨香港美食勺餐廳！

混合文本测试 (Mixed Text):
Order ID: 中文订单001
Customer: 张三 (Zhang San)
Total: $25.00 港币

谢谢光临！Thank you!
================================
"""
            
            data = {
                "text": chinese_text,
                "job_name": "Chinese Character Test"
            }
            
            response = requests.post(f"{self.server_url}/print", 
                                   headers=self.headers, 
                                   json=data, 
                                   timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                message = f"Chinese print successful: {result.get('message', 'No details')}"
                self.log_test("Chinese Character Print", True, message)
                return True
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', f"HTTP {response.status_code}")
                self.log_test("Chinese Character Print", False, error_msg)
                return False
                
        except Exception as e:
            self.log_test("Chinese Character Print", False, str(e))
            return False
    
    def test_receipt_printing(self):
        """Test receipt format printing"""
        try:
            receipt_data = {
                "receipt_data": {
                    "order_id": "TEST001",
                    "customer_name": "测试客户 (Test Customer)",
                    "items": [
                        {
                            "name": "叉烧饭 (Char Siu Rice)",
                            "quantity": 2,
                            "price": 15.50
                        },
                        {
                            "name": "云吞面 (Wonton Noodles)",
                            "quantity": 1,
                            "price": 12.00
                        },
                        {
                            "name": "奶茶 (Milk Tea)",
                            "quantity": 2,
                            "price": 5.50
                        }
                    ],
                    "total": "53.50",
                    "payment_method": "现金 (Cash)",
                    "order_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                "job_name": "Test Receipt"
            }
            
            response = requests.post(f"{self.server_url}/print", 
                                   headers=self.headers, 
                                   json=receipt_data, 
                                   timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                message = f"Receipt printed: {result.get('message', 'No details')}"
                self.log_test("Receipt Printing", True, message)
                return True
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', f"HTTP {response.status_code}")
                self.log_test("Receipt Printing", False, error_msg)
                return False
                
        except Exception as e:
            self.log_test("Receipt Printing", False, str(e))
            return False
    
    def test_built_in_test_print(self):
        """Test the server's built-in test print function"""
        try:
            response = requests.post(f"{self.server_url}/test-print", 
                                   headers=self.headers, 
                                   timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                message = "Built-in test print successful"
                self.log_test("Built-in Test Print", True, message)
                return True
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', f"HTTP {response.status_code}")
                self.log_test("Built-in Test Print", False, error_msg)
                return False
                
        except Exception as e:
            self.log_test("Built-in Test Print", False, str(e))
            return False
    
    def test_external_access(self, external_url=None):
        """Test external access if URL provided"""
        if not external_url:
            self.log_test("External Access Test", False, "No external URL provided - skipping")
            return False
        
        try:
            print(f"Testing external access: {external_url}")
            response = requests.get(f"{external_url}/status", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                message = f"External access working! Server: {data.get('computer', 'Unknown')}"
                self.log_test("External Access Test", True, message)
                return True
            else:
                self.log_test("External Access Test", False, f"HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_test("External Access Test", False, "Timeout - port forwarding may not be configured")
            return False
        except requests.exceptions.ConnectionError:
            self.log_test("External Access Test", False, "Connection failed - check network configuration")
            return False
        except Exception as e:
            self.log_test("External Access Test", False, str(e))
            return False
    
    def run_all_tests(self, external_url=None):
        """Run all tests and display results"""
        print("="*70)
        print("HK SAVOR SPOON PRINT SERVER - COMPREHENSIVE TEST SUITE")
        print("="*70)
        print(f"Testing server: {self.server_url}")
        print(f"API Key: {self.api_key[:10]}...")
        print()
        
        # Run tests in order
        tests = [
            self.test_server_status,
            self.test_api_authentication,
            self.test_printer_detection,
            self.test_simple_print,
            self.test_chinese_characters,
            self.test_receipt_printing,
            self.test_built_in_test_print,
        ]
        
        # Add external test if URL provided
        if external_url:
            tests.append(lambda: self.test_external_access(external_url))
        
        # Execute tests
        for test in tests:
            test()
            time.sleep(1)  # Small delay between tests
        
        # Display results
        print("="*70)
        print(f"TEST RESULTS: {self.passed_tests}/{self.total_tests} tests passed")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL TESTS PASSED! Your print server is working perfectly.")
        elif self.passed_tests >= self.total_tests * 0.8:
            print("⚠️  Most tests passed, but some issues found. Check details above.")
        else:
            print("❌ Multiple test failures. Please check your configuration.")
        
        print("="*70)
        
        return self.passed_tests == self.total_tests

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test HK Savor Spoon Print Server')
    parser.add_argument('--url', default=SERVER_URL, help='Server URL to test')
    parser.add_argument('--api-key', default=API_KEY, help='API key for authentication')
    parser.add_argument('--external-url', help='External URL to test (e.g., http://your-domain:5000)')
    
    args = parser.parse_args()
    
    try:
        tester = PrintServerTester(args.url, args.api_key)
        success = tester.run_all_tests(args.external_url)
        
        if not success:
            print("\n💡 TROUBLESHOOTING TIPS:")
            print("1. Make sure the print server is running")
            print("2. Check that a printer is set as default")
            print("3. Verify the API key matches the server configuration")
            print("4. For external access, check router port forwarding")
            print("5. Review the print_server.log file for detailed errors")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test suite error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
