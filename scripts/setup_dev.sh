#!/bin/bash

# Instagram Helper - Development Environment Setup Script
# This script automates the setup of the development environment for WSL2
# It creates virtual environments, installs dependencies, and configures the project

set -e  # Exit on any error

echo "🚀 Instagram Helper - Development Environment Setup"
echo "=================================================="
echo ""

# Check if we're in WSL2 environment
if [[ -f /proc/version ]] && grep -q Microsoft /proc/version; then
    echo "✅ Detected WSL2 environment - optimizing for Windows integration"
    echo "   This will enable browser sharing with Windows Brave/Chrome"
else
    echo "⚠️  This script is optimized for WSL2, but will continue..."
    echo "   For best results, run this in WSL2 with Windows browser integration"
fi

echo ""

# Check Python version and compatibility
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "🐍 Python Environment Check"
echo "   Version: $PYTHON_VERSION"

# Verify Python version compatibility
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
    echo "   ✅ Python $PYTHON_VERSION is compatible (requires 3.9+)"
else
    echo "   ❌ Python $PYTHON_VERSION is not compatible (requires 3.9+)"
    echo "   Please upgrade Python and try again"
    exit 1
fi

echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "   ✅ Virtual environment created: .venv/"
else
    echo "✅ Virtual environment already exists: .venv/"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate
echo "   ✅ Virtual environment activated"

# Upgrade pip to latest version
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
echo "   ✅ Pip upgraded to $(pip --version | cut -d' ' -f2)"

# Install the package in editable mode with development dependencies
echo "📥 Installing package with development dependencies..."
echo "   This includes: pytest, ruff, mypy, coverage, and more"
pip install -e ".[dev]"
echo "   ✅ Development dependencies installed"

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
echo "   This includes: Chromium, Firefox, and WebKit for testing"
playwright install
echo "   ✅ Playwright browsers installed"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p output
mkdir -p reports
echo "   ✅ Directories created: logs/, output/, reports/"

# Set up pre-commit hooks if available
if command -v pre-commit &> /dev/null; then
    echo "🔗 Setting up pre-commit hooks..."
    pre-commit install
    echo "   ✅ Pre-commit hooks configured"
else
    echo "ℹ️  pre-commit not found, skipping hook setup"
    echo "   To install: pip install pre-commit"
fi

echo ""
echo "🎉 Development Environment Setup Complete!"
echo "========================================"
echo ""
echo "📋 Next Steps:"
echo "   1. Activate the virtual environment:"
echo "      source .venv/bin/activate"
echo ""
echo "   2. Verify the installation:"
echo "      make help              # Show available commands"
echo "      make test             # Run tests"
echo "      make lint             # Check code quality"
echo ""
echo "🔧 Available Commands:"
echo "   make help               # Show all available commands"
echo "   make test               # Run test suite"
echo "   make test-cov           # Run tests with coverage"
echo "   make lint               # Check code style and quality"
echo "   make format             # Auto-format code"
echo "   make check-all          # Run all quality checks"
echo "   make clean              # Clean build artifacts"
echo "   make build              # Build package distribution"
echo ""
echo "🌐 Browser Integration (WSL2):"
echo "   The project is configured to work with Windows browsers"
echo "   Start Brave/Chrome on Windows with remote debugging:"
echo "   brave.exe --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0"
echo ""
echo "📚 Documentation:"
echo "   README.md               # Project overview and usage"
echo "   pyproject.toml          # Project configuration"
echo "   .github/workflows/ci.yml # CI pipeline configuration"
echo ""
echo "🚀 Happy coding!"
