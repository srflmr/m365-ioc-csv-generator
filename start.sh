#!/bin/bash
# ==============================================================================
# M365 IOC CSV Generator - Auto-Setup Launcher for Linux/Mac
# This script automatically sets up the environment and launches the application.
# ==============================================================================

APP_NAME="M365 IOC CSV Generator"
VENV_DIR="venv"
PYTHON_CMD=""
LOG_FILE="setup.log"
REQUIREMENTS_INSTALLED=".requirements_installed"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to find Python command
find_python_cmd() {
    # Try python3 first, then python
    for cmd in python3 python; do
        if command -v "$cmd" &> /dev/null; then
            # Check if version is 3.10+
            if $cmd -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# Function to handle errors
handle_error() {
    local exit_code=$1
    local step_name="$2"
    if [ $exit_code -ne 0 ]; then
        echo -e "${RED}[ERROR] $step_name failed${NC}"
        echo "  Check $LOG_FILE for details"
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

# Check Python installation
echo -e "${YELLOW}[1/6] Checking Python installation...${NC}"
PYTHON_CMD=$(find_python_cmd)
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}[ERROR] Python 3.10+ is not installed${NC}"
    echo ""
    echo "Please install Python 3.10+:"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-venv"
    echo "  - Fedora/RHEL:   sudo dnf install python3 python3-venv"
    echo "  - macOS:         brew install python3"
    echo ""
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "${GREEN}[OK] Found $PYTHON_VERSION${NC}"
echo ""

# Check Python version (minimum 3.10)
echo -e "${YELLOW}[2/6] Validating Python version...${NC}"
if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo -e "${RED}[ERROR] Python 3.10 or higher is required${NC}"
    $PYTHON_CMD --version
    echo ""
    echo "Please install a newer version of Python"
    exit 1
fi
echo -e "${GREEN}[OK] Python version is compatible${NC}"
echo ""

# Create virtual environment
echo -e "${YELLOW}[3/6] Setting up virtual environment...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1
    VENV_EXIT_CODE=$?

    if [ $VENV_EXIT_CODE -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment${NC}"
        echo "  Check $LOG_FILE for details"
        exit 1
    fi

    # Verify venv was created successfully by checking for activate script
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        echo -e "${RED}[ERROR] Virtual environment creation failed${NC}"
        echo "  The 'bin/activate' file was not created"
        echo "  Check $LOG_FILE for details"
        echo ""
        echo "  Possible causes:"
        echo "  - python3-venv package not installed (install with: sudo apt install python3-venv)"
        echo "  - Insufficient permissions"
        echo "  - Disk space issue"
        exit 1
    fi

    echo -e "${GREEN}[OK] Virtual environment created${NC}"
    rm -f "$REQUIREMENTS_INSTALLED"
else
    # Verify existing venv is valid
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        echo -e "${RED}[ERROR] Existing virtual environment is corrupted${NC}"
        echo "  Please delete the 'venv' directory and run this script again"
        exit 1
    fi
    echo -e "${GREEN}[OK] Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}[4/6] Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
handle_error $? "Virtual environment activation"
echo -e "${GREEN}[OK] Virtual environment activated${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}[5/6] Installing dependencies...${NC}"
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

# Create default directories
echo -e "${YELLOW}[6/6] Creating default directories...${NC}"
mkdir -p input output logs 2>> "$LOG_FILE"
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
python -m m365_ioc_csv
APP_EXIT_CODE=$?

# Handle exit code
if [ $APP_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "==============================================================================="
    echo -e "${RED}[ERROR] Application exited with errors${NC}"
    echo "  Check logs in 'logs' directory for details"
    echo "==============================================================================="
    echo ""
    exit 1
fi

echo ""
echo "Thank you for using $APP_NAME!"
