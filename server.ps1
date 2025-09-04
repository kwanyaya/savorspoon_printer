# HK Savor Spoon Printer Server Management v5.0
# =============================================
# PowerShell script for secure server management

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "status", "test", "security")]
    [string]$Action = "start",
    
    [switch]$v2,     # Use version 2 server (windows_print_server.py)
    [switch]$v4,     # Use version 4 server (robust_print_server_v4.py) 
    [switch]$secure, # Use secure v5 server (secure_print_server_v5.py) - DEFAULT
    [switch]$Help
)

# Configuration based on version selection
if ($v2) {
    $ServerScript = "windows_print_server.py"
    $Version = "v2.0"
} elseif ($v4) {
    $ServerScript = "robust_print_server_v4.py"
    $Version = "v4.0"
} else {
    # Default to secure v5
    $ServerScript = "secure_print_server_v5.py"
    $Version = "v5.0-secure"
}

$ServerPort = 8080
$ProcessName = "python"
$ApiKey = "hksavorspoon-secure-print-key-2025"

function Write-Banner {
    param([string]$Title)
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "  $Title ($Version)" -ForegroundColor White
    Write-Host "=" * 70 -ForegroundColor Cyan
}

function Get-ServerProcess {
    # Find Python process running our server
    return Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | 
           Where-Object { $_.CommandLine -like "*$ServerScript*" }
}

