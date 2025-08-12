"""Command-line interface for Instagram Helper."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from browser_manager import setup_browser
from config import settings
from instagram_scraper import InstagramPost, InstagramScraper
from report_generator import ReportData, generate_html_report
from utils import setup_logging

if TYPE_CHECKING:
    from config import Settings


logger = setup_logging(__name__)


class App:
    """Main application class for the Instagram Helper."""

    def __init__(self, app_settings: Settings, args: argparse.Namespace):
        self.settings = app_settings
        self.args = args
        self.all_posts: list[InstagramPost] = []

    def run(self) -> None:
        """Executes the main application logic."""
        with sync_playwright() as p:
            browser = self._setup_browser(p)
            try:
                page = self._get_browser_page(browser)
                scraper = InstagramScraper(page, self.settings)

                cutoff_date = datetime.now(self.settings.TIMEZONE) - timedelta(
                    days=self.args.days
                )
                accounts = self.args.accounts or self.settings.INSTAGRAM_ACCOUNTS

                logger.info(
                    f"Fetching posts from the last {self.args.days} days (since "
                    f"{cutoff_date.strftime('%Y-%m-%d')})."
                )
                logger.info(
                    f"Processing {len(accounts)} account(s): {', '.join(accounts)}"
                )

                for account in accounts:
                    posts = scraper.process_account(account, cutoff_date)
                    self.all_posts.extend(posts)

                self._generate_report(cutoff_date)

            finally:
                logger.debug("Closing browser.")
                browser.close()

    def _setup_browser(self, playwright: Playwright) -> Browser:
        """Sets up the browser, launching it if in headless mode."""
        if self.args.headless:
            logger.info("Running in headless mode.")
            return playwright.chromium.launch(headless=True)
        return setup_browser(playwright)

    def _get_browser_page(self, browser: Browser) -> Page:
        """Retrieves or creates a browser page."""
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        return context.pages[0] if context.pages else context.new_page()

    def _generate_report(self, cutoff_date: datetime) -> None:
        """Generates the HTML report."""
        if not self.all_posts:
            logger.info("No new posts found. No report generated.")
            return

        logger.info(f"Found {len(self.all_posts)} total posts. Generating report...")
        report_data = ReportData(posts=self.all_posts, cutoff_date=cutoff_date)
        report_path = generate_html_report(
            report_data, self.args.output, self.settings.TEMPLATE_PATH
        )

        if report_path:
            logger.info(f"Report generated: {report_path}")


def parse_args() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch recent Instagram posts and generate HTML reports.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=3,
        help="Number of days back to fetch posts from (default: 3)",
    )

    parser.add_argument(
        "--accounts",
        "-a",
        nargs="+",
        help="Specific Instagram accounts to fetch from (default: all configured accounts)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=settings.OUTPUT_DIR,
        help=f"Output directory for reports (default: {settings.OUTPUT_DIR})",
    )

    parser.add_argument(
        "--log-dir",
        type=Path,
        default=settings.LOG_DIR,
        help=f"Directory for log files (default: {settings.LOG_DIR})",
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the browser in headless mode (no GUI).",
    )
    
    return parser.parse_args()


def main() -> int:
    """Main CLI entry point."""
    try:
        args = parse_args()
        setup_logging(log_dir=args.log_dir)
        app = App(settings, args)
        app.run()
        logger.info("Scraping process completed successfully.")
        return 0
    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
