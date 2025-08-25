# Instagram Helper

A tool that automatically fetches recent posts from Instagram accounts and generates HTML reports. Designed for content creators, marketers, researchers, and social media analysts.

## What This Tool Does

Instagram Helper helps you:

- Monitor multiple Instagram accounts for recent activity
- Generate reports of Instagram posts with captions, dates, and metadata
- Track content trends across multiple accounts over time
- Automate social media monitoring without manual browsing
- Create content calendars based on recent Instagram activity

## Key Features

- **Instagram Scraping**: Automatically extracts post content, captions, and timestamps
- **GUI Interface**: Tkinter-based interface with real-time progress monitoring
- **HTML Reports**: Generates reports with statistics and post details
- **Browser Integration**: Works with Chrome, Brave, and Edge on Windows, Linux, and WSL2
- **Configuration Options**: Adjust settings without restarting the application
- **Progress Tracking**: Monitor scraping progress with logs and progress bars
- **Multiple Accounts**: Handle multiple Instagram accounts in a single session
- **Session Management**: Reuses browser sessions to maintain Instagram login state

## System Requirements

### Basic Requirements

- **Python 3.12 or newer** (required for modern type hints and features)
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+, CentOS 8+), or macOS 10.15+
- **Memory**: Minimum 4GB RAM, recommended 8GB+ for large operations
- **Storage**: At least 500MB free space for the application and reports
- **Network**: Stable internet connection for Instagram access

### Browser Requirements

- **Chromium-based browser** (Chrome, Brave, or Edge) with remote debugging enabled
- **Browser Version**: Chrome 90+, Brave 1.20+, or Edge 90+
- **Remote Debugging**: Must support Chrome DevTools Protocol (CDP)
- **Session Management**: Browser should maintain Instagram login sessions

### WSL2 Environment (Recommended)

This tool works best with Windows Subsystem for Linux 2:

- **WSL2 Benefits**:
  - Seamless Windows/Linux integration
  - Automatic path translation between Windows and Linux
  - Optimized browser process management
  - Better performance for development workflows

- **WSL2 Requirements**:
  - Windows 10 version 2004+ or Windows 11
  - WSL2 kernel update package installed
  - Virtualization enabled in BIOS

## Quick Start

```bash
# Clone the repository
git clone https://github.com/maxim/instagram-helper.git
cd instagram-helper

# Setup development environment
make setup-dev

# Activate the virtual environment
source venv/bin/activate
```

```bash
# Configuration is now hardcoded - no setup needed!
# The application uses predefined settings optimized for WSL2 environments.
```

```bash
# Run quality checks to ensure everything is working
make check-all

# Test the application
python run.py
```

### Common Setup Issues

| Issue | Solution |
|-------|----------|
| **Python version error** | Ensure Python 3.12+ is installed and in PATH |
| **Browser not found** | Verify BROWSER_PATH in .env points to valid executable |
| **Permission denied** | Check file permissions and ensure directories are writable |
| **WSL2 path issues** | Use Windows-style paths for browser directories, Linux-style for output |
| **Port 9222 in use** | Close existing browser instances or change BROWSER_DEBUG_PORT |
| **Import errors** | Ensure virtual environment is activated and dependencies are installed |

```bash
# Activate your virtual environment
source venv/bin/activate

# Launch the application
python run.py
```

## Usage

### GUI Interface

The Instagram Helper provides a simple interface with these main sections:

#### Configuration Panel

- **Post Age Limit**: Set maximum age of posts to scrape (in days)
- **Posts Per Account**: Limit number of posts to process per Instagram account
- **Timeout Settings**: Configure page load timeouts for reliable scraping
- **Real-time Updates**: Settings apply immediately without restarting

#### Account Management

- **Text Area Input**: Enter Instagram accounts, one per line
- **Bulk Operations**: Paste multiple accounts at once
- **Dynamic Updates**: Add/remove accounts on-the-fly
- **Validation**: Automatic filtering of empty lines and whitespace

#### Progress Monitoring

- **Real-time Progress Bar**: Visual indication of scraping progress
- **Status Updates**: Live status messages showing current operation
- **Log Streaming**: Detailed logs of all scraping activities
- **Error Reporting**: Clear error messages with context

