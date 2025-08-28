@echo off
echo ====================================================
echo HK Savor Spoon - Windows Print Server Setup
echo ====================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found!
python --version

:: Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

echo pip found!
echo.

:: Install required packages
echo Installing required Python packages...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    echo Please run this script as Administrator
    pause
    exit /b 1
)

echo.
echo ====================================================
echo Setup completed successfully!
echo ====================================================
echo.
echo Next steps:
echo 1. Connect your USB printer and set it as default
echo 2. Configure your firewall (see README.md)
echo 3. Set up port forwarding on your router
echo 4. Update the API key in windows_print_server.py
echo 5. Run the server with: python windows_print_server.py
echo.
echo For detailed instructions, see the setup guide.
echo.
pause
