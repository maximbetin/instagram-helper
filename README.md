# Instagram Helper

[![CI Pipeline](https://github.com/maximbetin/instagram-helper/actions/workflows/ci.yml/badge.svg)](https://github.com/maximbetin/instagram-helper/actions/workflows/ci.yml)

A tool that automatically fetches recent posts from specified Instagram accounts and generates a
stylized HTML report with global date sorting and corresponding links.

## Features

- **Automatic fetching**: Fetches posts from specified Instagram accounts
- **Date filtering**: Only fetches posts from the last few days (configurable)
- **HTML report generation**: Creates a stylized, responsive HTML report with all fetched posts
- **Global date sorting**: All posts are sorted by date across all accounts (newest first)
- **Interactive report**: HTML report includes copy-to-clipboard functionality for post links and
  captions
- **Progress tracking**: Real-time console output showing processing progress
- **CLI interface**: Command-line options for flexible usage
- **Environment configuration**: Support for environment variables
- **WSL2 Integration**: Optimized for Windows Subsystem for Linux 2
- **Quality Assurance**: Comprehensive testing, linting, and type checking
- **CI/CD**: Automated testing and building via GitHub Actions

## Requirements

- **Python**: 3.12 or higher
- **Operating System**: Windows, macOS, or Linux (including WSL2)
- **Browser**: Playwright automatically installs and manages Chromium browser

## Installation

1. Clone the repository

   ```bash
   git clone https://github.com/maximbetin/instagram-helper.git
   cd instagram-helper
   ```

2. Install Playwright browsers

   ```bash
   playwright install
   ```

3. Install the package with development dependencies

   ```bash
   pip install -e ".[dev]"
   ```

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
  --verbose, -v           Enable verbose logging
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

# Enable verbose logging
python cli.py --verbose
```

## WSL2 Integration

When running from WSL2, you can connect to an already-running Brave browser on Windows to reuse your
logged-in session and cookies. This is the recommended approach.

### Start Brave with Remote Debugging

**Option 1: Use the provided batch file (easiest)**:

1. Double-click `start_brave_debug.bat` in Windows
2. Keep the Brave window open while running the script

**Option 2: Manual command**:

```powershell
# Close all Brave instances first
Stop-Process -Name brave -Force -ErrorAction SilentlyContinue

# Start Brave with remote debugging enabled
& "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222
```

**Option 3: Bind to all interfaces (if you need external access)**:

```powershell
Stop-Process -Name brave -Force -ErrorAction SilentlyContinue
& "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0
```

### Connect from WSL2

1. Start Brave on Windows with remote debugging enabled (see above)
2. Run the tool from WSL2 - it will automatically connect:

   ```bash
   python cli.py
   ```

The app will first try to connect to the existing Brave instance, then fall back to launching
Chromium if needed.

### Troubleshooting WSL2

1. Confirm Windows is listening:

   ```powershell
   netstat -ano | findstr :9222
   ```

2. From WSL2, test the connection:

   ```bash
   curl "http://localhost:9222/json/version"
   ```

3. Make sure Brave is running with the `--remote-debugging-port=9222` flag
4. Check Windows Firewall if using external binding

## Configuration

### Environment Variables

```bash
# Browser settings
export BROWSER_DEBUG_PORT=9222
export BROWSER_LOAD_DELAY=5000
export BROWSER_LOAD_TIMEOUT=15000
# BROWSER_PATH is only needed if not using remote debugging
# export BROWSER_PATH="/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

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

Edit `config.py` to modify:

- **Post Fetching Settings**: Days back to fetch (default: 3), max posts per account (default: 3)
- **Instagram Accounts**: List of usernames to fetch posts from
- **Browser Settings**: Browser path, debug port, timeouts
- **Output Settings**: Output and log directories

## Output

The tool generates an interactive HTML report and detailed logs:

**HTML Report**:

- Summary statistics (total accounts checked, total posts found, date range)
- All posts sorted by date (newest first) with captions, dates, and account information
- Direct links to original Instagram posts
- Copy-to-clipboard buttons for post URLs and captions
- Responsive design for desktop and mobile

**Log Files**:

- Detailed logging of the scraping process
- Account processing status and results
- Error messages and debugging information
- Timestamps for all operations

**File Naming**:

- HTML reports: `DD-MM-YYYY.html` (e.g., `19-12-2024.html`)
- Log files: `DD-MM-YYYY.log` (e.g., `19-12-2024.log`)
- Default location: `/mnt/c/Users/Maxim/Desktop/ig_helper/`

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

2. **Instagram Rate Limiting**:

   - Reduce `INSTAGRAM_POST_LOAD_DELAY` values
   - Limit `INSTAGRAM_MAX_POSTS_PER_ACCOUNT`
   - Use longer delays between requests

3. **Package Installation Issues**:
   - Ensure virtual environment is activated
   - Check Python version compatibility (3.12+)
   - Verify all dependencies are available

### Debug Mode

Enable verbose logging:

```bash
python cli.py --verbose
```

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
