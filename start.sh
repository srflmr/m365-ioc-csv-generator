#!/bin/bash
# ==============================================================================
# M365 IOC CSV Generator - Auto-Setup Launcher for Linux/Mac
# This script automatically sets up the environment and launches the application.
# Version: 2.3
# ==============================================================================

# Change to script directory to ensure consistent paths
cd "$(dirname "$0")" || exit 1

APP_NAME="M365 IOC CSV Generator"
VENV_DIR=".venv"
PYTHON_CMD=""
LOG_FILE="setup.log"
REQUIREMENTS_INSTALLED=".requirements_installed"
SCRIPT_DIR="$(pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display log file safely (check for binary data)
safe_display_log() {
    local log_file="$1"
    local lines="${2:-20}"

    if [ ! -f "$log_file" ]; then
        return
    fi

    # Check if file is text (not binary)
    if file "$log_file" 2>/dev/null | grep -q "text\|ASCII\|UTF-8"; then
        if [ "$lines" = "all" ]; then
            cat "$log_file" | sed 's/^/  /'
        else
            tail -"$lines" "$log_file" | sed 's/^/  /'
        fi
    else
        echo "  Log file contains binary or non-text data"
        echo "  Use a hexdump viewer or text editor to inspect:"
        echo "    less $log_file"
        echo "    hexdump -C $log_file | head -20"
    fi
}

# Function to find Python command with version validation
find_python_cmd() {
    # Try python3, python, py (Windows launcher), python.exe (Git Bash)
    for cmd in python3 python py python.exe; do
        if command -v "$cmd" &> /dev/null; then
            # Check if version is 3.10+ BEFORE accepting this command
            if $cmd -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# Function to handle errors with full context
handle_error() {
    local exit_code=$1
    local step_name="$2"
    if [ $exit_code -ne 0 ]; then
        echo -e "${RED}[ERROR] $step_name failed${NC}"
        echo "  Log file: $SCRIPT_DIR/$LOG_FILE"
        if [ -f "$SCRIPT_DIR/$LOG_FILE" ]; then
            echo ""
            echo "  Last 20 lines of log:"
            safe_display_log "$SCRIPT_DIR/$LOG_FILE" 20
        fi
        exit 1
    fi
}

# Header
echo ""
echo "==============================================================================="
echo "  $APP_NAME"
echo "  Auto-Setup Launcher v2.3"
echo "==============================================================================="
echo ""

# Check Python installation and version in one step
echo -e "${YELLOW}[1/5] Checking Python installation (requires 3.10+)...${NC}"
PYTHON_CMD=$(find_python_cmd)
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}[ERROR] Python 3.10+ is not installed${NC}"
    echo ""
    echo "Please install Python 3.10+:"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-venv"
    echo "  - Fedora/RHEL:   sudo dnf install python3 python3-venv"
    echo "  - macOS:         brew install python3"
    echo "  - Windows:       https://www.python.org/downloads/"
    echo ""
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "${GREEN}[OK] Found $PYTHON_VERSION${NC}"
echo -e "${GREEN}[OK] Python version is compatible${NC}"
echo ""

