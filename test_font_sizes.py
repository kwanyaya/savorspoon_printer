#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Different Font Sizes for Star TSP100 Printer
"""

import requests
import json
import time

SERVER_URL = "http://localhost:5000"
API_KEY = "hksavorspoon-secure-print-key-2025"

def test_font_size(font_size, description):
    """Test printing with different font sizes"""
    
    test_text = f"""
{description}
========================================
         港式美味湯匙
         HK SAVOR SPOON  
========================================
訂單編號: 003
Font Size: {font_size}

這是字體大小測試
This is a font size test

謝謝！ Thank you!
========================================
"""
    
    payload = {
        "text": test_text,
        "font_size": font_size,
        "job_name": f"Font_Test_{font_size}",
        "api_key": API_KEY
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/print", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {description}: {result.get('message', 'Print sent')}")
        else:
            print(f"❌ {description}: Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ {description}: Error - {e}")

def main():
    print("🖨️  Testing Different Font Sizes - Star TSP100")
    print("=" * 50)
    
    # Check server status
    try:
        response = requests.get(f"{SERVER_URL}/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding")
            return
    except:
        print("❌ Cannot connect to server")
        return
    
    print("\n📝 Testing different font sizes...")
    
    # Test 1: Normal size
    print("\n1️⃣  Testing Normal Font Size...")
    test_font_size("normal", "Normal Size (Standard)")
    time.sleep(3)
    
    # Test 2: Large size (double width and height)
    print("\n2️⃣  Testing Large Font Size...")
    test_font_size("large", "Large Size (Double Width & Height)")
    time.sleep(3)
    
    # Test 3: Double height only
    print("\n3️⃣  Testing Double Height...")
    test_font_size("double_height", "Double Height Only")
    time.sleep(3)
    
    # Test 4: Double width only
    print("\n4️⃣  Testing Double Width...")
    test_font_size("double_width", "Double Width Only")
    time.sleep(3)
    
    print("\n🎉 Font size testing completed!")
    print("📋 Check your Star TSP100 printer to compare the different sizes")
    print("\n📖 Font Size Options for your API:")
    print("   • 'normal' - Standard size")
    print("   • 'large' - Double width and height (recommended)")
    print("   • 'double_height' - Tall text")
    print("   • 'double_width' - Wide text")

if __name__ == "__main__":
    main()
