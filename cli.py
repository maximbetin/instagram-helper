"""Command-line interface for Instagram Updates."""

import argparse
import sys
from datetime import datetime, timedelta

from playwright.sync_api import sync_playwright

from browser_manager import setup_browser
from config import INSTAGRAM_ACCOUNTS, LOG_DIR, OUTPUT_DIR, TIMEZONE
from instagram_scraper import process_account
from report_generator import generate_html_report
from utils import setup_logging


def parse_args():
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
        """
    )

    parser.add_argument(
        '--days', '-d',
        type=int,
        default=1,
        help='Number of days back to fetch posts from (default: 1)'
    )

    parser.add_argument(
        '--accounts', '-a',
        nargs='+',
        help='Specific Instagram accounts to fetch from (default: all configured accounts)'
    )

    parser.add_argument(
        '--output', '-o',
        default=OUTPUT_DIR,
        help=f'Output directory for reports (default: {OUTPUT_DIR})'
    )

    parser.add_argument(
        '--log-dir',
        default=LOG_DIR,
        help=f'Directory for log files (default: {LOG_DIR})'
    )

    parser.add_argument(
        '--no-open',
        action='store_true',
        help='Do not automatically open the generated report'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


def main():
    """Main CLI function."""
    args = parse_args()

    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_logging(log_dir=args.log_dir)
    logger.setLevel(log_level)

    # Determine accounts to process
    accounts_to_process = args.accounts if args.accounts else INSTAGRAM_ACCOUNTS

    try:
        with sync_playwright() as p:
            browser = setup_browser(p)
            page = browser.contexts[0].pages[0]

            cutoff_date = datetime.now(TIMEZONE) - timedelta(days=args.days)
            logger.info(f"Fetching posts not older than {cutoff_date.strftime('%d-%m-%Y')}.")
            logger.info(f"Processing {len(accounts_to_process)} accounts: {', '.join(accounts_to_process)}")

            all_posts = []
            for account in accounts_to_process:
                all_posts.extend(process_account(account, page, cutoff_date))

            if all_posts:
                logger.info(f"Found {len(all_posts)} posts. Generating HTML report...")
                template_path = 'templates/template.html'
                report_path = generate_html_report(all_posts, cutoff_date, args.output, template_path)

                if not args.no_open:
                    logger.info("Opening the HTML report...")
                    import os
                    os.startfile(report_path)
                else:
                    logger.info(f"Report saved to: {report_path}")
            else:
                logger.info("No new posts found to generate a report.")

        logger.info("Done :)")
        return 0

    except Exception as e:
        if "ECONNREFUSED" in str(e):
            logger.error(
                "Failed to connect to the browser. Please close all browser windows and try again."
            )
        else:
            logger.error(f"An error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
