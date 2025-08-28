# Star TSP100 Driver Diagnostic Script
# Checks driver and provides recommendations for Chinese printing

Write-Host "🌟 Star TSP100 Driver Diagnostic" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check current default printer
Write-Host "`n🔍 Checking Current Printer Configuration..." -ForegroundColor Yellow

$defaultPrinter = Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Default=True"

if ($defaultPrinter) {
    Write-Host "`nDefault Printer Details:" -ForegroundColor Green
    Write-Host "  Name: $($defaultPrinter.Name)" -ForegroundColor White
    Write-Host "  Driver: $($defaultPrinter.DriverName)" -ForegroundColor White
    Write-Host "  Port: $($defaultPrinter.PortName)" -ForegroundColor White
    Write-Host "  Status: $($defaultPrinter.PrinterStatus)" -ForegroundColor White
    
    # Check if it's a Star printer
    $isStar = $defaultPrinter.Name -like "*Star*"
    $isTSP = $defaultPrinter.Name -like "*TSP*"
    
    Write-Host "`nStar TSP100 Detection:" -ForegroundColor Yellow
    if ($isStar) {
        Write-Host "  ✅ Star Printer Detected" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Not a Star Printer" -ForegroundColor Red
    }
    
    if ($isTSP) {
        Write-Host "  ✅ TSP Series Detected" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Not TSP Series" -ForegroundColor Red
    }
} else {
    Write-Host "❌ No default printer found!" -ForegroundColor Red
}

# Check available Star drivers
Write-Host "`n🔍 Checking Available Star Drivers..." -ForegroundColor Yellow

$allDrivers = Get-WmiObject -Class Win32_PrinterDriver
$starDrivers = $allDrivers | Where-Object { $_.Name -like "*Star*" }

if ($starDrivers) {
    Write-Host "`nFound Star Drivers:" -ForegroundColor Green
    foreach ($driver in $starDrivers) {
        Write-Host "  ✅ $($driver.Name)" -ForegroundColor White
    }
} else {
    Write-Host "`n❌ No Star drivers found!" -ForegroundColor Red
    Write-Host "This is likely why Chinese characters are garbled!" -ForegroundColor Yellow
}

# Driver recommendations
Write-Host "`n💡 CHINESE CHARACTER ISSUE DIAGNOSIS:" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

if (-not $starDrivers) {
    Write-Host "`n🚨 PROBLEM IDENTIFIED:" -ForegroundColor Red
    Write-Host "  Your printer is using a generic Windows driver"
    Write-Host "  Generic drivers don't support Chinese characters properly"
    Write-Host "  This causes garbled text (squares, question marks, etc.)"
    
    Write-Host "`n✅ SOLUTION:" -ForegroundColor Green
    Write-Host "  Download and install proper Star TSP100 driver"
}

Write-Host "`n🔗 RECOMMENDED DRIVERS:" -ForegroundColor Yellow
Write-Host "1. Star CloudPRNT Driver (BEST for Chinese)" -ForegroundColor Green
Write-Host "   Download: https://www.star-m.jp/products/s_print/CloudPRNTSDK/"
Write-Host "   - Full Unicode support"
Write-Host "   - Best Chinese character handling"

Write-Host "`n2. Star TSP100 Universal Driver" -ForegroundColor Green
Write-Host "   Download: https://www.star-m.jp/products/s_print/WindowsDriver/"
Write-Host "   - Official Star driver"
Write-Host "   - Better than generic Windows driver"

Write-Host "`n🔧 INSTALLATION STEPS:" -ForegroundColor Cyan
Write-Host "1. Go to Settings → Printers & scanners"
Write-Host "2. Remove current Star TSP100 printer"
Write-Host "3. Download Star driver from above links"
Write-Host "4. Add printer again → Select 'Have Disk' → Browse to downloaded driver"
Write-Host "5. Set as default printer"
Write-Host "6. Test Chinese printing again"

# Open printer settings
Write-Host "`n🚀 Opening Printer Settings..." -ForegroundColor Green
Write-Host "Remove your current printer and reinstall with proper Star driver"

Start-Process "ms-settings:printers"

Write-Host "`n📋 QUICK SUMMARY:" -ForegroundColor Yellow
Write-Host "• Garbled Chinese = Wrong driver"
Write-Host "• Star printers need Star drivers for Chinese"
Write-Host "• Download CloudPRNT or Universal driver"
Write-Host "• Reinstall printer with new driver"

Read-Host "`nPress Enter to finish"
