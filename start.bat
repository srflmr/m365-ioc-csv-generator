@echo off
REM ==============================================================================
REM M365 IOC CSV Generator - Auto-Setup Launcher for Windows
REM This script automatically sets up the environment and launches the application.
REM Version: 2.5
REM ==============================================================================

SETLOCAL EnableDelayedExpansion

REM Change to script directory to ensure consistent paths
cd /d "%~dp0"

SET "APP_NAME=M365 IOC CSV Generator"
SET "VENV_DIR=.venv"
SET "PYTHON_CMD="
SET "LOG_FILE=setup.log"
SET "REQUIREMENTS_INSTALLED=.requirements_installed"

REM Header
echo.
echo ===============================================================================
echo   %APP_NAME%
echo   Auto-Setup Launcher v2.5
echo ===============================================================================
echo.

REM Check Python installation and version in one step
echo [1/5] Checking Python installation (requires 3.10+)...

REM Try multiple Python commands on Windows with version validation
for %%P in (python python3 py) do (
    %%P --version >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        REM Check if version is 3.10+ BEFORE accepting this command
        %%P -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
        if !ERRORLEVEL! equ 0 (
            set "PYTHON_CMD=%%P"
            goto :python_found
        )
    )
)

echo   [ERROR] Python 3.10+ is not installed or not in PATH
echo.
echo   Please install Python 3.10+ from: https://www.python.org/downloads/
echo   Make sure to check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:python_found
REM Defensive check: ensure PYTHON_CMD is set
if not defined PYTHON_CMD (
    echo   [ERROR] Internal error: PYTHON_CMD not set
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('%PYTHON_CMD% --version') do set PYTHON_VERSION=%%i
echo   [OK] Found %PYTHON_VERSION%
echo   [OK] Python version is compatible
echo.

REM Create virtual environment
echo [2/5] Setting up virtual environment...
set "VENV_CREATED=0"
if not exist "%VENV_DIR%" (
    echo   Creating virtual environment...

    REM Test if we can write to log file first
    echo. > "%LOG_FILE%" 2>nul
    if !ERRORLEVEL! neq 0 (
        echo   [ERROR] Cannot write to log file
        echo   Current directory: %CD%
        echo   Please check permissions and disk space
        pause
        exit /b 1
    )

    %PYTHON_CMD% -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
    if !ERRORLEVEL! neq 0 (
        echo   [ERROR] Failed to create virtual environment
        echo   Log file: %CD%\%LOG_FILE%
        echo.
        echo   Cleaning up partial virtual environment...
        rd /s /q "%VENV_DIR%" 2>nul
        echo.
        type "%LOG_FILE%"
        echo.
        pause
        exit /b 1
    )
    REM Verify venv was created successfully
    if not exist "%VENV_DIR%\Scripts\activate.bat" (
        echo   [ERROR] Virtual environment creation failed - activate.bat not found
        echo   Log file: %CD%\%LOG_FILE%
        echo.
        echo   Cleaning up partial virtual environment...
        rd /s /q "%VENV_DIR%" 2>nul
        echo.
        type "%LOG_FILE%"
        echo.
        pause
        exit /b 1
    )
    echo   [OK] Virtual environment created
    set "VENV_CREATED=1"
    del "%REQUIREMENTS_INSTALLED%" 2>nul
) else (
    REM Verify existing venv is valid
    if not exist "%VENV_DIR%\Scripts\activate.bat" (
        echo   [ERROR] Existing virtual environment is corrupted
        echo   Please delete the '.venv' folder and run this script again
        echo   Folder location: %CD%\%VENV_DIR%
        pause
        exit /b 1
    )
    echo   [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if !ERRORLEVEL! neq 0 (
    echo   [ERROR] Failed to activate virtual environment
    echo   Venv location: %CD%\%VENV_DIR%
    pause
    exit /b 1
)

REM CRITICAL FIX: Validate venv Python works
python --version >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo   [ERROR] Virtual environment Python is not working
    echo.
    echo   This can happen when:
    echo   - System Python was upgraded after venv was created
    echo   - Venv files are corrupted
    echo   - Venv is incomplete
    echo.
    echo   Please delete the '.venv' folder and run this script again:
    echo   rd /s /q .venv
    echo.
    echo   Venv location: %CD%\%VENV_DIR%
    pause
    exit /b 1
)

REM CRITICAL FIX: Validate venv Python version >= 3.10
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if !ERRORLEVEL! neq 0 (
    for /f "tokens=*" %%i in ('python --version') do set VENV_PYTHON_VERSION=%%i
    echo   [ERROR] Virtual environment Python version is incompatible
    echo   Found: %VENV_PYTHON_VERSION%
    echo   Required: 3.10 or higher
    echo.
    echo   This can happen when:
    echo   - Venv was created with older Python version
    echo   - System Python was upgraded
    echo.
    echo   Please delete the '.venv' folder and run this script again:
    echo   rd /s /q .venv
    echo.
    echo   Venv location: %CD%\%VENV_DIR%
    pause
    exit /b 1
)

echo   [OK] Virtual environment activated
echo   [OK] Virtual environment Python is working
echo.

REM Install dependencies
echo [4/5] Installing dependencies...

REM Check if dependencies need to be installed
REM Simplified logic: just check if marker file exists
REM Skip timestamp comparison to avoid CMD parsing issues
set "INSTALL_DEPENDENCIES=0"
if not exist "%REQUIREMENTS_INSTALLED%" (
    set "INSTALL_DEPENDENCIES=1"
)

if !INSTALL_DEPENDENCIES! equ 1 (
    echo   Installing packages (this may take a minute)...
    pip install -e . >> "%LOG_FILE%" 2>&1
    if !ERRORLEVEL! neq 0 (
        echo   [ERROR] Failed to install dependencies
        echo   Log file: %CD%\%LOG_FILE%
        echo.
        type "%LOG_FILE%"
        echo.
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
echo [5/5] Creating default directories...

REM Handle mkdir - already exists is OK, other errors are not
for %%D in (input output logs) do (
    if not exist "%%D" (
        mkdir "%%D" 2>nul
        if exist "%%D" (
            echo   [OK] Created %%D directory
        ) else (
            echo   [ERROR] Failed to create %%D directory
            pause
            exit /b 1
        )
    )
)
echo   [OK] Directories ready
echo.

REM Launch application
echo ===============================================================================
echo   Launching %APP_NAME%...
echo ===============================================================================
echo.
echo   Press Ctrl+C to exit the application
echo.

REM Use python from venv to ensure correct environment
python -m m365_ioc_csv

REM Handle exit code
if !ERRORLEVEL! neq 0 (
    echo.
    echo ===============================================================================
    echo   [ERROR] Application exited with errors
    echo   Check logs in 'logs' directory for details
    echo   Logs location: %CD%\logs\
    echo ===============================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo Thank you for using %APP_NAME%!
pause
