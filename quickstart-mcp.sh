#!/usr/bin/env bash
# Quick start script for the LangGraph MCP Server

set -e

echo "🚀 LangGraph MCP Server - Quick Start"
echo "======================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ uv found"

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
uv sync

echo ""
echo "✓ Dependencies installed"

# Run tests
echo ""
echo "🧪 Running tests..."
uv run pytest tests/test_mcp_server.py -v

echo ""
echo "✓ Tests passed"

# Show available commands
echo ""
echo "🎯 Available Commands:"
echo "======================================"
echo ""
echo "1. Run MCP Server (stdio):"
echo "   uv run python mcp_server.py"
echo ""
echo "2. Run MCP Inspector (web UI):"
echo "   uv run mcp dev mcp_server.py"
echo ""
echo "3. Install to MCP config:"
echo "   uv run mcp install mcp_server.py"
echo ""
echo "4. Run tests:"
echo "   uv run pytest tests/test_mcp_server.py -v"
echo ""
echo "📚 Documentation: backend/README_MCP.md"
echo ""
