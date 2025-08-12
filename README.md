# Instagram Helper

[![GitHub Actions](https://github.com/maximbetin/instagram-helper/actions/workflows/ci.yml/badge.svg)](https://github.com/maximbetin/instagram-helper/actions/workflows/ci.yml)

A tool that automatically fetches recent posts from specified Instagram accounts and generates a
stylized HTML report with global date sorting and corresponding links.

## Features

- **Automatic fetching**: Fetches posts from specified Instagram accounts
- **XPath-based caption extraction**: Uses precise XPath selectors for accurate extraction of full
  post content and descriptions
- **Date filtering**: Only fetches posts from the last few days (configurable)
- **HTML report generation**: Creates a stylized, responsive HTML report with all fetched posts
- **Global date sorting**: All posts are sorted by date across all accounts (newest first)
- **Interactive report**: HTML report includes copy-to-clipboard functionality for post links and
  captions
- **Progress tracking**: Real-time console output showing processing progress
- **CLI interface**: Command-line options for flexible usage
- **Environment configuration**: Support for environment variables
- **WSL2 Integration**: Optimized for Windows Subsystem for Linux 2 with automatic browser
  management
- **Debug capabilities**: Built-in page structure analysis for troubleshooting
- **Quality Assurance**: Comprehensive testing, linting, and type checking
- **CI/CD**: Automated testing and building via GitHub Actions

## Requirements

- **Python**: 3.12 or higher
- **Operating System**: Windows, macOS, or Linux (including WSL2)
- **Browser**: Uses your existing Brave browser (WSL2) or Playwright Chromium (fallback)

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/maximbetin/instagram-helper.git
   cd instagram-helper
   ```

2. **Set up virtual environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package**:

   ```bash
   # For normal use
   pip install -e .

   # For development
   pip install -e ".[dev]"
   ```

4. **Install Playwright browsers** (fallback only):

   ```bash
   playwright install chromium
   ```

**Note**: On WSL2, the tool uses your existing Windows Brave browser automatically. Playwright
browsers are only needed as a fallback.

## Usage

### Basic Usage

Run with default settings:

```bash
python cli.py
```

Or use the CLI interface for more options:

```bash
python cli.py --help
```

Or install the package and use the command-line tool:

```bash
pip install -e .
instagram-helper
```

### Default Behavior

- Fetches posts from the last 3 days
- Processes all configured Instagram accounts
- Saves HTML reports and logs to `/mnt/c/Users/Maxim/Desktop/ig_helper/`
- Automatically opens the generated report

### CLI Options

```bash
python cli.py [OPTIONS]

Options:
  --days, -d INT          Number of days back to fetch posts from (default: 3)
  --accounts, -a TEXT...  Specific Instagram accounts to fetch from
  --output, -o PATH       Output directory for reports (default: /mnt/c/Users/Maxim/Desktop/ig_helper)
  --log-dir PATH          Directory for log files (default: /mnt/c/Users/Maxim/Desktop/ig_helper)
  --no-open               Do not automatically open the generated report
      # Verbose mode is now enabled by default for detailed XPath logging
  --help                  Show this message and exit
```

### Examples

```bash
# Use default settings
python cli.py

# Fetch posts from last 3 days
python cli.py --days 3

# Only fetch from specific accounts
python cli.py --accounts gijon biodevas

# Save reports to custom directory
python cli.py --output ./reports

# Don't automatically open the report
python cli.py --no-open

# Verbose mode is now enabled by default for detailed XPath logging
python cli.py

# Debug caption extraction for specific accounts
python cli.py --accounts gijon --days 1
```

## WSL2 Integration

The Instagram Helper automatically handles browser setup when running from WSL2. It will launch your
Windows Brave browser directly from WSL2, preserving your existing profile, cookies, and login
sessions. The browser opens directly to Instagram for immediate use.

### Quick Start (WSL2)

1. **Set up your environment** (one-time setup):

   ```bash
   # Activate virtual environment
   source venv/bin/activate

   # Install dependencies
   pip install -e .
   ```

2. **Run the Instagram Helper** - it handles everything automatically:

   ```bash
   python cli.py
   ```

The tool will:

- Automatically launch Brave browser with remote debugging enabled
- Open Instagram directly for immediate access
- Use your existing Windows Brave profile (keeps you logged in)
- Connect to the browser via `localhost:9222`
- Extract complete post captions using XPath selectors
- Clean up browser processes gracefully when finished

### How It Works

The Instagram Helper uses a direct WSL2-to-Windows approach:

1. **Browser Path**: Uses `/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe`
2. **Profile Access**: Connects to your Windows Brave profile at
   `C:\Users\Maxim\AppData\Local\BraveSoftware\Brave-Browser\User Data`
3. **Network**: Connects via `localhost:9222` (no cross-network issues)
4. **Process Management**: Automatically stops existing Brave processes before launching

### Troubleshooting WSL2

If you encounter issues:

1. **Test browser connectivity**:

   ```bash
   curl http://localhost:9222/json/version
   ```

   Should return browser version info.

2. **Verbose logging is enabled by default** - shows detailed XPath extraction information

3. **Check browser path** - update in `.env` if Brave is installed elsewhere:

   ```bash
   BROWSER_PATH="/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
   ```

4. **Manual browser test**:

   ```bash
   "/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe" \
    --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0
   ```

## Configuration

### Environment Variables

```bash
# Instagram settings
export INSTAGRAM_POST_LOAD_DELAY=3000
export INSTAGRAM_MAX_POSTS_PER_ACCOUNT=3
export INSTAGRAM_POST_LOAD_TIMEOUT=20000
export INSTAGRAM_ACCOUNT_LOAD_DELAY=3000
export INSTAGRAM_RETRY_DELAY=2000
export INSTAGRAM_URL="https://www.instagram.com/"

# Output settings
export OUTPUT_DIR="/path/to/output"
export LOG_DIR="/path/to/logs"
export TIMEZONE_OFFSET=2
```

### Configuration File

Create or edit `.env` file to customize:

```bash
# Browser settings (WSL2)
BROWSER_PATH="/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
BROWSER_USER_DATA_DIR="C:\Users\YourUsername\AppData\Local\BraveSoftware\Brave-Browser\User Data"
BROWSER_DEBUG_PORT=9222

# Output settings
OUTPUT_DIR="/mnt/c/Users/YourUsername/Desktop/ig_helper"
LOG_DIR="/mnt/c/Users/YourUsername/Desktop/ig_helper"

# Instagram settings
INSTAGRAM_MAX_POSTS_PER_ACCOUNT=3
INSTAGRAM_POST_LOAD_DELAY=3000
```

Edit `config.py` to modify:

- **Instagram Accounts**: List of usernames to fetch posts from
- **Default Settings**: Timeouts, retry delays, etc.

## Output

The tool generates an interactive HTML report and detailed logs:

**HTML Report**:

- Summary statistics (total accounts checked, total posts found, date range)
- All posts sorted by date (newest first) with complete captions, descriptions, and metadata
- Full post content including event details, descriptions, people mentioned, and relevant hashtags
- Direct links to original Instagram posts
- Copy-to-clipboard buttons for post URLs and full captions
- Responsive design for desktop and mobile
- Clean, readable formatting with proper line breaks and emoji support

**Log Files**:

- Detailed logging of the scraping process
- Account processing status and results
- Error messages and debugging information
- Timestamps for all operations

**File Naming**:

- HTML reports: `DD-MM-YYYY.html` (e.g., `19-12-2024.html`)
- Log files: `DD-MM-YYYY.log` (e.g., `19-12-2024.log`)
- Default location: `/mnt/c/Users/Maxim/Desktop/ig_helper/`

## Technical Details

### Caption Extraction

The Instagram Helper uses XPath selectors for precise caption extraction:

```python
CAPTION_XPATHS = [
    "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/span",
    "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/h1",
]
```

This approach ensures reliable extraction of complete post content including:

- Full event descriptions and details
- People and organizations mentioned
- Dates and location information
- Relevant hashtags and social media tags

### XPath Logging and Debugging

The tool now provides comprehensive XPath logging by default to help with debugging and development:

**Available XPath Selectors**: All configured XPath selectors are logged at the start of caption
extraction **Attempt Tracking**: Each XPath attempt is logged with clear success/failure indicators:

- ✓ Success: Shows the XPath used and caption preview
- ✗ Element not found: XPath selector didn't match any elements
- ✗ Empty caption: Element found but contained no text
- ✗ Error: XPath evaluation failed with specific error details

**Example Log Output**:

```bash
[DEBUG] Available XPath selectors for caption extraction:
[DEBUG]   1. /html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/span
[DEBUG]   2. /html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/h1
[DEBUG] Attempting to extract caption using 2 XPath selectors...
[DEBUG] XPath attempt 1/2:
[DEBUG] Trying XPath: /html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/span
[DEBUG] ✓ Found caption using XPath: /html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/span...
[DEBUG]   Caption preview: 'Evento cultural en Gijón este fin de semana...'
[DEBUG] Caption successfully extracted on attempt 1
```

This detailed logging helps developers understand exactly which XPath selectors are working and
which need updating when Instagram changes their page structure.

### Debug Capabilities

The tool now provides detailed debugging information by default:

- Page structure analysis
- Element count reporting
- Potential caption candidate identification
- XPath selector success/failure logging with detailed XPath information
- Caption extraction attempts and results

## Development

### Setup

```bash
# Install with development dependencies
make setup-dev

# Install Playwright browsers
make install-browsers
```

### Available Commands

```bash
# Show all available commands
make help

# Run tests
make test

# Run tests with coverage
make test-cov

# Format and lint code
make format
make lint

# Run all quality checks
make check-all

# Clean build artifacts
make clean

# Build package
make build
```

### Code Quality Tools

- **Ruff**: Code formatting and linting (88 character line length)
- **MyPy**: Static type checking
- **Pytest**: Testing framework with coverage reporting

### Testing

```bash
# All tests
make test

# With coverage
make test-cov

# Specific test file
pytest tests/test_main.py -v

# Specific test function
pytest tests/test_main.py::test_get_account_post_urls -v
```

## CI/CD Pipeline

The project uses GitHub Actions for automated testing and quality assurance.

### CI Job

- **Python Version**: Tests against Python 3.12
- **Quality Checks**: Linting (ruff), type checking (mypy), tests (pytest)
- **Coverage**: Reports uploaded to Codecov

### Build Job

- **Trigger**: Only on main branch pushes
- **Actions**: Build package, test installation, verify CLI entry point

### Local Development Workflow

```bash
# 1. Set up development environment
make dev-setup

# 2. Make code changes

# 3. Run quality checks locally
make check-all

# 4. Commit and push (triggers CI)
git add .
git commit -m "Description of changes"
git push origin main
```

## Project Structure

```bash
instagram-helper/
├── .github/                 # GitHub-specific files
│   └── workflows/          # CI/CD pipeline definitions
├── cli.py                  # Command-line interface (main entry point)
├── config.py               # Configuration settings
├── utils.py                # Logging utilities
├── instagram_scraper.py    # Instagram scraping logic
├── report_generator.py     # HTML report generation
├── browser_manager.py      # Browser management
├── templates/              # HTML templates
├── tests/                  # Test suite
├── pyproject.toml          # Project configuration and dependencies
├── Makefile                # Development automation commands
└── README.md               # This file
```

## Dependencies

### Runtime Dependencies

- `playwright` - Browser automation and web scraping
- `jinja2` - HTML template rendering
- `python-dotenv` - Environment variable management

### Development Dependencies

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `ruff` - Code formatting and linting
- `mypy` - Static type checking
- `coverage[toml]` - Coverage measurement

## Troubleshooting

### Common Issues

1. **Browser Connection Issues**:

   - Ensure browser is running with remote debugging enabled
   - Check firewall settings and port accessibility
   - Verify WSL2 network configuration

2. **Caption Extraction Issues**:

   - Tool uses XPath selectors for Instagram's current layout
   - If captions appear empty, Instagram may have changed their DOM structure
   - Verbose logging is now enabled by default for detailed extraction debugging
   - Check log files for page structure analysis

3. **Instagram Rate Limiting**:

   - Reduce `INSTAGRAM_POST_LOAD_DELAY` values
   - Limit `INSTAGRAM_MAX_POSTS_PER_ACCOUNT`
   - Use longer delays between requests

4. **Package Installation Issues**:
   - Ensure virtual environment is activated
   - Check Python version compatibility (3.12+)
   - Verify all dependencies are available

### Debug Mode

Verbose logging is now enabled by default for detailed XPath and caption extraction information.

### Log Files

Check log files for detailed error information:

- Location: Configured via `LOG_DIR` environment variable
- Format: Daily log files with timestamps
- Content: Detailed operation logs and error traces

## Contributing

### Development Setup

1. Fork the repository
2. Clone your fork locally
3. Set up development environment: `make dev-setup`
4. Create a feature branch
5. Make changes and test locally
6. Ensure all quality checks pass: `make check-all`
7. Submit a pull request

### Code Standards

- Follow PEP 8 style guidelines (enforced by ruff)
- Use type hints for all functions (enforced by mypy)
- Write tests for new functionality
- Update documentation as needed
- Keep commits atomic and well-described

### Pull Request Process

1. **Automated Checks**: CI pipeline runs automatically
2. **Code Review**: All changes require review
3. **Quality Gates**: Must pass linting, type checking, and tests
4. **Build Verification**: Package must build and install correctly

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
