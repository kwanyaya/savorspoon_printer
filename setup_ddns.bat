@echo off
chcp 65001 >nul
title HK Savor Spoon - DDNS 配置工具

echo.
echo ======================================================
echo    HK Savor Spoon - DDNS 動態域名配置工具
echo ======================================================
echo.
echo 此工具將幫助您設置 DDNS，解決動態 IP 問題
echo 讓您的打印服務器擁有固定的網址！
echo.
echo 📋 準備工作：
echo 1. 確保您已註冊 DDNS 服務（推薦 DuckDNS）
echo 2. 記錄您的域名和認證信息
echo 3. 確保路由器已配置端口轉發
echo.
pause

echo.
echo 🚀 正在啟動 DDNS 配置工具...
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 錯誤：未找到 Python
    echo 請先安裝 Python 3.8 或更新版本
    echo 下載地址：https://python.org/downloads/
    pause
    exit /b 1
)

REM 檢查所需模組
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 正在安裝所需的 Python 模組...
    pip install requests
)

REM 啟動 DDNS 工具
python ddns_helper.py

echo.
echo 👋 DDNS 配置工具已退出
pause
