# Instagram Helper - Development Automation Makefile
# This Makefile provides common development tasks and automation commands

.PHONY: help install install-dev test test-cov lint format clean setup setup-dev run install-browsers build check-all

# Default target - show help
help:
	@echo "Instagram Helper - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup          Install package with runtime dependencies only"
	@echo "  setup-dev      Install package with development dependencies"
	@echo "  install-browsers Install Playwright browsers for testing"
	@echo "  dev-setup      Complete development environment setup (setup-dev + browsers)"
	@echo ""
	@echo "Development Commands:"
	@echo "  test           Run the full test suite"
	@echo "  test-cov       Run tests with coverage reporting"
	@echo "  lint           Run code linting and style checks (ruff)"
	@echo "  format         Auto-format code according to style guidelines (ruff)"
	@echo "  format-readme  Format README.md with Prettier"
	@echo "  format-all     Format all code and documentation (ruff + prettier)"
	@echo "  check-all      Run all quality checks (lint + type-check + test)"
	@echo "  clean          Clean all build artifacts and cache files"
	@echo ""
	@echo "Build Commands:"
	@echo "  build          Build package distribution (wheel + source)"
	@echo ""
	@echo "Usage Commands:"
	@echo "  run            Run the application with help display"
	@echo "  help           Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make dev-setup    # Set up complete development environment"
	@echo "  make check-all    # Run all quality checks before committing"
	@echo "  make format-all   # Format all code and documentation"
	@echo "  make build       # Build package for distribution"

# Install with runtime dependencies only
setup:
	@echo "Installing package with runtime dependencies..."
	pip install -e .

# Install with development dependencies
setup-dev:
	@echo "Installing package with development dependencies..."
	pip install -e ".[dev]"

# Install Playwright browsers
install-browsers:
	@echo "Installing Playwright browsers..."
	playwright install

# Install Node.js dependencies
setup-node:
	@echo "Installing Node.js dependencies..."
	npm install

# Complete development setup
dev-setup: setup-dev setup-node install-browsers
	@echo ""
	@echo "Development environment setup complete!"
	@echo "To activate the virtual environment:"
	@echo "  source .venv/bin/activate"
	@echo ""
	@echo "Available commands:"
	@echo "  make test      # Run tests"
	@echo "  make lint      # Check code quality"
	@echo "  make format    # Format code"
	@echo "  make format-readme # Format README.md"

# Run tests
test:
	@echo "Running test suite..."
	pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage reporting..."
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Run linting
lint:
	@echo "Running code linting and style checks..."
	ruff check .

# Format code
format:
	@echo "Auto-formatting code..."
	ruff format .

# Run all quality checks
check-all: lint
	@echo "Running type checking..."
	mypy .
	@echo "Running tests..."
	make test
	@echo "All quality checks passed!"

# Format README.md with Prettier
format-readme:
	@echo "Formatting README.md with Prettier..."
	npm run format:readme

# Format all code and documentation
format-all: format format-readme
	@echo "All formatting complete!"

# Clean build artifacts and cache files
clean:
	@echo "Cleaning build artifacts and cache files..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleanup complete!"

# Build package distribution
build:
	@echo "Building package distribution..."
	python -m build
	@echo "Package built successfully!"
	@echo "Distribution files:"
	@ls -la dist/

# Run the application
run:
	@echo "Running Instagram Helper..."
	instagram-helper --help
