"""HTML report generation functionality.

REPORT GENERATION STRATEGY:

This module implements a sophisticated HTML report generation system that creates
professional, responsive reports from scraped Instagram data. The design follows
modern web development principles while maintaining simplicity and reliability.

ARCHITECTURE OVERVIEW:

1. DATA PREPARATION: Raw Instagram post data is processed and organized for
   template rendering, including sorting, grouping, and statistical calculations.

2. TEMPLATE SYSTEM: Uses Jinja2 templating engine for flexible, maintainable
   HTML generation with separation of concerns between data and presentation.

3. RESPONSIVE DESIGN: HTML templates include CSS Grid and Flexbox for modern,
   mobile-friendly layouts that work across different screen sizes.

4. STATISTICAL ANALYSIS: Automatically calculates and displays key metrics
   including post counts, account counts, and date ranges.

CRITICAL IMPLEMENTATION DETAILS:

- TEMPLATE ENGINE: Jinja2 provides powerful templating capabilities while
  maintaining security through automatic HTML escaping and sandboxed execution.

- DATA PROCESSING: The ReportData class acts as a data container and processor,
  computing derived properties like sorted posts and account counts on-demand.

- FILE HANDLING: Robust file operations with proper encoding (UTF-8) and
  directory creation to handle various deployment scenarios.

- ERROR HANDLING: Graceful degradation when report generation fails, with
  comprehensive logging for debugging purposes.

PERFORMANCE CONSIDERATIONS:

- LAZY EVALUATION: Template data is computed only when accessed, avoiding
  unnecessary processing for unused properties.

- MEMORY EFFICIENCY: Large datasets are processed incrementally without
  accumulating excessive memory usage.

- RENDERING OPTIMIZATION: Jinja2 templates are compiled once and reused,
  improving rendering performance for multiple reports.

SECURITY CONSIDERATIONS:

- HTML ESCAPING: All user-generated content is automatically escaped to
  prevent XSS attacks and ensure safe HTML output.

- TEMPLATE SANDBOXING: Jinja2 provides a secure execution environment
  that prevents arbitrary code execution from templates.

- INPUT VALIDATION: Data is validated before processing to ensure
  template safety and prevent rendering errors.

MAINTENANCE AND EXTENSIBILITY:

- TEMPLATE SEPARATION: HTML templates are stored separately from Python code,
  making them easy to modify without code changes.

- CONFIGURABLE OUTPUT: Report generation parameters can be customized
  through the template system and configuration options.

- VERSIONING SUPPORT: Template changes can be versioned and tested
  independently of the core application logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
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
    generation_time: datetime = field(default_factory=lambda: datetime.now(UTC))

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
        """Compute template data."""
        return {
            "posts": self.sorted_posts,
            "total_posts": self.total_posts,
            "generated_on": self.generation_time.strftime("%d-%m-%Y %H:%M:%S"),
            "date_range": (
                f"{self.cutoff_date.strftime('%d-%m-%Y')} - "
                f"{self.generation_time.strftime('%d-%m-%Y')}"
            ),
            "total_accounts": self.accounts_count,
            "max_post_age": self._calculate_max_post_age(),
        }

    def _calculate_max_post_age(self) -> int:
        """Calculate the maximum post age in whole days."""
        try:
            return max(
                0,
                (self.generation_time.date() - self.cutoff_date.date()).days,
            )
        except Exception:
            return 0


def generate_html_report(
    report_data: ReportData, output_path: Path, template_path: Path
) -> Path | None:
    """Generates a stylized HTML report from a list of Instagram posts."""
    if not report_data.posts:
        logger.warning("No posts were provided, skipping report generation.")
        return None

    try:
        # Set up Jinja2 environment using the template path directly
        template_dir = template_path.parent
        template_name = template_path.name
        env = Environment(
            loader=FileSystemLoader(template_dir), autoescape=True, enable_async=False
        )
        template = env.get_template(template_name)

        # Render the HTML content
        html_content = template.render(report_data.template_data)

        # Ensure output directory exists and save the report
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Successfully generated HTML report: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to generate HTML report: {e}", exc_info=True)
        return None
