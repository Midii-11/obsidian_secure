@echo off
REM ObsidianSecure Launcher
REM This script launches the ObsidianSecure application

echo ================================================
echo ObsidianSecure - Secure Vault Encryption Tool
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or later from https://www.python.org/
    pause
    exit /b 1
)

echo Starting ObsidianSecure...
echo.

REM Run the application
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo Check that dependencies are installed: pip install -r requirements.txt
    pause
    exit /b 1
)
