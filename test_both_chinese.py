#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Both Simplified and Traditional Chinese Characters
For HK Savor Spoon Print Server with Star TSP100
"""

import requests
import json
import time

# Test server URL
SERVER_URL = "http://localhost:5000"
API_KEY = "hk_savor_spoon_2024"

def test_server_status():
    """Check if server is running"""
    try:
        response = requests.get(f"{SERVER_URL}/status")
        if response.status_code == 200:
            print("✅ Server is running")
            data = response.json()
            print(f"📄 Default Printer: {data.get('default_printer', 'Unknown')}")
            return True
        else:
            print("❌ Server is not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_print_text(text, description):
    """Test printing text with API"""
    try:
        payload = {
            "text": text,
            "api_key": API_KEY
        }
        
        response = requests.post(f"{SERVER_URL}/print", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {description}: {result.get('message', 'Print sent')}")
        else:
            print(f"❌ {description}: Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ {description}: Error - {e}")

def main():
    print("🖨️  Testing Both Chinese Character Sets - HK Savor Spoon")
    print("=" * 60)
    
    # Check server status
    if not test_server_status():
        print("\n❌ Please start the server first: python windows_print_server.py")
        return
    
    print("\n📝 Starting Chinese Character Tests...")
    
    # Test 1: English baseline
    print("\n1️⃣  Testing English (baseline)...")
    test_print_text("HK Savor Spoon - Print Test", "English baseline")
    time.sleep(2)
    
    # Test 2: Simplified Chinese
    print("\n2️⃣  Testing Simplified Chinese (简体中文)...")
    simplified_text = """港式美食店
简体中文测试
菜单：
- 牛肉面 $45
- 叉烧饭 $42
- 奶茶 $25
谢谢光临！"""
    test_print_text(simplified_text, "Simplified Chinese")
    time.sleep(2)
    
    # Test 3: Traditional Chinese
    print("\n3️⃣  Testing Traditional Chinese (繁體中文)...")
    traditional_text = """港式美食店
繁體中文測試
菜單：
- 牛肉麵 $45
- 叉燒飯 $42  
- 奶茶 $25
謝謝光臨！"""
    test_print_text(traditional_text, "Traditional Chinese")
    time.sleep(2)
    
    # Test 4: Mixed Chinese (both sets in same text)
    print("\n4️⃣  Testing Mixed Chinese (简体 + 繁體)...")
    mixed_text = """港式美食店 HK Savor Spoon
简体：欢迎光临
繁體：歡迎光臨
Menu 菜单 菜單:
- 牛肉面/牛肉麵 Beef Noodle $45
- 叉烧饭/叉燒飯 BBQ Pork Rice $42
- 奶茶 Milk Tea $25
谢谢/謝謝 Thank you!"""
    test_print_text(mixed_text, "Mixed Chinese Characters")
    time.sleep(2)
    
    # Test 5: Hong Kong specific characters
    print("\n5️⃣  Testing Hong Kong specific characters...")
    hk_text = """香港美食
港式茶餐廳
餐牌：
- 絲襪奶茶 $18
- 菠蘿包 $12
- 燒鵝飯 $48
- 雲吞麵 $38
歡迎蒞臨！
Thank you for dining with us!"""
    test_print_text(hk_text, "Hong Kong Traditional")
    time.sleep(2)
    
    # Test 6: Common restaurant phrases
    print("\n6️⃣  Testing Common Restaurant Phrases...")
    restaurant_text = """收據 Receipt
============================
HK Savor Spoon 港式美味
地址：香港中環
電話：+852 1234 5678

點餐明細：
1x 牛肉麵 Beef Noodle    $45.00
1x 叉燒飯 BBQ Pork Rice  $42.00  
1x 奶茶 Milk Tea        $25.00
============================
小計 Subtotal:          $112.00
服務費 Service (10%):     $11.20
總計 Total:             $123.20

謝謝光臨！
Thank you for your visit!
歡迎再來 Welcome back!"""
    test_print_text(restaurant_text, "Restaurant Receipt")
    
    print("\n🎉 All Chinese character tests completed!")
    print("📋 Please check your printer output to verify:")
    print("   ✓ Simplified Chinese characters display correctly")
    print("   ✓ Traditional Chinese characters display correctly") 
    print("   ✓ Mixed text prints properly")
    print("   ✓ Restaurant receipts format well")

if __name__ == "__main__":
    main()
