#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Star TSP100 Driver and Configuration Checker
Helps diagnose and fix Chinese character printing issues
"""

import win32print
import win32api
import subprocess
import sys

def check_printer_driver():
    """Check Star TSP100 driver information"""
    print("🔍 Checking Star TSP100 Driver Configuration")
    print("=" * 50)
    
    try:
        # Get default printer
        default_printer = win32print.GetDefaultPrinter()
        print(f"Default Printer: {default_printer}")
        
        # Get printer driver info
        printer_info = win32print.GetPrinter(win32print.OpenPrinter(default_printer), 2)
        
        print(f"\nPrinter Details:")
        print(f"  Name: {printer_info.get('pPrinterName', 'Unknown')}")
        print(f"  Driver: {printer_info.get('pDriverName', 'Unknown')}")
        print(f"  Port: {printer_info.get('pPortName', 'Unknown')}")
        print(f"  Print Processor: {printer_info.get('pPrintProcessor', 'Unknown')}")
        print(f"  Datatype: {printer_info.get('pDatatype', 'Unknown')}")
        
        # Check if it's a Star printer
        is_star = "star" in default_printer.lower()
        is_tsp100 = "tsp" in default_printer.lower()
        
        print(f"\nStar TSP100 Detection:")
        print(f"  Is Star Printer: {'✅ Yes' if is_star else '❌ No'}")
        print(f"  Is TSP Series: {'✅ Yes' if is_tsp100 else '❌ No'}")
        
        return printer_info, is_star and is_tsp100
        
    except Exception as e:
        print(f"❌ Error checking printer: {e}")
        return None, False

def check_available_drivers():
    """List available Star printer drivers"""
    print("\n🔍 Checking Available Star Drivers")
    print("=" * 50)
    
    try:
        # Get all printer drivers
        drivers = win32print.EnumPrinterDrivers(None, None, 2)
        
        star_drivers = []
        for driver in drivers:
            driver_name = driver.get('Name', '')
            if 'star' in driver_name.lower():
                star_drivers.append(driver_name)
                print(f"✅ Found: {driver_name}")
        
        if not star_drivers:
            print("❌ No Star printer drivers found!")
            print("\n💡 Recommended Actions:")
            print("1. Download latest Star TSP100 drivers from Star website")
            print("2. Install Universal Star Printer Driver")
            print("3. Use Star CloudPRNT driver for better Unicode support")
        
        return star_drivers
        
    except Exception as e:
        print(f"❌ Error listing drivers: {e}")
        return []

def test_raw_printing():
    """Test direct RAW printing to bypass driver issues"""
    print("\n🧪 Testing RAW Printing (Bypass Driver)")
    print("=" * 50)
    
    try:
        default_printer = win32print.GetDefaultPrinter()
        
        # Test simple Chinese text with ESC/POS commands
        chinese_test = "测试中文 Test Chinese 港式茶餐廳"
        
        # ESC/POS commands for Chinese
        commands = bytearray()
        commands.extend(b'\x1B\x40')  # Initialize
        commands.extend(b'\x1C\x43\x02')  # Chinese mode
        
        # Try different encodings
        encodings_to_test = ['gbk', 'gb2312', 'big5', 'utf-8']
        
        for encoding in encodings_to_test:
            try:
                print(f"Testing {encoding} encoding...")
                
                if encoding == 'utf-8':
                    text_bytes = chinese_test.encode('utf-8')
                elif encoding == 'gbk':
                    text_bytes = chinese_test.encode('gbk', errors='replace')
                elif encoding == 'gb2312':
                    text_bytes = chinese_test.encode('gb2312', errors='replace')
                elif encoding == 'big5':
                    text_bytes = chinese_test.encode('big5', errors='replace')
                
                full_command = commands + text_bytes + b'\x0A\x0A'
                
                # Send to printer
                printer_handle = win32print.OpenPrinter(default_printer)
                doc_info = (f"Test {encoding}", None, "RAW")
                job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
                win32print.StartPagePrinter(printer_handle)
                win32print.WritePrinter(printer_handle, bytes(full_command))
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                win32print.ClosePrinter(printer_handle)
                
                print(f"  ✅ {encoding} test sent to printer")
                
            except Exception as e:
                print(f"  ❌ {encoding} failed: {e}")
        
        print("\n📄 Check your printer - one of these encodings should show clear Chinese!")
        
    except Exception as e:
        print(f"❌ RAW printing test failed: {e}")

def get_driver_recommendations():
    """Provide driver recommendations for Star TSP100"""
    print("\n💡 Star TSP100 Driver Recommendations")
    print("=" * 50)
    
    print("For Chinese character support, you need:")
    print("\n1. 🌟 BEST OPTION: Star CloudPRNT Driver")
    print("   - Download from: https://www.star-m.jp/products/s_print/CloudPRNTSDK/")
    print("   - Supports Unicode/UTF-8 natively")
    print("   - Best Chinese character support")
    
    print("\n2. ✅ GOOD OPTION: Star TSP100 Universal Driver")
    print("   - Download from Star Micronics website")
    print("   - Look for 'TSP100 Windows Driver'")
    print("   - Make sure to get the latest version")
    
    print("\n3. ⚠️ CURRENT ISSUE:")
    print("   - Your current driver may not support Chinese properly")
    print("   - Generic Windows drivers often can't handle Chinese")
    print("   - Star printers need specific drivers for Asian languages")
    
    print("\n🔧 Installation Steps:")
    print("1. Uninstall current printer")
    print("2. Download new Star driver")
    print("3. Install with Administrator rights")
    print("4. Set printer as default")
    print("5. Test Chinese printing again")

def create_driver_fix_script():
    """Create a PowerShell script to help fix driver issues"""
    
    script_content = '''# Star TSP100 Driver Fix Script
# Run this as Administrator to help resolve Chinese printing issues

Write-Host "Star TSP100 Driver Diagnostic and Fix" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check current printer
$defaultPrinter = Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Default=True"
Write-Host "`nCurrent Default Printer:" -ForegroundColor Yellow
Write-Host "Name: $($defaultPrinter.Name)"
Write-Host "Driver: $($defaultPrinter.DriverName)"
Write-Host "Port: $($defaultPrinter.PortName)"

# Check for Star drivers
Write-Host "`nChecking for Star Drivers..." -ForegroundColor Yellow
$printerDrivers = Get-WmiObject -Class Win32_PrinterDriver | Where-Object { $_.Name -like "*Star*" }

if ($printerDrivers) {
    Write-Host "Found Star Drivers:" -ForegroundColor Green
    foreach ($driver in $printerDrivers) {
        Write-Host "  - $($driver.Name)" -ForegroundColor White
    }
} else {
    Write-Host "No Star drivers found!" -ForegroundColor Red
    Write-Host "You need to install Star TSP100 drivers for Chinese support" -ForegroundColor Yellow
}

# Printer settings recommendations
Write-Host "`nRecommended Settings:" -ForegroundColor Yellow
Write-Host "1. Download Star CloudPRNT or TSP100 Universal Driver"
Write-Host "2. Set Data Type to 'RAW' for direct ESC/POS commands"
Write-Host "3. Enable 'Print directly to printer' in Advanced settings"
Write-Host "4. Set Character Set to 'Chinese Simplified' or 'Chinese Traditional'"

# Open printer settings
Write-Host "`nOpening Printer Settings..." -ForegroundColor Yellow
Start-Process "ms-settings:printers"

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Remove current printer if Chinese doesn't work"
Write-Host "2. Add printer again with proper Star driver"
Write-Host "3. Configure for Chinese character support"
Write-Host "4. Test printing again"

Read-Host "`nPress Enter to continue"
'''
    
    with open('fix_star_driver.ps1', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"\n📝 Created 'fix_star_driver.ps1'")
    print("Run this PowerShell script as Administrator to help fix driver issues")

def main():
    """Main diagnostic function"""
    print("🌟 Star TSP100 Chinese Character Diagnostic Tool")
    print("=" * 60)
    print("This tool will help identify and fix Chinese printing issues")
    print("=" * 60)
    
    # Check current driver
    printer_info, is_star_tsp = check_printer_driver()
    
    # Check available Star drivers
    star_drivers = check_available_drivers()
    
    # Test RAW printing
    print(f"\n{'='*50}")
    user_input = input("Do you want to test RAW printing (bypass driver)? (y/n): ")
    if user_input.lower() == 'y':
        test_raw_printing()
    
    # Provide recommendations
    get_driver_recommendations()
    
    # Create fix script
    create_driver_fix_script()
    
    print(f"\n{'='*60}")
    print("🎯 SUMMARY:")
    
    if not is_star_tsp:
        print("❌ Printer detection issue - make sure Star TSP100 is default")
    
    if not star_drivers:
        print("❌ No Star drivers found - you need proper Star TSP100 drivers")
        print("🔗 Download from: https://www.star-m.jp/")
    else:
        print("✅ Star drivers found - but may need configuration for Chinese")
    
    print("\n💡 RECOMMENDED SOLUTION:")
    print("1. Download Star CloudPRNT driver (best for Chinese)")
    print("2. Uninstall current printer")
    print("3. Install with new driver")
    print("4. Configure for Chinese character set")
    print("5. Test printing again")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit")
'''

<function_calls>
<invoke name="create_file">
<parameter name="content">#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Star TSP100 Driver and Configuration Checker
Helps diagnose and fix Chinese character printing issues
"""