#### Control Panel

- **Start Scraping**: Begin the scraping process with current settings
- **Stop Scraping**: Safely stop ongoing operations
- **Clear Logs**: Reset the log display for new sessions
- **Progress Reset**: Clear progress indicators for new runs

### Configuration Options

#### Scraping Parameters

| Parameter | Description | Default | Recommended Range |
|-----------|-------------|---------|-------------------|
| **Post Age Limit** | Maximum age of posts to scrape | 7 days | 1-30 days |
| **Posts Per Account** | Number of posts to process per account | 5 posts | 1-20 posts |
| **Page Load Timeout** | Time to wait for page loading | 10 seconds | 5-30 seconds |

#### Performance Tuning

- **For Fast Scraping**: Lower timeout values, fewer posts per account
- **For Reliable Scraping**: Higher timeout values, conservative post limits
- **For Large Scale**: Balance between speed and Instagram's rate limiting

### Instagram Account Management

#### Adding Accounts

1. **Single Account**: Type the username (e.g., `instagram`)
2. **Multiple Accounts**: Paste a list, one per line
3. **Bulk Import**: Copy-paste from existing lists or spreadsheets

#### Account Validation

- **Format**: Usernames only (no @ symbols needed)
- **Filtering**: Empty lines and whitespace are automatically removed
- **Limits**: No hard limit on number of accounts
- **Persistence**: Accounts are remembered between sessions

#### Best Practices

- **Start Small**: Begin with 5-10 accounts to test configuration
- **Monitor Performance**: Watch for rate limiting or errors
- **Batch Processing**: Group similar accounts together
- **Regular Updates**: Refresh account lists periodically

### Report Generation

#### Automatic Reports

- **File Naming**: Reports use DD-MM-YYYY format (e.g., `15-01-2024.html`)
- **Output Location**: Configurable via `OUTPUT_DIR` environment variable
- **Format**: Professional HTML with responsive design
- **Content**: Post captions, dates, account information, and statistics

#### Report Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Statistics Summary**: Total posts, accounts, and date ranges
- **Account Grouping**: Posts organized by Instagram account
- **Search & Filter**: Easy navigation through large datasets
- **Export Ready**: Professional reports for sharing and analysis

### Performance Optimization

#### Scraping Speed

- **Parallel Processing**: Multiple accounts processed sequentially for stability
- **Smart Delays**: Built-in delays prevent Instagram rate limiting
- **Timeout Management**: Configurable timeouts for different network conditions
- **Error Recovery**: Continues processing even when individual posts fail

#### Resource Management

- **Memory Efficient**: Processes data incrementally without accumulation
- **Browser Cleanup**: Automatic cleanup of browser resources
- **Session Reuse**: Maintains Instagram login state across operations
- **Graceful Degradation**: Continues operation despite partial failures

### Workflow Examples

#### Daily Monitoring Workflow

1. **Morning Setup**: Launch application and verify accounts
2. **Configuration**: Set post age to 1 day, 10 posts per account
3. **Execution**: Start scraping and monitor progress
4. **Review**: Check generated reports for new content
5. **Analysis**: Review trends and engagement patterns

#### Weekly Analysis Workflow

1. **Extended Range**: Set post age to 7 days for weekly overview
2. **Comprehensive Scraping**: Increase posts per account to 20
3. **Batch Processing**: Process all accounts in one session
4. **Report Generation**: Create comprehensive weekly reports
5. **Trend Analysis**: Compare weekly data for insights

#### Research Workflow

1. **Target Selection**: Focus on specific account types or industries
2. **Deep Scraping**: Higher post limits for comprehensive data
3. **Multiple Sessions**: Run multiple scraping sessions for large datasets
4. **Data Compilation**: Combine reports for analysis
5. **Insight Generation**: Identify patterns and trends

## Configuration

### Hardcoded Configuration

The application now uses **hardcoded configuration values** optimized for WSL2 environments. This approach provides:

- **Zero Setup**: No environment variables or configuration files needed
- **Immediate Use**: Application works out of the box
- **Reliability**: No configuration errors or missing variables
- **PyInstaller Compatible**: Perfect for building standalone executables

### Current Configuration

The application is pre-configured with these optimized settings:

