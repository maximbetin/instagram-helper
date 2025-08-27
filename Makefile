.SILENT:
.DEFAULT_GOAL := help
.PHONY: help setup venv-ok lint lint-fix format format-check test coverage build rebuild run playwright-install clean clean-caches clean-venv

# --- Config -------------------------------------------------------------------
VENV    := venv
BIN     := $(VENV)\Scripts
PY      := "$(BIN)\python.exe"
PIP     := $(PY) -m pip
PYTEST  := $(PY) -m pytest
RUFF    := $(PY) -m ruff
MYPY    := $(PY) -m mypy
PYI     := $(PY) -m PyInstaller
STAMP   := $(VENV)\.ok
SPEC    := instagram_helper.spec
PYI_FLAGS := --noconfirm --clean

# --- Help ---------------------------------------------------------------------
help:
	echo Usage: make [target]
	echo Targets: setup | run | test | lint | lint-fix | format | format-check | coverage | build | rebuild | playwright-install | clean

# --- Environment ---------------------------------------------------------------
setup: $(STAMP)

# Recreate env when pyproject changes
$(STAMP): pyproject.toml
	echo Initializing development environment...
	python -m venv "$(VENV)"
	$(PIP) -q install -U pip
	$(PIP) -q install -e ".[dev]"
	$(PY) -m playwright install
	echo ok> $(STAMP)
	echo Development environment ready. Activate with:  . .\venv\Scripts\Activate.ps1

venv-ok: $(STAMP)

playwright-install: venv-ok
	$(PY) -m playwright install

# --- Quality / Test ------------------------------------------------------------
lint: venv-ok
	$(RUFF) check .
	$(MYPY) .

lint-fix: venv-ok
	$(RUFF) check . --fix

format: venv-ok
	$(RUFF) format .

format-check: venv-ok
	$(RUFF) format --check .

test: venv-ok
	$(PYTEST) tests/
	$(RUFF) check .
	$(RUFF) format --check .
	$(MYPY) .
	echo Tests and quality checks passed!

coverage: venv-ok
	$(PYTEST) --cov --cov-report=term-missing --cov-report=xml

# --- Build ---------------------------------------------------------------------
build: venv-ok
	echo Building executable with PyInstaller...
	if exist "$(SPEC)" ( $(PYI) $(PYI_FLAGS) "$(SPEC)" ) else ( $(PYI) $(PYI_FLAGS) -n InstagramHelper run.py )
	echo Executable built in dist\

rebuild: clean build

# --- Run -----------------------------------------------------------------------
run: venv-ok
	$(PY) run.py

# --- Clean ---------------------------------------------------------------------
clean: clean-caches clean-venv
	echo Complete cleanup finished! Run 'make setup' to recreate the environment.

clean-caches:
	echo Cleaning caches and build artifacts...
	if exist build rd /s /q build
	if exist dist rd /s /q dist
	if exist .coverage del /q .coverage
	if exist .pytest_cache rd /s /q .pytest_cache
	if exist .mypy_cache rd /s /q .mypy_cache
	if exist .ruff_cache rd /s /q .ruff_cache
	if exist htmlcov rd /s /q htmlcov
	if exist coverage.xml del /q coverage.xml
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
	for /d /r . %%d in (*.egg-info) do @if exist "%%d" rd /s /q "%%d"
	for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f"

clean-venv:
	if exist "$(STAMP)" del /q "$(STAMP)"
	if exist "$(VENV)\Scripts\deactivate.bat" call "$(VENV)\Scripts\deactivate.bat"
	if exist "$(VENV)" rd /s /q "$(VENV)"
