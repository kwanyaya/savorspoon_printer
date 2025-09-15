@echo off
echo ============================================================
echo HK SAVOR SPOON AUTO-RECOVERY PRINT SERVER
echo ============================================================
echo Starting server with automatic printer recovery...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as Administrator
    echo Some recovery features may not work properly
    echo Please run as Administrator for full functionality
    echo.
    pause
)

REM Start the auto-recovery print server
python auto_recovery_print_server.py

pause
