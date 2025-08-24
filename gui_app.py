"""Instagram Helper GUI Application."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from config import settings
from playwright.sync_api import sync_playwright, Browser, Page
from browser_manager import setup_browser
from instagram_scraper import InstagramScraper
from report_generator import ReportData, generate_html_report


class LogHandler(logging.Handler):
    """Custom log handler that sends log messages to a queue for GUI display."""

    def __init__(self, queue: queue.Queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        msg = self.format(record)
        self.queue.put(msg)


class InstagramHelperGUI:
    """Main GUI application for Instagram Helper."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Instagram Helper")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # Initialize variables
        self.log_queue = queue.Queue()
        self.scraping_thread: Optional[threading.Thread] = None
        self.stop_scraping = threading.Event()
        self.playwright: Optional[sync_playwright] = None
        self.browser: Optional[Browser] = None

        # Setup logging
        self.setup_logging()

        # Create GUI
        self.create_widgets()
        self.setup_layout()

        # Start log polling
        self.poll_logs()

        # Test logging to ensure both GUI and file logging work
        self.test_logging()

        # Load initial accounts
        self.load_accounts_from_config()

    def setup_logging(self):
        """Setup logging to capture messages for GUI display."""
        # Create a logger for the application
        self.logger = logging.getLogger("instagram_helper_gui")
        self.logger.setLevel(logging.INFO)

        # Add our custom handler
        log_handler = LogHandler(self.log_queue)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(log_handler)

                # Capture messages from specific loggers we care about, but don't interfere with root logger
        # This ensures file logging continues to work
        target_loggers = [
            "instagram_scraper",
            "browser_manager",
            "report_generator",
            "utils"
        ]

        for logger_name in target_loggers:
            logger = logging.getLogger(logger_name)
            # Add our handler without clearing existing ones
            # This preserves file logging while adding GUI display
            logger.addHandler(log_handler)

    def test_logging(self):
        """Test that logging is working properly for both GUI and file output."""
        # Test GUI logging
        self.logger.info("GUI logging test - this should appear in the GUI")

        # Test that other loggers still work
        test_logger = logging.getLogger("instagram_scraper")
        test_logger.info("Instagram scraper logging test - this should appear in both GUI and log files")

        # Test file logging specifically
        file_test_logger = logging.getLogger("file_test")
        if not file_test_logger.handlers:
            # Set up file logging for this test logger
            from utils import setup_logging
            file_test_logger = setup_logging("file_test", settings.LOG_DIR)
            file_test_logger.info("File logging test - this should appear in log files")

    def create_widgets(self):
        """Create all GUI widgets."""
                # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")

        # Control frame
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="10")

        # Start/Stop buttons
        self.start_button = ttk.Button(self.control_frame, text="Start Scraping", command=self.start_scraping)
        self.stop_button = ttk.Button(self.control_frame, text="Stop Scraping", command=self.stop_scraping_process, state="disabled")

        # Settings frame
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding="10")

        # Max post age
        ttk.Label(self.settings_frame, text="Max Post Age (days):").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.max_age_var = tk.StringVar(value="7")
        self.max_age_entry = ttk.Entry(self.settings_frame, textvariable=self.max_age_var, width=10)
        self.max_age_entry.grid(row=0, column=1, sticky="w", padx=(0, 10))

        # Max posts per account
        ttk.Label(self.settings_frame, text="Max Posts per Account:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.max_posts_var = tk.StringVar(value=str(settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT))
        self.max_posts_entry = ttk.Entry(self.settings_frame, textvariable=self.max_posts_var, width=10)
        self.max_posts_entry.grid(row=0, column=3, sticky="w", padx=(0, 10))

        # Timeout
        ttk.Label(self.settings_frame, text="Post Load Timeout (ms):").grid(row=0, column=4, sticky="w", padx=(0, 5))
        self.timeout_var = tk.StringVar(value=str(settings.INSTAGRAM_POST_LOAD_TIMEOUT))
        self.timeout_entry = ttk.Entry(self.settings_frame, textvariable=self.timeout_var, width=10)
        self.timeout_entry.grid(row=0, column=5, sticky="w")

        # Accounts frame
        self.accounts_frame = ttk.LabelFrame(self.main_frame, text="Instagram Accounts", padding="10")

        # Account list
        self.account_listbox = tk.Listbox(self.accounts_frame, height=8, selectmode=tk.EXTENDED)
        self.account_scrollbar = ttk.Scrollbar(self.accounts_frame, orient="vertical", command=self.account_listbox.yview)
        self.account_listbox.configure(yscrollcommand=self.account_scrollbar.set)

        # Account control buttons
        self.account_buttons_frame = ttk.Frame(self.accounts_frame)
        self.add_account_button = ttk.Button(self.account_buttons_frame, text="Add Account", command=self.add_account)
        self.remove_account_button = ttk.Button(self.account_buttons_frame, text="Remove Selected", command=self.remove_account)
        self.load_accounts_button = ttk.Button(self.account_buttons_frame, text="Load from Config", command=self.load_accounts_from_config)

        # Logs frame
        self.logs_frame = ttk.LabelFrame(self.main_frame, text="Logs", padding="10")

        # Log text area
        self.log_text = scrolledtext.ScrolledText(self.logs_frame, height=15, width=80)

        # Clear logs button
        self.clear_logs_button = ttk.Button(self.logs_frame, text="Clear Logs", command=self.clear_logs)

        # Progress frame
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Progress", padding="10")

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.progress_frame, textvariable=self.status_var)

        # Load initial accounts
        self.load_accounts_from_config()

    def setup_layout(self):
        """Setup the layout of all widgets."""
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        self.main_frame.grid_rowconfigure(0, weight=0)
        title_label = ttk.Label(self.main_frame, text="Instagram Helper", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Control frame
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.control_frame.grid_columnconfigure(1, weight=1)

        self.start_button.grid(row=0, column=0, padx=(0, 10))
        self.stop_button.grid(row=0, column=1)

        # Settings frame
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.settings_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Accounts frame
        self.main_frame.grid_rowconfigure(3, weight=0)
        self.accounts_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.accounts_frame.grid_columnconfigure(0, weight=1)

        self.account_listbox.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.account_scrollbar.grid(row=0, column=1, sticky="ns")

        self.account_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        self.add_account_button.grid(row=0, column=0, padx=(0, 5))
        self.remove_account_button.grid(row=0, column=1, padx=(0, 5))
        self.load_accounts_button.grid(row=0, column=2)

        # Logs frame
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.logs_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        self.logs_frame.grid_columnconfigure(0, weight=1)
        self.logs_frame.grid_rowconfigure(0, weight=1)

        self.log_text.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.clear_logs_button.grid(row=1, column=0, pady=(10, 0))

        # Progress frame
        self.main_frame.grid_rowconfigure(5, weight=0)
        self.progress_frame.grid(row=5, column=0, columnspan=2, sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.status_label.grid(row=1, column=0, sticky="w")

    def load_accounts_from_config(self):
        """Load accounts from the configuration file."""
        self.account_listbox.delete(0, tk.END)
        for account in settings.INSTAGRAM_ACCOUNTS:
            self.account_listbox.insert(tk.END, account)

    def add_account(self):
        """Add a new account to the list."""
        dialog = AccountDialog(self.root, "Add Instagram Account")
        if dialog.result:
            account = dialog.result.strip()
            if account and account not in self.get_accounts():
                self.account_listbox.insert(tk.END, account)

    def remove_account(self):
        """Remove selected accounts from the list."""
        selection = self.account_listbox.curselection()
        if selection:
            # Remove from end to avoid index shifting issues
            for index in reversed(selection):
                self.account_listbox.delete(index)

    def get_accounts(self) -> list[str]:
        """Get the current list of accounts."""
        return list(self.account_listbox.get(0, tk.END))

    def get_settings(self) -> dict:
        """Get current settings from the GUI."""
        try:
            max_age = int(self.max_age_var.get())
            max_posts = int(self.max_posts_var.get())
            timeout = int(self.timeout_var.get())

            if max_age <= 0 or max_posts <= 0 or timeout <= 0:
                raise ValueError("All values must be positive integers")

            return {
                "max_age_days": max_age,
                "max_posts_per_account": max_posts,
                "timeout_ms": timeout
            }
        except ValueError as e:
            messagebox.showerror("Invalid Settings", f"Please check your settings: {e}")
            return None

    def start_scraping(self):
        """Start the scraping process in a separate thread."""
        accounts = self.get_accounts()
        if not accounts:
            messagebox.showwarning("No Accounts", "Please add at least one Instagram account.")
            return

        settings_dict = self.get_settings()
        if not settings_dict:
            return

        # Disable start button, enable stop button
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting...")

        # Start scraping thread
        self.scraping_thread = threading.Thread(
            target=self.scraping_worker,
            args=(accounts, settings_dict),
            daemon=True
        )
        self.scraping_thread.start()

    def stop_scraping_process(self):
        """Stop the scraping process."""
        self.stop_scraping.set()
        self.status_var.set("Stopping...")

    def scraping_worker(self, accounts: list[str], settings_dict: dict):
        """Worker thread for scraping."""
        try:
            self.logger.info("Starting Instagram scraping process...")

            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=settings_dict["max_age_days"])
            self.logger.info(f"Cutoff date: {cutoff_date}")

            # Update settings with GUI values
            settings.update_instagram_settings(
                settings_dict["max_posts_per_account"],
                settings_dict["timeout_ms"]
            )

            # Initialize browser
            self.playwright = sync_playwright()
            self.browser = setup_browser(self.playwright.start())
            page = self._get_browser_page(self.browser)

            if not page:
                self.logger.error("Failed to initialize browser")
                return

            # Create scraper
            scraper = InstagramScraper(page, settings)

            # Process accounts
            total_accounts = len(accounts)
            all_posts = []

            for i, account in enumerate(accounts):
                if self.stop_scraping.is_set():
                    self.logger.info("Scraping stopped by user")
                    break

                self.logger.info(f"Processing account {i+1}/{total_accounts}: @{account}")

                # Update progress
                progress = (i / total_accounts) * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                self.root.after(0, lambda s=f"Processing @{account}...": self.status_var.set(s))

                # Scrape posts
                posts = scraper.process_account(account, cutoff_date)
                all_posts.extend(posts)

                self.logger.info(f"Found {len(posts)} posts for @{account}")

            # Generate report
            if all_posts and not self.stop_scraping.is_set():
                self.logger.info("Generating HTML report...")
                self.root.after(0, lambda: self.status_var.set("Generating report..."))

                report_data = ReportData(posts=all_posts, cutoff_date=cutoff_date)
                output_path = Path(settings.OUTPUT_DIR) / f"{datetime.now().strftime('%d-%m-%Y')}.html"
                generate_html_report(report_data, output_path, settings.TEMPLATE_PATH)

                self.logger.info(f"Report generated: {output_path}")

            # Update final status
            if self.stop_scraping.is_set():
                self.root.after(0, lambda: self.status_var.set("Stopped"))
            else:
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: self.status_var.set(f"Complete - {len(all_posts)} posts found"))

        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))
        finally:
            # Cleanup
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

            # Re-enable start button, disable stop button
            self.root.after(0, lambda: self.start_button.config(state="normal"))
            self.root.after(0, lambda: self.stop_button.config(state="disabled"))

    def poll_logs(self):
        """Poll the log queue and update the log display."""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        finally:
            # Schedule next poll
            self.root.after(100, self.poll_logs)

    def _get_browser_page(self, browser: Browser) -> Page:
        """Retrieves or creates a browser page."""
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        return context.pages[0] if context.pages else context.new_page()

    def clear_logs(self):
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


class AccountDialog:
    """Simple dialog for adding Instagram accounts."""

    def __init__(self, parent, title):
        self.result = None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        # Create widgets
        ttk.Label(self.dialog, text="Enter Instagram account name:").pack(pady=(20, 5))

        self.entry = ttk.Entry(self.dialog, width=30)
        self.entry.pack(pady=(0, 20))
        self.entry.focus()

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack()

        ttk.Button(button_frame, text="Add", command=self.ok_clicked).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT)

        # Bind Enter key
        self.entry.bind("<Return>", lambda e: self.ok_clicked())

        # Wait for dialog to close
        self.dialog.wait_window()

    def ok_clicked(self):
        """Handle OK button click."""
        self.result = self.entry.get()
        self.dialog.destroy()

    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.dialog.destroy()


def main():
    """Main entry point for the GUI application."""
    app = InstagramHelperGUI()
    app.run()


if __name__ == "__main__":
    main()
