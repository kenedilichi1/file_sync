@echo off
setlocal enabledelayedexpansion
title FileSync Installer
echo ==================================================
echo 🚀 FileSync Installer - Secure File Sharing
echo ==================================================

:: 1️⃣ Go to project root
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%\.."

:: 2️⃣ Check for Python installation
echo 🔍 Checking for Python 3...
set "PYTHON_CMD="

:: Try various commands
where python3 >nul 2>nul && set "PYTHON_CMD=python3"
if "%PYTHON_CMD%"=="" (
    where python >nul 2>nul && set "PYTHON_CMD=python"
)
if "%PYTHON_CMD%"=="" (
    where py >nul 2>nul && set "PYTHON_CMD=py -3"
)

:: 3️⃣ If Python not found, download it automatically
if "%PYTHON_CMD%"=="" (
    echo ⚠️ Python 3 not found. Installing automatically...

    set "PYTHON_INSTALLER=python-installer.exe"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe"

    echo 🌐 Downloading Python 3.12.6 from official site...
    powershell -Command "Invoke-WebRequest '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"

    if not exist "%PYTHON_INSTALLER%" (
        echo ❌ Failed to download Python. Check your internet connection.
        pause
        exit /b 1
    )

    echo ⚙️ Installing Python silently...
    start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

    echo 🧹 Cleaning up installer...
    del "%PYTHON_INSTALLER%" >nul 2>nul

    echo ✅ Python installed successfully!
    set "PYTHON_CMD=python"
)

:: 4️⃣ Verify Python version
for /f "tokens=2 delims= " %%v in ('%PYTHON_CMD% --version 2^>^&1') do set "VER=%%v"
for /f "tokens=1 delims=." %%a in ("%VER%") do set "MAJOR=%%a"
if %MAJOR% LSS 3 (
    echo ❌ Python 3 or higher is required. Found version %VER%.
    pause
    exit /b 1
)

:: 5️⃣ Create virtual environment
echo 📦 Creating virtual environment...
%PYTHON_CMD% -m venv filesync_env

if not exist "filesync_env\Scripts\activate.bat" (
    echo ❌ Virtual environment creation failed.
    pause
    exit /b 1
)

:: 6️⃣ Activate environment and install dependencies
call filesync_env\Scripts\activate.bat

echo 🔧 Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo 📥 Installing FileSync...
python -m pip install -e .

if errorlevel 1 (
    echo ❌ Installation failed. Check setup.py or dependencies.
    pause
    exit /b 1
)

echo ✅ Installation complete!
echo.
echo To run FileSync manually:
echo   call filesync_env\Scripts\activate.bat
echo   python src\cli.py --gui
echo.
echo Or use the run script:
echo   scripts\run.bat
pause
