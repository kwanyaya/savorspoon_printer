# Fix Windows Firewall for HK Savor Spoon Print Server
# Run this as Administrator

Write-Host "🛡️ Configuring Windows Firewall for Print Server" -ForegroundColor Green
Write-Host "=" * 50

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "Then run: .\fix_firewall.ps1" -ForegroundColor Cyan
    pause
    exit
}

try {
    # Remove any existing rules
    Write-Host "🧹 Removing existing firewall rules..." -ForegroundColor Yellow
    netsh advfirewall firewall delete rule name="HK Savor Spoon Print Server" | Out-Null
    netsh advfirewall firewall delete rule name="HK Savor Spoon" | Out-Null
    
    # Add new inbound rule
    Write-Host "➕ Adding inbound rule for port 5000..." -ForegroundColor Yellow
    $result1 = netsh advfirewall firewall add rule name="HK Savor Spoon Print Server" dir=in action=allow protocol=TCP localport=5000
    
    # Add outbound rule (just in case)
    Write-Host "➕ Adding outbound rule for port 5000..." -ForegroundColor Yellow
    $result2 = netsh advfirewall firewall add rule name="HK Savor Spoon Print Server Out" dir=out action=allow protocol=TCP localport=5000
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Firewall rules added successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to add firewall rules" -ForegroundColor Red
    }
    
    # Show current rules
    Write-Host "`n📋 Current firewall rules for port 5000:" -ForegroundColor Cyan
    netsh advfirewall firewall show rule name="HK Savor Spoon Print Server"
    
} catch {
    Write-Host "❌ Error configuring firewall: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🔍 Testing local server access..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/status" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Local server is accessible" -ForegroundColor Green
    
    $data = $response.Content | ConvertFrom-Json
    Write-Host "Current server IP: $($data.local_ip)" -ForegroundColor Cyan
    Write-Host "Make sure your router port forwarding uses this IP!" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Local server test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure the print server is running: python windows_print_server.py" -ForegroundColor Yellow
}

Write-Host "`n📋 Next steps:" -ForegroundColor Green
Write-Host "1. Verify router port forwarding uses the correct internal IP" -ForegroundColor White
Write-Host "2. Test external access: http://58.153.166.26:5000/status" -ForegroundColor White
Write-Host "3. If still not working, try restarting your router" -ForegroundColor White

pause
