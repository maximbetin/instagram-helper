.PHONY: help install install-dev test test-cov lint format clean setup setup-dev run install-browsers

# Default target
help:
	@echo "Instagram Helper - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  setup          Install package with runtime dependencies"
	@echo "  setup-dev      Install package with development dependencies"
	@echo "  install-browsers Install Playwright browsers"
	@echo ""
	@echo "Development:"
	@echo "  test           Run tests"
	@echo "  test-cov       Run tests with coverage"
	@echo "  lint           Run linting (ruff)"
@echo "  format         Format code (ruff)"
	@echo "  clean          Clean build artifacts"
	@echo ""
	@echo "Usage:"
	@echo "  run            Run the application"
	@echo "  help           Show this help message"

# Install with runtime dependencies
setup:
	pip install -e .

# Install with development dependencies
setup-dev:
	pip install -e ".[dev]"

# Install Playwright browsers
install-browsers:
	playwright install

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=. --cov-report=html --cov-report=term-missing

# Run linting
lint:
	ruff check .

# Format code
format:
	ruff format .

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the application
run:
	instagram-helper --help

# Full development setup
dev-setup: setup-dev install-browsers
	@echo "Development environment setup complete!"
	@echo "Run 'source venv/bin/activate' to activate the virtual environment"
