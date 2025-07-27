"""Instagram browser launcher with post fetching."""

import os
import time
from datetime import datetime, timedelta

from playwright.sync_api import sync_playwright

from browser_manager import setup_browser
from config import INSTAGRAM_ACCOUNTS, INSTAGRAM_MAX_POST_AGE, LOG_DIR, OUTPUT_DIR, TIMEZONE
from instagram_scraper import process_account
from report_generator import generate_html_report
from utils import setup_logging

# Initialize logger with file logging
logger = setup_logging(log_dir=LOG_DIR)

def main():
    """Main function to run the Instagram scraper."""
    try:
        with sync_playwright() as p:
            browser = setup_browser(p)
            page = browser.contexts[0].pages[0]

            cutoff_date = datetime.now(TIMEZONE) - timedelta(days=INSTAGRAM_MAX_POST_AGE)
            logger.info(f"Fetching posts not older than {cutoff_date.strftime('%d-%m-%Y')}.")

            all_posts = []
            failed_accounts = []

            for account in INSTAGRAM_ACCOUNTS:
                try:
                    account_posts = process_account(account, page, cutoff_date)
                    all_posts.extend(account_posts)
                    # Brief pause between accounts to avoid rate limiting
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Failed to process account @{account}: {e}")
                    failed_accounts.append(account)
                    continue

            if failed_accounts:
                logger.warning(f"Failed to process {len(failed_accounts)} account(s): {', '.join(failed_accounts)}")

            if all_posts:
                logger.info("Generating the HTML report...")
                template_path = 'templates/template.html'
                report_path = generate_html_report(all_posts, cutoff_date, OUTPUT_DIR, template_path)
                logger.info("Opening the HTML report...")
                os.startfile(report_path)
            else:
                logger.info("No new posts found to generate a report.")

        logger.info("Done :)")
    except Exception as e:
        if "ECONNREFUSED" in str(e):
            logger.error(
                "Failed to connect to the browser. Please close all browser windows and try again."
            )
        else:
            logger.error(f"An error occurred: {e}", exc_info=True)
            raise

if __name__ == "__main__":  # pragma: no cover
    main()
