@echo off
setlocal ENABLEDELAYEDEXPANSION

set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..") do set PROJECT_ROOT=%%~fI

REM --- Check that venv exists ---
if not exist "%PROJECT_ROOT%\filesync_env\" (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

REM --- Activate virtual environment ---
call "%PROJECT_ROOT%\filesync_env\Scripts\activate.bat"
echo 🚀 Starting FileSync...
cd /d "%PROJECT_ROOT%"
set PYTHONPATH=src

REM --- Run the app (point to cli.py directly) ---
python src\cli.py %*
if %errorlevel% neq 0 (
    echo ❌ FileSync exited with an error code %errorlevel%.
)

echo.
pause
endlocal
