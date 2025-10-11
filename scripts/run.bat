@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting FileSync...

:: Get the directory of this script (e.g., scripts\)
set SCRIPT_DIR=%~dp0

:: Move up one folder to project root
pushd "%SCRIPT_DIR%\.."

:: Check that virtual environment exists
if not exist "filesync_env\Scripts\activate.bat" (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call "filesync_env\Scripts\activate.bat"

:: Set Python path so imports work
set PYTHONPATH=src

:: Detect available Python command
set PYTHON_CMD=

for %%P in (python python3 py) do (
    %%P --version >nul 2>&1 && (
        set PYTHON_CMD=%%P
        goto :FOUND_PYTHON
    )
)

echo ❌ Python not found. Please install Python 3.
pause
exit /b 1

:FOUND_PYTHON
echo 🐍 Using Python command: %PYTHON_CMD%

:: Run FileSync
%PYTHON_CMD% -m src.cli --gui

if errorlevel 1 (
    echo ❌ FileSync crashed or failed to start.
    pause
)

popd
endlocal
