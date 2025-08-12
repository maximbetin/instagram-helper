"""HTML report generation functionality."""

import logging
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from instagram_scraper import InstagramPost
from utils import setup_logging

logger = setup_logging(__name__)


def generate_html_report(
    posts: list[InstagramPost],
    cutoff_date: datetime,
    output_dir: Path,
    template_path: str,
    logger: logging.Logger,
) -> str | None:
    """Generate a stylized HTML report from a list of Instagram posts."""
    if not posts:
        logger.warning("No posts were provided, skipping report generation.")
        return None

    # Sort posts by date, newest first
    posts.sort(key=lambda p: p.date_posted, reverse=True)

    # Prepare data for the template
    now = datetime.now()
    template_data = {
        "posts": posts,
        "total_posts": len(posts),
        "generated_on": now.strftime("%d-%m-%Y %H:%M:%S"),
        "date_range": f"{cutoff_date.strftime('%d-%m-%Y')} - {now.strftime('%d-%m-%Y')}",
        "accounts_count": len({p.account for p in posts}),
    }

    try:
        # Set up Jinja2 environment
        template_dir = Path(template_path).parent
        template_name = Path(template_path).name
        env = Environment(
            loader=FileSystemLoader(template_dir), autoescape=True, enable_async=False
        )
        template = env.get_template(template_name)

        # Render the HTML content
        html_content = template.render(template_data)

        # Ensure output directory exists and save the report
        output_dir.mkdir(parents=True, exist_ok=True)
        report_filename = f"instagram_report_{now.strftime('%Y%m%d_%H%M%S')}.html"
        report_path = output_dir / report_filename

        with report_path.open("w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Successfully generated HTML report: {report_path}")
        return str(report_path)

    except Exception as e:
        logger.error(f"Failed to generate HTML report: {e}", exc_info=True)
        return None
