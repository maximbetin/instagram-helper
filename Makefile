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
	@echo "  run            Run the GUI application"
	@echo ""
	@echo "Quick Run Shortcuts:"
	@echo "  run-gui        Run the Instagram Helper GUI"

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
	@echo "Running GUI application..."
	@./venv/bin/python gui_app.py

# --- Quick Run Shortcuts -----------------------------------------------------
# Ensure venv exists and is set up before running
ensure-venv:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Creating one..."; \
		python3 -m venv venv; \
		./venv/bin/pip install -e ".[dev]"; \
		echo "Development environment created."; \
	fi

run-gui: ensure-venv
	@echo "Running Instagram Helper GUI..."
	@./venv/bin/python gui_app.py
