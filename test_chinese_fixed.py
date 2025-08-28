#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Chinese Print Test - Fixed Version
Tests the new printing method that avoids the Notepad file error
"""

import requests
import json

def test_simple_chinese():
    """Test simple Chinese printing with the fixed method"""
    
    print("🔧 Testing Fixed Chinese Printing Method...")
    print("=" * 50)
    
    # Simple Chinese test
    chinese_text = """
================================
       港式美味湯匙
       HK SAVOR SPOON  
================================

測試中文列印功能
Testing Chinese Print Function

菜品 Menu Items:
• 白切雞飯 - Chicken Rice
• 雲吞湯 - Wonton Soup  
• 港式奶茶 - HK Milk Tea

謝謝惠顧！
Thank you!

================================
"""

    headers = {
        "X-API-Key": "hksavorspoon-secure-print-key-2025",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "text": chinese_text,
        "job_name": "中文測試-修復版"
    }
    
    try:
        print("Sending Chinese print test (Fixed Method)...")
        response = requests.post(
            "http://localhost:5000/print", 
            headers=headers, 
            json=data, 
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Chinese print sent!")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Method: {result.get('message', '').split('(')[-1].replace(')', '') if '(' in result.get('message', '') else 'Unknown'}")
            print("\n📄 Check your Star TSP100 printer for the Chinese output!")
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to print server!")
        print("   Make sure server is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🍜 HK Savor Spoon - Fixed Chinese Print Test")
    print("This test uses the improved printing method")
    print("that avoids the '找不到檔案 記事本' error\n")
    
    success = test_simple_chinese()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test PASSED! Chinese printing should work now.")
        print("The server now uses direct printer API for better reliability.")
    else:
        print("❌ Test FAILED. Check the error messages above.")
    
    print("\n💡 What was fixed:")
    print("• Uses direct printer API instead of Notepad")
    print("• Proper UTF-8 encoding for Chinese characters")
    print("• Fallback methods if direct printing fails")
    print("• Better error handling and logging")
