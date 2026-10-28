@echo off
title Real OS Mouse & Keyboard RPA Bot Runner
echo ===============================================================
echo     REAL OS-LEVEL PURCHASE ORDER MANAGEMENT RPA BOT
echo   (Controls Physical Mouse, Real Keyboard Typing, and Screen)
echo ===============================================================
echo.
echo NOTE: Keep your hands off the mouse for a few seconds once it starts,
echo as the bot will physically move your cursor and type onto your screen!
echo.
cd /d "%~dp0"
.venv\Scripts\python.exe real_os_automation_bot.py --reset
echo.
echo ===============================================================
echo Automation Complete! Check the Screenshots/ and Emails/ folders.
echo ===============================================================
pause
