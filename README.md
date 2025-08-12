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

### Quick Start (WSL2)

For WSL2 users, the fastest way to get started:

```bash
# Run the WSL2-specific setup script
./setup-dev.sh

# Or use the Makefile command
make setup-wsl2
```

This script automatically:

- Checks Python 3.12+ availability
- Creates and activates a virtual environment
- Installs all Python and Node.js dependencies
- Sets up Playwright browsers
- Runs initial quality checks
- Provides next steps guidance

### Manual Setup

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install with development dependencies
make setup-dev

# Install Playwright browsers
make install-browsers

# Install Node.js dependencies for Prettier
make setup-node
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

The project uses a comprehensive set of quality assurance tools configured in `pyproject.toml`:

#### Ruff - Code Linting and Formatting

- **Configuration**: Located in `pyproject.toml` under `[tool.ruff]`
- **Line Length**: 88 characters (Black-compatible)
- **Rules**: Enforces PEP 8, pyflakes, isort, and flake8-bugbear
- **Commands**:

  ```bash
  make lint          # Check code quality
  make format        # Auto-format code
  ruff check .       # Direct linting
  ruff format .      # Direct formatting
  ```

#### MyPy - Static Type Checking

- **Configuration**: Located in `pyproject.toml` under `[tool.mypy]`
- **Strict Mode**: Enabled with comprehensive type checking
- **Target**: Python 3.12+
- **Commands**:

  ```bash
  make type-check    # Run type checking
  mypy .             # Direct type checking
  ```

#### Pytest - Testing Framework

- **Configuration**: Located in `pyproject.toml` under `[tool.pytest.ini_options]`
- **Coverage**: Integrated with coverage.py for comprehensive reporting
- **Commands**:

  ```bash
  make test          # Run test suite
  make test-cov      # Run tests with coverage
  make test-fast     # Run tests without coverage (faster)
  pytest tests/ -v   # Direct test execution
  ```

#### Prettier - Documentation Formatting

- **Configuration**: Located in `.prettierrc` and `package.json`
- **Target**: README.md formatting only
- **Commands**:

  ```bash
  make format-readme # Format README.md
  npm run format:readme    # Direct formatting
  npm run format:check     # Check formatting
  ```

### Quality Check Workflow

#### Before Committing

```bash
# Run all quality checks
make check-all

# This runs:
# 1. ruff check . (linting)
# 2. mypy . (type checking)
# 3. pytest tests/ (testing)
```

#### Code Formatting

```bash
# Format all code and documentation
make format-all

# This runs:
# 1. ruff format . (Python code)
# 2. npm run format:readme (README.md)
```

#### Individual Checks

```bash
# Linting only
make lint

# Type checking only
make type-check

# Testing only
make test

# README formatting only
make format-readme
```

### Testing

```bash
# All tests
make test

# With coverage
make test-cov

# Fast tests (no coverage)
make test-fast

# Specific test file
pytest tests/test_main.py -v

# Specific test function
pytest tests/test_main.py::test_get_account_post_urls -v

# Run with specific markers
pytest -m "not slow" tests/  # Skip slow tests
pytest -m integration tests/  # Run only integration tests
```

### Development Environment (WSL2)

#### Virtual Environment Management

The project uses Python virtual environments for dependency isolation:

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate (WSL2)
source venv/bin/activate

# Deactivate
deactivate

# Install dependencies in venv
pip install -e ".[dev]"
```

#### Node.js Dependencies

Prettier is managed via npm for README.md formatting:

```bash
# Install Node.js dependencies
npm install

# Check README.md formatting
npm run format:check

# Format README.md
npm run format:readme
```

#### WSL2-Specific Considerations

- **Python Paths**: Use `python3.12` or `python3` commands
- **Virtual Environment**: Always activate before running quality checks
- **File Permissions**: Ensure scripts are executable (`chmod +x setup-dev.sh`)
- **Network**: Localhost connections work seamlessly between WSL2 and Windows

## CI/CD Pipeline

The project uses GitHub Actions for automated testing and quality assurance.

### CI Job

- **Python Version**: Tests against Python 3.12
- **Node.js**: Version 18 for Prettier
- **Quality Checks**:
  - Linting (ruff)
  - Type checking (mypy)
  - Tests (pytest with coverage)
  - README formatting (Prettier)
- **Coverage**: Reports uploaded to Codecov
- **Dependencies**: Installs both Python and Node.js dependencies

### Build Job

- **Trigger**: Only on main branch pushes
- **Actions**: Build package, test installation, verify CLI entry point

### Local Development Workflow

```bash
# 1. Set up development environment (WSL2)
./setup-dev.sh
# OR
make setup-wsl2