#### Browser Configuration
- **Browser Path**: `/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe`
- **User Data Directory**: `C:\Users\Maxim\AppData\Local\BraveSoftware\Brave-Browser\User Data`
- **Profile Directory**: `Default`
- **Debug Port**: `9222`
- **Load Delay**: `5000ms`
- **Start URL**: `https://www.instagram.com/`

#### Instagram Configuration
- **Max Posts Per Account**: `3`
- **Post Load Timeout**: `20000ms`
- **Base URL**: `https://www.instagram.com/`

#### Output Configuration
- **Output Directory**: `/mnt/c/Users/Maxim/Desktop/ig_helper`
- **Log Directory**: `/mnt/c/Users/Maxim/Desktop/ig_helper`
- **Template Path**: `templates/template.html`

#### Timezone Configuration
- **Timezone Offset**: `+2 hours` (Central European Time)

### Customizing Configuration

To modify these settings, edit the `config.py` file directly:

```python
# Example: Change max posts per account
INSTAGRAM_MAX_POSTS_PER_ACCOUNT: int = 10

# Example: Change output directory
OUTPUT_DIR: Path = field(
    default_factory=lambda: Path("/mnt/c/Users/YourUsername/Desktop/ig_reports")
)
```

# Instagram Configuration
INSTAGRAM_MAX_POSTS_PER_ACCOUNT=5
INSTAGRAM_POST_LOAD_TIMEOUT=10000

# Output Configuration
OUTPUT_DIR="/Users/username/Documents/Instagram-Reports"
LOG_DIR="/Users/username/Documents/Instagram-Logs"
TIMEZONE_OFFSET=-5
```

## Important Notes

**CRITICAL**: Do not modify the caption selectors in `instagram_scraper.py`. These selectors are fragile and changes will break the tool's functionality.

**Instagram Dependencies**: The tool's success depends on Instagram's HTML structure remaining consistent. The tool may need updates if Instagram makes significant changes to their pages.

**Rate Limiting**: Instagram may block requests if too many are made too quickly. The default settings are conservative to avoid this.

**WSL2 Optimization**: This tool is specifically designed for Windows Subsystem for Linux 2 environments and may not work optimally in other setups.

**Browser Management**: The tool always launches a new browser instance to ensure reliable operation. If you encounter connection errors, close any existing browser instances and try again.

**Account Management**: Instagram accounts are now managed directly through the GUI text area, making it easier to customize without editing external files.

## Implementation Details

This section explains the key implementation decisions and architectural choices.

### Configuration Management

**Why a frozen dataclass with validation?**

- **Immutability**: The `Settings` class is frozen to prevent runtime modification
- **Validation timing**: Validation happens after all fields are set
- **Environment detection**: Automatically detects testing environments and provides fallback values

**Why use `object.__setattr__` for updates?**

- **Frozen constraint bypass**: Since the dataclass is frozen, we use `object.__setattr__` to update values during initialization
- **Type safety**: Maintains type checking while allowing necessary post-initialization modifications

### WSL2 Browser Integration

**Why complex WSL2 detection and handling?**

- **Cross-platform compatibility**: WSL2 runs Linux but often needs to launch Windows browsers
- **Path translation**: Automatically handles Windows/Linux path differences
- **Process management**: Different process killing strategies for Windows vs Linux environments

**Key WSL2 detection logic:**

```python
is_wsl2 = (
    os.name == "posix"  # Linux shell
    and "microsoft" in os.uname().release.lower()  # WSL2 kernel
    and ("win" in str(browser_path).lower() or ".exe" in str(browser_path).lower())  # Windows browser
)
```

### Instagram Caption Extraction

**Why hardcoded XPath instead of CSS selectors?**

- **Fragility**: Instagram's HTML structure changes frequently, making CSS selectors unreliable
- **Specificity**: The exact XPath targets the specific caption element
- **Maintenance**: When Instagram changes their structure, only this one XPath needs updating

**CRITICAL WARNING**: Do not modify this XPath selector. Instagram's HTML structure is fragile and changes will break caption extraction.

### GUI Account Management

**Why text area instead of listbox with buttons?**

- **Simplicity**: Direct text input eliminates complex dialog logic
- **Bulk operations**: Users can paste multiple accounts at once
- **No file dependencies**: Eliminates external text files
- **Immediate feedback**: Changes are visible immediately

**Account parsing logic:**

```python
# Each line becomes an account, empty lines are automatically filtered
return [line.strip() for line in self.account_text.get(1.0, tk.END).splitlines() if line.strip()]
```

### Timezone Handling

**Why timezone conversion in the scraper?**

- **Instagram's UTC timestamps**: Instagram provides all dates in UTC
- **User preference**: Users can configure their local timezone via `TIMEZONE_OFFSET`
- **Consistent reporting**: All dates in reports are converted to the user's local timezone

**Timezone conversion flow:**

1. Instagram provides UTC timestamp
2. Parse as UTC datetime: `datetime.fromisoformat(dt_attr.replace("Z", "+00:00"))`
3. Convert to user's timezone: `utc_dt.astimezone(self.settings.TIMEZONE)`

### Browser Process Management

**Why kill existing browser processes?**

- **Port conflicts**: Only one browser can use port 9222 for remote debugging
- **Session conflicts**: Existing browser instances may have different debugging configurations
- **Clean state**: Ensures the tool starts with a known browser state

**Process killing strategy:**

- **WSL2/Windows**: Uses `taskkill.exe /f /im brave.exe`
- **Linux/macOS**: Uses `pkill -f brave`
- **Fallback handling**: Gracefully handles missing process management tools

### Threading Architecture

**Why separate scraping thread?**

- **GUI responsiveness**: Prevents the GUI from freezing during long scraping operations
- **Progress updates**: Allows real-time progress updates and log streaming
- **Cancellation support**: Users can stop scraping without killing the entire application

**Thread safety considerations:**

- **Queue-based logging**: Log messages are sent via a thread-safe queue
- **GUI updates**: All GUI updates are scheduled on the main thread using `root.after()`
- **State management**: Thread-safe event flags for stopping operations

### Error Handling

**Why graceful degradation over strict validation?**

- **User experience**: The tool continues working even if some posts fail to scrape
- **Instagram volatility**: Instagram's structure changes frequently, so partial failures are expected
- **Logging strategy**: Comprehensive logging allows users to understand what failed and why

**Error handling patterns:**

- **Try-catch blocks**: Around all Instagram-specific operations
- **Fallback values**: Default values when environment variables are missing
- **User feedback**: Clear error messages and status updates in the GUI

## Building Executables

### PyInstaller Build

The application can be built into standalone executables using PyInstaller:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed run.py --name instagram-helper

# The executable will be created in the dist/ directory
```

