"""Integration tests for the main function."""

from main import main
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path to allow absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@patch('main.os.startfile')
@patch('main.generate_html_report', return_value='report.html')
@patch('main.process_account', return_value=[{'post': 1}])
@patch('main.setup_browser')
@patch('main.sync_playwright')
def test_main(mock_playwright, mock_setup_browser, mock_process, mock_generate_report, mock_startfile):
    """Test the main execution function."""
    mock_p = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_p
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_browser.contexts[0].pages[0] = mock_page
    mock_setup_browser.return_value = mock_browser

    main()

    assert mock_process.called
    mock_generate_report.assert_called_once()
    mock_startfile.assert_called_once_with('report.html')


@patch('main.generate_html_report')
@patch('main.process_account', return_value=[])
@patch('main.setup_browser')
@patch('main.sync_playwright')
def test_main_no_posts(mock_playwright, mock_setup_browser, mock_process, mock_generate_report):
    """Test the main execution function when no posts are found."""
    mock_p = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_p
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_browser.contexts[0].pages[0] = mock_page
    mock_setup_browser.return_value = mock_browser

    main()

    assert mock_process.called
    mock_generate_report.assert_not_called()


def test_main_econnrefused_branch(monkeypatch):
    """Covers the ECONNREFUSED error branch in main()."""
    class DummyContextManager:
        def __enter__(self):
            class DummyBrowser:
                contexts = [[type('Pg', (), {})()]]
            return DummyBrowser()

        def __exit__(self, exc_type, exc_val, exc_tb): return False

    def fake_setup_browser(*a, **k):
        raise Exception("ECONNREFUSED")

    monkeypatch.setattr('main.sync_playwright', lambda: DummyContextManager())
    monkeypatch.setattr('main.setup_browser', fake_setup_browser)
    monkeypatch.setattr('main.INSTAGRAM_ACCOUNTS', ['test'])
    monkeypatch.setattr('main.process_account', lambda *a, **k: [])
    monkeypatch.setattr('main.generate_html_report', lambda *a, **k: 'report.html')
    monkeypatch.setattr('main.os.startfile', lambda *a, **k: None)

    from unittest.mock import patch
    main_logger_calls = []
    with patch('main.logger') as mock_logger:
        def log_side_effect(*args, **kwargs):
            main_logger_calls.append(args[0])
        mock_logger.error.side_effect = log_side_effect
        main()
    assert any("Failed to connect to the browser" in msg for msg in main_logger_calls)


def test_main_generic_error_branch(monkeypatch):
    """Covers the generic error/raise branch in main()."""
    class DummyContextManager:
        def __enter__(self):
            class DummyBrowser:
                contexts = [[type('Pg', (), {})()]]
            return DummyBrowser()

        def __exit__(self, exc_type, exc_val, exc_tb): return False

    def fake_setup_browser(*a, **k):
        raise Exception("Some other error")

    monkeypatch.setattr('main.sync_playwright', lambda: DummyContextManager())
    monkeypatch.setattr('main.setup_browser', fake_setup_browser)
    monkeypatch.setattr('main.INSTAGRAM_ACCOUNTS', ['test'])
    monkeypatch.setattr('main.process_account', lambda *a, **k: [])
    monkeypatch.setattr('main.generate_html_report', lambda *a, **k: 'report.html')
    monkeypatch.setattr('main.os.startfile', lambda *a, **k: None)

    from unittest.mock import patch

    import pytest
    main_logger_calls = []
    with patch('main.logger') as mock_logger:
        def log_side_effect(*args, **kwargs):
            main_logger_calls.append(args[0])
        mock_logger.error.side_effect = log_side_effect
        with pytest.raises(Exception, match="Some other error"):
            main()
    assert any("An error occurred:" in msg for msg in main_logger_calls)


def test_main_exact_econnrefused(monkeypatch):
    """Guarantee coverage for the ECONNREFUSED error branch in main()."""
    class DummyContextManager:
        def __enter__(self):
            class DummyBrowser:
                contexts = [[type('Pg', (), {})()]]
            return DummyBrowser()

        def __exit__(self, exc_type, exc_val, exc_tb): return False

    def fake_setup_browser(*a, **k):
        raise Exception("ECONNREFUSED")

    monkeypatch.setattr('main.sync_playwright', lambda: DummyContextManager())
    monkeypatch.setattr('main.setup_browser', fake_setup_browser)
    monkeypatch.setattr('main.INSTAGRAM_ACCOUNTS', ['test'])
    monkeypatch.setattr('main.process_account', lambda *a, **k: [])
    monkeypatch.setattr('main.generate_html_report', lambda *a, **k: 'report.html')
    monkeypatch.setattr('main.os.startfile', lambda *a, **k: None)

    from unittest.mock import patch
    main_logger_calls = []
    with patch('main.logger') as mock_logger:
        def log_side_effect(*args, **kwargs):
            main_logger_calls.append(args[0])
        mock_logger.error.side_effect = log_side_effect
        main()
    assert any("Failed to connect to the browser" in msg for msg in main_logger_calls)
