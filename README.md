# Instagram Helper

Instagram Helper is a simple tool that scrapes recent Instagram posts and saves them as HTML reports.

## Features

* Scrapes post content, captions, and timestamps.
* Provides a Tkinter-based interface with live progress.
* Generates HTML reports with summaries and search functions.
* Works with Chrome, Brave, or Edge using remote debugging.
* Supports multiple accounts in a single run.
* Keeps the browser session so the Instagram login remains active.

## Requirements

* Python 3.12 or newer.
* Windows 10/11, Linux (Ubuntu 20.04 or later), or macOS 10.15 or later.
* At least 4 GB of RAM (8 GB recommended for larger runs).
* A Chromium-based browser (Chrome, Brave, or Edge) with remote debugging enabled.
* WSL2 is recommended on Windows for smoother operation.

## Setup

Clone the repository and create the environment:

```bash
git clone https://github.com/maxim/instagram-helper.git
cd instagram-helper
make setup
```

Activate the virtual environment:

```bash
. .\venv\Scripts\Activate.ps1   # On Windows
# source venv/bin/activate      # On Linux/macOS
```

Run the tests and start the application:

```bash
make test
python run.py
```

## Development

Run all quality checks:

```bash
make test
```

Build an executable using either PyInstaller:

```bash
pyinstaller instagram_helper.spec
```

or the provided Makefile:

```bash
make build
```

The Makefile also provides:

* `make setup` to create the environment.
* `make test` to run tests.
* `make build` to build an executable.
* `make clean` to remove build files.

## Configuration

The tool comes preconfigured with defaults optimized for Windows.
It was originally developed on WSL2, but development is now focused on Windows (see [Notes](#notes) below).

To change the settings, edit the `config.py` file directly.

For example:

```python
INSTAGRAM_MAX_POSTS_PER_ACCOUNT = 10
OUTPUT_DIR = Path("C:/Users/YourUsername/Desktop/ig_reports")
```

### Common issues

| Problem              | Solution                                                    |
| -------------------- | ----------------------------------------------------------- |
| Python version error | Install Python 3.12+ and check PATH                         |
| Browser not found    | Update the executable path in `config.py`                   |
| Port 9222 in use     | Close existing browser sessions or change the debug port    |
| Import errors        | Activate the virtual environment and reinstall dependencies |

## Usage

The interface has four parts:

* **Configuration panel**: set the post age limit, the number of posts per account, and the page load timeout.
* **Account list**: enter one Instagram username per line, with support for bulk pasting.
* **Progress display**: view the progress bar, log output, and current status.
* **Control buttons**: start or stop the scraper, clear logs, or reset progress.

### Settings

* The tool processes **three posts per account**, limits posts to **seven days old**, and waits up to **20 seconds** for each page to load.
* Reports are created automatically in **HTML format** and named by date, for example `15-01-2024.html`.
* They are responsive and include **summaries**, **account grouping**, and a **search function**.

## Notes

* The codebase was originally developed on WSL2, but browser automation was unreliable. Since the pipeline uses a Windows image and the GUI is built as an `.exe`, development is now focused on Windows for consistency.
* Do not change the caption selectors in `instagram_scraper.py`, since they are fragile and will likely break the tool.
* The tool depends on the HTML structure of Instagram, so it may stop working if Instagram changes their pages.
* The default settings are conservative to avoid hitting Instagram's rate limits.
* Each run starts a new browser instance. If you get connection errors, close any running browsers first.
