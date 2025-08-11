#!/bin/bash

# Instagram Helper Development Setup Script for WSL2
# This script sets up the development environment

set -e

echo "🚀 Setting up Instagram Helper development environment..."

# Check if we're in WSL2
if [[ -f /proc/version ]] && grep -q Microsoft /proc/version; then
    echo "✅ Detected WSL2 environment"
else
    echo "⚠️  This script is optimized for WSL2, but will continue..."
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "🐍 Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install the package in editable mode with dev dependencies
echo "📥 Installing package in editable mode with development dependencies..."
pip install -e ".[dev]"

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p output
mkdir -p reports

# Set up pre-commit hooks if available
if command -v pre-commit &> /dev/null; then
    echo "🔗 Setting up pre-commit hooks..."
    pre-commit install
else
    echo "ℹ️  pre-commit not found, skipping hook setup"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "To activate the environment in the future:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "To format code:"
echo "  ruff format ."
echo ""
echo "To lint code:"
echo "  ruff check ."
echo ""
echo "To run the application:"
echo "  instagram-helper --help"
