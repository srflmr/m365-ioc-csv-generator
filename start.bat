@echo off
REM ==============================================================================
REM M365 IOC CSV Generator - Auto-Setup Launcher for Windows
REM This script automatically sets up the environment and launches the application.
REM ==============================================================================

SETLOCAL EnableDelayedExpansion
SET "APP_NAME=M365 IOC CSV Generator"
SET "VENV_DIR=venv"
SET "PYTHON_CMD=python"
SET "LOG_FILE=setup.log"
SET "REQUIREMENTS_INSTALLED=.requirements_installed"

REM Header
echo.
echo ===============================================================================
echo   %APP_NAME%
echo   Auto-Setup Launcher v2.0
echo ===============================================================================
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo   [ERROR] Python is not installed or not in PATH
    echo.
    echo   Please install Python 3.10+ from: https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('%PYTHON_CMD% --version') do set PYTHON_VERSION=%%i
echo   [OK] Found %PYTHON_VERSION%
echo.

REM Check Python version (minimum 3.10)
echo [2/6] Validating Python version...
%PYTHON_CMD% check_python_version.py
if %ERRORLEVEL% neq 0 (
    echo   [ERROR] Python 3.10 or higher is required
    %PYTHON_CMD% --version
    echo.
    echo   Please install a newer version of Python
    pause
    exit /b 1
)
echo   [OK] Python version is compatible
echo.

REM Create virtual environment
echo [3/6] Setting up virtual environment...
if not exist "%VENV_DIR%" (
    echo   Creating virtual environment...
    %PYTHON_CMD% -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% neq 0 (
        echo   [ERROR] Failed to create virtual environment
        echo   Check %LOG_FILE% for details
        pause
        exit /b 1
    )
    REM Verify venv was created successfully
    if not exist "%VENV_DIR%\Scripts\activate.bat" (
        echo   [ERROR] Virtual environment creation failed - activate.bat not found
        echo   Check %LOG_FILE% for details
        pause
        exit /b 1
    )
    echo   [OK] Virtual environment created
    del "%REQUIREMENTS_INSTALLED%" 2>nul
) else (
    REM Verify existing venv is valid
    if not exist "%VENV_DIR%\Scripts\activate.bat" (
        echo   [ERROR] Existing virtual environment is corrupted
        echo   Please delete the 'venv' folder and run this script again
        pause
        exit /b 1
    )
    echo   [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [4/6] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo   [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo   [OK] Virtual environment activated
echo.

REM Install dependencies
echo [5/6] Installing dependencies...
if not exist "%REQUIREMENTS_INSTALLED%" (
    echo   Installing packages (this may take a minute)...
    pip install -e . >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% neq 0 (
        echo   [ERROR] Failed to install dependencies
        echo   Check %LOG_FILE% for details
        pause
        exit /b 1
    )
    echo. > "%REQUIREMENTS_INSTALLED%"
    echo   [OK] Dependencies installed
) else (
    echo   [OK] Dependencies already installed (skipping)
)
echo.

REM Create default directories
echo [6/6] Creating default directories...
if not exist "input" mkdir input
if not exist "output" mkdir output
if not exist "logs" mkdir logs
echo   [OK] Directories ready
echo.

REM Launch application
echo ===============================================================================
echo   Launching %APP_NAME%...
echo ===============================================================================
echo.
echo   Press Ctrl+C to exit the application
echo.

python -m m365_ioc_csv

REM Handle exit code
if %ERRORLEVEL% neq 0 (
    echo.
    echo ===============================================================================
    echo   [ERROR] Application exited with errors
    echo   Check logs in 'logs' directory for details
    echo ===============================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo Thank you for using %APP_NAME%!
pause
