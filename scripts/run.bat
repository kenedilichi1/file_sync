@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting FileSync...

REM --- Get project root (one level up from scripts folder)
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%\.."
set PROJECT_ROOT=%cd%

REM --- Check if virtual environment exists ---
if not exist "%PROJECT_ROOT%\filesync_env" (
    echo ❌ Virtual environment not found.
    echo 💡 Please run install.bat first to set up the environment.
    pause
    exit /b 1
)

REM --- Activate the virtual environment ---
call "%PROJECT_ROOT%\filesync_env\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment.
    echo 🔧 Try running "install.bat" again.
    pause
    exit /b 1
)

REM --- Move to project root ---
cd "%PROJECT_ROOT%"
set PYTHONPATH=src

REM --- Detect Python command ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python not found. Please ensure it's installed and added to PATH.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

REM --- Run the FileSync main entry point ---
echo 🖥️  Launching GUI...
%PYTHON_CMD% -m src.cli --gui
if errorlevel 1 (
    echo ❌ FileSync failed to start.
    pause
    exit /b 1
)

endlocal
