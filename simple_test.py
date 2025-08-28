#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to check server and print Traditional Chinese
"""

import requests
import json

def main():
    print("Testing Traditional Chinese Support...")
    
    # Check server status
    try:
        response = requests.get("http://localhost:5000/status", timeout=5)
        print(f"✅ Server is running: {response.json()}")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return
    
    # Test Traditional Chinese
    traditional_text = "繁體中文測試：謝謝光臨！"
    
    payload = {
        "text": traditional_text,
        "api_key": "hk_savor_spoon_2024"
    }
    
    try:
        response = requests.post("http://localhost:5000/print", json=payload, timeout=10)
        print(f"✅ Print response: {response.json()}")
    except Exception as e:
        print(f"❌ Print failed: {e}")

if __name__ == "__main__":
    main()
