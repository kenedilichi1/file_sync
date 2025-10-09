@echo off
setlocal

set SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
set PROJECT_ROOT=%SCRIPT_DIR%\..

if not exist "%PROJECT_ROOT%\filesync_env" (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

call "%PROJECT_ROOT%\filesync_env\Scripts\activate.bat"
echo 🚀 Starting FileSync...
cd "%PROJECT_ROOT%"
set PYTHONPATH=src

:: Try python3 first, fall back to python
python3 -c "from cli import main; main()" %*
if errorlevel 1 (
    echo ℹ️  python3 not found, trying python...
    python -c "from cli import main; main()" %*
)

endlocal