### Build Options

- **`--onefile`**: Creates a single executable file
- **`--windowed`**: Runs without console window (Windows)
- **`--name`**: Sets the output filename

### Deployment

The built executable:
- **No Python installation required** on target machines
- **No environment variables needed** - all configuration is hardcoded
- **Self-contained** - includes all dependencies
- **Cross-platform** - build on Linux for Linux, Windows for Windows

### CI/CD Pipeline

The GitHub Actions workflow automatically:
- Runs tests on Ubuntu and Windows
- Builds executables using PyInstaller
- Creates releases with downloadable executables
- Tags releases with version numbers

## Development

### Quality Checks

This project uses `ruff` (linting/formatting), `mypy` (static type checking), and `pytest` (tests).

- **Run all checks**:

  ```bash
  make check-all
  ```

- **Format code**:

  ```bash
  make format
  ```

- **Run tests**:

  ```bash
  make test
  ```

Configurations live in `pyproject.toml` and are executed via the `Makefile`.

### Makefile Commands

The `Makefile` provides commands to streamline development:

- `make setup-dev`: Sets up the development environment
- `make test`: Runs the test suite
- `make format`: Formats code with `ruff`
- `make lint`: Lints code with `ruff`
- `make type-check`: Runs `mypy`
- `make check-all`: Runs formatting, linting, type checking, and tests
- `make clean`: Removes build artifacts

### Common Development Workflows

```bash
# Setup and activate environment
make setup-dev
source venv/bin/activate

# Run quality checks before committing
make check-all

# Test with custom parameters
python run.py

# Run specific test files
./venv/bin/pytest tests/test_instagram_scraper.py -v
```
