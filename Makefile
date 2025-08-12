# Makefile for Instagram Helper

.PHONY: help setup-dev test lint format type-check check-all clean run

# Default target
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  setup-dev      Set up the development environment"
	@echo "  test           Run tests with pytest"
	@echo "  lint           Lint code with ruff"
	@echo "  format         Format code with ruff"
	@echo "  type-check     Run static type checking with mypy"
	@echo "  check-all      Run all quality checks (format, lint, type-check, test)"
	@echo "  clean          Remove build artifacts and cache files"
	@echo "  run            Run the CLI tool with --help"
	@echo ""
	@echo "Quick Run Shortcuts:"
	@echo "  quick-run      Run with default settings (3 days, headless)"
	@echo "  quick-run-interactive  Run with default settings (3 days, interactive)"
	@echo "  run-week       Run for last 7 days (headless)"
	@echo "  run-month      Run for last 30 days (headless)"

# --- Setup --------------------------------------------------------------------
setup-dev:
	@echo "Setting up development environment..."
	@python -m venv venv
	@./venv/bin/pip install -e ".[dev]"
	@echo "Development environment created. Activate with 'source venv/bin/activate'"

# --- Quality Checks -----------------------------------------------------------
test:
	@echo "Running tests..."
	@./venv/bin/pytest tests/

lint:
	@echo "Linting code..."
	@./venv/bin/ruff check .

format:
	@echo "Formatting code..."
	@./venv/bin/ruff format .

type-check:
	@echo "Running type checks..."
	@./venv/bin/mypy .

check-all: format lint type-check test
	@echo "All quality checks passed."

# --- Miscellaneous ------------------------------------------------------------
clean:
	@echo "Cleaning up..."
	@rm -rf build dist .coverage .pytest_cache .mypy_cache .ruff_cache htmlcov
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

run:
	@echo "Running CLI tool..."
	@./venv/bin/python cli.py --help

# --- Quick Run Shortcuts -----------------------------------------------------
# Ensure venv exists and is set up before running
ensure-venv:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Creating one..."; \
		python3 -m venv venv; \
		./venv/bin/pip install -e ".[dev]"; \
		echo "Development environment created."; \
	fi

quick-run: ensure-venv
	@echo "Running Instagram Helper with default settings (last 3 days, headless)..."
	@./venv/bin/python cli.py --days 3 --headless
	@echo "Done! Check the output directory for your report."

quick-run-interactive: ensure-venv
	@echo "Running Instagram Helper with default settings (last 3 days, interactive)..."
	@./venv/bin/python cli.py --days 3
	@echo "Done! Check the output directory for your report."

run-week: ensure-venv
	@echo "Running Instagram Helper for last 7 days (headless)..."
	@./venv/bin/python cli.py --days 7 --headless
	@echo "Done! Check the output directory for your report."

run-month: ensure-venv
	@echo "Running Instagram Helper for last 30 days (headless)..."
	@./venv/bin/python cli.py --days 30 --headless
	@echo "Done! Check the output directory for your report."
