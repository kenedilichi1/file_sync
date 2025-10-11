@echo off
setlocal

echo 🚀 Installing FileSync...

:: Detect Python command
set PYTHON_CMD=

for %%P in (python python3 py) do (
    %%P --version >nul 2>&1 && (
        set PYTHON_CMD=%%P
        goto :FOUND_PYTHON
    )
)

echo ❌ Python 3 is required but not installed.
pause
exit /b 1

:FOUND_PYTHON
for /f "tokens=2 delims= " %%V in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%V
echo Found Python %PYTHON_VERSION%

:: Create virtual environment
echo 📦 Creating virtual environment...
%PYTHON_CMD% -m venv filesync_env

:: Activate venv
if exist filesync_env\Scripts\activate.bat (
    echo 🔧 Activating virtual environment...
    call filesync_env\Scripts\activate.bat
) else (
    echo ❌ Failed to create virtual environment.
    pause
    exit /b 1
)

:: Install package from project root
echo 📥 Installing FileSync...
pushd "%~dp0\.." 
pip install --upgrade pip
pip install -e .
popd

if errorlevel 1 (
    echo ❌ Installation failed.
    pause
    exit /b 1
)

echo ✅ Installation complete!
echo.
echo To run FileSync:
echo   call filesync_env\Scripts\activate.bat
echo   filesync --gui
echo.
pause
endlocal
