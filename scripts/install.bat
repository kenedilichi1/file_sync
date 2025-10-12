@echo off
setlocal ENABLEDELAYEDEXPANSION
echo 🚀 Installing FileSync...

REM --- Detect project root (one level above scripts folder) ---
set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..") do set PROJECT_ROOT=%%~fI

REM --- Try to find Python executable ---
set "PYTHON_CMD="
for %%P in (python3 python py) do (
    where %%P >nul 2>nul
    if !errorlevel! EQU 0 (
        set "PYTHON_CMD=%%P"
        goto :found_python
    )
)

echo ❌ Python 3 is required but not installed or not found in PATH.
echo Please install Python 3.0+ and check the "Add to PATH" option during installation.
pause
exit /b 1

:found_python
echo ✅ Using Python command: %PYTHON_CMD%

REM --- Check Python version ---
for /f "tokens=2 delims= " %%v in ('%PYTHON_CMD% --version 2^>^&1') do set VER=%%v
for /f "tokens=1 delims=." %%a in ("%VER%") do set MAJOR=%%a
if "!MAJOR!" LSS "3" (
    echo ❌ Python 3.0 or higher is required. Found version %VER%.
    pause
    exit /b 1
)
echo ✅ Detected Python version %VER%

REM --- Create virtual environment ---
echo 📦 Creating virtual environment...
cd /d "%PROJECT_ROOT%"
%PYTHON_CMD% -m venv filesync_env

REM --- Activate virtual environment ---
echo 🔧 Activating virtual environment...
call "%PROJECT_ROOT%\filesync_env\Scripts\activate.bat"

REM --- Install package in editable mode ---
echo 📥 Installing FileSync...
pip install -e .

echo ✅ Installation complete!
echo.
echo To run FileSync manually:
echo   call filesync_env\Scripts\activate.bat
echo   python src\cli.py --gui
echo.
echo Or use the run script:
echo   scripts\run.bat
echo.
pause
endlocal
