@echo off
chcp 65001 > nul
echo.
echo 🚀 LocalSync Windows Setup
echo ==========================
echo.
echo Starting Python-based installer...
echo.
timeout /t 2 /nobreak >nul
python install-windows.py
pause