import win32print
import win32api
import subprocess
import sys

def check_printer_driver():
    """Check Star TSP100 driver information"""
    print("🔍 Checking Star TSP100 Driver Configuration")
    print("=" * 50)
    
    try:
        # Get default printer
        default_printer = win32print.GetDefaultPrinter()
        print(f"Default Printer: {default_printer}")
        
        # Get printer driver info
        printer_info = win32print.GetPrinter(win32print.OpenPrinter(default_printer), 2)
        
        print(f"\nPrinter Details:")
        print(f"  Name: {printer_info.get('pPrinterName', 'Unknown')}")
        print(f"  Driver: {printer_info.get('pDriverName', 'Unknown')}")
        print(f"  Port: {printer_info.get('pPortName', 'Unknown')}")
        print(f"  Print Processor: {printer_info.get('pPrintProcessor', 'Unknown')}")
        print(f"  Datatype: {printer_info.get('pDatatype', 'Unknown')}")
        
        # Check if it's a Star printer
        is_star = "star" in default_printer.lower()
        is_tsp100 = "tsp" in default_printer.lower()
        
        print(f"\nStar TSP100 Detection:")
        print(f"  Is Star Printer: {'✅ Yes' if is_star else '❌ No'}")
        print(f"  Is TSP Series: {'✅ Yes' if is_tsp100 else '❌ No'}")
        
        return printer_info, is_star and is_tsp100
        
    except Exception as e:
        print(f"❌ Error checking printer: {e}")
        return None, False

