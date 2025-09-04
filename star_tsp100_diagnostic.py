# -*- coding: utf-8 -*-
"""
Star TSP100 Silent Print Diagnostic
===================================
Jobs appear in queue but printer doesn't respond physically
"""

import win32print
import win32api
import time
import subprocess
import os

def diagnose_star_tsp100_issue():
    """Diagnose why Star TSP100 jobs complete in queue but don't print"""
    
    print("STAR TSP100 SILENT PRINT DIAGNOSTIC")
    print("="*50)
    
    printer_name = "Star TSP100 Cutter (TSP143)"
    
    # 1. Check printer driver and port
    print("\n1. PRINTER DRIVER AND PORT ANALYSIS:")
    try:
        handle = win32print.OpenPrinter(printer_name)
        info = win32print.GetPrinter(handle, 2)
        
        port = info['pPortName']
        driver = info['pDriverName']
        status = info['Status']
        
        print(f"   Printer Name: {info['pPrinterName']}")
        print(f"   Driver: {driver}")
        print(f"   Port: {port}")
        print(f"   Status: {status}")
        
        # Analyze port type
        if 'USB' in port.upper():
            print(f"   📌 USB CONNECTION DETECTED: {port}")
            print(f"      This is often the source of Star TSP100 issues!")
        
        win32print.ClosePrinter(handle)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Check Device Manager for printer issues
    print(f"\n2. DEVICE MANAGER CHECK:")
    print(f"   Please manually check Device Manager:")
    print(f"   - Open Device Manager (devmgmt.msc)")
    print(f"   - Look under 'Printers' or 'USB devices'")
    print(f"   - Check if Star TSP100 has yellow warning icon")
    print(f"   - If found, right-click → Update driver")
    
    # 3. Star TSP100 specific tests
    print(f"\n3. STAR TSP100 SPECIFIC TESTS:")
    
    # Test 1: Check if we can send ESC/POS commands directly
    print(f"   Testing direct ESC/POS communication...")
    try:
        handle = win32print.OpenPrinter(printer_name)
        
        # Try to send a simple initialization command
        doc_info = ("Star Test", None, "RAW")
        job_id = win32print.StartDocPrinter(handle, 1, doc_info)
        win32print.StartPagePrinter(handle)
        
        # Send Star TSP100 specific initialization
        init_commands = b'\x1B\x40'  # ESC @ (Initialize printer)
        init_commands += b'\x1B\x61\x01'  # ESC a 1 (Center align)
        init_commands += b'STAR TSP100 TEST\n'
        init_commands += b'\x1B\x64\x05'  # ESC d 5 (Feed 5 lines)
        init_commands += b'\x1D\x56\x00'  # GS V 0 (Cut paper)
        
        bytes_written = win32print.WritePrinter(handle, init_commands)
        print(f"   ✅ Sent {bytes_written} bytes to printer")
        
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print(f"   📋 Job ID {job_id} sent - Check if printer responds")
        
    except Exception as e:
        print(f"   ❌ Direct ESC/POS test failed: {e}")
    
    # 4. Power and connection test
    print(f"\n4. PHYSICAL PRINTER CHECKLIST:")
    print(f"   □ Printer power LED is ON (solid green)")
    print(f"   □ USB cable firmly connected to computer")
    print(f"   □ USB cable firmly connected to printer")
    print(f"   □ Try different USB port on computer")
    print(f"   □ Try different USB cable")
    print(f"   □ Thermal paper roll installed correctly")
    print(f"   □ Printer cover/lid is closed properly")
    print(f"   □ No error lights blinking on printer")
    
    # 5. Star-specific troubleshooting
    print(f"\n5. STAR TSP100 TROUBLESHOOTING:")
    print(f"   Common Star TSP100 Issues:")
    print(f"   ")
    print(f"   A. DRIVER ISSUES:")
    print(f"      - Download latest Star TSP100 driver from:")
    print(f"        https://www.star-m.jp/products/s_print/sdk/windows.html")
    print(f"      - Uninstall current driver completely")
    print(f"      - Install fresh Star driver")
    print(f"   ")
    print(f"   B. USB COMMUNICATION:")
    print(f"      - Star printers can be picky about USB ports")
    print(f"      - Try USB 2.0 port instead of USB 3.0")
    print(f"      - Avoid USB hubs - connect directly")
    print(f"   ")
    print(f"   C. PRINTER SETTINGS:")
    print(f"      - In printer properties, check 'Print directly to printer'")
    print(f"      - Disable 'Enable bidirectional support'")
    print(f"      - Set paper size to 'Roll Paper 80mm'")
    
    # 6. Manual test recommendation
    print(f"\n6. MANUAL TESTS TO TRY:")
    print(f"   ")
    print(f"   TEST 1 - Printer Self Test:")
    print(f"   - Turn OFF printer")
    print(f"   - Hold FEED button while turning ON")
    print(f"   - Should print configuration/test page")
    print(f"   - If this fails → Hardware problem")
    print(f"   ")
    print(f"   TEST 2 - Windows Test Page:")
    print(f"   - Control Panel → Printers")
    print(f"   - Right-click Star TSP100 → Properties")
    print(f"   - Click 'Print Test Page'")
    print(f"   - If this fails → Driver problem")
    print(f"   ")
    print(f"   TEST 3 - Notepad Test:")
    print(f"   - Open Notepad")
    print(f"   - Type: 'Hello World Test'")
    print(f"   - Print to Star TSP100")
    print(f"   - If this fails → Windows/Driver issue")

def test_star_printer_settings():
    """Test and display current Star printer settings"""
    
    print(f"\n" + "="*50)
    print("CURRENT STAR PRINTER SETTINGS")
    print("="*50)
    
    printer_name = "Star TSP100 Cutter (TSP143)"
    
    try:
        handle = win32print.OpenPrinter(printer_name)
        
        # Get printer info levels
        for level in [1, 2, 3, 4, 5]:
            try:
                info = win32print.GetPrinter(handle, level)
                print(f"\nLevel {level} Info:")
                if isinstance(info, dict):
                    for key, value in info.items():
                        if value is not None:
                            print(f"  {key}: {value}")
                else:
                    print(f"  {info}")
            except Exception as e:
                continue
        
        # Check printer capabilities
        try:
            print(f"\nPrinter Capabilities:")
            caps = win32print.GetPrinterDriverData(handle)
            print(f"  Driver Data Available: {len(caps) if caps else 0} bytes")
        except:
            print(f"  Driver Data: Not accessible")
        
        win32print.ClosePrinter(handle)
        
    except Exception as e:
        print(f"Error reading printer settings: {e}")

if __name__ == "__main__":
    diagnose_star_tsp100_issue()
    test_star_printer_settings()
    
    print(f"\n" + "="*50)
    print("NEXT STEPS:")
    print("="*50)
    print("1. Try the printer self-test (hold FEED while powering on)")
    print("2. If self-test works, try Windows test page")
    print("3. If Windows test page fails, reinstall Star driver")
    print("4. Check USB connection and try different port")
    print("5. Report back which tests work/fail")
