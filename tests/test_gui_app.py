"""Tests for gui_app.py using mock-based testing."""

import logging
import queue
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
import tkinter as tk

import pytest

from gui_app import InstagramHelperGUI, LogHandler, AccountDialog


class TestLogHandler:
    """Test the custom log handler."""

    def test_log_handler_initialization(self) -> None:
        """Test LogHandler initialization."""
        mock_queue = MagicMock()
        handler = LogHandler(mock_queue)
        assert handler.queue == mock_queue

    def test_log_handler_emit(self) -> None:
        """Test log handler emit method."""
        mock_queue = MagicMock()
        handler = LogHandler(mock_queue)

        # Create a mock log record
        mock_record = MagicMock()
        mock_record.getMessage.return_value = "Test log message"
        mock_record.getLevelName.return_value = "INFO"
        mock_record.getTime.return_value = 1234567890.0
        mock_record.getName.return_value = "test_logger"

        # Mock the formatter
        with patch.object(handler, 'formatter') as mock_formatter:
            mock_formatter.format.return_value = "Formatted log message"
            handler.emit(mock_record)

            mock_formatter.format.assert_called_once_with(mock_record)
            mock_queue.put.assert_called_once_with("Formatted log message")


class TestInstagramHelperGUI:
    """Test the main GUI application class."""

    @pytest.fixture
    def mock_tkinter(self) -> None:
        """Mock tkinter components."""
        with patch('gui_app.tk') as mock_tk, \
             patch('gui_app.ttk') as mock_ttk, \
             patch('gui_app.messagebox') as mock_messagebox, \
             patch('gui_app.scrolledtext') as mock_scrolledtext:

            # Mock Tk root
            mock_root = MagicMock()
            mock_tk.Tk.return_value = mock_root
            mock_tk.END = "end"  # Mock tk.END constant

            # Mock ttk components
            mock_frame = MagicMock()
            mock_ttk.Frame.return_value = mock_frame
            mock_ttk.LabelFrame.return_value = mock_frame
            mock_ttk.Button.return_value = MagicMock()
            mock_ttk.Entry.return_value = MagicMock()
            mock_ttk.Label.return_value = MagicMock()
            mock_ttk.Progressbar.return_value = MagicMock()

            # Mock scrolledtext
            mock_scrolledtext.ScrolledText.return_value = MagicMock()

            yield {
                'tk': mock_tk,
                'ttk': mock_ttk,
                'messagebox': mock_messagebox,
                'scrolledtext': mock_scrolledtext,
                'root': mock_root,
                'frame': mock_frame
            }

    @pytest.fixture
    def mock_dependencies(self) -> None:
        """Mock external dependencies."""
        with patch('gui_app.setup_browser') as mock_setup_browser, \
             patch('gui_app.InstagramScraper') as mock_scraper_class, \
             patch('gui_app.generate_html_report') as mock_generate_report, \
             patch('gui_app.settings') as mock_settings, \
             patch('gui_app.sync_playwright') as mock_sync_playwright:

            # Mock settings
            mock_settings.INSTAGRAM_ACCOUNTS = ["test_account1", "test_account2"]
            mock_settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT = 5
            mock_settings.INSTAGRAM_POST_LOAD_TIMEOUT = 10000
            mock_settings.update_instagram_settings = MagicMock()

            # Mock scraper
            mock_scraper = MagicMock()
            mock_scraper_class.return_value = mock_scraper

            # Mock browser setup
            mock_browser = MagicMock()
            mock_page = MagicMock()
            mock_browser.new_page.return_value = mock_page
            mock_setup_browser.return_value = (mock_browser, mock_page)

            # Mock playwright
            mock_playwright_instance = MagicMock()
            mock_playwright_instance.start.return_value = mock_browser
            mock_sync_playwright.return_value = mock_playwright_instance

            yield {
                'setup_browser': mock_setup_browser,
                'scraper_class': mock_scraper_class,
                'scraper': mock_scraper,
                'generate_report': mock_generate_report,
                'settings': mock_settings,
                'browser': mock_browser,
                'page': mock_page,
                'sync_playwright': mock_sync_playwright,
                'playwright_instance': mock_playwright_instance
            }

    def test_gui_initialization(self, mock_tkinter, mock_dependencies) -> None:
        """Test GUI application initialization."""
        with patch('gui_app.logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            app = InstagramHelperGUI()

            # Verify Tkinter setup
            mock_tkinter['tk'].Tk.assert_called_once()
            mock_tkinter['root'].title.assert_called_once_with("Instagram Helper")
            mock_tkinter['root'].geometry.assert_called_once_with("1400x700")
            mock_tkinter['root'].minsize.assert_called_once_with(1200, 600)

            # Verify variables initialization
            assert app.log_queue is not None
            assert app.scraping_thread is None
            assert app.stop_scraping is not None
            assert app.playwright is None
            assert app.browser is None

            # Verify logging setup
            mock_get_logger.assert_called()

    def test_setup_logging(self, mock_tkinter, mock_dependencies) -> None:
        """Test logging setup."""
        with patch('gui_app.logging.getLogger') as mock_get_logger, \
             patch('gui_app.LogHandler') as mock_handler_class:

            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_handler = MagicMock()
            mock_handler_class.return_value = mock_handler

            app = InstagramHelperGUI()

            # Verify logger configuration
            mock_logger.setLevel.assert_called_with(logging.INFO)
            mock_logger.addHandler.assert_called()

            # Verify handler setup for target loggers
            assert mock_get_logger.call_count >= 5  # Main logger + 4 target loggers

    def test_load_accounts_from_config(self, mock_tkinter, mock_dependencies) -> None:
        """Test loading accounts from configuration."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the account listbox
            app.account_listbox = MagicMock()

            # Call the method
            app.load_accounts_from_config()

            # Verify accounts were added to listbox
            assert app.account_listbox.insert.call_count == 2
            app.account_listbox.insert.assert_any_call("end", "test_account1")
            app.account_listbox.insert.assert_any_call("end", "test_account2")

    def test_add_account(self, mock_tkinter, mock_dependencies) -> None:
        """Test adding a new account."""
        with patch('gui_app.logging.getLogger'), \
             patch('gui_app.AccountDialog') as mock_dialog_class:

            mock_dialog = MagicMock()
            mock_dialog.result = "new_account"
            mock_dialog_class.return_value = mock_dialog

            app = InstagramHelperGUI()

            # Mock the account listbox and get_accounts method
            app.account_listbox = MagicMock()
            app.get_accounts = MagicMock(return_value=["existing_account"])

            # Call the method
            app.add_account()

            # Verify dialog was created
            mock_dialog_class.assert_called_once_with(app.root, "Add Account")

            # Verify account was added
            app.account_listbox.insert.assert_called_once_with("end", "new_account")

    def test_add_account_empty(self, mock_tkinter, mock_dependencies) -> None:
        """Test adding an empty account (should do nothing)."""
        with patch('gui_app.logging.getLogger'), \
             patch('gui_app.AccountDialog') as mock_dialog_class:

            mock_dialog = MagicMock()
            mock_dialog.result = ""
            mock_dialog_class.return_value = mock_dialog

            app = InstagramHelperGUI()

            # Mock the account listbox
            app.account_listbox = MagicMock()

            # Call the method
            app.add_account()

            # Verify nothing was added
            app.account_listbox.insert.assert_not_called()

    def test_add_account_duplicate(self, mock_tkinter, mock_dependencies) -> None:
        """Test adding a duplicate account (should do nothing)."""
        with patch('gui_app.logging.getLogger'), \
             patch('gui_app.AccountDialog') as mock_dialog_class:

            mock_dialog = MagicMock()
            mock_dialog.result = "existing_account"
            mock_dialog_class.return_value = mock_dialog

            app = InstagramHelperGUI()

            # Mock the account listbox and get_accounts method
            app.account_listbox = MagicMock()
            app.get_accounts = MagicMock(return_value=["existing_account"])

            # Call the method
            app.add_account()

            # Verify nothing was added
            app.account_listbox.insert.assert_not_called()

    def test_remove_account(self, mock_tkinter, mock_dependencies) -> None:
        """Test removing an account."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the account listbox
            app.account_listbox = MagicMock()
            app.account_listbox.curselection.return_value = [0]

            # Call the method
            app.remove_account()

            # Verify account was removed
            app.account_listbox.delete.assert_called_once_with(0)

    def test_remove_account_no_selection(self, mock_tkinter, mock_dependencies) -> None:
        """Test removing account with no selection (should do nothing)."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the account listbox
            app.account_listbox = MagicMock()
            app.account_listbox.curselection.return_value = []

            # Call the method
            app.remove_account()

            # Verify nothing was deleted
            app.account_listbox.delete.assert_not_called()

    def test_get_accounts(self, mock_tkinter, mock_dependencies) -> None:
        """Test getting accounts list."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the account listbox
            app.account_listbox = MagicMock()
            app.account_listbox.get.return_value = ["account1", "account2"]

            # Call the method
            result = app.get_accounts()

            # Verify result
            assert result == ["account1", "account2"]
            app.account_listbox.get.assert_called_once_with(0, "end")

    def test_get_settings_valid(self, mock_tkinter, mock_dependencies) -> None:
        """Test getting valid settings from GUI."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the GUI variables
            app.max_age_var = MagicMock()
            app.max_age_var.get.return_value = "30"
            app.max_posts_var = MagicMock()
            app.max_posts_var.get.return_value = "5"
            app.timeout_var = MagicMock()
            app.timeout_var.get.return_value = "10000"

            # Call the method
            result = app.get_settings()

            # Verify result
            assert result == {
                "max_age_days": 30,
                "max_posts_per_account": 5,
                "timeout_ms": 10000
            }

    def test_get_settings_invalid(self, mock_tkinter, mock_dependencies) -> None:
        """Test getting invalid settings from GUI."""
        with patch('gui_app.logging.getLogger'), \
             patch('gui_app.messagebox.showerror') as mock_showerror:

            app = InstagramHelperGUI()

            # Mock the GUI variables with invalid values
            app.max_age_var = MagicMock()
            app.max_age_var.get.return_value = "-5"
            app.max_posts_var = MagicMock()
            app.max_posts_var.get.return_value = "5"
            app.timeout_var = MagicMock()
            app.timeout_var.get.return_value = "10000"

            # Call the method
            result = app.get_settings()

            # Verify error was shown and result is None
            mock_showerror.assert_called_once()
            assert result is None

    def test_start_scraping(self, mock_tkinter, mock_dependencies) -> None:
        """Test starting the scraping process."""
        with patch('gui_app.logging.getLogger'), \
             patch('gui_app.threading.Thread') as mock_thread_class:

            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread

            app = InstagramHelperGUI()

            # Mock the required methods and attributes
            app.get_accounts = MagicMock(return_value=["test_account"])
            app.get_settings = MagicMock(return_value={
                "max_age_days": 30,
                "max_posts_per_account": 5,
                "timeout_ms": 10000
            })
            app.start_button = MagicMock()
            app.stop_button = MagicMock()
            app.progress_var = MagicMock()
            app.status_var = MagicMock()

            # Call the method
            app.start_scraping()

            # Verify thread was created and started
            mock_thread_class.assert_called_once()
            mock_thread.start.assert_called_once()

            # Verify UI state changes
            assert app.scraping_thread is not None
            app.start_button.config.assert_called_with(state="disabled")
            app.stop_button.config.assert_called_with(state="normal")

    def test_start_scraping_no_accounts(self, mock_tkinter, mock_dependencies) -> None:
        """Test starting scraping with no accounts."""
        with patch('gui_app.logging.getLogger'), \
             patch('gui_app.messagebox.showwarning') as mock_showwarning:

            app = InstagramHelperGUI()

            # Mock the get_accounts method to return empty list
            app.get_accounts = MagicMock(return_value=[])

            # Call the method
            app.start_scraping()

            # Verify warning was shown
            mock_showwarning.assert_called_once_with(
                "No Accounts", "Please add at least one Instagram account."
            )

    def test_start_scraping_no_settings(self, mock_tkinter, mock_dependencies) -> None:
        """Test starting scraping with invalid settings."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the required methods
            app.get_accounts = MagicMock(return_value=["test_account"])
            app.get_settings = MagicMock(return_value=None)  # Invalid settings

            # Call the method
            app.start_scraping()

            # Should return early without starting thread
            assert app.scraping_thread is None

    def test_stop_scraping_process(self, mock_tkinter, mock_dependencies) -> None:
        """Test stopping the scraping process."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the status variable
            app.status_var = MagicMock()

            # Call the method
            app.stop_scraping_process()

            # Verify stop event was set
            assert app.stop_scraping.is_set()
            app.status_var.set.assert_called_once_with("Stopping...")

    def test_poll_logs(self, mock_tkinter, mock_dependencies) -> None:
        """Test log polling functionality."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the log text widget and root
            app.log_text = MagicMock()
            app.root = MagicMock()

            # Mock the queue with some messages
            app.log_queue = MagicMock()
            app.log_queue.get_nowait.side_effect = ["Log message 1", "Log message 2", queue.Empty()]

            # Call the method
            app.poll_logs()

            # Verify log messages were processed
            assert app.log_text.insert.call_count == 2
            app.log_text.insert.assert_any_call("end", "Log message 1\n")
            app.log_text.insert.assert_any_call("end", "Log message 2\n")

            # Verify next poll was scheduled
            app.root.after.assert_called_once_with(100, app.poll_logs)

    def test_poll_logs_empty_queue(self, mock_tkinter, mock_dependencies) -> None:
        """Test log polling with empty queue."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the log text widget and root
            app.log_text = MagicMock()
            app.root = MagicMock()

            # Mock the queue as empty
            app.log_queue = MagicMock()
            app.log_queue.get_nowait.side_effect = queue.Empty()

            # Call the method
            app.poll_logs()

            # Verify no messages were processed
            app.log_text.insert.assert_not_called()

            # Verify next poll was scheduled
            app.root.after.assert_called_once_with(100, app.poll_logs)

    def test_clear_logs(self, mock_tkinter, mock_dependencies) -> None:
        """Test clearing log display."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the log text widget
            app.log_text = MagicMock()

            # Call the method
            app.clear_logs()

            # Verify logs were cleared
            app.log_text.delete.assert_called_once_with(1.0, "end")

    def test_get_browser_page(self, mock_tkinter, mock_dependencies) -> None:
        """Test getting browser page."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the browser
            mock_browser = MagicMock()
            mock_context = MagicMock()
            mock_page = MagicMock()

            mock_browser.contexts = [mock_context]
            mock_context.pages = [mock_page]

            # Call the method
            result = app._get_browser_page(mock_browser)

            # Verify result
            assert result == mock_page

    def test_get_browser_page_new_context(self, mock_tkinter, mock_dependencies) -> None:
        """Test getting browser page when no contexts exist."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the browser with no contexts
            mock_browser = MagicMock()
            mock_context = MagicMock()
            mock_page = MagicMock()

            mock_browser.contexts = []
            mock_browser.new_context.return_value = mock_context
            mock_context.pages = [mock_page]

            # Call the method
            result = app._get_browser_page(mock_browser)

            # Verify result
            assert result == mock_page
            mock_browser.new_context.assert_called_once()

    def test_get_browser_page_new_page(self, mock_tkinter, mock_dependencies) -> None:
        """Test getting browser page when no pages exist."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the browser
            mock_browser = MagicMock()
            mock_context = MagicMock()
            mock_page = MagicMock()

            mock_browser.contexts = [mock_context]
            mock_context.pages = []
            mock_context.new_page.return_value = mock_page

            # Call the method
            result = app._get_browser_page(mock_browser)

            # Verify result
            assert result == mock_page
            mock_context.new_page.assert_called_once()

    def test_run(self, mock_tkinter, mock_dependencies) -> None:
        """Test running the GUI application."""
        with patch('gui_app.logging.getLogger'):
            app = InstagramHelperGUI()

            # Mock the root window
            app.root = MagicMock()

            # Call the method
            app.run()

            # Verify mainloop was called
            app.root.mainloop.assert_called_once()


class TestAccountDialog:
    """Test the account dialog class."""

    @pytest.fixture
    def mock_tkinter(self) -> None:
        """Mock tkinter components."""
        with patch('gui_app.tk') as mock_tk, \
             patch('gui_app.ttk') as mock_ttk:

            # Mock Toplevel
            mock_dialog = MagicMock()
            mock_tk.Toplevel.return_value = mock_dialog

            # Mock ttk components
            mock_ttk.Label.return_value = MagicMock()
            mock_ttk.Entry.return_value = MagicMock()
            mock_ttk.Frame.return_value = MagicMock()
            mock_ttk.Button.return_value = MagicMock()

            yield {
                'tk': mock_tk,
                'ttk': mock_ttk,
                'dialog': mock_dialog
            }

    def test_dialog_initialization(self, mock_tkinter) -> None:
        """Test dialog initialization."""
        mock_parent = MagicMock()

        dialog = AccountDialog(mock_parent, "Test Dialog")

        # Verify dialog was created
        mock_tkinter['tk'].Toplevel.assert_called_once_with(mock_parent)
        mock_tkinter['dialog'].title.assert_called_once_with("Test Dialog")
        mock_tkinter['dialog'].geometry.assert_called()
        mock_tkinter['dialog'].transient.assert_called_once_with(mock_parent)
        mock_tkinter['dialog'].grab_set.assert_called_once()

    def test_ok_clicked(self, mock_tkinter) -> None:
        """Test OK button click."""
        mock_parent = MagicMock()

        dialog = AccountDialog(mock_parent, "Test Dialog")

        # Mock the entry widget
        dialog.entry = MagicMock()
        dialog.entry.get.return_value = "test_account"

        # Call the method
        dialog.ok_clicked()

        # Verify result was set and dialog destroyed
        assert dialog.result == "test_account"
        mock_tkinter['dialog'].destroy.assert_called_once()

    def test_cancel_clicked(self, mock_tkinter) -> None:
        """Test Cancel button click."""
        mock_parent = MagicMock()

        dialog = AccountDialog(mock_parent, "Test Dialog")

        # Call the method
        dialog.cancel_clicked()

        # Verify dialog was destroyed
        mock_tkinter['dialog'].destroy.assert_called_once()
