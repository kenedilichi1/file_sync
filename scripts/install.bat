@echo off
echo 🚀 Installing FileSync...

:: Try python3 first, then python, then py
python3 --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        py --version >nul 2>&1
        if errorlevel 1 (
            echo ❌ Python 3 is required but not installed. Please install Python 3.0 or higher.
            pause
            exit /b 1
        ) else (
            set PYTHON_CMD=py
        )
    ) else (
        set PYTHON_CMD=python
    )
) else (
    set PYTHON_CMD=python3
)

:: Check Python version
for /f "tokens=2" %%I in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%I
echo Found Python %PYTHON_VERSION%

:: Extract major version
for /f "tokens=1 delims=." %%A in ("%PYTHON_VERSION%") do set MAJOR_VERSION=%%A

:: Check if Python 3 or higher
if "%MAJOR_VERSION%" LSS "3" (
    echo ❌ Python 3.0 or higher is required. Current version: %PYTHON_VERSION%
    pause
    exit /b 1
)

:: Create virtual environment
echo 📦 Creating virtual environment...
%PYTHON_CMD% -m venv filesync_env

:: Activate virtual environment
echo 🔧 Activating virtual environment...
call filesync_env\Scripts\activate.bat

:: Install package
echo 📥 Installing FileSync...
pip install -e .

echo ✅ Installation complete!
echo.
echo To run FileSync:
echo   filesync_env\Scripts\activate.bat
echo   filesync --gui
echo.
echo Or use the run script:
echo   scripts\run.bat
pause