# Create virtual environment
echo -e "${YELLOW}[2/5] Setting up virtual environment...${NC}"
VENV_CREATED=0
if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating virtual environment..."

    # Test if we can write to log file first
    touch "$LOG_FILE" 2>/dev/null || {
        echo -e "${RED}[ERROR] Cannot write to log file${NC}"
        echo "  Current directory: $SCRIPT_DIR"
        echo "  Please check permissions and disk space"
        exit 1
    }

    $PYTHON_CMD -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1
    VENV_EXIT_CODE=$?

    if [ $VENV_EXIT_CODE -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment${NC}"
        echo "  Log file: $SCRIPT_DIR/$LOG_FILE"
        echo ""
        echo "  Cleaning up partial virtual environment..."
        rm -rf "$VENV_DIR" 2>/dev/null
        echo ""
        echo "  Error details:"
        safe_display_log "$LOG_FILE" "all"
        echo ""
        echo ""
        echo "  Possible causes:"
        echo "  - python3-venv package not installed (install with: sudo apt install python3-venv)"
        echo "  - Insufficient permissions"
        echo "  - Disk space issue"
        exit 1
    fi

    # Verify venv was created successfully by checking for activate script
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        echo -e "${RED}[ERROR] Virtual environment creation failed${NC}"
        echo "  The 'bin/activate' file was not created"
        echo "  Venv location: $SCRIPT_DIR/$VENV_DIR"
        echo "  Log file: $SCRIPT_DIR/$LOG_FILE"
        echo ""
        echo "  Cleaning up partial virtual environment..."
        rm -rf "$VENV_DIR" 2>/dev/null
        echo ""
        echo "  Error details:"
        safe_display_log "$LOG_FILE" "all"
        exit 1
    fi

    echo -e "${GREEN}[OK] Virtual environment created${NC}"
    VENV_CREATED=1
    rm -f "$REQUIREMENTS_INSTALLED"
else
    # Verify existing venv is valid
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        echo -e "${RED}[ERROR] Existing virtual environment is corrupted${NC}"
        echo "  Please delete the '.venv' directory and run this script again"
        echo "  Venv location: $SCRIPT_DIR/$VENV_DIR"
        exit 1
    fi
    echo -e "${GREEN}[OK] Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}[3/5] Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to activate virtual environment${NC}"
    echo "  Venv location: $SCRIPT_DIR/$VENV_DIR"
    exit 1
fi

# CRITICAL FIX: Validate venv Python works
python --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Virtual environment Python is not working${NC}"
    echo ""
    echo "  This can happen when:"
    echo "  - System Python was upgraded after venv was created"
    echo "  - Venv files are corrupted"
    echo "  - Venv is incomplete"
    echo ""
    echo "  Please delete the '.venv' directory and run this script again:"
    echo "    rm -rf .venv"
    echo ""
    echo "  Venv location: $SCRIPT_DIR/$VENV_DIR"
    exit 1
fi

# CRITICAL FIX: Validate venv Python version >= 3.10
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    VENV_PYTHON_VERSION=$(python --version)
    echo -e "${RED}[ERROR] Virtual environment Python version is incompatible${NC}"
    echo "  Found: $VENV_PYTHON_VERSION"
    echo "  Required: 3.10 or higher"
    echo ""
    echo "  This can happen when:"
    echo "  - Venv was created with older Python version"
    echo "  - System Python was upgraded"
    echo ""
    echo "  Please delete the '.venv' directory and run this script again:"
    echo "    rm -rf .venv"
    echo ""
    echo "  Venv location: $SCRIPT_DIR/$VENV_DIR"
    exit 1
fi

echo -e "${GREEN}[OK] Virtual environment activated${NC}"
echo -e "${GREEN}[OK] Virtual environment Python is working${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}[4/5] Installing dependencies...${NC}"

# Check if dependencies need to be installed
INSTALL_DEPENDENCIES=0
if [ ! -f "$REQUIREMENTS_INSTALLED" ]; then
    INSTALL_DEPENDENCIES=1
else
    # Check if pyproject.toml exists and is newer
    if [ -f "pyproject.toml" ]; then
        if [ "pyproject.toml" -nt "$REQUIREMENTS_INSTALLED" ]; then
            echo "  [INFO] pyproject.toml has been updated"
            INSTALL_DEPENDENCIES=1
        fi
    fi
fi

if [ $INSTALL_DEPENDENCIES -eq 1 ]; then
    echo "  Installing packages (this may take a minute)..."
    pip install -e . >> "$LOG_FILE" 2>&1
    handle_error $? "Dependency installation"
    touch "$REQUIREMENTS_INSTALLED"
    echo -e "${GREEN}[OK] Dependencies installed${NC}"
else
    echo -e "${GREEN}[OK] Dependencies already installed (skipping)${NC}"
fi
echo ""

# Create default directories with error checking
echo -e "${YELLOW}[5/5] Creating default directories...${NC}"
for dir in input output logs; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir" 2>> "$LOG_FILE" || {
            echo -e "${RED}[ERROR] Failed to create $dir directory${NC}"
            echo "  Please check permissions"
            exit 1
        }
        echo -e "  ${GREEN}[OK] Created $dir directory${NC}"
    fi
done
echo -e "${GREEN}[OK] Directories ready${NC}"
echo ""

# Launch application
echo "==============================================================================="
echo "  Launching $APP_NAME..."
echo "==============================================================================="
echo ""
echo -e "${BLUE}Press Ctrl+C to exit the application${NC}"
echo ""

# Run the app and capture exit code
# Use python from venv to ensure correct environment
python -m m365_ioc_csv
APP_EXIT_CODE=$?

# Handle exit code
if [ $APP_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "==============================================================================="
    echo -e "${RED}[ERROR] Application exited with errors${NC}"
    echo "  Check logs in 'logs' directory for details"
    echo "  Logs location: $SCRIPT_DIR/logs/"
    echo "==============================================================================="
    echo ""
    exit 1
fi

echo ""
echo "Thank you for using $APP_NAME!"