def check_available_drivers():
    """List available Star printer drivers"""
    print("\n🔍 Checking Available Star Drivers")
    print("=" * 50)
    
    try:
        # Get all printer drivers
        drivers = win32print.EnumPrinterDrivers(None, None, 2)
        
        star_drivers = []
        for driver in drivers:
            driver_name = driver.get('Name', '')
            if 'star' in driver_name.lower():
                star_drivers.append(driver_name)
                print(f"✅ Found: {driver_name}")
        
        if not star_drivers:
            print("❌ No Star printer drivers found!")
            print("\n💡 Recommended Actions:")
            print("1. Download latest Star TSP100 drivers from Star website")
            print("2. Install Universal Star Printer Driver")
            print("3. Use Star CloudPRNT driver for better Unicode support")
        
        return star_drivers
        
    except Exception as e:
        print(f"❌ Error listing drivers: {e}")
        return []

def test_raw_printing():
    """Test direct RAW printing to bypass driver issues"""
    print("\n🧪 Testing RAW Printing (Bypass Driver)")
    print("=" * 50)
    
    try:
        default_printer = win32print.GetDefaultPrinter()
        
        # Test simple Chinese text with ESC/POS commands
        chinese_test = "测试中文 Test Chinese 港式茶餐廳"
        
        # ESC/POS commands for Chinese
        commands = bytearray()
        commands.extend(b'\x1B\x40')  # Initialize
        commands.extend(b'\x1C\x43\x02')  # Chinese mode
        
        # Try different encodings
        encodings_to_test = ['gbk', 'gb2312', 'big5', 'utf-8']
        
        for encoding in encodings_to_test:
            try:
                print(f"Testing {encoding} encoding...")
                
                if encoding == 'utf-8':
                    text_bytes = chinese_test.encode('utf-8')
                elif encoding == 'gbk':
                    text_bytes = chinese_test.encode('gbk', errors='replace')
                elif encoding == 'gb2312':
                    text_bytes = chinese_test.encode('gb2312', errors='replace')
                elif encoding == 'big5':
                    text_bytes = chinese_test.encode('big5', errors='replace')
                
                full_command = commands + text_bytes + b'\x0A\x0A'
                
                # Send to printer
                printer_handle = win32print.OpenPrinter(default_printer)
                doc_info = (f"Test {encoding}", None, "RAW")
                job_id = win32print.StartDocPrinter(printer_handle, 1, doc_info)
                win32print.StartPagePrinter(printer_handle)
                win32print.WritePrinter(printer_handle, bytes(full_command))
                win32print.EndPagePrinter(printer_handle)
                win32print.EndDocPrinter(printer_handle)
                win32print.ClosePrinter(printer_handle)
                
                print(f"  ✅ {encoding} test sent to printer")
                
            except Exception as e:
                print(f"  ❌ {encoding} failed: {e}")
        
        print("\n📄 Check your printer - one of these encodings should show clear Chinese!")
        
    except Exception as e:
        print(f"❌ RAW printing test failed: {e}")

