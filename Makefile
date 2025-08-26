# Makefile for Instagram Helper

.PHONY: help init test format clean run

# Default target
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  init           Initialize development environment (create venv, install deps)"
	@echo "  test           Run tests and all quality checks"
	@echo "  format         Format code with ruff"
	@echo "  clean          Remove build artifacts, cache files, and virtual environment"
	@echo "  run            Run the GUI application"

# --- Setup --------------------------------------------------------------------
init:
	@echo "Initializing development environment..."
	@python -m venv venv
	@./venv/bin/pip install -e ".[dev]"
	@echo "Development environment ready. Activate with 'source venv/bin/activate'"

# --- Testing & Quality --------------------------------------------------------
test:
	@echo "Running tests and quality checks..."
	@./venv/bin/pytest tests/
	@echo "Running code quality checks..."
	@./venv/bin/ruff check .
	@./venv/bin/ruff format --check .
	@./venv/bin/mypy .
	@echo "All tests and quality checks passed."

format:
	@echo "Formatting code..."
	@./venv/bin/ruff format .

# --- Cleanup ------------------------------------------------------------------
clean:
	@echo "Cleaning up..."
	@rm -rf build dist .coverage .pytest_cache .mypy_cache .ruff_cache htmlcov coverage.xml venv
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Complete cleanup finished. Run 'make init' to recreate the environment."

# --- Run ----------------------------------------------------------------------
run:
	@echo "Running GUI application..."
	@./venv/bin/python gui_app.py
