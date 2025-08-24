"""Tests for the main entry point."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from run import main


def test_main_success() -> None:
    """Test successful main function execution."""
    mock_gui = MagicMock()
    mock_gui.run = MagicMock()
    
    with patch('run.InstagramHelperGUI', return_value=mock_gui), \
         patch('builtins.print') as mock_print:
        
        main()
        
        mock_gui.run.assert_called_once()
        mock_print.assert_called_with("Launching Instagram Helper GUI...")


def test_main_import_error() -> None:
    """Test main function with import error."""
    with patch('run.InstagramHelperGUI', side_effect=ImportError("Module not found")), \
         patch('builtins.print') as mock_print, \
         patch('sys.exit') as mock_exit:
        
        main()
        
        # Check error messages
        mock_print.assert_any_call("Error importing required modules: Module not found")
        mock_print.assert_any_call("Please ensure all dependencies are installed:")
        mock_print.assert_any_call("  pip install -e .")
        mock_exit.assert_called_with(1)


def test_main_gui_error() -> None:
    """Test main function with GUI error."""
    mock_gui = MagicMock()
    mock_gui.run.side_effect = Exception("GUI failed to start")
    
    with patch('run.InstagramHelperGUI', return_value=mock_gui), \
         patch('builtins.print') as mock_print, \
         patch('sys.exit') as mock_exit:
        
        main()
        
        # Check error messages
        mock_print.assert_any_call("Error starting GUI: GUI failed to start")
        mock_exit.assert_called_with(1)


def test_main_gui_creation_error() -> None:
    """Test main function with GUI creation error."""
    with patch('run.InstagramHelperGUI', side_effect=Exception("Failed to create GUI")), \
         patch('builtins.print') as mock_print, \
         patch('sys.exit') as mock_exit:
        
        main()
        
        # Check error messages
        mock_print.assert_any_call("Error starting GUI: Failed to create GUI")
        mock_exit.assert_called_with(1)


def test_main_system_exit_handling() -> None:
    """Test that SystemExit is handled properly."""
    mock_gui = MagicMock()
    mock_gui.run.side_effect = SystemExit(0)
    
    with patch('run.InstagramHelperGUI', return_value=mock_gui), \
         patch('builtins.print') as mock_print:
        
        # Should not call sys.exit for SystemExit
        with pytest.raises(SystemExit):
            main()


def test_main_keyboard_interrupt_handling() -> None:
    """Test that KeyboardInterrupt is handled properly."""
    mock_gui = MagicMock()
    mock_gui.run.side_effect = KeyboardInterrupt()
    
    with patch('run.InstagramHelperGUI', return_value=mock_gui), \
         patch('builtins.print') as mock_print:
        
        # Should not call sys.exit for KeyboardInterrupt
        with pytest.raises(KeyboardInterrupt):
            main()


def test_main_import_error_different_message() -> None:
    """Test main function with different import error message."""
    with patch('run.InstagramHelperGUI', side_effect=ImportError("No module named 'tkinter'")), \
         patch('builtins.print') as mock_print, \
         patch('sys.exit') as mock_exit:
        
        main()
        
        # Check error messages
        mock_print.assert_any_call("Error importing required modules: No module named 'tkinter'")
        mock_print.assert_any_call("Please ensure all dependencies are installed:")
        mock_print.assert_any_call("  pip install -e .")
        mock_exit.assert_called_with(1)


def test_main_gui_error_different_message() -> None:
    """Test main function with different GUI error message."""
    with patch('run.InstagramHelperGUI', side_effect=Exception("Tkinter not available")), \
         patch('builtins.print') as mock_print, \
         patch('sys.exit') as mock_exit:
        
        main()
        
        # Check error messages
        mock_print.assert_any_call("Error starting GUI: Tkinter not available")
        mock_exit.assert_called_with(1)


def test_main_successful_execution_flow() -> None:
    """Test the complete successful execution flow."""
    mock_gui = MagicMock()
    mock_gui.run = MagicMock()
    
    with patch('run.InstagramHelperGUI', return_value=mock_gui), \
         patch('builtins.print') as mock_print:
        
        main()
        
        # Verify the complete flow
        mock_print.assert_called_with("Launching Instagram Helper GUI...")
        mock_gui.run.assert_called_once()


def test_main_error_handling_order() -> None:
    """Test that error handling follows the correct order."""
    # First test import error
    with patch('run.InstagramHelperGUI', side_effect=ImportError("Import failed")), \
         patch('builtins.print') as mock_print, \
         patch('sys.exit') as mock_exit:
        
        main()
        
        # Should handle ImportError first
        mock_print.assert_any_call("Error importing required modules: Import failed")
        mock_exit.assert_called_with(1)
        
        # Reset mocks
        mock_print.reset_mock()
        mock_exit.reset_mock()
    
    # Then test general exception
    with patch('run.InstagramHelperGUI', side_effect=Exception("General error")), \
         patch('builtins.print') as mock_print, \
         patch('sys.exit') as mock_exit:
        
        main()
        
        # Should handle general Exception second
        mock_print.assert_any_call("Error starting GUI: General error")
        mock_exit.assert_called_with(1)
