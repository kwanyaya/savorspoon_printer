# Port Forwarding Check Script for HK Savor Spoon Print Server
# Run this as Administrator to check and configure port forwarding

Write-Host "🔍 HK Savor Spoon Print Server - Port Forwarding Check" -ForegroundColor Green
Write-Host "=" * 60

# Check 1: Is the print server running?
Write-Host "`n1️⃣  Checking if print server is running..." -ForegroundColor Yellow
$portCheck = netstat -an | findstr ":5000"
if ($portCheck) {
    Write-Host "✅ Print server is running on port 5000" -ForegroundColor Green
    Write-Host "   $portCheck" -ForegroundColor Cyan
} else {
    Write-Host "❌ Print server is NOT running on port 5000" -ForegroundColor Red
    Write-Host "   Please start: python windows_print_server.py" -ForegroundColor Yellow
}

# Check 2: Windows Firewall
Write-Host "`n2️⃣  Checking Windows Firewall..." -ForegroundColor Yellow
$firewallRules = netsh advfirewall firewall show rule name=all | findstr -i "5000"
if ($firewallRules) {
    Write-Host "✅ Found firewall rules for port 5000:" -ForegroundColor Green
    $firewallRules | ForEach-Object { Write-Host "   $_" -ForegroundColor Cyan }
} else {
    Write-Host "❌ No firewall rules found for port 5000" -ForegroundColor Red
    Write-Host "   Need to add firewall rule..." -ForegroundColor Yellow
    
    # Try to add firewall rule
    try {
        $result = netsh advfirewall firewall add rule name="HK Savor Spoon Print Server" dir=in action=allow protocol=TCP localport=5000
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Firewall rule added successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to add firewall rule. Run as Administrator!" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error adding firewall rule: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Check 3: Local network access
Write-Host "`n3️⃣  Testing local network access..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://192.168.124.182:5000/status" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Local network access works!" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Local network access failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check 4: External IP and router information
Write-Host "`n4️⃣  Checking external IP and router info..." -ForegroundColor Yellow
try {
    $externalIP = (Invoke-WebRequest -Uri "http://ifconfig.me/ip" -UseBasicParsing -TimeoutSec 10).Content.Trim()
    Write-Host "🌐 Your external IP: $externalIP" -ForegroundColor Cyan
    
    # Get default gateway (router IP)
    $gateway = (Get-NetRoute -DestinationPrefix "0.0.0.0/0").NextHop | Select-Object -First 1
    Write-Host "🏠 Router IP (Gateway): $gateway" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Could not get external IP: $($_.Exception.Message)" -ForegroundColor Red
}

# Check 5: Test external access (if port forwarding is configured)
Write-Host "`n5️⃣  Testing external access..." -ForegroundColor Yellow
if ($externalIP) {
    try {
        Write-Host "   Testing: http://$externalIP:5000/status" -ForegroundColor Cyan
        $extResponse = Invoke-WebRequest -Uri "http://$externalIP:5000/status" -TimeoutSec 10 -UseBasicParsing
        Write-Host "✅ External access works! Port forwarding is configured!" -ForegroundColor Green
        Write-Host "   Your public print server URL: http://$externalIP:5000" -ForegroundColor Yellow
    } catch {
        Write-Host "❌ External access failed - Port forwarding may not be configured" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
    }
}

# Summary and next steps
Write-Host "`n📋 Summary:" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

Write-Host "`n🔧 Router Port Forwarding Configuration:" -ForegroundColor Cyan
Write-Host "   Router IP: $gateway (access this in your browser)"
Write-Host "   External Port: 5000"
Write-Host "   Internal IP: 192.168.124.182"
Write-Host "   Internal Port: 5000"
Write-Host "   Protocol: TCP"

Write-Host "`n🌐 After configuring router port forwarding:" -ForegroundColor Cyan
Write-Host "   Your public print server will be: http://$externalIP:5000"
Write-Host "   Test URL: http://$externalIP:5000/status"

Write-Host "`n⚡ Quick Test Commands:" -ForegroundColor Cyan
Write-Host "   Local test:    curl http://192.168.124.182:5000/status"
Write-Host "   External test: curl http://$externalIP:5000/status"

Write-Host "`n📱 For your HK Savor Spoon website:" -ForegroundColor Green
Write-Host "   Use this URL: http://$externalIP:5000"
Write-Host "   API Endpoint: http://$externalIP:5000/print"
