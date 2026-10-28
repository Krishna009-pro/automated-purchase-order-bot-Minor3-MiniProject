@echo off
title Automated Purchase Order RPA Bot Launcher
echo ===============================================================
echo        AUTOMATED PURCHASE ORDER MANAGEMENT BOT (RPA)
echo ===============================================================
echo.
echo Choose an automation mode:
echo   [1] REAL OS Automation (Moves your real mouse, types on screen)
echo   [2] Fast Background Engine (Updates Excel, takes screenshots, sends email)
echo   [3] Interactive Web Dashboard (Streamlit browser interface)
echo.
set /p choice="Enter choice [1, 2, or 3] (default is 1): "
if "%choice%"=="" set choice=1

cd /d "%~dp0"

if "%choice%"=="1" (
    echo.
    echo Starting Real OS Mouse ^& Keyboard Automation...
    echo (Do not touch the mouse while the bot is moving it)
    .venv\Scripts\python.exe real_os_automation_bot.py --reset
) else if "%choice%"=="2" (
    echo.
    echo Starting Background Automation Engine...
    .venv\Scripts\python.exe sap_po_updater_bot.py --reset
) else if "%choice%"=="3" (
    echo.
    echo Launching Streamlit Web Dashboard...
    .venv\Scripts\streamlit.exe run app.py
) else (
    echo Invalid choice. Starting Real OS Automation by default...
    .venv\Scripts\python.exe real_os_automation_bot.py --reset
)

echo.
pause
