"""HTML report generation functionality."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader

from utils import setup_logging

if TYPE_CHECKING:
    from instagram_scraper import InstagramPost

logger = setup_logging(__name__)


@dataclass
class ReportData:
    """Holds all data required for generating the HTML report."""

    posts: list[InstagramPost]
    cutoff_date: datetime
    generation_time: datetime = field(default_factory=datetime.now)

    @property
    def total_posts(self) -> int:
        return len(self.posts)

    @property
    def accounts_count(self) -> int:
        return len({p.account for p in self.posts})

    @property
    def sorted_posts(self) -> list[InstagramPost]:
        return sorted(self.posts, key=lambda p: p.date_posted, reverse=True)

    @property
    def template_data(self) -> dict[str, str | int | list[InstagramPost]]:
        # Compute max_post_age in whole days for the template
        generation_time_normalized = self.generation_time
        try:
            if (
                self.generation_time.tzinfo is None
                and self.cutoff_date.tzinfo is not None
            ):
                generation_time_normalized = self.generation_time.replace(
                    tzinfo=self.cutoff_date.tzinfo
                )
            max_post_age = max(
                0,
                (generation_time_normalized.date() - self.cutoff_date.date()).days,
            )
        except Exception:
            max_post_age = 0

        return {
            "posts": self.sorted_posts,
            "total_posts": self.total_posts,
            "generated_on": self.generation_time.strftime("%d-%m-%Y %H:%M:%S"),
            "date_range": (
                f"{self.cutoff_date.strftime('%d-%m-%Y')} - "
                f"{self.generation_time.strftime('%d-%m-%Y')}"
            ),
            # Match keys expected by the default HTML template
            "total_accounts": self.accounts_count,
            "max_post_age": max_post_age,
        }


def generate_html_report(
    report_data: ReportData, output_dir: Path, template_path: str
) -> Path | None:
    """Generates a stylized HTML report from a list of Instagram posts."""
    if not report_data.posts:
        logger.warning("No posts were provided, skipping report generation.")
        return None

    try:
        # Set up Jinja2 environment
        template_dir = Path(template_path).parent
        template_name = Path(template_path).name
        env = Environment(
            loader=FileSystemLoader(template_dir), autoescape=True, enable_async=False
        )
        template = env.get_template(template_name)

        # Render the HTML content
        html_content = template.render(report_data.template_data)

        # Ensure output directory exists and save the report
        output_dir.mkdir(parents=True, exist_ok=True)
        report_filename = f"instagram_report_{report_data.generation_time.strftime('%Y%m%d_%H%M%S')}.html"
        report_path = output_dir / report_filename

        with report_path.open("w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Successfully generated HTML report: {report_path}")
        return report_path

    except Exception as e:
        logger.error(f"Failed to generate HTML report: {e}", exc_info=True)
        return None
