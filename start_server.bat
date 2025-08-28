@echo off
title HK Savor Spoon Print Server

echo ====================================================
echo Starting HK Savor Spoon Windows Print Server
echo ====================================================

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please run setup.bat first.
    pause
    exit /b 1
)

:: Check if the server file exists
if not exist "windows_print_server.py" (
    echo ERROR: windows_print_server.py not found in current directory
    echo Please run this script from the correct folder
    pause
    exit /b 1
)

:: Start the server
echo Starting print server...
echo Press Ctrl+C to stop the server
echo.

python windows_print_server.py

echo.
echo Server stopped.
pause
