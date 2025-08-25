"""Tests for main functionality."""

from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from instagram_scraper import InstagramPost
from report_generator import ReportData, generate_html_report


@pytest.fixture
def sample_posts() -> list[InstagramPost]:
    """Provides sample Instagram posts for testing."""
    return [
        InstagramPost(
            url="https://instagram.com/p/1/",
            account="account1",
            caption="Post 1",
            date_posted=datetime.now(UTC) - timedelta(hours=1),
        ),
        InstagramPost(
            url="https://instagram.com/p/2/",
            account="account2",
            caption="Post 2",
            date_posted=datetime.now(UTC) - timedelta(hours=2),
        ),
        InstagramPost(
            url="https://instagram.com/p/3/",
            account="account1",  # Same account as first post
            caption="Post 3",
            date_posted=datetime.now(UTC) - timedelta(hours=3),
        ),
    ]


@pytest.fixture
def report_data(sample_posts: list[InstagramPost]) -> ReportData:
    """Provides a ReportData instance for testing."""
    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    return ReportData(posts=sample_posts, cutoff_date=cutoff_date)


# Report Generator Tests
def test_report_data_properties(report_data: ReportData) -> None:
    """Test ReportData properties."""
    assert report_data.total_posts == 3
    assert report_data.accounts_count == 2  # Only 2 unique accounts
    assert len(report_data.sorted_posts) == 3
    # Posts should be sorted by date (newest first)
    assert (
        report_data.sorted_posts[0].date_posted
        > report_data.sorted_posts[1].date_posted
    )
    assert (
        report_data.sorted_posts[1].date_posted
        > report_data.sorted_posts[2].date_posted
    )


def test_report_data_template_data(report_data: ReportData) -> None:
    """Test ReportData template_data property."""
    template_data = report_data.template_data

    assert template_data["posts"] == report_data.sorted_posts
    assert template_data["total_posts"] == 3
    assert template_data["total_accounts"] == 2
    assert "generated_on" in template_data
    assert "date_range" in template_data
    assert "max_post_age" in template_data
    assert template_data["max_post_age"] >= 0


def test_report_data_timezone_handling() -> None:
    """Test ReportData timezone handling in template_data."""
    # Create data with timezone-aware cutoff date
    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    generation_time = datetime.now()  # Naive datetime

    report_data = ReportData(
        posts=[], cutoff_date=cutoff_date, generation_time=generation_time
    )

    template_data = report_data.template_data
    assert "max_post_age" in template_data
    assert template_data["max_post_age"] >= 0


def test_generate_html_report_no_posts() -> None:
    """Test HTML report generation with no posts."""
    report_data = ReportData(posts=[], cutoff_date=datetime.now(UTC))

    result = generate_html_report(
        report_data, Path("/tmp/report.html"), "templates/template.html"
    )

    assert result is None


def test_generate_html_report_success(tmp_path: Path, report_data: ReportData) -> None:
    """Test successful HTML report generation."""
    # Create template directory and file
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_path = template_dir / "template.html"
    template_path.write_text("""
        <html>
            <body>
                <h1>{{ total_posts }} posts</h1>
                <p>Generated on {{ generated_on }}</p>
                <p>Date range: {{ date_range }}</p>
                <p>Accounts: {{ total_accounts }}</p>
                <p>Max age: {{ max_post_age }} days</p>
                {% for post in posts %}
                <div>{{ post.account }}: {{ post.caption }}</div>
                {% endfor %}
            </body>
        </html>
    """)

    result = generate_html_report(
        report_data, tmp_path / "report.html", str(template_path)
    )

    assert result is not None
    assert result.exists()
    assert result.suffix == ".html"

    # Check content
    content = result.read_text()
    assert "3 posts" in content
    assert "Generated on" in content
    assert "account1" in content
    assert "account2" in content


def test_generate_html_report_file_write_error(
    tmp_path: Path, report_data: ReportData
) -> None:
    """Test HTML report generation with file write errors."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_path = template_dir / "template.html"
    template_path.write_text("<html>{{ total_posts }}</html>")

    # Use a path that will definitely cause a write error
    # Try to write to a system directory that requires elevated permissions
    import os
    import platform

    if platform.system() == "Windows":
        # On Windows, try to write to a system directory
        output_file = Path("C:/Windows/System32/report.html")
    else:
        # On Unix, try to write to a system directory
        output_file = Path("/usr/bin/report.html")

    # This should cause a permission error when trying to write
    result = generate_html_report(
        report_data, output_file, str(template_path)
    )

    assert result is None


def test_generate_html_report_directory_creation(
    tmp_path: Path, report_data: ReportData
) -> None:
    """Test HTML report generation with directory creation."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_path = template_dir / "template.html"
    template_path.write_text("<html>{{ total_posts }}</html>")

    # Use non-existent output directory
    output_dir = tmp_path / "new_output"

    result = generate_html_report(
        report_data, output_dir / "report.html", str(template_path)
    )

    assert result is not None
    assert output_dir.exists()


def test_report_data_empty_posts() -> None:
    """Test ReportData with empty posts list."""
    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    report_data = ReportData(posts=[], cutoff_date=cutoff_date)

    assert report_data.total_posts == 0
    assert report_data.accounts_count == 0
    assert len(report_data.sorted_posts) == 0
    assert report_data.template_data["total_posts"] == 0
    assert report_data.template_data["total_accounts"] == 0


def test_report_data_single_post() -> None:
    """Test ReportData with single post."""
    post = InstagramPost(
        url="https://instagram.com/p/1/",
        account="single_account",
        caption="Single post",
        date_posted=datetime.now(UTC),
    )

    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    report_data = ReportData(posts=[post], cutoff_date=cutoff_date)

    assert report_data.total_posts == 1
    assert report_data.accounts_count == 1
    assert len(report_data.sorted_posts) == 1
    assert report_data.sorted_posts[0] == post


def test_report_data_custom_generation_time() -> None:
    """Test ReportData with custom generation time."""
    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    custom_time = datetime(2024, 1, 1, 12, 0, 0)

    report_data = ReportData(
        posts=[], cutoff_date=cutoff_date, generation_time=custom_time
    )

    template_data = report_data.template_data
    assert "01-01-2024 12:00:00" in template_data["generated_on"]


def test_report_data_timezone_aware_dates() -> None:
    """Test ReportData with timezone-aware dates."""
    # Create timezone-aware dates
    est_tz = timezone(timedelta(hours=-5))

    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    generation_time = datetime.now(est_tz)

    report_data = ReportData(
        posts=[], cutoff_date=cutoff_date, generation_time=generation_time
    )

    template_data = report_data.template_data
    assert "max_post_age" in template_data
    assert template_data["max_post_age"] >= 0
