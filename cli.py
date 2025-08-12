"""Command-line interface for Instagram Helper."""

import argparse
import logging
import os
import sys
import webbrowser
from datetime import datetime, timedelta

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from browser_manager import setup_browser
from config import (
    FILE_PROTOCOL,
    INSTAGRAM_ACCOUNTS,
    LOG_DIR,
    OUTPUT_DIR,
    TEMPLATE_PATH,
    TIMEZONE,
)
from instagram_scraper import process_account
from report_generator import generate_html_report
from utils import setup_logging

load_dotenv()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch recent Instagram posts and generate HTML reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
            python cli.py                           # Use default settings
            python cli.py --days 3                  # Fetch posts from last 3 days
            python cli.py --accounts aytoviedo      # Only fetch from specific accounts
            python cli.py --output ./reports        # Save reports to custom directory
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

    return parser.parse_args()


def main() -> int:
    """Main CLI function."""
    args = parse_args()

    # Setup logging
    logger = setup_logging(
        log_dir=args.log_dir,
        log_level=logging.DEBUG,  # Always use DEBUG level for verbose output
    )

    # Determine accounts to process
    accounts_to_process = args.accounts if args.accounts else INSTAGRAM_ACCOUNTS

    browser = None
    context = None
    try:
        with sync_playwright() as p:
            browser = setup_browser(p)
            # Safely get an existing context/page or create new ones
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()

            cutoff_date = datetime.now(TIMEZONE) - timedelta(days=args.days)
            logger.info(
                f"Fetching posts from the last {args.days} days (since {cutoff_date.strftime('%Y-%m-%d')})."
            )
            logger.info(
                f"Processing {len(accounts_to_process)} account(s): {', '.join(accounts_to_process)}"
            )

            all_posts = []
            for account in accounts_to_process:
                posts = process_account(account, page, cutoff_date)
                all_posts.extend(posts)

            if all_posts:
                logger.info(f"Total posts found: {len(all_posts)}. Generating HTML report...")
                report_path = generate_html_report(
                    all_posts, cutoff_date, args.output, TEMPLATE_PATH, logger
                )
                if report_path:
                    logger.info(f"Report successfully generated at: {report_path}")
            else:
                logger.info("No new posts found. No report will be generated.")

            # Gracefully close browser resources
            try:
                if context:
                    logger.debug("Closing browser context.")
                    context.close()
                if browser:
                    logger.debug("Closing browser.")
                    browser.close()
            except Exception as e:
                logger.warning(f"Browser cleanup finished with a minor issue: {e}")

        logger.info("Scraping process completed successfully.")
        return 0

    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
