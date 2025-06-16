from posts_display import display_posts, format_post_date


def test_format_post_date():
  assert format_post_date("2024-06-10T12:34:56+00:00") == "2024-06-10 12:34 UTC"


def test_display_posts_no_posts(capsys):
  display_posts({})
  captured = capsys.readouterr()
  assert "No new posts found" in captured.out


def test_display_posts_with_posts(capsys):
  posts = {
      "testaccount": [
          {
              "url": "https://instagram.com/p/abc123/",
              "date": "2024-06-10T12:34:56+00:00",
              "shortcode": "abc123"
          },
          {
              "url": "https://instagram.com/p/def456/",
              "date": "2024-06-09T10:00:00+00:00",
              "shortcode": "def456"
          }
      ]
  }
  display_posts(posts)
  captured = capsys.readouterr()
  assert "TESTACCOUNT" in captured.out
  assert "2024-06-10 12:34 UTC" in captured.out
  assert "https://instagram.com/p/abc123/" in captured.out
  assert "abc123" in captured.out
  assert "def456" in captured.out
  assert len([line for line in captured.out.splitlines() if line.strip() == '-' * 50]) == 2


def test_display_posts_shortcode_in_output(capsys):
  posts = {
      "testaccount": [
          {
              "url": "https://instagram.com/p/xyz789/",
              "date": "2024-06-08T08:00:00+00:00",
              "shortcode": "xyz789"
          }
      ]
  }
  display_posts(posts)
  captured = capsys.readouterr()
  assert "xyz789" in captured.out
