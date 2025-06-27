"""HTML report generation functionality."""

import os
from datetime import datetime
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

from config import INSTAGRAM_ACCOUNTS, INSTAGRAM_MAX_POST_AGE
from utils import setup_logging

logger = setup_logging(__name__)


def generate_html_report(posts: List[Dict], cutoff_date: datetime, output_dir: str, template_path: str) -> str:
    """Generate a stylized HTML report of fetched posts using a template."""
    # Sort posts by date, newest first, regardless of the account
    posts.sort(key=lambda p: p['date_posted'], reverse=True)

    # Format date after sorting
    for post in posts:
        post['date_posted'] = post['date_posted'].strftime('%d-%m-%Y')

    generated_on = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    filename = f"instagram_updates_{datetime.now().strftime('%Y%m%d')}.html"
    output_file = os.path.join(output_dir, filename)

    date_range = f"{cutoff_date.strftime('%d-%m-%Y')} to {datetime.now().strftime('%d-%m-%Y')}"

    template_data = {
        'posts': posts,
        'date_range': date_range,
        'total_posts': len(posts),
        'generated_on': generated_on,
        'max_post_age': INSTAGRAM_MAX_POST_AGE,
        'total_accounts': len(INSTAGRAM_ACCOUNTS),
    }

    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    html_content = template.render(**template_data)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"HTML report generated: {output_file}")
    return output_file
