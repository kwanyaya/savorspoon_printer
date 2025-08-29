#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HK Savor Spoon - DDNS Setup and Configuration Tool
幫助設置動態 DNS 服務，解決動態 IP 問題
"""

import requests
import json
import time
import socket
import subprocess
import platform
from datetime import datetime

class DDNSHelper:
    """DDNS 設置和監控工具"""
    
    def __init__(self):
        self.current_ip = None
        self.ddns_config = self.load_ddns_config()
    
    def load_ddns_config(self):
        """載入 DDNS 配置"""
        try:
            with open('ddns_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "service_provider": "",
                "domain_name": "",
                "username": "",
                "password": "",
                "update_interval": 300,  # 5分鐘檢查一次
                "last_update": "",
                "enabled": False
            }
    
    def save_ddns_config(self):
        """保存 DDNS 配置"""
        with open('ddns_config.json', 'w', encoding='utf-8') as f:
            json.dump(self.ddns_config, f, indent=2, ensure_ascii=False)
    
    def get_public_ip(self):
        """獲取當前公網 IP"""
        ip_services = [
            "https://api.ipify.org",
            "https://icanhazip.com",
            "https://ipecho.net/plain",
            "https://myexternalip.com/raw"
        ]
        
        for service in ip_services:
            try:
                response = requests.get(service, timeout=10)
                if response.status_code == 200:
                    ip = response.text.strip()
                    print(f"✅ 當前公網 IP: {ip}")
                    return ip
            except Exception as e:
                print(f"⚠️ 服務 {service} 無法訪問: {e}")
                continue
        
        print("❌ 無法獲取公網 IP 地址")
        return None
    
    def check_ddns_providers(self):
        """顯示支持的 DDNS 服務商"""
        providers = {
            "No-IP": {
                "網站": "https://www.noip.com",
                "免費方案": "是 (最多3個主機名)",
                "更新API": "支持",
                "特色": "老牌服務，穩定可靠"
            },
            "DuckDNS": {
                "網站": "https://www.duckdns.org", 
                "免費方案": "是 (無限制)",
                "更新API": "支持",
                "特色": "完全免費，簡單易用"
            },
            "Dynu": {
                "網站": "https://www.dynu.com",
                "免費方案": "是 (最多4個主機名)",
                "更新API": "支持", 
                "特色": "功能豐富，支持多種記錄類型"
            },
            "FreeDNS": {
                "網站": "https://freedns.afraid.org",
                "免費方案": "是",
                "更新API": "支持",
                "特色": "社群驅動，域名選擇多"
            }
        }
        
        print("\n🌐 推薦的 DDNS 服務商:")
        print("=" * 60)
        
        for name, info in providers.items():
            print(f"\n📍 {name}")
            for key, value in info.items():
                print(f"   {key}: {value}")
    
    def setup_ddns_config(self):
        """互動式 DDNS 配置設置"""
        print("\n🔧 DDNS 配置設置")
        print("=" * 40)
        
        self.check_ddns_providers()
        
        print("\n請按照以下步驟配置 DDNS:")
        print("1. 選擇一個 DDNS 服務商並註冊帳號")
        print("2. 創建您的域名 (例如: hksavorspoon.ddns.net)")
        print("3. 輸入以下信息:")
        
        # 獲取用戶輸入
        service = input("\n服務商 (no-ip/duckdns/dynu/freedns): ").lower().strip()
        domain = input("您的 DDNS 域名 (例如: hksavorspoon.ddns.net): ").strip()
        username = input("用戶名: ").strip()
        password = input("密碼: ").strip()
        
        # 保存配置
        self.ddns_config.update({
            "service_provider": service,
            "domain_name": domain,
            "username": username,
            "password": password,
            "enabled": True,
            "last_update": datetime.now().isoformat()
        })
        
        self.save_ddns_config()
        print(f"\n✅ DDNS 配置已保存!")
        print(f"📋 域名: {domain}")
        print(f"🔧 服務商: {service}")
        
        return True
    
    def update_duckdns(self, domain, token, ip):
        """更新 DuckDNS"""
        url = f"https://www.duckdns.org/update?domains={domain}&token={token}&ip={ip}"
        response = requests.get(url)
        return response.text.strip() == "OK"
    
    def update_noip(self, hostname, username, password, ip):
        """更新 No-IP"""
        url = f"https://dynupdate.no-ip.com/nic/update?hostname={hostname}&myip={ip}"
        response = requests.get(url, auth=(username, password))
        return "good" in response.text or "nochg" in response.text
    
    def update_ddns(self):
        """更新 DDNS 記錄"""
        if not self.ddns_config.get("enabled"):
            print("❌ DDNS 未啟用")
            return False
        
        current_ip = self.get_public_ip()
        if not current_ip:
            return False
        
        # 檢查 IP 是否變化
        if current_ip == self.current_ip:
            print("ℹ️ IP 地址沒有變化，無需更新")
            return True
        
        service = self.ddns_config.get("service_provider", "").lower()
        domain = self.ddns_config.get("domain_name", "")
        username = self.ddns_config.get("username", "")
        password = self.ddns_config.get("password", "")
        
        print(f"🔄 正在更新 DDNS 記錄...")
        print(f"   域名: {domain}")
        print(f"   新 IP: {current_ip}")
        
        success = False
        
        try:
            if service == "duckdns":
                # DuckDNS 使用 token 而不是密碼
                success = self.update_duckdns(domain.split('.')[0], password, current_ip)
            elif service == "no-ip" or service == "noip":
                success = self.update_noip(domain, username, password, current_ip)
            elif service == "dynu":
                # Dynu API 調用
                url = f"https://api.dynu.com/nic/update?hostname={domain}&myip={current_ip}"
                response = requests.get(url, auth=(username, password))
                success = "good" in response.text or "nochg" in response.text
            else:
                print(f"❌ 不支持的服務商: {service}")
                return False
            
            if success:
                self.current_ip = current_ip
                self.ddns_config["last_update"] = datetime.now().isoformat()
                self.save_ddns_config()
                print(f"✅ DDNS 更新成功!")
                print(f"🌐 您的打印服務器現在可以通過以下地址訪問:")
                print(f"   http://{domain}:5000/status")
                return True
            else:
                print(f"❌ DDNS 更新失敗")
                return False
                
        except Exception as e:
            print(f"❌ DDNS 更新出錯: {e}")
            return False
    
    def test_ddns_access(self):
        """測試 DDNS 域名訪問"""
        domain = self.ddns_config.get("domain_name", "")
        if not domain:
            print("❌ 未配置 DDNS 域名")
            return False
        
        print(f"\n🧪 測試 DDNS 訪問: {domain}")
        print("=" * 40)
        
        # 測試域名解析
        try:
            ip = socket.gethostbyname(domain)
            print(f"✅ 域名解析成功: {domain} -> {ip}")
        except Exception as e:
            print(f"❌ 域名解析失敗: {e}")
            return False
        
        # 測試打印服務器訪問
        try:
            response = requests.get(f"http://{domain}:5000/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 打印服務器訪問成功!")
                print(f"   服務器: {data.get('computer', 'Unknown')}")
                print(f"   打印機: {data.get('default_printer', 'None')}")
                return True
            else:
                print(f"❌ 打印服務器響應錯誤: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 無法訪問打印服務器: {e}")
            print("💡 請檢查:")
            print("   1. 打印服務器是否正在運行")
            print("   2. 路由器端口轉發是否配置正確")
            print("   3. 防火牆設置")
            return False
    
    def generate_laravel_config(self):
        """生成 Laravel 配置代碼"""
        domain = self.ddns_config.get("domain_name", "")
        if not domain:
            print("❌ 未配置 DDNS 域名")
            return
        
        print(f"\n📋 Laravel 配置代碼")
        print("=" * 40)
        print("將以下代碼添加到您的 Laravel .env 文件:")
        print()
        print(f"# HK Savor Spoon 打印服務器配置 (DDNS)")
        print(f"WINDOWS_PRINT_SERVER_URL=http://{domain}:5000")
        print(f"WINDOWS_PRINT_SERVER_API_KEY=hksavorspoon-secure-print-key-2025")
        print()
        print("PHP 使用示例:")
        print(f"""
