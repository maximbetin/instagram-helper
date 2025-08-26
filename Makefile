# Makefile for Instagram Helper

.PHONY: help init test format clean run build-exe

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
	@echo "  build-exe      Build executable with PyInstaller (includes templates)"

# --- Setup --------------------------------------------------------------------
init:
	@echo "Initializing development environment..."
	@python.exe -m venv venv
	@venv/Scripts/pip.exe install -e ".[dev]"
	@echo "Development environment ready. Activate with 'venv\\Scripts\\activate'"

# --- Testing & Quality --------------------------------------------------------
test:
	@echo "Running tests and quality checks..."
	@venv/Scripts/pytest.exe tests/
	@echo "Running code quality checks..."
	@venv/Scripts/ruff.exe check .
	@venv/Scripts/ruff.exe format --check .
	@venv/Scripts/mypy.exe .
	@echo "All tests and quality checks passed."

format:
	@echo "Formatting code..."
	@venv/Scripts/ruff.exe format .

# --- Build --------------------------------------------------------------------
build-exe:
	@echo "Building executable with PyInstaller..."
	@venv/Scripts/pyinstaller.exe instagram_helper.spec
	@echo "Executable built successfully in dist/ directory"

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
	@venv/Scripts/python.exe gui_app.py
