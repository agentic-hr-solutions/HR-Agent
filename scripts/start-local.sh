#!/bin/bash

# Start Azure Functions Local Development Server
# This script ensures the correct working directory and Python version

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Navigate to backend directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../backend"

cd "$BACKEND_DIR"

echo -e "${GREEN}🚀 Starting Azure Functions Local Server${NC}"
echo "Working directory: $(pwd)"
echo ""

# Check for required files
if [ ! -f "host.json" ]; then
    echo "❌ host.json not found in $(pwd)"
    exit 1
fi

if [ ! -f "function_app.py" ]; then
    echo "❌ function_app.py not found in $(pwd)"
    exit 1
fi

if [ ! -f "local.settings.json" ]; then
    echo -e "${YELLOW}⚠️  local.settings.json not found, creating from .env...${NC}"
    ../scripts/sync-env.sh
fi

echo "✅ All required files found"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "✅ Activating Python virtual environment..."
    source .venv/bin/activate
    PYTHON_PATH=$(which python)
    echo "Python: $PYTHON_PATH"
    
    # Force Azure Functions to use venv Python
    export languageWorkers__python__defaultExecutablePath="$PYTHON_PATH"
else
    echo -e "${YELLOW}⚠️  No virtual environment found, using system Python${NC}"
fi

# Start Functions
echo -e "${GREEN}Starting Azure Functions Core Tools...${NC}"
echo "API will be available at: http://localhost:7071"
echo ""
echo "Press Ctrl+C to stop"
echo ""

exec func start
