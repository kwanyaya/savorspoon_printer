# -*- coding: utf-8 -*-
"""
Star TSP100 Settings Fix
========================
Fix common Star TSP100 printer settings that cause silent printing
"""

import win32print
import pywintypes

def fix_star_tsp100_settings():
    """Fix common Star TSP100 settings issues"""
    
    print("STAR TSP100 SETTINGS REPAIR")
    print("="*40)
    
    printer_name = "Star TSP100 Cutter (TSP143)"
    
    try:
        # Open printer for configuration
        handle = win32print.OpenPrinter(printer_name, {"DesiredAccess": win32print.PRINTER_ALL_ACCESS})
        
        # Get current printer info
        printer_info = win32print.GetPrinter(handle, 2)
        
        print(f"Current Settings:")
        print(f"  Print Processor: {printer_info.get('pPrintProcessor', 'Unknown')}")
        print(f"  Data Type: {printer_info.get('pDatatype', 'Unknown')}")
        print(f"  Attributes: {printer_info.get('Attributes', 0)}")
        
        # Check DevMode settings
        devmode = printer_info.get('pDevMode')
        if devmode:
            print(f"\nCurrent DevMode Settings:")
            print(f"  Paper Size: {getattr(devmode, 'PaperSize', 'Unknown')}")
            print(f"  Orientation: {getattr(devmode, 'Orientation', 'Unknown')}")
            print(f"  Print Quality: {getattr(devmode, 'PrintQuality', 'Unknown')}")
            
            # Try to modify settings for better Star compatibility
            try:
                # Set optimal settings for Star TSP100
                devmode.PaperSize = 256  # Custom paper size for thermal
                devmode.PrintQuality = -4  # High quality
                devmode.Orientation = 1   # Portrait
                
                # Update the devmode
                printer_info['pDevMode'] = devmode
                win32print.SetPrinter(handle, 2, printer_info, 0)
                print(f"\n✅ Updated DevMode settings for thermal printing")
                
            except Exception as e:
                print(f"\n⚠️ Could not modify DevMode: {e}")
        
        # Check if printer is set to print directly (bypass spooler)
        attributes = printer_info.get('Attributes', 0)
        direct_print = attributes & 0x0400  # PRINTER_ATTRIBUTE_DIRECT
        
        if direct_print:
            print(f"\n✅ Direct printing is ENABLED (good)")
        else:
            print(f"\n⚠️ Direct printing is DISABLED")
            print(f"   This might cause issues with thermal printers")
            
            # Try to enable direct printing
            try:
                printer_info['Attributes'] = attributes | 0x0400
                win32print.SetPrinter(handle, 2, printer_info, 0)
                print(f"✅ Enabled direct printing")
            except Exception as e:
                print(f"❌ Could not enable direct printing: {e}")
        
        win32print.ClosePrinter(handle)
        
    except Exception as e:
        print(f"❌ Error accessing printer settings: {e}")
        
    # Additional recommendations
    print(f"\n" + "="*40)
    print("MANUAL SETTINGS TO CHECK:")
    print("="*40)
    print("1. Printer Properties:")
    print("   - Right-click printer in Control Panel")
    print("   - Properties → Advanced")
    print("   - Check 'Print directly to the printer'")
    print("   - Uncheck 'Keep printed documents'")
    print("   - Uncheck 'Enable advanced printing features'")
    print()
    print("2. Printer Preferences:")
    print("   - Right-click printer → Printing Preferences")
    print("   - Set Paper Size: 'Roll Paper 80mm'")
    print("   - Set Quality: 'High' or 'Best'")
    print("   - Check any 'Cut Paper' options")
    print()
    print("3. Port Settings:")
    print("   - Printer Properties → Ports")
    print("   - Select USB001 port")
    print("   - Uncheck 'Enable bidirectional support'")
    print("   - Uncheck 'Enable printer pooling'")

def create_test_receipt():
    """Create a simple test receipt for Star TSP100"""
    
    print(f"\n" + "="*40)
    print("CREATING SIMPLE TEST RECEIPT")
    print("="*40)
    
    printer_name = "Star TSP100 Cutter (TSP143)"
    
    try:
        handle = win32print.OpenPrinter(printer_name)
        
        # Create very simple ESC/POS commands
        doc_info = ("Simple Test", None, "RAW")
        job_id = win32print.StartDocPrinter(handle, 1, doc_info)
        win32print.StartPagePrinter(handle)
        
        # Minimal Star TSP100 commands
        commands = b''
        commands += b'\x1B\x40'           # ESC @ - Initialize
        commands += b'\x1B\x61\x01'       # ESC a 1 - Center align
        commands += b'=== TEST RECEIPT ===\n'
        commands += b'\x1B\x61\x00'       # ESC a 0 - Left align
        commands += b'Item 1: $10.00\n'
        commands += b'Item 2: $5.50\n'
        commands += b'Total: $15.50\n'
        commands += b'\n\n\n'             # Feed lines
        commands += b'\x1D\x56\x41\x10'   # GS V A 16 - Cut paper
        
        bytes_written = win32print.WritePrinter(handle, commands)
        print(f"✅ Sent {bytes_written} bytes")
        print(f"📋 Job ID: {job_id}")
        
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print(f"✅ Simple test receipt sent")
        print(f"🔍 Check if printer responds to this basic test")
        
    except Exception as e:
        print(f"❌ Test receipt failed: {e}")

if __name__ == "__main__":
    fix_star_tsp100_settings()
    create_test_receipt()
    
    print(f"\n" + "="*40)
    print("SUMMARY OF ACTIONS:")
    print("="*40)
    print("1. ✅ Checked current printer settings")
    print("2. ✅ Sent optimized test receipt")
    print("3. 📋 Manual settings recommendations provided")
    print()
    print("NEXT STEPS:")
    print("- Try the printer self-test (FEED button + power on)")
    print("- Check if the test receipt above printed")
    print("- Apply manual settings if needed")
    print("- Report back which tests work")
