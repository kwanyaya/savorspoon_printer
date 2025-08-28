#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Star TSP100 Traditional Chinese Fix
Configures printer to support both Simplified AND Traditional Chinese
"""

import win32print
import requests
import time

def configure_traditional_chinese():
    """Configure Star TSP100 for Traditional Chinese (Big5) support"""
    
    print("🇹🇼 Configuring Star TSP100 for Traditional Chinese")
    print("=" * 60)
    
    try:
        default_printer = win32print.GetDefaultPrinter()
        print(f"Configuring: {default_printer}")
        
        # Traditional Chinese configuration commands
        config_sets = [
            {
                "name": "Big5 Traditional Chinese",
                "commands": b'\x1B\x40\x1B\x74\x0E\x1B\x52\x0F',  # Init + Big5 + Traditional charset
                "test_text": "繁體中文測試 港式美味湯匙"
            },
            {
                "name": "Unicode Traditional Chinese", 
                "commands": b'\x1B\x40\x1C\x2E\x1B\x74\x00',  # Init + Unicode + Default table
                "test_text": "繁體中文測試 港式美味湯匙"
            },
            {
                "name": "Extended Character Set",
                "commands": b'\x1B\x40\x1B\x74\x10\x1C\x43\x01',  # Init + Extended table + Traditional mode
                "test_text": "繁體中文測試 港式美味湯匙"
            }
        ]
        
        for i, config in enumerate(config_sets, 1):
            print(f"\n{i}. Testing {config['name']}...")
            
            try:
                # Open printer
                printer_handle = win32print.OpenPrinter(default_printer)
                doc_info = (f"Traditional Chinese Test {i}", None, "RAW")
                job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
                win32print.StartPagePrinter(printer_handle)
                
                # Prepare commands
                commands = bytearray()
                commands.extend(config['commands'])
                
                # Add test header
                header = f"Test {i}: {config['name']}\n".encode('ascii')
                commands.extend(header)
                
                # Encode text with Big5 for Traditional Chinese
                try:
                    text_big5 = config['test_text'].encode('big5', errors='replace')
                    commands.extend(text_big5)
                except:
                    # Fallback to UTF-8
                    text_utf8 = config['test_text'].encode('utf-8', errors='replace')
                    commands.extend(text_utf8)
                
                commands.extend(b'\x0A\x0A')  # Line feeds
                
                # Send to printer
                win32print.WritePrinter(printer_handle, bytes(commands))
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                win32print.ClosePrinter(printer_handle)
                
                print(f"   ✅ {config['name']} configuration sent")
                time.sleep(1)  # Small delay between tests
                
            except Exception as e:
                print(f"   ❌ {config['name']} failed: {e}")
        
        print(f"\n{'='*60}")
        print("📄 CHECK YOUR PRINTER OUTPUT!")
        print("Look for the test that shows clear Traditional Chinese: 繁體中文測試")
        print("That configuration works best for Traditional Chinese")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def test_mixed_chinese():
    """Test mixed Simplified and Traditional Chinese"""
    
    print("\n🔀 Testing Mixed Chinese Character Support")
    print("=" * 60)
    
    # Mixed Chinese test cases
    test_cases = [
        {
            "name": "HK Style Mixed (Big5)",
            "encoding": "big5",
            "charset_cmd": b'\x1B\x40\x1B\x74\x0E',  # Big5 charset
            "text": """
================================
       港式美味湯匙
       HK SAVOR SPOON  
================================
訂單編號: 港001 (繁體)
客戶姓名: 陳小明 (繁體)
--------------------------------
菜品明細 (繁體):
白切雞飯 x2 (繁體)
雲吞湯 x1 (繁體) 
港式奶茶 x2 (繁體)
--------------------------------
謝謝惠顧！(繁體)
歡迎再次光臨 (繁體)
================================
"""
        },
        {
            "name": "Simplified Chinese (GB2312)",
            "encoding": "gb2312", 
            "charset_cmd": b'\x1B\x40\x1B\x74\x0F',  # GB2312 charset
            "text": """
================================
       港式美味汤匙
       HK SAVOR SPOON  