function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Start-Server {
    Write-Banner "STARTING HK SAVOR SPOON PRINT SERVER"
    
    # Check if already running
    $existing = Get-ServerProcess
    if ($existing) {
        Write-Host "⚠️  Server already running (PID: $($existing.Id))" -ForegroundColor Yellow
        return
    }
    
    # Check if port is available
    if (Test-Port -Port $ServerPort) {
        Write-Host "❌ Port $ServerPort is already in use" -ForegroundColor Red
        Write-Host "   Use 'server.ps1 stop' to stop any existing server" -ForegroundColor Yellow
        return
    }
    
    # Start the server
    Write-Host "🚀 Starting server..." -ForegroundColor Green
    Write-Host "   Script: $ServerScript" -ForegroundColor Gray
    Write-Host "   Port: $ServerPort" -ForegroundColor Gray
    Write-Host ""
    
    try {
        Start-Process -FilePath "python" -ArgumentList $ServerScript -NoNewWindow
        Start-Sleep -Seconds 3
        
        if (Test-Port -Port $ServerPort) {
            Write-Host "✅ Server started successfully!" -ForegroundColor Green
            Write-Host "   Local: http://localhost:$ServerPort" -ForegroundColor Cyan
            Write-Host "   Status: http://localhost:$ServerPort/status" -ForegroundColor Cyan
        } else {
            Write-Host "❌ Server failed to start" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Error starting server: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-Server {
    Write-Banner "STOPPING PRINT SERVER"
    
    $processes = Get-ServerProcess
    if (-not $processes) {
        Write-Host "ℹ️  No server process found" -ForegroundColor Yellow
        return
    }
    
    foreach ($process in $processes) {
        Write-Host "🛑 Stopping server (PID: $($process.Id))..." -ForegroundColor Yellow
        try {
            $process.Kill()
            Write-Host "✅ Server stopped" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Error stopping server: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Show-Status {
    Write-Banner "SERVER STATUS"
    
    # Check process
    $process = Get-ServerProcess
    if ($process) {
        Write-Host "✅ Server Process: Running (PID: $($process.Id))" -ForegroundColor Green
    } else {
        Write-Host "❌ Server Process: Not running" -ForegroundColor Red
    }
    
    # Check port
    if (Test-Port -Port $ServerPort) {
        Write-Host "✅ Port $ServerPort: Available" -ForegroundColor Green
        
        # Try to get status from API
        try {
            $headers = @{ "X-API-Key" = $ApiKey }
            $response = Invoke-RestMethod -Uri "http://localhost:$ServerPort/status" -Headers $headers -TimeoutSec 5
            Write-Host "✅ API Response: $($response.status)" -ForegroundColor Green
            Write-Host "   Server: $($response.server)" -ForegroundColor Gray
            Write-Host "   Version: $($response.version)" -ForegroundColor Gray
            if ($response.printer) {
                Write-Host "   Printer: $($response.printer)" -ForegroundColor Gray
            }
            if ($response.circuit_breaker) {
                $cb = $response.circuit_breaker
                Write-Host "   Circuit Breaker: $($cb.state) (failures: $($cb.failures))" -ForegroundColor Gray
            }
            if ($response.queue_size -ne $null) {
                Write-Host "   Queue Size: $($response.queue_size)" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host "⚠️  API not responding" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Port $ServerPort: Not responding" -ForegroundColor Red
    }
    
    # Show network info
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" })[0].IPAddress
    Write-Host ""
    Write-Host "🌐 Network Access:" -ForegroundColor Cyan
    Write-Host "   Local: http://localhost:$ServerPort" -ForegroundColor Gray
    Write-Host "   Network: http://$ip`:$ServerPort" -ForegroundColor Gray
}

function Test-Server {
    Write-Banner "TESTING PRINT SERVER"
    
    Write-Host "🧪 Running comprehensive test suite..." -ForegroundColor Yellow
    try {
        python printer_test_suite.py
    }
    catch {
        Write-Host "❌ Test suite failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-Security {
    Write-Banner "SECURITY STATUS & MONITORING"
    
    if (-not (Test-Port -Port $ServerPort)) {
        Write-Host "❌ Server is not running" -ForegroundColor Red
        return
    }
    
    try {
        $headers = @{ "X-API-Key" = $ApiKey }
        
        # Get security status
        $secResponse = Invoke-RestMethod -Uri "http://localhost:$ServerPort/security-status" -Headers $headers -TimeoutSec 5
        
        Write-Host "🛡️  Security Status:" -ForegroundColor Cyan
        Write-Host "   Blocked IPs: $($secResponse.blocked_ips)" -ForegroundColor Yellow
        
        if ($secResponse.blocked_list -and $secResponse.blocked_list.Count -gt 0) {
            Write-Host "   Currently Blocked:" -ForegroundColor Red
            foreach ($ip in $secResponse.blocked_list) {
                Write-Host "     - $ip" -ForegroundColor Red
            }
        }
        
        Write-Host "   Rate Limited IPs: $($secResponse.rate_limited_ips)" -ForegroundColor Yellow
        
        Write-Host ""
        Write-Host "📊 Security Config:" -ForegroundColor Cyan
        $config = $secResponse.security_config
        Write-Host "   Rate Limit: $($config.RATE_LIMIT_REQUESTS) requests per $($config.RATE_LIMIT_WINDOW)s" -ForegroundColor Gray
        Write-Host "   Block Duration: $($config.BLOCK_DURATION)s" -ForegroundColor Gray
        Write-Host "   Suspicious Threshold: $($config.SUSPICIOUS_THRESHOLD)" -ForegroundColor Gray
        
        # Get queue status
        $queueResponse = Invoke-RestMethod -Uri "http://localhost:$ServerPort/queue" -Headers $headers -TimeoutSec 5
        
        Write-Host ""
        Write-Host "🔄 Circuit Breaker & Queue:" -ForegroundColor Cyan
        $cb = $queueResponse.circuit_breaker
        Write-Host "   State: $($cb.state)" -ForegroundColor $(if ($cb.state -eq "CLOSED") { "Green" } else { "Yellow" })
        Write-Host "   Failures: $($cb.failures)" -ForegroundColor Gray
        Write-Host "   Queue Size: $($queueResponse.queue_size)" -ForegroundColor Gray
        
        # Show recent log entries (if log file exists)
        $logFile = "print_server_secure.log"
        if (Test-Path $logFile) {
            Write-Host ""
            Write-Host "📋 Recent Security Events (last 10):" -ForegroundColor Cyan
            Get-Content $logFile -Tail 10 | Where-Object { $_ -match "🚫|🔍|⚡|🚨" } | ForEach-Object {
                if ($_ -match "🚫|🚨") {
                    Write-Host "   $_" -ForegroundColor Red
                } elseif ($_ -match "🔍|⚡") {
                    Write-Host "   $_" -ForegroundColor Yellow
                }
            }
        }
        
    }
    catch {
        Write-Host "❌ Error getting security status: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Restart-Server {
    Write-Banner "RESTARTING PRINT SERVER"
    Stop-Server
    Start-Sleep -Seconds 2
    Start-Server
}

# Main execution
if ($Help) {
    Write-Host "HK Savor Spoon Print Server Management v5.0" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: server.ps1 [action] [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Cyan
    Write-Host "  start     - Start the print server" -ForegroundColor Gray
    Write-Host "  stop      - Stop the print server" -ForegroundColor Gray
    Write-Host "  restart   - Restart the print server" -ForegroundColor Gray
    Write-Host "  status    - Show server status" -ForegroundColor Gray
    Write-Host "  test      - Run test suite" -ForegroundColor Gray
    Write-Host "  security  - Show security monitoring" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Version Options:" -ForegroundColor Cyan
    Write-Host "  -secure   - Use secure v5.0 server (DEFAULT)" -ForegroundColor Green
    Write-Host "  -v4       - Use robust v4.0 server" -ForegroundColor Gray
    Write-Host "  -v2       - Use basic v2.0 server" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\server.ps1 start -secure  # Start secure server (default)" -ForegroundColor Gray
    Write-Host "  .\server.ps1 status         # Show status" -ForegroundColor Gray
    Write-Host "  .\server.ps1 security       # Security monitoring" -ForegroundColor Gray
    Write-Host "  .\server.ps1 start -v4      # Start v4 server instead" -ForegroundColor Gray
    exit
}

switch ($Action.ToLower()) {
    "start" { Start-Server }
    "stop" { Stop-Server }
    "restart" { Restart-Server }
    "status" { Show-Status }
    "test" { Test-Server }
    "security" { Show-Security }
    default { 
        Write-Host "Usage: server.ps1 [start|stop|restart|status|test|security] [options]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Cyan
        Write-Host "  start     - Start the print server" -ForegroundColor Gray
        Write-Host "  stop      - Stop the print server" -ForegroundColor Gray
        Write-Host "  restart   - Restart the print server" -ForegroundColor Gray
        Write-Host "  status    - Show server status" -ForegroundColor Gray
        Write-Host "  test      - Run test suite" -ForegroundColor Gray
        Write-Host "  security  - Show security monitoring" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Version Options: -secure (default), -v4, -v2" -ForegroundColor Gray
        Write-Host "Use -Help for detailed usage information" -ForegroundColor Gray
    }
}
