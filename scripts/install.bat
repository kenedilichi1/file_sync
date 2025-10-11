@echo off
echo 🚀 Installing FileSync...

:: Always switch to the project root (one level above "scripts")
cd /d "%~dp0\.."

:: Detect Python command
set "PYTHON_CMD="

python3 --version >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=python3"
) else (
    python --version >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    ) else (
        py --version >nul 2>&1
        if %errorlevel%==0 (
            set "PYTHON_CMD=py"
        ) else (
            echo ❌ Python 3 is required but not installed. Please install Python 3.0 or higher.
            pause
            exit /b 1
        )
    )
)

:: Display detected Python version
for /f "tokens=2" %%I in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%I
echo ✅ Found Python %PYTHON_VERSION%

:: Extract major version
for /f "tokens=1 delims=." %%A in ("%PYTHON_VERSION%") do set MAJOR_VERSION=%%A

:: Check if version >= 3
if "%MAJOR_VERSION%" LSS "3" (
    echo ❌ Python 3.0 or higher is required. Current version: %PYTHON_VERSION%
    pause
    exit /b 1
)

:: Create virtual environment
echo 📦 Creating virtual environment (filesync_env)...
%PYTHON_CMD% -m venv filesync_env

if not exist "filesync_env" (
    echo ❌ Failed to create virtual environment.
    pause
    exit /b 1
)

:: Activate the environment
echo 🔧 Activating virtual environment...
call filesync_env\Scripts\activate.bat

:: Install FileSync package
echo 📥 Installing FileSync in editable mode...
pip install -e .

if %errorlevel% neq 0 (
    echo ❌ Installation failed.
    pause
    exit /b 1
)

echo ✅ Installation complete!
echo.
echo To run FileSync manually:
echo   call filesync_env\Scripts\activate.bat
echo   filesync --gui
echo.
echo Or simply run:
echo   scripts\run.bat
echo.
pause
