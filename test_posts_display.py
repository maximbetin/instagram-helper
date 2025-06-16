from posts_display import clean_caption, display_posts, format_post_date


def test_clean_caption():
  # Test empty caption
  assert clean_caption("") == "No caption"
  assert clean_caption(None) == "No caption"

  # Test basic cleaning
  assert clean_caption("Hello...world") == "Hello. world"
  assert clean_caption("Hello    world") == "Hello world"

  # Test sentence splitting
  input_text = "First sentence. Second sentence. Third sentence!"
  expected = "First sentence.\nSecond sentence.\nThird sentence!"
  assert clean_caption(input_text) == expected

  # Test emoji removal
  assert clean_caption("Hello 👋 world") == "Hello world"
  assert clean_caption("🎾 Tennis match") == "Tennis match"

  # Test special characters
  assert clean_caption("Hello @world") == "Hello world"
  assert clean_caption("Hello #world") == "Hello"

  # Test real-world example
  input_text = """🎾  En Oviedo, el deporte se vive también al aire libre. Las pistas de tenis y pádel del Parque del Oeste son el lugar perfecto para entrenar, competir o simplemente pasarlo bien con amig@s. Una instalación de referencia para quienes disfrutan del deporte con vistas.
📍  C/ Antón Sánchez, Oviedo
🚶 ‍♂️ Accesible a pie, en bus (líneas B, G, L, J, C, D, F) y tren (línea C7) @aytoviedo @deportesayov"""
  expected = """En Oviedo, el deporte se vive también al aire libre.
Las pistas de tenis y pádel del Parque del Oeste son el lugar perfecto para entrenar, competir o simplemente pasarlo bien con amigs.
Una instalación de referencia para quienes disfrutan del deporte con vistas.
C Antón Sánchez, Oviedo.
Accesible a pie, en bus líneas B, G, L, J, C, D, F y tren línea C7."""
  assert clean_caption(input_text) == expected


def test_format_post_date():
  assert format_post_date("2024-06-10T12:34:56+02:00") == "2024-06-10 12:34 Madrid"


def test_display_posts_no_posts(capsys):
  display_posts({})
  captured = capsys.readouterr()
  assert "No new posts found" in captured.out


def test_display_posts_with_posts(capsys):
  posts = {
      "testaccount": [
          {
              "url": "https://instagram.com/p/abc123/",
              "date": "2024-06-10T12:34:56+02:00",
              "shortcode": "abc123",
              "caption": """First sentence. Second sentence with emoji 👋. Third sentence with #hashtag.
                Email: test@example.com
                https://test.com"""
          },
          {
              "url": "https://instagram.com/p/def456/",
              "date": "2024-06-09T10:00:00+02:00",
              "shortcode": "def456",
              "caption": "Another test post with emoji 👋 and #tag. Second sentence here."
          }
      ]
  }
  display_posts(posts)
  captured = capsys.readouterr()
  assert "TESTACCOUNT" in captured.out
  assert "2024-06-10 12:34 Madrid" in captured.out
  assert "https://instagram.com/p/abc123/" in captured.out
  assert "First sentence." in captured.out
  assert "Second sentence with emoji." in captured.out
  assert "Third sentence with." in captured.out
  assert "Another test post with emoji and." in captured.out
  assert "Second sentence here." in captured.out
  assert len([line for line in captured.out.splitlines() if line.strip() == '-' * 50]) == 2


def test_display_posts_shortcode_in_output(capsys):
  posts = {
      "testaccount": [
          {
              "url": "https://instagram.com/p/xyz789/",
              "date": "2024-06-08T08:00:00+02:00",
              "shortcode": "xyz789",
              "caption": """Test caption with multiple sentences. Second sentence here. Third sentence with emoji 👋."""
          }
      ]
  }
  display_posts(posts)
  captured = capsys.readouterr()
  assert "xyz789" in captured.out
  assert "Test caption with multiple sentences." in captured.out
  assert "Second sentence here." in captured.out
  assert "Third sentence with emoji." in captured.out
