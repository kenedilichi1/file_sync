@echo off
echo 🚀 Installing FileSync...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo Found Python %PYTHON_VERSION%

:: Create virtual environment
echo 📦 Creating virtual environment...
python -m venv filesync_env

:: Activate virtual environment
echo 🔧 Activating virtual environment...
call filesync_env\Scripts\activate.bat

:: Install package
echo 📥 Installing FileSync...
pip install -e .

echo ✅ Installation complete!
echo.
echo To run FileSync:
echo   filesync_env\Scripts\activate.bat
echo   filesync --gui
echo.
echo Or use the run script:
echo   scripts\run.bat
pause