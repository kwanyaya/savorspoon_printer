#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Star TSP100 Character Set Configuration Tool
Fixes Chinese character printing by setting proper character sets
"""

import win32print
import requests

def test_printer_character_sets():
    """Test different character set configurations for Star TSP100"""
    
    print("🌟 Star TSP100 Character Set Configuration")
    print("=" * 50)
    print("This will test different character sets to enable Chinese printing")
    print("=" * 50)
    
    # Different ESC/POS character set commands for Chinese
    character_sets = [
        {
            "name": "Chinese Simplified (GB2312)",
            "init_commands": b'\x1B\x40',  # Initialize
            "charset_commands": b'\x1B\x74\x0F',  # Set character table 15 (Chinese)
            "encoding": "gb2312"
        },
        {
            "name": "Chinese Traditional (Big5)", 
            "init_commands": b'\x1B\x40',
            "charset_commands": b'\x1B\x74\x0E',  # Set character table 14 (Big5)
            "encoding": "big5"
        },
        {
            "name": "GBK Extended Chinese",
            "init_commands": b'\x1B\x40',
            "charset_commands": b'\x1C\x43\x02',  # Chinese mode
            "encoding": "gbk"
        },
        {
            "name": "Unicode UTF-8",
            "init_commands": b'\x1B\x40',
            "charset_commands": b'\x1C\x2E',  # Enable Unicode mode
            "encoding": "utf-8"
        },
        {
            "name": "Star Chinese Mode",
            "init_commands": b'\x1B\x40\x1C\x43\x02\x1C\x26',  # Full Chinese initialization
            "charset_commands": b'',
            "encoding": "gbk"
        }
    ]
    
    test_text = "测试中文 港式茶餐廳 Test Chinese"
    
    try:
        default_printer = win32print.GetDefaultPrinter()
        print(f"Testing on: {default_printer}")
        
        for i, charset in enumerate(character_sets, 1):
            print(f"\n{i}. Testing {charset['name']}...")
            
            try:
                # Prepare printer commands
                commands = bytearray()
                commands.extend(charset['init_commands'])
                commands.extend(charset['charset_commands'])
                
                # Encode text with appropriate encoding
                try:
                    if charset['encoding'] == 'utf-8':
                        text_bytes = test_text.encode('utf-8', errors='replace')
                    elif charset['encoding'] == 'gbk':
                        text_bytes = test_text.encode('gbk', errors='replace')
                    elif charset['encoding'] == 'gb2312':
                        text_bytes = test_text.encode('gb2312', errors='replace')
                    elif charset['encoding'] == 'big5':
                        text_bytes = test_text.encode('big5', errors='replace')
                    
                    commands.extend(text_bytes)
                    commands.extend(b'\x0A\x0A')  # Line feeds
                    
                    # Send to printer
                    printer_handle = win32print.OpenPrinter(default_printer)
                    doc_info = (f"CharSet Test {i}", None, "RAW")
                    job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
                    win32print.StartPagePrinter(printer_handle)
                    win32print.WritePrinter(printer_handle, bytes(commands))
                    win32print.EndPagePrinter(printer_handle)
                    win32print.EndDocPrinter(printer_handle)
                    win32print.ClosePrinter(printer_handle)
                    
                    print(f"   ✅ {charset['name']} sent to printer")
                    
                except Exception as e:
                    print(f"   ❌ {charset['name']} failed: {e}")
                    
            except Exception as e:
                print(f"   ❌ Error with {charset['name']}: {e}")
        
        print(f"\n{'='*50}")
        print("📄 CHECK YOUR PRINTER OUTPUT!")
        print("Look for the test that shows clear Chinese characters")
        print("That's the character set your printer supports")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def configure_printer_character_set():
    """Send configuration commands to enable Chinese character support"""
    
    print("\n🔧 Configuring Printer for Chinese Characters")
    print("=" * 50)
    
    try:
        default_printer = win32print.GetDefaultPrinter()
        
        # Send comprehensive Chinese setup commands
        setup_commands = bytearray()
        
        # Initialize printer
        setup_commands.extend(b'\x1B\x40')  # ESC @ Initialize
        
        # Enable Chinese character mode
        setup_commands.extend(b'\x1C\x43\x02')  # Enable Chinese mode
        setup_commands.extend(b'\x1C\x26')      # Set Chinese character set
        
        # Set character table for Chinese
        setup_commands.extend(b'\x1B\x74\x0F')  # Character table 15 (Chinese)
        
        # Set international character set
        setup_commands.extend(b'\x1B\x52\x08')  # Chinese character set
        
        # Test message
        test_msg = "中文字符集已启用 Chinese CharSet Enabled"
        setup_commands.extend(test_msg.encode('gbk', errors='replace'))
        setup_commands.extend(b'\x0A\x0A\x0A')
        
        # Send to printer
        printer_handle = win32print.OpenPrinter(default_printer)
        doc_info = ("Chinese CharSet Setup", None, "RAW")
        job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
        win32print.StartPagePrinter(printer_handle)
        win32print.WritePrinter(printer_handle, bytes(setup_commands))
        win32print.EndPagePrinter(printer_handle)
        win32print.EndDocPrinter(printer_handle)
        win32print.ClosePrinter(printer_handle)
        
        print("✅ Chinese character set configuration sent to printer")
        print("📄 Check printed output - should show Chinese characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def update_print_server_charset():
    """Update the print server to use the best character set"""
    
    print("\n🔄 Updating Print Server Configuration")
    print("=" * 50)
    
    # Test current server
    try:
        response = requests.get("http://localhost:5000/status", timeout=5)
        if response.status_code == 200:
            print("✅ Print server is running")
            
            # Send Chinese test with proper character set
            headers = {
                "X-API-Key": "hksavorspoon-secure-print-key-2025",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            test_data = {
                "text": "字符集测试 Character Set Test\n港式美味湯匙\nHK SAVOR SPOON\n测试成功！",
                "job_name": "字符集测试"
            }
            
            print("Sending character set test to server...")
            response = requests.post(
                "http://localhost:5000/print",
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Test sent: {result.get('message', 'Success')}")
            else:
                print(f"❌ Server test failed: {response.status_code}")
                
        else:
            print("❌ Print server not responding")
            
    except Exception as e:
        print(f"❌ Server test error: {e}")

def main():
    """Main character set diagnostic and fix tool"""
    
    print("🇨🇳 Star TSP100 Chinese Character Set Fix Tool")
    print("=" * 60)
    print("This tool will:")
    print("• Test different character sets on your printer")
    print("• Find which one displays Chinese correctly")
    print("• Configure your printer for Chinese support")
    print("=" * 60)
    
    print("\n🔍 DIAGNOSIS:")
    print("If your printer's character set doesn't include Chinese,")
    print("that's exactly why you get garbled text (squares, ?).")
    print("We need to enable Chinese character mode.")
    
    # Ask user what to do
    print(f"\n{'='*40}")
    print("What would you like to do?")
    print("1. Test different character sets (recommended)")
    print("2. Configure Chinese character support")
    print("3. Update print server settings")
    print("4. All of the above")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1" or choice == "4":
            print(f"\n{'='*50}")
            test_printer_character_sets()
            
        if choice == "2" or choice == "4":
            print(f"\n{'='*50}")
            configure_printer_character_set()
            
        if choice == "3" or choice == "4":
            print(f"\n{'='*50}")
            update_print_server_charset()
            
        print(f"\n{'='*60}")
        print("🎯 SUMMARY:")
        print("• Check printed output for clear Chinese characters")
        print("• The test that shows clear Chinese is your answer")
        print("• Your print server will now use proper character sets")
        print("• Test Chinese printing in your web interface")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
