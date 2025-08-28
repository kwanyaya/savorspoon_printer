#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Printing Test for HK Savor Spoon Print Server
"""

import requests
import json

# Configuration
SERVER_URL = "http://localhost:5000"
API_KEY = "hksavorspoon-secure-print-key-2025"

def test_chinese_printing():
    """Test printing Chinese characters"""
    
    print("🇨🇳 Testing Chinese Character Printing...")
    print("=" * 50)
    
    # Chinese receipt test
    chinese_text = """
================================
       港式美味湯匙
       HK SAVOR SPOON  
================================
訂單編號: CHN001
客戶姓名: 李小明
日期時間: 2025-08-26 19:00:00
--------------------------------

菜品明細:
白切雞飯 x2
  單價: $15.50 = $31.00

雲吞湯 x1  
  單價: $8.00 = $8.00

奶茶 x2
  單價: $4.50 = $9.00

港式燒鴨飯 x1
  單價: $18.00 = $18.00

--------------------------------
小計: $57.00
總計: $57.00
付款方式: 現金
--------------------------------

謝謝惠顧！
歡迎再次光臨港式美味湯匙
hksavorspoon.com

================================
"""

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "text": chinese_text,
        "job_name": "中文測試列印"
    }
    
    try:
        print("Sending Chinese print request...")
        response = requests.post(
            f"{SERVER_URL}/print", 
            headers=headers, 
            json=data, 
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chinese print request sent successfully!")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Job Name: {result.get('job_name', 'Unknown')}")
            return True
        else:
            print(f"❌ Print failed with status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to print server!")
        print("   Make sure the server is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chinese_receipt():
    """Test printing a Chinese receipt with proper formatting"""
    
    print("\n🧾 Testing Chinese Receipt Printing...")
    print("=" * 50)
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    receipt_data = {
        "receipt_data": {
            "order_id": "港001",
            "customer_name": "張三豐",
            "items": [
                {
                    "name": "白切雞飯",
                    "quantity": 2,
                    "price": 15.50
                },
                {
                    "name": "雲吞湯",
                    "quantity": 1,
                    "price": 8.00
                },
                {
                    "name": "港式奶茶",
                    "quantity": 2,
                    "price": 4.50
                },
                {
                    "name": "燒鴨飯",
                    "quantity": 1,
                    "price": 18.00
                }
            ],
            "total": "55.00",
            "payment_method": "現金",
            "order_time": "2025-08-26 19:00:00"
        },
        "job_name": "中文收據#港001"
    }
    
    try:
        print("Sending Chinese receipt print request...")
        response = requests.post(
            f"{SERVER_URL}/print", 
            headers=headers, 
            json=receipt_data, 
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chinese receipt printed successfully!")
            print(f"   Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Receipt print failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all Chinese printing tests"""
    print("🍜 HK Savor Spoon - Chinese Printing Test")
    print("=" * 50)
    
    # Test 1: Simple Chinese text
    test1_success = test_chinese_printing()
    
    # Test 2: Chinese receipt format
    test2_success = test_chinese_receipt()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Chinese Text Print: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   Chinese Receipt: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All Chinese printing tests passed!")
        print("Your Star TSP100 printer supports Chinese characters!")
    else:
        print("\n⚠️  Some tests failed. Check your printer settings.")
        print("For Chinese printing, ensure your printer supports UTF-8 encoding.")
    
    print("\n📝 Note: Check your Star TSP100 printer for the printed output.")

if __name__ == "__main__":
    main()
