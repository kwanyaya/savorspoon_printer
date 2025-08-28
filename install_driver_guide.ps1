# Star TSP100 Driver Installation Guide
# Step-by-step instructions for installing and configuring the driver

Write-Host "🌟 Star TSP100 Driver Installation Guide" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

Write-Host "`n📋 STEP-BY-STEP INSTALLATION:" -ForegroundColor Yellow

Write-Host "`n1. ❌ REMOVE OLD PRINTER FIRST" -ForegroundColor Red
Write-Host "   • Go to Settings → Printers & scanners"
Write-Host "   • Find your current Star TSP100"
Write-Host "   • Click on it → Remove device"
Write-Host "   • Wait for removal to complete"

Write-Host "`n2. 📦 INSTALL NEW DRIVER" -ForegroundColor Green
Write-Host "   • Right-click the downloaded driver file"
Write-Host "   • Select 'Run as Administrator'"
Write-Host "   • Follow installation wizard"
Write-Host "   • Accept license agreement"
Write-Host "   • Complete installation"

Write-Host "`n3. 🔌 ADD PRINTER WITH NEW DRIVER" -ForegroundColor Green
Write-Host "   • Go to Settings → Printers & scanners"
Write-Host "   • Click 'Add a printer or scanner'"
Write-Host "   • Wait for scan, then click 'The printer that I want isn't listed'"
Write-Host "   • Select 'Add a local printer or network printer'"
Write-Host "   • Choose 'Use an existing port' → USB001 (or similar)"
Write-Host "   • In driver selection, look for 'Star TSP100' or 'Star CloudPRNT'"
Write-Host "   • Select your exact model (TSP143)"
Write-Host "   • Name it 'Star TSP100 Cutter (TSP143)'"
Write-Host "   • Set as default printer"

Write-Host "`n4. ⚙️ CONFIGURE FOR CHINESE" -ForegroundColor Blue
Write-Host "   • Right-click printer → Printer properties"
Write-Host "   • Go to Advanced tab"
Write-Host "   • Set 'Print directly to the printer' (if available)"
Write-Host "   • Set Data type to 'RAW'"
Write-Host "   • Click OK"

Write-Host "`n5. 🧪 TEST CHINESE PRINTING" -ForegroundColor Magenta
Write-Host "   • Go back to your print server test interface"
Write-Host "   • Try the Chinese print test"
Write-Host "   • Check if characters print clearly"

Write-Host "`n🚀 Opening Printer Settings..." -ForegroundColor Green
Start-Process "ms-settings:printers"

Write-Host "`n⏰ WHAT TO EXPECT:" -ForegroundColor Yellow
Write-Host "• Installation takes 2-5 minutes"
Write-Host "• You may need to restart after installation"
Write-Host "• New driver should support Chinese characters"
Write-Host "• Test printing should show clear Chinese text"

Write-Host "`n❓ IF YOU HAVE PROBLEMS:" -ForegroundColor Red
Write-Host "• Make sure to 'Run as Administrator'"
Write-Host "• Disconnect and reconnect USB cable"
Write-Host "• Restart computer after installation"
Write-Host "• Check Windows Update for additional drivers"

Read-Host "`nPress Enter when you've completed the installation"
