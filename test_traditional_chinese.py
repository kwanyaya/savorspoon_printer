#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traditional Chinese Print Test & Diagnosis Tool
Tests various encoding methods to find the best one for your printer
"""

import sys
import requests
import json

# Test Traditional Chinese text samples
traditional_samples = {
    "basic": "繁體中文測試",
    "restaurant": "歡迎光臨香港美食勺餐廳！",
    "receipt": "訂單編號：TC001\n客戶：陳先生\n總計：$128.50\n謝謝光臨！",
    "mixed": "Order #TC001\n客戶：張小姐\nTotal: $99.99\n謝謝惠顧！"
}

def test_traditional_chinese_printing():
    """Test Traditional Chinese printing with various samples"""
    
    server_url = "http://localhost:5000"
    api_key = "hksavorspoon-secure-print-key-2025"
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    print("🔍 Traditional Chinese Print Diagnosis")
    print("="*50)
    
    # Test server connection first
    try:
        response = requests.get(f"{server_url}/status", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Please start the print server first.")
            return False
        
        server_info = response.json()
        printer_name = server_info.get('default_printer', 'Unknown')
        print(f"✅ Server connected")
        print(f"📰 Default Printer: {printer_name}")
        print()
        
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please make sure the print server is running on localhost:5000")
        return False
    
    # Test each Traditional Chinese sample
    success_count = 0
    total_tests = len(traditional_samples)
    
    for test_name, text_sample in traditional_samples.items():
        print(f"🧪 Testing: {test_name}")
        print(f"📝 Text: {text_sample}")
        
        try:
            test_data = {
                "text": f"""
================================
Traditional Chinese Test: {test_name}
================================
{text_sample}

If these characters print correctly,
Traditional Chinese support is working!
================================
""",
                "job_name": f"Traditional Chinese Test - {test_name}"
            }
            
            response = requests.post(f"{server_url}/print", 
                                   headers=headers, 
                                   json=test_data, 
                                   timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Print sent: {result.get('message', 'Success')}")
                success_count += 1
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', f"HTTP {response.status_code}")
                print(f"❌ Print failed: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests successful")
    
    if success_count == total_tests:
        print("🎉 All Traditional Chinese tests passed!")
        print("Your printer should be able to handle Traditional Chinese characters.")
    elif success_count > 0:
        print("⚠️  Some tests passed, some failed. There may be encoding issues.")
        print("Check the printed output to see which characters display correctly.")
    else:
        print("❌ All tests failed. Traditional Chinese support needs fixing.")
        print("\n💡 Troubleshooting suggestions:")
        print("1. Check if your printer supports Chinese character sets")
        print("2. Verify printer drivers are properly installed")
        print("3. Check the print server logs for detailed error messages")
    
    return success_count == total_tests

if __name__ == "__main__":
    print("Traditional Chinese Print Diagnosis Tool")
    print("This tool will test various Traditional Chinese text samples")
    print("Make sure your print server is running before continuing.\n")
    
    input("Press Enter to start testing...")
    
    try:
        success = test_traditional_chinese_printing()
        
        if not success:
            print("\n🔧 Next Steps:")
            print("1. Run this test and check the printed output")
            print("2. If characters appear as squares/question marks, it's an encoding issue")
            print("3. If nothing prints, check printer connection and drivers")
            print("4. Report the results so we can fix the encoding strategy")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest error: {e}")