def get_driver_recommendations():
    """Provide driver recommendations for Star TSP100"""
    print("\n💡 Star TSP100 Driver Recommendations")
    print("=" * 50)
    
    print("For Chinese character support, you need:")
    print("\n1. 🌟 BEST OPTION: Star CloudPRNT Driver")
    print("   - Download from: https://www.star-m.jp/products/s_print/CloudPRNTSDK/")
    print("   - Supports Unicode/UTF-8 natively")
    print("   - Best Chinese character support")
    
    print("\n2. ✅ GOOD OPTION: Star TSP100 Universal Driver")
    print("   - Download from Star Micronics website")
    print("   - Look for 'TSP100 Windows Driver'")
    print("   - Make sure to get the latest version")
    
    print("\n3. ⚠️ CURRENT ISSUE:")
    print("   - Your current driver may not support Chinese properly")
    print("   - Generic Windows drivers often can't handle Chinese")
    print("   - Star printers need specific drivers for Asian languages")
    
    print("\n🔧 Installation Steps:")
    print("1. Uninstall current printer")
    print("2. Download new Star driver")
    print("3. Install with Administrator rights")
    print("4. Set printer as default")
    print("5. Test Chinese printing again")

def main():
    """Main diagnostic function"""
    print("🌟 Star TSP100 Chinese Character Diagnostic Tool")
    print("=" * 60)
    print("This tool will help identify and fix Chinese printing issues")
    print("=" * 60)
    
    # Check current driver
    printer_info, is_star_tsp = check_printer_driver()
    
    # Check available Star drivers
    star_drivers = check_available_drivers()
    
    # Test RAW printing
    print(f"\n{'='*50}")
    user_input = input("Do you want to test RAW printing (bypass driver)? (y/n): ")
    if user_input.lower() == 'y':
        test_raw_printing()
    
    # Provide recommendations
    get_driver_recommendations()
    
    print(f"\n{'='*60}")
    print("🎯 SUMMARY:")
    
    if not is_star_tsp:
        print("❌ Printer detection issue - make sure Star TSP100 is default")
    
    if not star_drivers:
        print("❌ No Star drivers found - you need proper Star TSP100 drivers")
        print("🔗 Download from: https://www.star-m.jp/")
    else:
        print("✅ Star drivers found - but may need configuration for Chinese")
    
    print("\n💡 RECOMMENDED SOLUTION:")
    print("1. Download Star CloudPRNT driver (best for Chinese)")
    print("2. Uninstall current printer")
    print("3. Install with new driver")
    print("4. Configure for Chinese character set")
    print("5. Test printing again")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit")
