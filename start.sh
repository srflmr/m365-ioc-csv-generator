#!/bin/bash
# ==============================================================================
# M365 IOC CSV Generator - Auto-Setup Launcher for Linux/Mac
# This script automatically sets up the environment and launches the application.
# ==============================================================================

APP_NAME="M365 IOC CSV Generator"
VENV_DIR=".venv"
PYTHON_CMD=""
LOG_FILE="setup.log"
REQUIREMENTS_INSTALLED=".requirements_installed"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
            tail -20 "$SCRIPT_DIR/$LOG_FILE" | sed 's/^/  /'
        fi
        exit 1
    fi
}

# Header
echo ""
echo "==============================================================================="
echo "  $APP_NAME"
echo "  Auto-Setup Launcher v2.0"
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
        echo "  Error details:"
        cat "$LOG_FILE" | sed 's/^/  /'
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
        echo "  Error details:"
        cat "$LOG_FILE" | sed 's/^/  /'
        exit 1
    fi

    echo -e "${GREEN}[OK] Virtual environment created${NC}"
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
echo -e "${GREEN}[OK] Virtual environment activated${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}[4/5] Installing dependencies...${NC}"
if [ ! -f "$REQUIREMENTS_INSTALLED" ]; then
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
mkdir -p input 2>> "$LOG_FILE" || {
    echo -e "${RED}[ERROR] Failed to create input directory${NC}"
    echo "  Please check permissions"
    exit 1
}
mkdir -p output 2>> "$LOG_FILE" || {
    echo -e "${RED}[ERROR] Failed to create output directory${NC}"
    echo "  Please check permissions"
    exit 1
}
mkdir -p logs 2>> "$LOG_FILE" || {
    echo -e "${RED}[ERROR] Failed to create logs directory${NC}"
    echo "  Please check permissions"
    exit 1
}
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
