@echo off
echo ================================================
echo HK Savor Spoon - Dynamic DNS Setup Guide
echo ================================================
echo.
echo This script helps you set up a permanent domain name
echo that automatically updates when your IP changes.
echo.

:MENU
echo Choose your preferred solution:
echo.
echo 1. No-IP Dynamic DNS (Free, Recommended)
echo 2. DuckDNS (Free, Simple)
echo 3. Ngrok Tunnel (Free/Paid)
echo 4. Check Current IP
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto NOIP
if "%choice%"=="2" goto DUCKDNS
if "%choice%"=="3" goto NGROK
if "%choice%"=="4" goto CHECKIP
if "%choice%"=="5" goto EXIT

echo Invalid choice. Please try again.
goto MENU

:NOIP
echo.
echo ================================================
echo Setting up No-IP Dynamic DNS
echo ================================================
echo.
echo Step 1: Create Account
echo - Go to: https://www.noip.com/sign-up
echo - Choose FREE account
echo - Verify your email
echo.
echo Step 2: Create Hostname
echo - Login to No-IP dashboard
echo - Click "Create Hostname"
echo - Choose name like: hksavorspoon.ddns.net
echo - Set IP to your current external IP
echo.
echo Step 3: Download Update Client
echo - Download No-IP DUC (Dynamic Update Client)
echo - Install on this computer
echo - Login with your No-IP account
echo - Select your hostname
echo.
echo Step 4: Update Website
echo - Change WINDOWS_PRINT_SERVER_URL to:
echo   http://hksavorspoon.ddns.net:8080
echo.
echo Press any key to open No-IP website...
pause >nul
start https://www.noip.com/sign-up
goto MENU

:DUCKDNS
echo.
echo ================================================
echo Setting up DuckDNS (Alternative)
echo ================================================
echo.
echo Step 1: Get Token
echo - Go to: https://www.duckdns.org/
echo - Login with Google/GitHub
echo - Note your token
echo.
echo Step 2: Create Domain
echo - Choose subdomain: hksavorspoon.duckdns.org
echo - Click "add domain"
echo.
echo Step 3: Setup Auto-Update
echo - Use the IP monitor script we created
echo - Or setup Windows Task Scheduler
echo.
echo Press any key to open DuckDNS website...
pause >nul
start https://www.duckdns.org/
goto MENU

:NGROK
echo.
echo ================================================
echo Setting up Ngrok Tunnel
echo ================================================
echo.
echo Step 1: Download Ngrok
echo - Go to: https://ngrok.com/download
echo - Download Windows version
echo - Extract to C:\ngrok\
echo.
echo Step 2: Get Auth Token
echo - Sign up at: https://dashboard.ngrok.com/signup
echo - Copy your authtoken
echo.
echo Step 3: Setup
echo - Run: ngrok authtoken YOUR_TOKEN
echo - Run: ngrok http 8080
echo - Copy the public URL (like: https://abc123.ngrok.io)
echo.
echo Step 4: Update Website
echo - Use the ngrok URL in your website
echo - Example: https://abc123.ngrok.io
echo.
echo Press any key to open Ngrok website...
pause >nul
start https://ngrok.com/download
goto MENU

:CHECKIP
echo.
echo ================================================
echo Checking Current IP Address
echo ================================================
echo.
python -c "import requests; print('Current External IP:', requests.get('http://ifconfig.me/ip', timeout=10).text.strip())" 2>nul
if errorlevel 1 (
    echo Python/requests not available. Using PowerShell...
    powershell -command "try { (Invoke-WebRequest -Uri 'http://ifconfig.me/ip' -UseBasicParsing).Content.Trim() } catch { 'Unable to get IP' }"
)
echo.
echo Print Server URLs:
echo - Local: http://localhost:8080/status
echo - Network: http://192.168.0.184:8080/status
echo.
pause
goto MENU

:EXIT
echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo Next Steps:
echo 1. Choose one of the solutions above
echo 2. Update your HK Savor Spoon website configuration
echo 3. Test the new URL
echo.
echo For automatic IP monitoring, run:
echo python ip_monitor.py
echo.
pause
exit /b

echo.
