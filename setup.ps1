# HK Savor Spoon Print Server - PowerShell Setup Script
# Run this script as Administrator for complete setup

param(
    [switch]$InstallService,
    [switch]$UninstallService,
    [switch]$StartService,
    [switch]$StopService,
    [string]$ServiceName = "HKSavorSpoonPrintServer"
)

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "   HK Savor Spoon - Windows Print Server Setup" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Function to check if Python is installed
function Test-PythonInstallation {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "✗ Python not found" -ForegroundColor Red
        return $false
    }
    return $false
}

# Function to install Python packages
function Install-PythonPackages {
    Write-Host "`nInstalling Python packages..." -ForegroundColor Yellow
    
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python packages installed successfully" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "✗ Failed to install Python packages" -ForegroundColor Red
            return $false
        }
    }
    else {
        Write-Host "✗ requirements.txt not found" -ForegroundColor Red
        return $false
    }
}

# Function to configure Windows Firewall
function Set-FirewallRule {
    param([int]$Port = 5000)
    
    Write-Host "`nConfiguring Windows Firewall..." -ForegroundColor Yellow
    
    try {
        # Remove existing rule if it exists
        Remove-NetFirewallRule -DisplayName "HKSavorSpoon Print Server" -ErrorAction SilentlyContinue
        
        # Create new inbound rule
        New-NetFirewallRule -DisplayName "HKSavorSpoon Print Server" -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow -Profile Any
        
        Write-Host "✓ Firewall rule created for port $Port" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Failed to configure firewall: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to get network information
function Get-NetworkInfo {
    Write-Host "`nNetwork Information:" -ForegroundColor Yellow
    
    $adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.InterfaceDescription -notlike "*Loopback*" }
    
    foreach ($adapter in $adapters) {
        $ip = Get-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
        if ($ip) {
            Write-Host "  Interface: $($adapter.Name)" -ForegroundColor Cyan
            Write-Host "  IP Address: $($ip.IPAddress)" -ForegroundColor White
            Write-Host "  Subnet: $($ip.PrefixLength)" -ForegroundColor White
            Write-Host ""
        }
    }
}

# Function to test printer setup
function Test-PrinterSetup {
    Write-Host "`nTesting printer setup..." -ForegroundColor Yellow
    
    $defaultPrinter = Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Default=True"
    
    if ($defaultPrinter) {
        Write-Host "✓ Default printer found: $($defaultPrinter.Name)" -ForegroundColor Green
        Write-Host "  Status: $($defaultPrinter.WorkOffline -eq $false ? 'Online' : 'Offline')" -ForegroundColor White
        return $true
    }
    else {
        Write-Host "✗ No default printer found" -ForegroundColor Red
        Write-Host "  Please set up a printer in Windows Settings" -ForegroundColor Yellow
        return $false
    }
}

# Function to install as Windows Service
function Install-WindowsService {
    Write-Host "`nInstalling Windows Service..." -ForegroundColor Yellow
    
    $nssm = "C:\nssm\win64\nssm.exe"
    if (-not (Test-Path $nssm)) {
        Write-Host "✗ NSSM not found at $nssm" -ForegroundColor Red
        Write-Host "  Please download NSSM from https://nssm.cc/ and extract to C:\nssm\" -ForegroundColor Yellow
        return $false
    }
    
    $pythonPath = (Get-Command python).Source
    $scriptPath = Join-Path (Get-Location) "windows_print_server.py"
    
    # Install service
    & $nssm install $ServiceName $pythonPath $scriptPath
    & $nssm set $ServiceName AppDirectory (Get-Location)
    & $nssm set $ServiceName Description "HK Savor Spoon Windows Print Server"
    & $nssm set $ServiceName Start SERVICE_AUTO_START
    
    Write-Host "✓ Service installed: $ServiceName" -ForegroundColor Green
    return $true
}

# Function to uninstall Windows Service
function Uninstall-WindowsService {
    Write-Host "`nUninstalling Windows Service..." -ForegroundColor Yellow
    
    $nssm = "C:\nssm\win64\nssm.exe"
    if (-not (Test-Path $nssm)) {
        Write-Host "✗ NSSM not found" -ForegroundColor Red
        return $false
    }
    
    & $nssm stop $ServiceName
    & $nssm remove $ServiceName confirm
    
    Write-Host "✓ Service uninstalled: $ServiceName" -ForegroundColor Green
    return $true
}

# Main setup process
function Start-Setup {
    Write-Host "`nStarting setup process..." -ForegroundColor Green
    
    # Check Python installation
    if (-not (Test-PythonInstallation)) {
        Write-Host "`nPlease install Python 3.8+ from https://python.org" -ForegroundColor Yellow
        Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        return
    }
    
    # Install Python packages
    if (-not (Install-PythonPackages)) {
        Read-Host "Press Enter to exit"
        return
    }
    
    # Configure firewall
    Set-FirewallRule -Port 5000
    
    # Test printer setup
    Test-PrinterSetup
    
    # Show network information
    Get-NetworkInfo
    
    Write-Host "`n======================================================" -ForegroundColor Cyan
    Write-Host "              Setup Completed!" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "1. Update API key in windows_print_server.py" -ForegroundColor White
    Write-Host "2. Configure router port forwarding (port 5000)" -ForegroundColor White
    Write-Host "3. Set up Dynamic DNS (optional but recommended)" -ForegroundColor White
    Write-Host "4. Start the server: .\start_server.bat" -ForegroundColor White
    Write-Host "5. Test the server: python test_server.py" -ForegroundColor White
    Write-Host "`nTo install as Windows Service:" -ForegroundColor Yellow
    Write-Host ".\setup.ps1 -InstallService" -ForegroundColor White
    Write-Host ""
}

# Handle command line parameters
if ($InstallService) {
    Install-WindowsService
}
elseif ($UninstallService) {
    Uninstall-WindowsService
}
elseif ($StartService) {
    Start-Service $ServiceName
    Write-Host "✓ Service started: $ServiceName" -ForegroundColor Green
}
elseif ($StopService) {
    Stop-Service $ServiceName
    Write-Host "✓ Service stopped: $ServiceName" -ForegroundColor Green
}
else {
    Start-Setup
}

Read-Host "`nPress Enter to exit"
