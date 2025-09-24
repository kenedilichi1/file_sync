@echo off
chcp 65001 > nul
echo.
echo 🚀 LocalSync Windows Setup
echo ==========================
echo.
echo This will install LocalSync on your Windows system.
echo.
echo 📋 What this will do:
echo • Check Python installation
echo • Install LocalSync and dependencies  
echo • Create easy-to-use launcher
echo • Set up everything automatically
echo.
pause

echo.
echo 🔍 Checking Python...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo.
    echo Please install Python 3.7+ from:
    echo 📥 https://python.org/downloads
    echo.
    echo After installing Python, run this setup again.
    pause
    exit /b 1
)

echo ✅ Python found!
echo.
echo 📦 Installing LocalSync...
echo ⏳ This may take a few minutes...
echo.

:: Try installation with error handling
python install-windows.py

if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Installation had some issues.
    echo 💡 Try these solutions:
    echo 1. Run this file as Administrator
    echo 2. Check if Python is in PATH
    echo 3. Try manual installation
    echo.
    pause
)

echo.
echo 🎉 Setup complete!
echo.
echo 📝 Next steps:
echo 1. Double-click 'LocalSync.bat' to start
echo 2. Create account and start sharing files!
echo.
pause