@echo off
setlocal ENABLEDELAYEDEXPANSION
echo 🚀 Installing FileSync...

REM --- Detect project root (one level above scripts folder) ---
set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..") do set PROJECT_ROOT=%%~fI

REM --- Check for Python (python3 → python → py) ---
where python3 >nul 2>nul
if %errorlevel%==0 (
    set PYTHON_CMD=python3
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PYTHON_CMD=python
    ) else (
        where py >nul 2>nul
        if %errorlevel%==0 (
            set PYTHON_CMD=py
        ) else (
            echo ❌ Python 3 is required but not installed.
            pause
            exit /b 1
        )
    )
)

REM --- Check Python version ---
for /f "tokens=2" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set VER=%%v
for /f "tokens=1 delims=." %%a in ("%VER%") do set MAJOR=%%a
if !MAJOR! LSS 3 (
    echo ❌ Python 3.0 or higher is required. Found version %VER%.
    pause
    exit /b 1
)
echo ✅ Found Python %VER%

REM --- Create virtual environment ---
echo 📦 Creating virtual environment...
cd /d "%PROJECT_ROOT%"
%PYTHON_CMD% -m venv filesync_env

REM --- Activate virtual environment ---
echo 🔧 Activating virtual environment...
call "%PROJECT_ROOT%\filesync_env\Scripts\activate.bat"

REM --- Install project in editable mode ---
echo 📥 Installing FileSync...
pip install -e .

echo ✅ Installation complete!
echo.
echo To run FileSync manually:
echo   call filesync_env\Scripts\activate.bat
echo   filesync --gui
echo.
echo Or use the run script:
echo   scripts\run.bat
echo.
pause
endlocal