================================
订单编号: 简001 (简体)
客户姓名: 李小红 (简体)
--------------------------------
菜品明细 (简体):
白切鸡饭 x2 (简体)
云吞汤 x1 (简体)
港式奶茶 x2 (简体)  
--------------------------------
谢谢惠顾！(简体)
欢迎再次光临 (简体)
================================
"""
        }
    ]
    
    try:
        default_printer = win32print.GetDefaultPrinter()
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{i}. Testing {test['name']}...")
            
            try:
                printer_handle = win32print.OpenPrinter(default_printer)
                doc_info = (f"Mixed Chinese Test {i}", None, "RAW")
                job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
                win32print.StartPagePrinter(printer_handle)
                
                # Prepare commands
                commands = bytearray()
                commands.extend(test['charset_cmd'])
                
                # Encode with appropriate encoding
                try:
                    if test['encoding'] == 'big5':
                        text_encoded = test['text'].encode('big5', errors='replace')
                    elif test['encoding'] == 'gb2312':
                        text_encoded = test['text'].encode('gb2312', errors='replace')
                    else:
                        text_encoded = test['text'].encode('utf-8', errors='replace')
                    
                    commands.extend(text_encoded)
                    commands.extend(b'\x0A\x0A\x1B\x64\x03')  # Line feeds + cut
                    
                    win32print.WritePrinter(printer_handle, bytes(commands))
                    
                except Exception as encoding_error:
                    print(f"   ❌ Encoding error: {encoding_error}")
                    continue
                
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                win32print.ClosePrinter(printer_handle)
                
                print(f"   ✅ {test['name']} sent to printer")
                time.sleep(2)  # Delay between tests
                
            except Exception as e:
                print(f"   ❌ {test['name']} failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mixed Chinese test failed: {e}")
        return False

def update_print_server_for_traditional():
    """Test the updated print server with Traditional Chinese"""
    
    print("\n🔄 Testing Print Server with Traditional Chinese")
    print("=" * 60)
    
    try:
        # Test server connection
        response = requests.get("http://localhost:5000/status", timeout=5)
        if response.status_code != 200:
            print("❌ Print server not running")
            return False
        
        print("✅ Print server is running")
        
        # Test Traditional Chinese through server
        headers = {
            "X-API-Key": "hksavorspoon-secure-print-key-2025",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        traditional_test = {
            "text": """
================================
       港式美味湯匙 (繁體)
       HK SAVOR SPOON  
================================
訂單編號: 繁001
客戶姓名: 陳小明
日期時間: 2025-08-26 20:30:00
--------------------------------

菜品明細 (繁體中文):
白切雞飯 x2
  單價: $15.50 = $31.00

雲吞湯 x1  
  單價: $8.00 = $8.00

港式奶茶 x2
  單價: $4.50 = $9.00

--------------------------------
小計: $48.00
總計: $48.00
付款方式: 現金
--------------------------------

謝謝惠顧！(繁體)
歡迎再次光臨港式美味湯匙
hksavorspoon.com

================================
""",
            "job_name": "繁體中文測試"
        }
        
        print("Sending Traditional Chinese test to server...")
        response = requests.post(
            "http://localhost:5000/print",
            headers=headers,
            json=traditional_test,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Traditional Chinese test sent!")
            print(f"   Message: {result.get('message', 'Success')}")
            return True
        else:
            print(f"❌ Server test failed: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Server test error: {e}")
        return False

def main():
    """Main Traditional Chinese fix tool"""
    
    print("🇹🇼 Star TSP100 Traditional Chinese Fix Tool")
    print("=" * 70)
    print("Problem: Simplified Chinese (簡體) works, Traditional (繁體) doesn't")
    print("Solution: Configure Big5 encoding and Traditional Chinese charset")
    print("=" * 70)
    
    print("\n🔍 ISSUE ANALYSIS:")
    print("• Your printer charset is set to 簡體中文 (Simplified Chinese)")
    print("• This uses GB2312/GBK encoding")
    print("• Traditional Chinese needs Big5 encoding or Unicode")
    print("• We need to enable Traditional Chinese character support")
    
    try:
        # Step 1: Configure Traditional Chinese
        print(f"\n{'='*50}")
        print("STEP 1: Configure Traditional Chinese Support")
        configure_traditional_chinese()
        
        # Step 2: Test mixed Chinese
        print(f"\n{'='*50}")
        print("STEP 2: Test Mixed Chinese Characters")
        test_mixed_chinese()
        
        # Step 3: Test through print server
        print(f"\n{'='*50}")
        print("STEP 3: Test Print Server")
        update_print_server_for_traditional()
        
        print(f"\n{'='*70}")
        print("🎯 NEXT STEPS:")
        print("1. Check printed output for clear Traditional Chinese")
        print("2. If Traditional Chinese is clear, your printer now supports both!")
        print("3. Test your web interface with Traditional Chinese text")
        print("4. Consider switching printer charset to 'Unicode' for full support")
        
        print(f"\n💡 PRINTER SETTINGS RECOMMENDATION:")
        print("• Current: 簡體中文 (works for Simplified)")
        print("• Better: Try switching to 'Unicode' or '繁體中文' if available")
        print("• Best: Use 'Multi-language' or 'International' if available")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
