"""Command-line interface for Instagram Helper."""

import argparse
import logging
import os
import sys
import webbrowser
from datetime import datetime, timedelta

from playwright.sync_api import sync_playwright

from browser_manager import setup_browser
from config import (
    BROWSER_CONNECTION_ERROR,
    FILE_PROTOCOL,
    INSTAGRAM_ACCOUNTS,
    LOG_DIR,
    OUTPUT_DIR,
    TIMEZONE,
)
from instagram_scraper import process_account
from report_generator import generate_html_report
from utils import setup_logging

# Constants
TEMPLATE_PATH = "templates/template.html"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch recent Instagram posts and generate HTML reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                           # Use default settings
  python cli.py --days 3                  # Fetch posts from last 3 days
  python cli.py --accounts gijon biodevas # Only fetch from specific accounts
  python cli.py --output ./reports        # Save reports to custom directory
  python cli.py --no-open                 # Don't automatically open the report
        """,
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
        default=OUTPUT_DIR,
        help=f"Output directory for reports (default: {OUTPUT_DIR})",
    )

    parser.add_argument(
        "--log-dir",
        default=LOG_DIR,
        help=f"Directory for log files (default: {LOG_DIR})",
    )

    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not automatically open the generated report",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser.parse_args()


def open_report(report_path: str, logger: logging.Logger) -> None:
    """Open the generated report in the default browser."""
    try:
        # Use webbrowser module for cross-platform compatibility
        webbrowser.open(f"{FILE_PROTOCOL}{os.path.abspath(report_path)}")
        logger.info("Opening the HTML report...")
    except (OSError, ValueError) as e:
        logger.warning(f"Could not automatically open report: {e}")
        logger.info(f"Please open manually: {report_path}")
    except Exception as e:
        logger.warning(f"Unexpected error opening report: {e}")
        logger.info(f"Please open manually: {report_path}")


def main() -> int:
    """Main CLI function."""
    args = parse_args()

    # Setup logging
    logger = setup_logging(
        log_dir=args.log_dir, log_level=logging.DEBUG if args.verbose else logging.INFO
    )

    # Determine accounts to process
    accounts_to_process = args.accounts if args.accounts else INSTAGRAM_ACCOUNTS

    try:
        with sync_playwright() as p:
            browser = setup_browser(p)
            # Safely get an existing page or create a new page if none exists
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            cutoff_date = datetime.now(TIMEZONE) - timedelta(days=args.days)
            logger.info(
                f"Fetching posts not older than {cutoff_date.strftime('%d-%m-%Y')}."
            )
            logger.info(
                f"Processing {len(accounts_to_process)} accounts: {', '.join(accounts_to_process)}"
            )

            all_posts = []
            for account in accounts_to_process:
                posts = process_account(account, page, cutoff_date)
                all_posts.extend(posts)

            if all_posts:
                logger.info(f"Found {len(all_posts)} posts. Generating HTML report...")
                report_path = generate_html_report(
                    all_posts, cutoff_date, args.output, TEMPLATE_PATH
                )

                if not args.no_open and report_path:
                    open_report(report_path, logger)
                else:
                    logger.info(f"Report saved to: {report_path}")
            else:
                logger.info("No new posts found to generate a report.")

        logger.info("Done :)")
        return 0

    except Exception as e:
        if BROWSER_CONNECTION_ERROR in str(e):
            logger.error(
                "Failed to connect to the browser. Please close all browser windows and try again."
            )
        else:
            logger.error(f"An error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
