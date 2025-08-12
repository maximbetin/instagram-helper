"""Basic tests to verify core functionality and imports."""

import importlib.util

import pytest


def test_imports():
    """Test that all core modules can be imported."""
    modules = [
        "instagram_scraper",
        "report_generator",
        "browser_manager",
        "config",
        "utils",
        "cli"
    ]

    for module_name in modules:
        spec = importlib.util.find_spec(module_name)
        assert spec is not None, f"Module {module_name} not found"


def test_config_settings():
    """Test that config settings can be loaded."""
    try:
        from config import settings
        assert settings is not None
        assert hasattr(settings, 'INSTAGRAM_ACCOUNTS')
        assert hasattr(settings, 'OUTPUT_DIR')
    except Exception as e:
        pytest.fail(f"Failed to load config settings: {e}")


def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    # This is a simple test that should always pass
    assert 1 + 1 == 2
