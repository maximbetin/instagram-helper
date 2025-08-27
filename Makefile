# Makefile for Instagram Helper
.PHONY: help setup test clean build

# --- Help ---------------------------------------------------------------------
help:
	@echo Usage: make [target]
	@echo Targets:
	@echo    setup          Initialize development environment (create venv, install deps)
	@echo    test           Run tests and all quality checks
	@echo    clean          Remove build artifacts, cache files, and virtual environment
	@echo    build          Build executable with PyInstaller (includes templates)

# --- Setup --------------------------------------------------------------------
setup:
	@echo Initializing development environment...
	@python.exe -m venv venv
	@venv/Scripts/pip.exe install -e ".[dev]"
	@echo Development environment ready! Activate with '. .\venv\Scripts\Activate.ps1'

# --- Test ---------------------------------------------------------------------
test:
	@venv\Scripts\pytest.exe tests/
	@venv\Scripts\ruff.exe check .
	@venv\Scripts\ruff.exe format --check .
	@venv\Scripts\mypy.exe .
	@echo Tests and quality checks passed!

# --- Build --------------------------------------------------------------------
build:
	@echo Building executable with PyInstaller...
	@venv\Scripts\pyinstaller.exe instagram_helper.spec
	@echo Executable built successfully in dist/ directory!

# --- Clean --------------------------------------------------------------------
clean:
	@echo Cleaning up...
	@if exist build rmdir /s /q build
	@if exist dist rmdir /s /q dist
	@if exist .coverage del .coverage
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist .mypy_cache rmdir /s /q .mypy_cache
	@if exist .ruff_cache rmdir /s /q .ruff_cache
	@if exist htmlcov rmdir /s /q htmlcov
	@if exist coverage.xml del coverage.xml
	@if exist venv rmdir /s /q venv
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /s /q "%%d"
	@for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f"
	@echo Complete cleanup finished! Run 'make setup' to recreate the environment!
