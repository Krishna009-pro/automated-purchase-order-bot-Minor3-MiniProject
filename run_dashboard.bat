@echo off
title Automated Purchase Order RPA Bot - Web Dashboard
echo =======================================================
echo    AUTOMATED PURCHASE ORDER RPA BOT - WEB DASHBOARD
echo =======================================================
echo.
cd /d "%~dp0"
echo Launching Streamlit Web Dashboard at http://localhost:8501 ...
.venv\Scripts\streamlit.exe run app.py
pause
