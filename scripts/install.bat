@echo off
setlocal enabledelayedexpansion
echo 🚀 Installing FileSync...

REM --- Get project root (one level up from scripts folder)
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%\.."
set PROJECT_ROOT=%cd%

REM --- Try to detect Python command ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python 3 is required but not installed. Please install Python 3.0 or higher.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

REM --- Check Python version ---
for /f "tokens=2 delims= " %%i in ('%PYTHON_CMD% --version 2^>^&1') do set VERSION=%%i
for /f "tokens=1 delims=." %%a in ("%VERSION%") do set MAJOR=%%a
if "%MAJOR%" LSS "3" (
    echo ❌ Python 3 or higher is required. Found version %VERSION%
    pause
    exit /b 1
)
echo ✅ Found Python %VERSION%

REM --- Create or reuse virtual environment ---
if not exist "%PROJECT_ROOT%\filesync_env" (
    echo 📦 Creating virtual environment...
    %PYTHON_CMD% -m venv "%PROJECT_ROOT%\filesync_env"
) else (
    echo ♻️  Reusing existing virtual environment...
)

REM --- Activate virtual environment ---
echo 🔧 Activating virtual environment...
call "%PROJECT_ROOT%\filesync_env\Scripts\activate.bat"

REM --- Upgrade pip ---
echo ⚙️  Upgrading pip...
pip install --upgrade pip

REM --- Install dependencies if available ---
if exist "%PROJECT_ROOT%\requirements.txt" (
    echo 📥 Installing dependencies from requirements.txt...
    pip install -r "%PROJECT_ROOT%\requirements.txt"
) else (
    echo ⚠️  No requirements.txt found, skipping dependency installation.
)

REM --- Install FileSync in editable mode ---
echo 📦 Installing FileSync package...
pip install -e "%PROJECT_ROOT%"

echo ✅ Installation complete!
echo.
echo To run FileSync:
echo   call filesync_env\Scripts\activate.bat
echo   filesync --gui
echo.
echo Or just run:
echo   scripts\run.bat
echo.
pause
endlocal
