#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick DuckDNS Test Tool
Test DuckDNS registration and domain creation
"""

import requests
import json

def test_duckdns_setup():
    """Test DuckDNS domain and token"""
    
    print("🦆 DuckDNS 快速測試工具")
    print("=" * 40)
    print("此工具幫助您測試 DuckDNS 設置是否正確")
    print()
    
    # Get user input
    domain = input("請輸入您的 DuckDNS 域名 (不含 .duckdns.org): ").strip()
    token = input("請輸入您的 DuckDNS Token: ").strip()
    
    if not domain or not token:
        print("❌ 域名和 Token 都是必需的")
        return False
    
    full_domain = f"{domain}.duckdns.org"
    print(f"\n🧪 測試域名: {full_domain}")
    
    # Test 1: Get current IP
    try:
        print("1️⃣ 獲取當前 IP...")
        ip_response = requests.get("https://api.ipify.org", timeout=10)
        current_ip = ip_response.text.strip()
        print(f"   當前 IP: {current_ip}")
    except Exception as e:
        print(f"❌ 無法獲取 IP: {e}")
        return False
    
    # Test 2: Update DuckDNS
    try:
        print("2️⃣ 測試 DuckDNS 更新...")
        update_url = f"https://www.duckdns.org/update?domains={domain}&token={token}&ip={current_ip}"
        response = requests.get(update_url, timeout=10)
        
        if response.text.strip() == "OK":
            print("✅ DuckDNS 更新成功!")
        else:
            print(f"❌ DuckDNS 更新失敗: {response.text}")
            print("💡 請檢查域名和 Token 是否正確")
            return False
            
    except Exception as e:
        print(f"❌ DuckDNS 更新出錯: {e}")
        return False
    
    # Test 3: Check domain resolution
    try:
        print("3️⃣ 測試域名解析...")
        import socket
        import time
        
        # Wait a bit for DNS to update
        print("   等待 DNS 更新 (10秒)...")
        time.sleep(10)
        
        resolved_ip = socket.gethostbyname(full_domain)
        print(f"   域名解析結果: {resolved_ip}")
        
        if resolved_ip == current_ip:
            print("✅ 域名解析正確!")
        else:
            print("⚠️ 域名解析的 IP 與當前 IP 不同")
            print("   這可能是正常的，DNS 需要時間同步")
            
    except Exception as e:
        print(f"⚠️ 域名解析測試: {e}")
        print("   這可能是正常的，DNS 需要時間同步")
    
    # Show configuration
    print(f"\n📋 您的 DuckDNS 配置:")
    print(f"   域名: {full_domain}")
    print(f"   Token: {token[:8]}...")
    print(f"   更新 URL: https://www.duckdns.org/update?domains={domain}&token={token}&ip=")
    
    print(f"\n🎯 下一步:")
    print(f"1. 在路由器中配置 DDNS:")
    print(f"   - 主機名: {full_domain}")
    print(f"   - 密碼/Token: {token}")
    print(f"2. 運行完整設置: python ddns_helper.py")
    print(f"3. 在 Laravel 中使用: http://{full_domain}:5000")
    
    return True

def show_duckdns_registration_guide():
    """Show DuckDNS registration steps"""
    
    print("🦆 DuckDNS 註冊指南")
    print("=" * 40)
    print()
    print("📋 註冊步驟:")
    print("1. 訪問: https://www.duckdns.org")
    print("2. 點擊 'sign in with' 並選擇:")
    print("   - Google (推薦)")
    print("   - GitHub")  
    print("   - Reddit")
    print("   - Twitter")
    print("3. 登入後創建您的域名:")
    print("   - 輸入: hksavorspoon (或您喜歡的名稱)")
    print("   - 點擊 'add domain'")
    print("4. 記下您的 Token (這是您的密碼)")
    print()
    print("✅ 完全免費，無需信用卡，立即可用!")
    print()

if __name__ == "__main__":
    while True:
        print("\n🦆 DuckDNS 設置助手")
        print("=" * 30)
        print("1. 查看註冊指南")
        print("2. 測試 DuckDNS 設置")  
        print("0. 退出")
        
        choice = input("\n請選擇 (0-2): ").strip()
        
        if choice == "1":
            show_duckdns_registration_guide()
        elif choice == "2":
            test_duckdns_setup()
        elif choice == "0":
            print("👋 再見!")
            break
        else:
            print("❌ 無效選項")
