@echo off
setlocal

set SCRIPT_DIR=%~dp0
rem Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

set PROJECT_ROOT=%SCRIPT_DIR%\..

:: Check if virtual environment exists
if not exist "%PROJECT_ROOT%\filesync_env" (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call "%PROJECT_ROOT%\filesync_env\Scripts\activate.bat"

echo 🚀 Starting FileSync...

:: Run FileSync as a Python module (so relative imports work)
cd "%PROJECT_ROOT%"
python -m src.cli %*

endlocal
