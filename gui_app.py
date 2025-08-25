"""Instagram Helper GUI Application."""

import logging
import queue
import threading
import tkinter as tk
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk
from typing import Any

from playwright.sync_api import Browser, Page, sync_playwright

from browser_manager import setup_browser
from config import settings
from instagram_scraper import InstagramScraper
from report_generator import ReportData, generate_html_report


class LogHandler(logging.Handler):
    """Custom log handler that sends log messages to a queue for GUI display."""

    def __init__(self, queue: queue.Queue) -> None:
        super().__init__()
        self.queue = queue

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.queue.put(msg)


class InstagramHelperGUI:
    """Main GUI application for Instagram Helper."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Instagram Helper")
        self.root.geometry("1400x700")
        self.root.minsize(1200, 600)

        # Initialize variables
        self.log_queue: queue.Queue = queue.Queue()
        self.scraping_thread: threading.Thread | None = None
        self.stop_scraping = threading.Event()
        self.playwright: Any | None = None
        self.browser: Browser | None = None

        # Setup logging
        self.setup_logging()

        # Create GUI
        self.create_widgets()
        self.setup_layout()

        # Start log polling
        self.poll_logs()

        # Load initial accounts
        self.load_initial_accounts()

    def setup_logging(self) -> None:
        """Setup logging to capture messages for GUI display."""
        self.logger = logging.getLogger("instagram_helper_gui")
        self.logger.setLevel(logging.INFO)

        # Add our custom handler
        log_handler = LogHandler(self.log_queue)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)

        # Capture messages from specific loggers we care about
        target_loggers = [
            "instagram_scraper",
            "browser_manager",
            "report_generator",
            "utils",
        ]

        for logger_name in target_loggers:
            logger = logging.getLogger(logger_name)
            logger.addHandler(log_handler)

    def create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")

        # Control frame
        self.control_frame = ttk.LabelFrame(
            self.main_frame, text="Actions", padding="10"
        )

        # Start/Stop buttons
        self.start_button = ttk.Button(
            self.control_frame, text="Start Scraping", command=self.start_scraping
        )
        self.stop_button = ttk.Button(
            self.control_frame,
            text="Stop Scraping",
            command=self.stop_scraping_process,
            state="disabled",
        )

        # Settings frame
        self.settings_frame = ttk.LabelFrame(
            self.main_frame, text="Settings", padding="15"
        )

        # Max post age
        ttk.Label(self.settings_frame, text="Max Age (days):").grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        self.max_age_var = tk.StringVar(value="7")
        self.max_age_entry = ttk.Entry(
            self.settings_frame, textvariable=self.max_age_var, width=10
        )
        self.max_age_entry.grid(row=0, column=1, sticky="w", padx=(0, 25))

        # Max posts per account
        ttk.Label(self.settings_frame, text="Max Posts:").grid(
            row=0, column=2, sticky="w", padx=(0, 5)
        )
        self.max_posts_var = tk.StringVar(
            value=str(settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT)
        )
        self.max_posts_entry = ttk.Entry(
            self.settings_frame, textvariable=self.max_posts_var, width=10
        )
        self.max_posts_entry.grid(row=0, column=3, sticky="w", padx=(0, 25))

        # Timeout
        ttk.Label(self.settings_frame, text="Timeout (ms):").grid(
            row=0, column=4, sticky="w", padx=(0, 5)
        )
        self.timeout_var = tk.StringVar(value=str(settings.INSTAGRAM_POST_LOAD_TIMEOUT))
        self.timeout_entry = ttk.Entry(
            self.settings_frame, textvariable=self.timeout_var, width=10
        )
        self.timeout_entry.grid(row=0, column=5, sticky="w")

        # Accounts frame
        self.accounts_frame = ttk.LabelFrame(
            self.main_frame, text="Accounts", padding="10"
        )

        # Account input text area
        ttk.Label(
            self.accounts_frame, text="Enter Instagram accounts (one per line):"
        ).pack(anchor="w")
        self.account_text = scrolledtext.ScrolledText(
            self.accounts_frame, height=8, width=80
        )
        self.account_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Load initial accounts
        self.load_initial_accounts()

        # Logs frame
        self.logs_frame = ttk.LabelFrame(self.main_frame, text="Logs", padding="10")

        # Log text area
        self.log_text = scrolledtext.ScrolledText(self.logs_frame, height=15, width=100)

        # Clear logs button
        self.clear_logs_button = ttk.Button(
            self.logs_frame, text="Clear", command=self.clear_logs
        )

        # Progress frame
        self.progress_frame = ttk.LabelFrame(
            self.main_frame, text="Progress", padding="10"
        )

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, variable=self.progress_var, maximum=100
        )

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.progress_frame, textvariable=self.status_var)

    def setup_layout(self) -> None:
        """Setup the layout of all widgets."""
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            self.main_frame, text="Instagram Helper", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        # Control frame
        self.control_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        self.stop_button.grid(row=0, column=1)

        # Settings frame
        self.settings_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        # Accounts frame
        self.accounts_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.account_text.pack(fill=tk.BOTH, expand=True, padx=(0, 5))

        # Logs frame
        self.logs_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.clear_logs_button.grid(row=1, column=0, pady=(10, 0))

        # Progress frame
        self.progress_frame.grid(row=5, column=0, sticky="ew")
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.status_label.grid(row=1, column=0, sticky="w")

        # Configure grid weights
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.accounts_frame.grid_columnconfigure(0, weight=1)
        self.accounts_frame.grid_rowconfigure(0, weight=1)
        self.logs_frame.grid_columnconfigure(0, weight=1)
        self.logs_frame.grid_rowconfigure(0, weight=1)
        self.progress_frame.grid_columnconfigure(0, weight=1)

    def load_initial_accounts(self) -> None:
        """Load initial accounts from the text area."""
        self.account_text.delete(1.0, tk.END)
        for i, account in enumerate(settings.INSTAGRAM_ACCOUNTS):
            if i > 0:
                self.account_text.insert(tk.END, "\n")
            self.account_text.insert(tk.END, account)

    def get_accounts(self) -> list[str]:
        """Get the current list of accounts from the text area."""
        return [
            line.strip()
            for line in self.account_text.get(1.0, tk.END).splitlines()
            if line.strip()
        ]

    def get_settings(self) -> dict[str, int] | None:
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
                "timeout_ms": timeout,
            }
        except ValueError as e:
            messagebox.showerror("Invalid Settings", f"Please check your settings: {e}")
            return None

    def start_scraping(self) -> None:
        """Start the scraping process in a separate thread."""
        accounts = self.get_accounts()
        if not accounts:
            messagebox.showwarning(
                "No Accounts", "Please add at least one Instagram account."
            )
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
            target=self.scraping_worker, args=(accounts, settings_dict), daemon=True
        )
        self.scraping_thread.start()

    def stop_scraping_process(self) -> None:
        """Stop the scraping process."""
        self.stop_scraping.set()
        self.status_var.set("Stopping...")

    def scraping_worker(
        self, accounts: list[str], settings_dict: dict[str, int]
    ) -> None:
        """Worker thread for scraping."""
        try:
            self.logger.info("Starting Instagram scraping process...")

            # Calculate cutoff date with timezone info
            cutoff_date = datetime.now(UTC) - timedelta(
                days=settings_dict["max_age_days"]
            )
            self.logger.info(f"Cutoff date: {cutoff_date}")

            # Update settings with GUI values
            settings.update_instagram_settings(
                settings_dict["max_posts_per_account"], settings_dict["timeout_ms"]
            )

            # Initialize Playwright
            self.playwright_context = sync_playwright()
            self.playwright_instance = self.playwright_context.start()
            self.browser = setup_browser(self.playwright_instance)
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

                self.logger.info(
                    f"Processing account {i + 1}/{total_accounts}: @{account}"
                )

                # Update progress
                progress = (i / total_accounts) * 100
                self.root.after(0, self._update_progress, progress)
                self.root.after(0, self._update_status, f"Processing @{account}...")

                # Scrape posts
                posts = scraper.process_account(account, cutoff_date)
                all_posts.extend(posts)

                self.logger.info(f"Found {len(posts)} posts for @{account}")

            # Generate report
            if all_posts and not self.stop_scraping.is_set():
                self.logger.info("Generating HTML report...")
                self.root.after(0, self._update_status, "Generating report...")

                report_data = ReportData(posts=all_posts, cutoff_date=cutoff_date)
                date_str = datetime.now(UTC).strftime("%d-%m-%Y")
                output_path = Path(settings.OUTPUT_DIR) / f"{date_str}.html"
                generate_html_report(report_data, output_path, settings.TEMPLATE_PATH)

                self.logger.info(f"Report generated: {output_path}")

            # Update final status
            if self.stop_scraping.is_set():
                self.root.after(0, self._update_status, "Stopped")
            else:
                self.root.after(0, self._update_progress, 100)
                self.root.after(
                    0,
                    self._update_status,
                    f"Complete - {len(all_posts)} posts found",
                )

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error during scraping: {error_msg}")
            self.root.after(0, self._update_status, f"Error: {error_msg}")
        finally:
            # Cleanup
            if self.browser:
                self.browser.close()
            if hasattr(self, "playwright_instance") and self.playwright_instance:
                self.playwright_instance.stop()

            # Re-enable start button, disable stop button
            self.root.after(0, self.start_button.config, "normal")
            self.root.after(0, self.stop_button.config, "disabled")

    def poll_logs(self) -> None:
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

    def _update_progress(self, value: float) -> None:
        """Update progress bar value."""
        self.progress_var.set(value)

    def _update_status(self, message: str) -> None:
        """Update status label message."""
        self.status_var.set(message)

    def clear_logs(self) -> None:
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)

    def run(self) -> None:
        """Start the GUI application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = InstagramHelperGUI()
    app.run()