// 測試連接
$response = Http::get(env('WINDOWS_PRINT_SERVER_URL') . '/status');

// 發送打印
$response = Http::withHeaders([
    'X-API-Key' => env('WINDOWS_PRINT_SERVER_API_KEY'),
    'Content-Type' => 'application/json'
])->post(env('WINDOWS_PRINT_SERVER_URL') . '/print', [
    'text' => '測試打印內容',
    'job_name' => 'Test Print'
]);
""")
    
    def monitor_ddns(self):
        """持續監控 DDNS 狀態"""
        print("\n🔍 開始 DDNS 監控...")
        print("按 Ctrl+C 停止監控")
        print("=" * 40)
        
        try:
            while True:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n[{current_time}] 檢查 DDNS 狀態...")
                
                self.update_ddns()
                
                interval = self.ddns_config.get("update_interval", 300)
                print(f"⏰ {interval} 秒後再次檢查...")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 DDNS 監控已停止")

def main():
    """主函數"""
    print("🌐 HK Savor Spoon - DDNS 配置工具")
    print("解決動態 IP 問題，實現穩定的遠程打印")
    print("=" * 50)
    
    helper = DDNSHelper()
    
    while True:
        print("\n📋 請選擇操作:")
        print("1. 查看支持的 DDNS 服務商")
        print("2. 配置 DDNS 設置")
        print("3. 手動更新 DDNS")
        print("4. 測試 DDNS 訪問")
        print("5. 生成 Laravel 配置")
        print("6. 開始 DDNS 監控")
        print("7. 查看當前配置")
        print("0. 退出")
        
        choice = input("\n請輸入選項 (0-7): ").strip()
        
        if choice == "1":
            helper.check_ddns_providers()
        elif choice == "2":
            helper.setup_ddns_config()
        elif choice == "3":
            helper.update_ddns()
        elif choice == "4":
            helper.test_ddns_access()
        elif choice == "5":
            helper.generate_laravel_config()
        elif choice == "6":
            helper.monitor_ddns()
        elif choice == "7":
            print(f"\n📋 當前 DDNS 配置:")
            config = helper.ddns_config
            print(f"   服務商: {config.get('service_provider', '未設置')}")
            print(f"   域名: {config.get('domain_name', '未設置')}")
            print(f"   用戶名: {config.get('username', '未設置')}")
            print(f"   狀態: {'啟用' if config.get('enabled') else '禁用'}")
            print(f"   最後更新: {config.get('last_update', '從未')}")
        elif choice == "0":
            print("👋 再見!")
            break
        else:
            print("❌ 無效選項，請重新選擇")

if __name__ == "__main__":
    main()