# 2. Make code changes

# 3. Run quality checks locally
make check-all

# 4. Format code and documentation
make format-all

# 5. Commit and push (triggers CI)
git add .
git commit -m "Description of changes"
git push origin main
```

### Quality Assurance Tools

The project uses a comprehensive set of tools to ensure code quality and consistency:

#### Code Quality

- **Ruff**: Fast Python linter and formatter that enforces PEP 8 style guidelines
  - Configured in `pyproject.toml` with 88-character line length
  - Enforces multiple rule sets: E (pycodestyle), W (pycodestyle), F (pyflakes), I (isort), B (flake8-bugbear)
- **MyPy**: Static type checker that ensures type safety across the codebase
  - Strict mode enabled with comprehensive type checking
  - Configured to target Python 3.12+
- **Pytest**: Testing framework with comprehensive test coverage reporting
  - Integrated with coverage.py for detailed coverage analysis
  - Supports test markers for slow/integration tests

#### Documentation Formatting

- **Prettier**: Markdown formatter that ensures consistent README.md formatting
  - Configured in `.prettierrc` with markdown-specific settings
  - 88-character line width, double quotes, spaces for indentation

#### Configuration Files

- **`pyproject.toml`**: Central configuration for Python tools (ruff, mypy, pytest, coverage)
- **`.prettierrc`**: Prettier configuration for README.md formatting
- **`package.json`**: Node.js dependencies and scripts for Prettier
- **`Makefile`**: Development automation commands for all quality checks

#### Commands

```bash
# Run all quality checks
make check-all          # Lint + type-check + test

# Format code and documentation
make format             # Format Python code with ruff
make format-readme      # Format README.md with Prettier
make format-all         # Format everything (ruff + prettier)

# Testing
make test               # Run test suite
make test-cov          # Run tests with coverage reporting
make test-fast         # Run tests without coverage (faster)

# Linting and type checking
make lint               # Run ruff linting
make type-check         # Run mypy type checking
ruff check .            # Direct ruff linting
mypy .                  # Direct mypy type checking
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
- `prettier` - Markdown formatting for README.md

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

#### Option 1: WSL2 Quick Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/maximbetin/instagram-helper.git
cd instagram-helper

# Run the automated setup script
./setup-dev.sh
```

#### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/maximbetin/instagram-helper.git
cd instagram-helper

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
make setup-dev
make setup-node
make install-browsers
```

#### Option 3: Makefile Commands

```bash
# Complete development setup
make dev-setup

# WSL2-specific setup
make setup-wsl2
```

### Development Workflow

1. Fork the repository
2. Clone your fork locally
3. Set up development environment using one of the options above
4. Create a feature branch
5. Make changes and test locally
6. Ensure all quality checks pass: `make check-all`
7. Format code and documentation: `make format-all`
8. Submit a pull request

### WSL2 Development Setup Script

The `setup-dev.sh` script provides an automated way to set up the complete development environment:

#### Features

- **Automatic Detection**: Checks Python 3.12+ and Node.js availability
- **Virtual Environment**: Creates and activates a Python virtual environment
- **Dependency Installation**: Installs all Python and Node.js dependencies
- **Browser Setup**: Installs Playwright browsers for testing
- **Quality Checks**: Runs initial quality checks to verify setup
- **WSL2 Optimized**: Designed specifically for WSL2 environments

#### What It Does

1. **Environment Checks**: Verifies Python 3.12+ and Node.js
2. **Virtual Environment**: Creates `venv/` directory and activates it
3. **Python Dependencies**: Installs package in development mode with all dev dependencies
4. **Node.js Dependencies**: Installs Prettier for README.md formatting
5. **Playwright Browsers**: Installs browser binaries for testing
6. **Initial Quality Checks**: Runs ruff, mypy, and pytest to verify setup
7. **Guidance**: Provides next steps and available commands

#### Usage

```bash
# Make executable (first time only)
chmod +x setup-dev.sh

# Run the setup
./setup-dev.sh

# Or use the Makefile command
make setup-wsl2
```

### Code Standards

- Follow PEP 8 style guidelines (enforced by ruff)
- Use type hints for all functions (enforced by mypy)
- Write tests for new functionality
- Update documentation as needed
- Keep commits atomic and well-described
- Ensure README.md is properly formatted (enforced by Prettier)

### Pull Request Process

1. **Automated Checks**: CI pipeline runs automatically
2. **Code Review**: All changes require review
3. **Quality Gates**: Must pass linting, type checking, and tests
4. **Build Verification**: Package must build and install correctly

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
