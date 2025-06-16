import re
import unicodedata
from datetime import datetime
from typing import Dict, List

from utils import logger


def clean_caption(caption: str) -> str:
  """Clean Instagram caption by removing emojis, hashtags, and non-text elements."""
  if not caption:
    return ""

  # Remove emojis
  caption = re.sub(r'[\U00010000-\U0010ffff]', '', caption)

  # Remove hashtags
  caption = re.sub(r'#\w+', '', caption)

  # Normalize unicode and clean punctuation
  caption = unicodedata.normalize('NFKC', caption)
  caption = re.sub(r'[^\w\s.,!?;:()\-@/\n]', '', caption)
  caption = re.sub(r' +', ' ', caption)

  # Clean lines - remove empty lines and lines with only punctuation
  lines = [line.strip() for line in caption.split('\n')]
  cleaned_lines = [
      line for line in lines
      if line and not re.fullmatch(r'[.,:;\-–— ]{1,5}', line) and len(line) > 1
  ]

  # Remove consecutive blank lines
  result = '\n'.join(
      line for i, line in enumerate(cleaned_lines)
      if line or (i > 0 and cleaned_lines[i - 1])
  ).strip()

  return result


def format_post_date(date_str: str) -> str:
  """Format ISO date string to a more readable format."""
  dt = datetime.fromisoformat(date_str)
  return dt.strftime("%B %d, %Y at %H:%M")


def display_summary(posts: Dict[str, List[Dict[str, str]]]) -> None:
  """Display minimal summary information."""
  if not posts:
    print("No new posts found in the last 7 days.")
    return

  total_posts = sum(len(account_posts) for account_posts in posts.values())
  total_accounts = len(posts)

  print(f"Found {total_posts} new posts from {total_accounts} accounts.")

  for account, account_posts in posts.items():
    print(f"  @{account}: {len(account_posts)} posts")


def _get_css_styles() -> str:
  """Get CSS styles for the HTML report."""
  return """
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }

        .container {
            max-width: 1200px; margin: 0 auto; background: white;
            border-radius: 15px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #E91E63, #9C27B0);
            color: white; padding: 30px 40px; text-align: center;
        }

        .header h1 { font-size: 2.5em; font-weight: 300; margin-bottom: 10px; }
        .header .subtitle { opacity: 0.9; font-size: 1.1em; }

        .summary {
            background: #f8f9fa; padding: 20px 40px;
            border-bottom: 1px solid #e9ecef;
        }

        .summary-stats { display: flex; justify-content: space-around; text-align: center; }
        .stat { flex: 1; }
        .stat-number { font-size: 2em; font-weight: bold; color: #E91E63; display: block; }
        .stat-label { color: #666; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }

        .account-section { margin: 30px 0; padding: 0 40px; }

        .account-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; padding: 20px 30px; margin: 0 -40px 20px;
            border-radius: 10px; display: flex; justify-content: space-between;
            align-items: center;
        }

        .account-name { font-size: 1.5em; font-weight: 500; }
        .post-count { background: rgba(255, 255, 255, 0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.9em; }

        .post {
            background: white; border: 1px solid #e9ecef; border-radius: 12px;
            margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            overflow: hidden; transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .post:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1); }

        .post-header {
            background: #f8f9fa; padding: 15px 20px; border-bottom: 1px solid #e9ecef;
            display: flex; justify-content: space-between; align-items: center;
        }

        .post-title { font-weight: 600; color: #495057; }
        .post-date { color: #6c757d; font-size: 0.9em; }
        .post-content { padding: 20px; }

        .post-url {
            display: inline-block; background: #E91E63; color: white;
            text-decoration: none; padding: 8px 15px; border-radius: 5px;
            font-size: 0.9em; margin-bottom: 15px;
            transition: background-color 0.2s ease;
        }

        .post-url:hover { background: #C2185B; }
        .caption { color: #495057; line-height: 1.8; font-size: 1.05em; }
        .no-caption { color: #6c757d; font-style: italic; }
        .footer { background: #f8f9fa; text-align: center; padding: 20px; color: #6c757d; font-size: 0.9em; }

        @media (max-width: 768px) {
            .container { margin: 10px; border-radius: 10px; }
            .header, .account-section { padding: 20px; }
            .summary-stats { flex-direction: column; gap: 20px; }
            .account-header { flex-direction: column; gap: 10px; text-align: center; }
        }
    """


def _generate_post_html(post: Dict[str, str], post_num: int, total_posts: int) -> str:
  """Generate HTML for a single post."""
  formatted_date = format_post_date(post['date'])
  cleaned_caption = clean_caption(post['caption'])

  if not cleaned_caption or cleaned_caption == "No caption":
    caption_html = '<div class="no-caption">No caption available</div>'
  else:
    caption_html = f'<div class="caption">{cleaned_caption.replace(chr(10), "<br>")}</div>'

  return f"""
            <div class="post">
                <div class="post-header">
                    <div class="post-title">📸 Post {post_num}/{total_posts}</div>
                    <div class="post-date">📅 {formatted_date}</div>
                </div>
                <div class="post-content">
                    <a href="{post['url']}" target="_blank" class="post-url">🔗 View on Instagram</a>
                    <div><strong>💬 Caption:</strong></div>
                    {caption_html}
                </div>
            </div>"""


def generate_html_report(posts: Dict[str, List[Dict[str, str]]], output_file: str = "instagram_posts.html") -> None:
  """Generate a beautiful HTML report of Instagram posts."""
  html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Posts Summary</title>
    <style>{_get_css_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📸 Instagram Posts Summary</h1>
            <div class="subtitle">Beautiful overview of your recent Instagram activity</div>
        </div>"""

  if not posts:
    html_content += """
        <div class="summary">
            <div style="text-align: center; padding: 40px;">
                <h2 style="color: #6c757d;">🕐 No new posts found in the last 7 days</h2>
            </div>
        </div>"""
  else:
    total_posts = sum(len(account_posts) for account_posts in posts.values())
    total_accounts = len(posts)

    html_content += f"""
        <div class="summary">
            <div class="summary-stats">
                <div class="stat">
                    <span class="stat-number">{total_accounts}</span>
                    <span class="stat-label">Account{'s' if total_accounts != 1 else ''}</span>
                </div>
                <div class="stat">
                    <span class="stat-number">{total_posts}</span>
                    <span class="stat-label">New Post{'s' if total_posts != 1 else ''}</span>
                </div>
            </div>
        </div>"""

    for account, account_posts in posts.items():
      html_content += f"""
        <div class="account-section">
            <div class="account-header">
                <div class="account-name">👤 @{account}</div>
                <div class="post-count">{len(account_posts)} new post{'s' if len(account_posts) != 1 else ''}</div>
            </div>"""

      for i, post in enumerate(account_posts, 1):
        html_content += _generate_post_html(post, i, len(account_posts))

      html_content += "        </div>"

  html_content += f"""
        <div class="footer">
            Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""

  try:
    with open(output_file, 'w', encoding='utf-8') as f:
      f.write(html_content)
    logger.info(f"HTML report generated: {output_file}")
    print(f"HTML report saved: {output_file}")
  except Exception as e:
    logger.error(f"Failed to generate HTML report: {e}")
    print(f"Error generating HTML report: {e}")


def display_posts(posts: Dict[str, List[Dict[str, str]]]) -> None:
  """Display minimal summary and generate HTML report."""
  display_summary(posts)
  generate_html_report(posts)
