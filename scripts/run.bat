@echo off
setlocal ENABLEDELAYEDEXPANSION

set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..") do set PROJECT_ROOT=%%~fI

REM --- Check if virtual environment exists ---
if not exist "%PROJECT_ROOT%\filesync_env" (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

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
echo Please install Python 3.0+ and check "Add to PATH" during installation.
pause
exit /b 1

:found_python
echo ✅ Using Python command: %PYTHON_CMD%

REM --- Activate virtual environment ---
echo 🔧 Activating virtual environment...
call "%PROJECT_ROOT%\filesync_env\Scripts\activate.bat"

REM --- Run FileSync ---
echo 🚀 Starting FileSync...
cd /d "%PROJECT_ROOT%"
set PYTHONPATH=src

%PYTHON_CMD% -m src.cli %*
if errorlevel 1 (
    echo ❌ FileSync exited with an error.
    pause
    exit /b 1
)

endlocal
pause
