# HK Savor Spoon - Quick IP Setup Script
# This script gets your current IP and helps setup fixed domain

Write-Host "=" * 50 -ForegroundColor Green
Write-Host "HK Savor Spoon - IP Setup Assistant" -ForegroundColor Green  
Write-Host "=" * 50 -ForegroundColor Green
Write-Host ""

# Function to get external IP
function Get-ExternalIP {
    $services = @(
        "http://ifconfig.me/ip",
        "http://ipinfo.io/ip", 
        "http://api.ipify.org",
        "http://checkip.amazonaws.com"
    )
    
    foreach ($service in $services) {
        try {
            $ip = (Invoke-WebRequest -Uri $service -UseBasicParsing -TimeoutSec 10).Content.Trim()
            if ($ip -match "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$") {
                return $ip
            }
        }
        catch {
            continue
        }
    }
    return $null
}

# Get current IP
Write-Host "🔍 Checking your current external IP..." -ForegroundColor Yellow
$currentIP = Get-ExternalIP

if ($currentIP) {
    Write-Host "✅ Current External IP: $currentIP" -ForegroundColor Green
    Write-Host "🔗 Current Print Server URL: http://$currentIP`:8080" -ForegroundColor Cyan
    
    # Save IP to file
    $config = @{
        ip = $currentIP
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        print_url = "http://$currentIP`:8080"
    }
    $config | ConvertTo-Json | Out-File -FilePath "current_ip.json" -Encoding UTF8
    
    Write-Host ""
    Write-Host "💾 IP saved to current_ip.json" -ForegroundColor Green
} else {
    Write-Host "❌ Unable to get external IP. Check internet connection." -ForegroundColor Red
    return
}

Write-Host ""
Write-Host "📋 Available Solutions for Fixed IP:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 🆓 No-IP Dynamic DNS (Recommended)"
Write-Host "   - Free permanent domain name"
Write-Host "   - Auto-updates when IP changes"
Write-Host "   - Setup: https://www.noip.com/"
Write-Host ""
Write-Host "2. 🦆 DuckDNS (Simple & Free)"
Write-Host "   - Easy setup with Google login"
Write-Host "   - Setup: https://www.duckdns.org/"
Write-Host ""
Write-Host "3. 🚇 Ngrok Tunnel (Instant)"
Write-Host "   - Works immediately"
Write-Host "   - No router config needed"
Write-Host "   - Setup: https://ngrok.com/"
Write-Host ""
Write-Host "4. 💰 Static IP from ISP (Business)"
Write-Host "   - Call your ISP for static IP service"
Write-Host "   - Cost: ~$10-30/month"
Write-Host ""

# Quick setup options
Write-Host "🚀 Quick Setup Options:" -ForegroundColor Green
Write-Host ""
Write-Host "A. Test current IP (temporary fix):"
Write-Host "   Update website to: http://$currentIP`:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "B. Setup No-IP (5 minutes):"
Write-Host "   1. Go to https://www.noip.com/sign-up"
Write-Host "   2. Create hostname: hksavorspoon.ddns.net"
Write-Host "   3. Download No-IP DUC client"
Write-Host "   4. Update website to: http://hksavorspoon.ddns.net:8080"
Write-Host ""
Write-Host "C. Setup Ngrok (2 minutes):"
Write-Host "   1. Download from https://ngrok.com/download"
Write-Host "   2. Run: ngrok http 8080"
Write-Host "   3. Use the provided https URL"
Write-Host ""

$choice = Read-Host "Which option would you like to setup? (A/B/C/N for none)"

switch ($choice.ToUpper()) {
    "A" {
        Write-Host ""
        Write-Host "🔧 Testing current IP setup..." -ForegroundColor Yellow
        Write-Host "Update your HK Savor Spoon website:" -ForegroundColor Green
        Write-Host "WINDOWS_PRINT_SERVER_URL = 'http://$currentIP`:8080'" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⚠️  Note: This IP may change! Consider option B or C for permanent solution." -ForegroundColor Yellow
    }
    "B" {
        Write-Host ""
        Write-Host "🔗 Opening No-IP website..." -ForegroundColor Green
        Start-Process "https://www.noip.com/sign-up"
        Write-Host "Follow the steps above to complete setup." -ForegroundColor Yellow
    }
    "C" {
        Write-Host ""
        Write-Host "🔗 Opening Ngrok website..." -ForegroundColor Green
        Start-Process "https://ngrok.com/download"
        Write-Host "Download, extract, and run: ngrok http 8080" -ForegroundColor Yellow
    }
    default {
        Write-Host "Setup cancelled. Current IP saved for reference." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📊 To monitor IP changes automatically, run:" -ForegroundColor Green
Write-Host "python ip_monitor.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Setup complete! Check current_ip.json for details." -ForegroundColor Green
