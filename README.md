# Instagram Helper

A **professional-grade GUI tool** that automatically fetches recent posts from specified Instagram accounts and generates comprehensive HTML reports with real-time monitoring and dynamic configuration options.

## What This Tool Does

Instagram Helper is designed for **content creators, marketers, researchers, and social media analysts** who need to:

- **Monitor multiple Instagram accounts** simultaneously for recent activity
- **Generate professional reports** of Instagram posts with captions, dates, and metadata
- **Track content trends** across multiple accounts over time
- **Automate social media monitoring** without manual browsing
- **Create content calendars** based on recent Instagram activity

## Key Capabilities

- **Smart Instagram Scraping**: Automatically detects and extracts post content, captions, and timestamps
- **Professional GUI Interface**: Tkinter-based interface with real-time progress monitoring
- **Comprehensive Reporting**: Generates beautiful HTML reports with statistics and post details
- **Cross-Platform Browser Integration**: Works with Chrome, Brave, and Edge across Windows, Linux, and WSL2
- **Dynamic Configuration**: Adjust settings on-the-fly without restarting the application
- **Real-Time Monitoring**: Watch scraping progress live with detailed logs and progress bars
- **Batch Processing**: Handle multiple Instagram accounts efficiently in a single session
- **Session Persistence**: Reuses browser sessions to maintain Instagram login state

## Features

- **GUI Interface**: Modern Tkinter-based interface with real-time monitoring and progress tracking
- **Real-Time Logs**: Monitor scraping progress as it happens with detailed status updates
- **Dynamic Configuration**: Adjust post age limits, post counts, and timeout values without editing files
- **Account Management**: Add, remove, or modify Instagram accounts dynamically through the GUI
- **Progress Tracking**: Visual progress bar and status updates for long-running operations
- **HTML Reports**: Automatically generated professional reports in your output directory
- **Browser Automation**: Smart browser management with Playwright and WSL2 optimization
- **Code Quality**: Enforced through `ruff`, `mypy`, and comprehensive test coverage
- **Cross-Platform**: Optimized for WSL2 with support for Windows, Linux, and macOS
- **Error Handling**: Graceful degradation and comprehensive error reporting

## Prerequisites

### **System Requirements**

- **Python 3.12+** (strict requirement for modern type hints and features)
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+, CentOS 8+), or macOS 10.15+
- **Memory**: Minimum 4GB RAM, recommended 8GB+ for large scraping operations
- **Storage**: At least 500MB free space for the application and generated reports
- **Network**: Stable internet connection for Instagram access

### **Browser Requirements**

- **Chromium-based browser** (Chrome, Brave, or Edge) with remote debugging enabled
- **Browser Version**: Chrome 90+, Brave 1.20+, or Edge 90+
- **Remote Debugging**: Must support Chrome DevTools Protocol (CDP)
- **Session Management**: Browser should be able to maintain Instagram login sessions

### **WSL2 Environment (Recommended)**

This tool is **specifically optimized for Windows Subsystem for Linux 2** environments:

- **WSL2 Benefits**:
  - Seamless Windows/Linux integration
  - Automatic path translation between Windows and Linux
  - Optimized browser process management
  - Better performance for development workflows

- **WSL2 Requirements**:
  - Windows 10 version 2004+ or Windows 11
  - WSL2 kernel update package installed
  - Virtualization enabled in BIOS

### Browser Setup Requirements

Your browser must support remote debugging. The tool will automatically:

- **Launch your browser** with `--remote-debugging-port=9222`
- **Kill existing browser processes** to prevent conflicts
- **Handle WSL2-specific path translations** automatically
- **Provide clear error messages** if connection fails
- **Manage browser profiles** and user data directories
- **Handle cross-platform compatibility** between Windows and Linux

## Getting Started

### Quick Setup Guide

Follow these steps to get Instagram Helper running in minutes:

1. **Environment Setup**:
   - Clone the repository and run `make setup-dev` to prepare the environment
   - Activate the virtual environment: `source venv/bin/activate`

2. **Configuration**:
   - Create a `.env` file in the project root with your browser settings
   - See the [Environment Variables](#environment-variables) section for detailed configuration
   - **Optional**: Customize Instagram accounts directly in the GUI

3. **First Run**:
   - Execute `python run.py` to launch the GUI application
   - Configure your scraping parameters in the GUI
   - Add Instagram accounts you want to monitor
   - Click "Start Scraping" to begin

### Detailed Setup Instructions

#### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/maximbetin/instagram-helper.git
cd instagram-helper

# Setup development environment (creates virtual environment and installs dependencies)
make setup-dev

# Activate the virtual environment
source venv/bin/activate
```

#### Step 2: Browser Configuration

```bash
# Create configuration file
cp .env.example .env  # if available, or create manually

# Edit .env file with your browser paths
nano .env
```

Example .env configuration for WSL2 users:

```env
# Browser Configuration
BROWSER_PATH="/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
BROWSER_USER_DATA_DIR="C:\Users\YourUsername\AppData\Local\BraveSoftware\Brave-Browser\User Data"
BROWSER_PROFILE_DIR="Default"
BROWSER_DEBUG_PORT=9222

# Instagram Configuration
INSTAGRAM_MAX_POSTS_PER_ACCOUNT=5
INSTAGRAM_POST_LOAD_TIMEOUT=10000

# Output Configuration
OUTPUT_DIR="/mnt/c/Users/YourUsername/Documents/Instagram-Reports"
LOG_DIR="/mnt/c/Users/YourUsername/Documents/Instagram-Logs"
```

#### Step 3: Verify Installation

```bash
# Run quality checks to ensure everything is working
make check-all

# Test the application
python run.py
```

### Common Setup Issues & Solutions

| Issue | Solution |
|-------|----------|
| **Python version error** | Ensure Python 3.12+ is installed and in PATH |
| **Browser not found** | Verify BROWSER_PATH in .env points to valid executable |
| **Permission denied** | Check file permissions and ensure directories are writable |
| **WSL2 path issues** | Use Windows-style paths for browser directories, Linux-style for output |
| **Port 9222 in use** | Close existing browser instances or change BROWSER_DEBUG_PORT |
| **Import errors** | Ensure virtual environment is activated and dependencies are installed |

### **First-Time User Checklist**

- [ ] Python 3.12+ installed and accessible
- [ ] Repository cloned and virtual environment created
- [ ] `.env` file configured with browser paths
- [ ] Browser supports remote debugging
- [ ] Instagram account accessible in browser
- [ ] Output directories are writable
- [ ] Application launches without errors
- [ ] Can add Instagram accounts in GUI
- [ ] Scraping starts and progresses normally

## Requirements

- Python 3.12+ (strict requirement)
- A virtual environment (recommended)
- Access to a Chromium-based browser with remote debugging enabled
- WSL2 environment (Windows Subsystem for Linux 2)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/maximbetin/instagram-helper.git
   cd instagram-helper
   ```

2. **Set Up the Development Environment**

   Use the provided `Makefile` to simplify setup:

   ```bash
   make setup-dev
   ```

   After setup, activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

## Usage

### **Quick Start**

The fastest way to get started:

```bash
# Activate your virtual environment
source venv/bin/activate

# Launch the application
python run.py
```

### **GUI Interface Overview**

The Instagram Helper provides an intuitive, professional interface with the following main sections:

#### **1. Configuration Panel**

- **Post Age Limit**: Set maximum age of posts to scrape (in days)
- **Posts Per Account**: Limit number of posts to process per Instagram account
- **Timeout Settings**: Configure page load timeouts for reliable scraping
- **Real-time Updates**: Settings apply immediately without restarting

#### **2. Account Management**

- **Text Area Input**: Enter Instagram accounts, one per line
- **Bulk Operations**: Paste multiple accounts at once
- **Dynamic Updates**: Add/remove accounts on-the-fly
- **Validation**: Automatic filtering of empty lines and whitespace

#### **3. Progress Monitoring**

- **Real-time Progress Bar**: Visual indication of scraping progress
- **Status Updates**: Live status messages showing current operation
- **Log Streaming**: Detailed logs of all scraping activities
- **Error Reporting**: Clear error messages with context

#### **4. Control Panel**

- **Start Scraping**: Begin the scraping process with current settings
- **Stop Scraping**: Safely stop ongoing operations
- **Clear Logs**: Reset the log display for new sessions
- **Progress Reset**: Clear progress indicators for new runs

### **Configuration Options**

#### **Scraping Parameters**

| Parameter | Description | Default | Recommended Range |
|-----------|-------------|---------|-------------------|
| **Post Age Limit** | Maximum age of posts to scrape | 7 days | 1-30 days |
| **Posts Per Account** | Number of posts to process per account | 5 posts | 1-20 posts |
| **Page Load Timeout** | Time to wait for page loading | 10 seconds | 5-30 seconds |

#### **Performance Tuning**

- **For Fast Scraping**: Lower timeout values, fewer posts per account
- **For Reliable Scraping**: Higher timeout values, conservative post limits
- **For Large Scale**: Balance between speed and Instagram's rate limiting

### **Instagram Account Management**

#### **Adding Accounts**

1. **Single Account**: Type the username (e.g., `instagram`)
2. **Multiple Accounts**: Paste a list, one per line
3. **Bulk Import**: Copy-paste from existing lists or spreadsheets

#### **Account Validation**

- **Format**: Usernames only (no @ symbols needed)
- **Filtering**: Empty lines and whitespace are automatically removed
- **Limits**: No hard limit on number of accounts
- **Persistence**: Accounts are remembered between sessions

#### **Best Practices**

- **Start Small**: Begin with 5-10 accounts to test configuration
- **Monitor Performance**: Watch for rate limiting or errors
- **Batch Processing**: Group similar accounts together
- **Regular Updates**: Refresh account lists periodically

### **Report Generation**

#### **Automatic Reports**

- **File Naming**: Reports use DD-MM-YYYY format (e.g., `15-01-2024.html`)
- **Output Location**: Configurable via `OUTPUT_DIR` environment variable
- **Format**: Professional HTML with responsive design
- **Content**: Post captions, dates, account information, and statistics

#### **Report Features**

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Statistics Summary**: Total posts, accounts, and date ranges
- **Account Grouping**: Posts organized by Instagram account
- **Search & Filter**: Easy navigation through large datasets
- **Export Ready**: Professional reports for sharing and analysis

### **Performance Optimization**

#### **Scraping Speed**

- **Parallel Processing**: Multiple accounts processed sequentially for stability
- **Smart Delays**: Built-in delays prevent Instagram rate limiting
- **Timeout Management**: Configurable timeouts for different network conditions
- **Error Recovery**: Continues processing even when individual posts fail

#### **Resource Management**

- **Memory Efficient**: Processes data incrementally without accumulation
- **Browser Cleanup**: Automatic cleanup of browser resources
- **Session Reuse**: Maintains Instagram login state across operations
- **Graceful Degradation**: Continues operation despite partial failures

### **Workflow Examples**

#### **Daily Monitoring Workflow**

1. **Morning Setup**: Launch application and verify accounts
2. **Configuration**: Set post age to 1 day, 10 posts per account
3. **Execution**: Start scraping and monitor progress
4. **Review**: Check generated reports for new content
5. **Analysis**: Review trends and engagement patterns

#### **Weekly Analysis Workflow**

1. **Extended Range**: Set post age to 7 days for weekly overview
2. **Comprehensive Scraping**: Increase posts per account to 20
3. **Batch Processing**: Process all accounts in one session
4. **Report Generation**: Create comprehensive weekly reports
5. **Trend Analysis**: Compare weekly data for insights

#### **Research Workflow**

1. **Target Selection**: Focus on specific account types or industries
2. **Deep Scraping**: Higher post limits for comprehensive data
3. **Multiple Sessions**: Run multiple scraping sessions for large datasets
4. **Data Compilation**: Combine reports for analysis
5. **Insight Generation**: Identify patterns and trends

## Configuration

### **Environment Variables Overview**

The application uses environment variables for configuration, loaded from a `.env` file in the project root. This approach provides:

- **Flexibility**: Easy configuration changes without code modifications
- **Environment Isolation**: Different settings for development, testing, and production
- **Security**: Sensitive paths and settings kept separate from code
- **Portability**: Configuration can be shared across different systems

### **Environment Variables**

#### **Required Variables**

These variables must be set for the application to function:

| Variable | Description | Example |
|----------|-------------|---------|
| `BROWSER_PATH` | Absolute path to browser executable | `"/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"` |
| `BROWSER_USER_DATA_DIR` | Path to browser user data directory | `"C:\Users\YourUsername\AppData\Local\BraveSoftware\Brave-Browser\User Data"` |

#### **Browser Configuration (Optional)**

| Variable | Description | Default | Recommended |
|----------|-------------|---------|-------------|
| `BROWSER_PROFILE_DIR` | Browser profile directory to use | `"Default"` | `"Default"` or custom profile name |
| `BROWSER_DEBUG_PORT` | Remote debugging port | `9222` | `9222` (avoid conflicts) |
| `BROWSER_START_URL` | URL opened when launching browser | `"https://www.instagram.com/"` | Instagram or blank page |
| `BROWSER_LOAD_DELAY` | Milliseconds to wait after browser launch | `5000` | `3000-10000` based on system speed |
| `BROWSER_CONNECT_SCHEME` | Connection scheme for CDP | `"http"` | `"http"` (standard) |
| `BROWSER_REMOTE_HOST` | Hostname for remote debugger | `"localhost"` | `"localhost"` (WSL2) or `"127.0.0.1"` |

#### **Instagram Configuration (Optional)**

| Variable | Description | Default | Recommended Range |
|----------|-------------|---------|-------------------|
| `INSTAGRAM_URL` | Base URL for Instagram | `"https://www.instagram.com/"` | Keep default |
| `INSTAGRAM_MAX_POSTS_PER_ACCOUNT` | Maximum posts per account | `5` | `1-50` (higher = slower) |
| `INSTAGRAM_POST_LOAD_TIMEOUT` | Page load timeout in milliseconds | `10000` | `5000-30000` based on network |

#### **Output Configuration (Optional)**

| Variable | Description | Default | Recommended |
|----------|-------------|---------|-------------|
| `OUTPUT_DIR` | Directory for HTML reports | Project root | Dedicated reports directory |
| `LOG_DIR` | Directory for log files | Project root | Dedicated logs directory |
| `TEMPLATE_PATH` | Path to HTML template | `"templates/template.html"` | Keep default |

#### **Timezone Configuration (Optional)**

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `TIMEZONE_OFFSET` | Hour offset from UTC | `2` | `-5` (EST), `0` (UTC), `+1` (CET) |

### **Configuration Examples**

#### **WSL2 Windows Browser Configuration**

```env
# Browser Configuration for WSL2 with Windows Brave
BROWSER_PATH="/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
BROWSER_USER_DATA_DIR="C:\Users\YourUsername\AppData\Local\BraveSoftware\Brave-Browser\User Data"
BROWSER_PROFILE_DIR="Default"
BROWSER_DEBUG_PORT=9222
BROWSER_START_URL="https://www.instagram.com/"
BROWSER_LOAD_DELAY=5000
BROWSER_CONNECT_SCHEME="http"
BROWSER_REMOTE_HOST="localhost"

# Instagram Configuration
INSTAGRAM_MAX_POSTS_PER_ACCOUNT=10
INSTAGRAM_POST_LOAD_TIMEOUT=15000

# Output Configuration
OUTPUT_DIR="/mnt/c/Users/YourUsername/Documents/Instagram-Reports"
LOG_DIR="/mnt/c/Users/YourUsername/Documents/Instagram-Logs"
TIMEZONE_OFFSET=2
```

#### **Native Linux Configuration**

```env
# Browser Configuration for Native Linux
BROWSER_PATH="/usr/bin/brave-browser"
BROWSER_USER_DATA_DIR="/home/username/.config/BraveSoftware/Brave-Browser"
BROWSER_PROFILE_DIR="Default"
BROWSER_DEBUG_PORT=9222
BROWSER_START_URL="https://www.instagram.com/"
BROWSER_LOAD_DELAY=3000
BROWSER_CONNECT_SCHEME="http"
BROWSER_REMOTE_HOST="localhost"

# Instagram Configuration
INSTAGRAM_MAX_POSTS_PER_ACCOUNT=5
INSTAGRAM_POST_LOAD_TIMEOUT=10000

# Output Configuration
OUTPUT_DIR="/home/username/Documents/Instagram-Reports"
LOG_DIR="/home/username/Documents/Instagram-Logs"
TIMEZONE_OFFSET=0
```

#### **macOS Configuration**

```env
# Browser Configuration for macOS
BROWSER_PATH="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
BROWSER_USER_DATA_DIR="/Users/username/Library/Application Support/BraveSoftware/Brave-Browser"
BROWSER_PROFILE_DIR="Default"
BROWSER_DEBUG_PORT=9222
BROWSER_START_URL="https://www.instagram.com/"
BROWSER_LOAD_DELAY=3000
BROWSER_CONNECT_SCHEME="http"
BROWSER_REMOTE_HOST="localhost"

# Instagram Configuration
INSTAGRAM_MAX_POSTS_PER_ACCOUNT=5
INSTAGRAM_POST_LOAD_TIMEOUT=10000

# Output Configuration
OUTPUT_DIR="/Users/username/Documents/Instagram-Reports"
LOG_DIR="/Users/username/Documents/Instagram-Logs"
TIMEZONE_OFFSET=-5
```

### **Instagram Account Configuration**

#### **Pre-configured Accounts**

The tool comes with **50 pre-configured Instagram accounts** including:

**Cultural Institutions:**

- `agendagijon`, `centroniemeyer`, `aytoviedo`, `aytocastrillon`
- `bibliotecasdegijonxixon`, `conectaoviedo`, `conocerasturias`

**Educational & Research:**

- `biodevas`, `cultura.gijon`, `museosgijon`
- `fundacioncajastur`, `turismogijon`, `gijonimpulsa`

**And many more** covering various sectors and interests.

#### **Customization Options**

**1. GUI Management (Recommended)**

- **Text Area Input**: Enter accounts directly in the GUI
- **Bulk Operations**: Paste multiple accounts at once
- **Real-time Updates**: Changes apply immediately
- **No File Dependencies**: Everything managed through the interface

**2. Code Configuration**

- **Default Accounts**: Modify `config.py` for permanent changes
- **Post Limits**: Adjust `INSTAGRAM_MAX_POSTS_PER_ACCOUNT`
- **Timeout Settings**: Change `INSTAGRAM_POST_LOAD_TIMEOUT`
- **Account Lists**: Update the default account list

#### **Account Management Best Practices**

- **Start with Defaults**: Use pre-configured accounts to test functionality
- **Add Gradually**: Add new accounts incrementally to avoid overwhelming
- **Group by Purpose**: Organize accounts by monitoring objective
- **Regular Review**: Periodically review and update account lists
- **Validate Access**: Ensure accounts are publicly accessible

### Performance Tuning

#### **Scraping Speed vs. Reliability**

| Goal | Posts Per Account | Timeout | Post Age Limit |
|------|-------------------|---------|----------------|
| **Fast Scraping** | 3-5 | 5000ms | 1-3 days |
| **Balanced** | 5-10 | 10000ms | 3-7 days |
| **Comprehensive** | 10-20 | 15000ms | 7-14 days |
| **Research** | 20-50 | 20000ms | 14-30 days |

#### Network Optimization

- **Timeout Values**: Higher for slower networks, lower for fast connections
- **Post Limits**: Balance between speed and Instagram's rate limiting
- **Batch Size**: Process accounts in smaller groups for better reliability
- **Delay Settings**: Adjust browser load delays based on system performance

#### Resource Management

- **Memory Usage**: Monitor memory consumption during large scraping operations
- **Browser Instances**: Ensure proper cleanup of browser resources
- **File Output**: Use dedicated directories for reports and logs
- **Session Management**: Maintain Instagram login state for efficiency

## Troubleshooting

### Quick Diagnostic Commands

Run these commands to quickly identify common issues:

```bash
# Check Python version
python --version

# Verify virtual environment
which python

# Check browser process status
ps aux | grep brave

# Test port availability
netstat -tlnp | grep 9222

# Verify file permissions
ls -la .env
ls -la output/
```

### Critical Issues & Solutions

#### 1. Application Won't Start

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Import Error** | Missing dependencies | Run `make setup-dev` and activate venv |
| **Python Version Error** | Wrong Python version | Install Python 3.12+ and update PATH |
| **Permission Denied** | File permission issues | Check file permissions and ownership |
| **Module Not Found** | Virtual environment not activated | Run `source venv/bin/activate` |

Diagnostic Steps:

```bash
# Check Python version
python --version

# Verify virtual environment
echo $VIRTUAL_ENV

# Check dependencies
pip list | grep -E "(playwright|jinja2|dotenv)"

# Test imports
python -c "import playwright; import jinja2; print('OK')"
```

#### 2. Browser Connection Failures

| Symptom | Cause | Solution |
|---------|-------|----------|
| **"BROWSER_PATH not set"** | Missing environment variable | Add BROWSER_PATH to .env file |
| **"Connection refused"** | Port 9222 in use or browser not running | Close existing browsers, check port |
| **"Browser not found"** | Invalid browser path | Verify BROWSER_PATH points to valid executable |
| **"Permission denied"** | Browser executable not accessible | Check file permissions and ownership |

Diagnostic Commands:

```bash
# Check browser process status
ps aux | grep -E "(brave|chrome|edge)"

# Kill existing browser processes
pkill -f brave
pkill -f chrome
pkill -f edge

# Test port availability
netstat -tlnp | grep 9222

# Verify browser path
ls -la "$BROWSER_PATH"
```

WSL2-Specific Solutions:

```bash
# Check WSL2 environment
uname -a | grep microsoft

# Test Windows browser from WSL2
wsl.exe "tasklist | findstr brave"

# Kill Windows browser processes
wsl.exe "taskkill /f /im brave.exe"
```

#### 3. Instagram Scraping Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| **"No post links found"** | Instagram HTML structure changed | Update XPath selectors (see critical warnings) |
| **"Timeout loading post"** | Slow network or Instagram response | Increase INSTAGRAM_POST_LOAD_TIMEOUT |
| **"Rate limited"** | Too many requests too quickly | Reduce INSTAGRAM_MAX_POSTS_PER_ACCOUNT |
| **"Authentication failed"** | Session expired or invalid | Clear browser cookies and re-login |

Diagnostic Steps:

```bash
# Test Instagram connectivity
curl -I "https://www.instagram.com/"

# Check network latency
ping instagram.com

# Verify browser session
# Open Instagram manually in browser and check login status
```

Rate Limiting Solutions:

- **Reduce post count**: Set `INSTAGRAM_MAX_POSTS_PER_ACCOUNT=3`
- **Increase delays**: Set `INSTAGRAM_POST_LOAD_TIMEOUT=20000`
- **Batch processing**: Process fewer accounts per session
- **Session rotation**: Use different browser profiles

#### 4. WSL2 Integration Problems

| Symptom | Cause | Solution |
|---------|-------|----------|
| **Path translation errors** | Windows/Linux path format issues | Use correct path formats for each OS |
| **Browser launch failures** | WSL2 detection logic failing | Verify WSL2 environment and browser paths |
| **Process management errors** | Windows process commands not working | Check wsl.exe availability and permissions |
| **File access issues** | Cross-platform file permissions | Ensure proper ownership and permissions |

WSL2 Diagnostic Commands:

```bash
# Verify WSL2 environment
uname -a
cat /proc/version

# Check Windows integration
wsl.exe "echo WSL2 Windows integration working"

# Test path translation
wsl.exe "dir C:\Users"

# Verify browser paths
ls -la "/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/"
```

WSL2 Path Best Practices:

- **Browser paths**: Use Windows format (`C:\Users\...`)
- **Output paths**: Use Linux format (`/mnt/c/Users/...`)
- **Profile paths**: Use Windows format for browser user data
- **Template paths**: Use Linux format for application files

### Advanced Troubleshooting

#### 1. Performance Issues

Slow Scraping:

```bash
# Monitor system resources
htop
iostat 1
free -h

# Check browser memory usage
ps aux | grep brave | awk '{print $6}' | numfmt --to=iec

# Monitor network activity
iftop
```

Memory Leaks:

- **Browser cleanup**: Ensure browser processes are properly terminated
- **Resource monitoring**: Watch memory usage during long operations
- **Session management**: Limit concurrent browser instances

#### 2. Network Problems

Connection Issues:

```bash
# Test network connectivity
ping -c 4 instagram.com
traceroute instagram.com

# Check DNS resolution
nslookup instagram.com
dig instagram.com

# Test HTTP connectivity
curl -v "https://www.instagram.com/"
```

**Proxy Configuration:**

- **Environment variables**: Set HTTP_PROXY and HTTPS_PROXY if needed
- **Browser settings**: Configure proxy in browser if required
- **Network policies**: Check corporate firewall and proxy settings

#### 3. File System Issues

Permission Problems:

```bash
# Check file permissions
ls -la .env
ls -la output/
ls -la logs/

# Fix permissions if needed
chmod 644 .env
chmod 755 output/
chmod 755 logs/

# Check ownership
ls -la | grep -E "(\.env|output|logs)"
```

Disk Space Issues:

```bash
# Check disk usage
df -h
du -sh output/
du -sh logs/

# Clean up old files
find output/ -name "*.html" -mtime +30 -delete
find logs/ -name "*.log" -mtime +30 -delete
```

### Troubleshooting Checklist

Before Reporting Issues:

- [ ] **Environment Check**: Python 3.12+, virtual environment activated
- [ ] **Configuration**: .env file properly configured with valid paths
- [ ] **Browser Status**: Browser supports remote debugging, port 9222 available
- [ ] **Network**: Stable internet connection, Instagram accessible
- [ ] **Permissions**: Output and log directories are writable
- [ ] **Dependencies**: All required packages installed and accessible
- [ ] **Logs**: Check application logs for specific error messages
- [ ] **Reproduction**: Issue can be consistently reproduced

Information to Include in Bug Reports:

1. **Environment Details**: OS, Python version, WSL2 version (if applicable)
2. **Configuration**: Relevant .env settings (without sensitive information)
3. **Error Messages**: Complete error messages and stack traces
4. **Reproduction Steps**: Step-by-step instructions to reproduce the issue
5. **Expected vs. Actual**: What you expected to happen vs. what actually happened
6. **Log Files**: Relevant log file contents (if available)
7. **Screenshots**: GUI screenshots showing the issue (if applicable)

### Getting Help

Self-Help Resources:

- **This README**: Comprehensive troubleshooting guide
- **Code Comments**: Inline documentation explaining implementation details
- **Architecture Documentation**: Understanding the system design
- **Development Workflow**: Testing and debugging procedures

Community Support:

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share solutions
- **Documentation**: Contribute improvements and clarifications

Professional Support:

- **Detailed Bug Reports**: Include all required information
- **Feature Requests**: Explain use case and expected behavior
- **Contributions**: Submit pull requests with improvements

## Frequently Asked Questions (FAQ)

### Setup & Installation

#### Q: Why do I need Python 3.12+ specifically?

**A:** Python 3.12+ is required for several reasons:

- **Modern Type Hints**: Advanced type annotation features used throughout the codebase
- **Performance Improvements**: Better performance for web scraping operations
- **Security Updates**: Latest security patches and vulnerability fixes
- **Library Compatibility**: Required by Playwright and other dependencies
- **Future-Proofing**: Ensures long-term maintainability and support

#### Q: Can I use this tool without WSL2?

**A:** Yes, but with limitations:

- **Native Linux/macOS**: Full functionality with native browser support
- **Native Windows**: Works but may have path and process management issues
- **WSL2 (Recommended)**: Optimized for cross-platform browser integration
- **Other WSL versions**: May work but not officially supported

#### **Q: What browsers are supported?**

**A:** Any Chromium-based browser that supports remote debugging:

- **Brave Browser** (recommended for WSL2 users)
- **Google Chrome** (full compatibility)
- **Microsoft Edge** (full compatibility)
- **Chromium** (Linux only, limited testing)

#### **Q: Do I need to install Playwright separately?**

**A:** No, Playwright is automatically installed with the tool:

- **Automatic Installation**: Included in the project dependencies
- **Browser Drivers**: Automatically downloaded on first run
- **Version Management**: Handled by the project's dependency system
- **Updates**: Managed through regular dependency updates

### **Instagram & Scraping**

#### **Q: Is this tool safe to use with Instagram?**

**A:** The tool is designed with Instagram's terms of service in mind:

- **Respectful Scraping**: Built-in delays and rate limiting
- **Session Reuse**: Maintains your existing Instagram login
- **No Authentication**: Only accesses publicly available content
- **Conservative Defaults**: Default settings avoid triggering rate limits
- **Graceful Degradation**: Continues working even with partial failures

#### **Q: Why does Instagram sometimes block the tool?**

**A:** Instagram has sophisticated anti-bot measures:

- **Rate Limiting**: Too many requests too quickly
- **Behavioral Analysis**: Unusual access patterns
- **IP Monitoring**: Multiple requests from same IP
- **Session Detection**: Suspicious browser behavior

**Solutions:**

- Reduce posts per account
- Increase timeouts between requests
- Use different browser profiles
- Process accounts in smaller batches

#### **Q: What happens if Instagram changes their website?**

**A:** The tool is designed to handle Instagram's volatility:

- **Graceful Degradation**: Continues working with partial data
- **Comprehensive Logging**: Detailed error reporting for debugging
- **Modular Design**: Easy to update specific components
- **Fallback Strategies**: Multiple approaches for data extraction
- **Community Updates**: Regular updates based on Instagram changes

#### **Q: Can I scrape private Instagram accounts?**

**A:** No, and this is by design:

- **Public Content Only**: Only accessible public posts
- **Privacy Respect**: Cannot bypass Instagram's privacy settings
- **Legal Compliance**: Respects Instagram's terms of service
- **Ethical Design**: Designed for legitimate monitoring purposes

### **Performance & Optimization**

#### **Q: How fast can the tool scrape Instagram?**

**A:** Speed depends on several factors:

- **Network Conditions**: Internet speed and latency
- **Instagram Response**: Instagram's server performance
- **Configuration**: Posts per account and timeout settings
- **System Resources**: Available memory and CPU

**Typical Performance:**

- **Fast Network**: 1-2 seconds per post
- **Average Network**: 3-5 seconds per post
- **Slow Network**: 5-10 seconds per post
- **Rate Limited**: 10+ seconds per post

#### **Q: How many accounts can I monitor at once?**

**A:** There's no hard limit, but practical limits exist:

- **Recommended**: 10-50 accounts per session
- **Maximum**: 100+ accounts (with performance degradation)
- **Optimal**: 20-30 accounts for best performance
- **Batch Processing**: Process large lists in smaller groups

#### **Q: Will the tool use a lot of memory?**

**A:** The tool is designed to be memory-efficient:

- **Incremental Processing**: Data processed as it's collected
- **Streaming Logs**: Logs don't accumulate in memory
- **Browser Cleanup**: Automatic cleanup of browser resources
- **Memory Monitoring**: Built-in memory usage tracking

**Typical Memory Usage:**

- **Idle**: 50-100 MB
- **Active Scraping**: 200-500 MB
- **Large Operations**: 500 MB - 1 GB
- **Peak Usage**: 1-2 GB (temporary, during processing)

### **GUI & User Interface**

#### **Q: Can I run the tool without a GUI?**

**A:** Currently, the tool is GUI-only, but this may change:

- **Current Design**: Tkinter-based GUI interface
- **Future Plans**: Command-line interface under consideration
- **Automation**: GUI can be automated with external tools
- **Headless Mode**: May be added in future versions

#### **Q: Is the GUI responsive during scraping?**

**A:** Yes, the GUI remains fully responsive:

- **Multi-threaded Design**: Scraping runs in separate thread
- **Real-time Updates**: Progress and logs update continuously
- **Interactive Controls**: Start/stop buttons work during operation
- **Status Monitoring**: Real-time progress and status information

#### **Q: Can I customize the GUI appearance?**

**A:** Limited customization is available:

- **Theme Support**: Basic Tkinter theming
- **Layout**: Fixed layout optimized for functionality
- **Colors**: Some color customization possible
- **Fonts**: System default fonts (platform-dependent)

### **Reports & Output**

#### **Q: What format are the reports in?**

**A:** Reports are generated in HTML format:

- **Professional Design**: Modern, responsive HTML layout
- **Cross-Platform**: Works on desktop, tablet, and mobile
- **No Dependencies**: Self-contained HTML files
- **Easy Sharing**: Can be opened in any web browser
- **Print Friendly**: Optimized for printing and PDF conversion

#### **Q: Can I export data to other formats?**

**A:** Currently HTML only, but other formats may be added:

- **Current**: HTML reports with embedded data
- **Future Plans**: CSV, JSON, and Excel export
- **Data Extraction**: HTML can be parsed for data extraction
- **Third-party Tools**: Use external tools to convert HTML to other formats

#### **Q: How long are reports kept?**

**A:** Report retention is configurable:

- **Default**: Reports stored indefinitely
- **Customization**: Can be configured via environment variables
- **Cleanup**: Manual cleanup of old reports
- **Storage**: Limited only by available disk space

### **Security & Privacy**

#### **Q: Is my Instagram login information safe?**

**A:** Yes, your login information is protected:

- **Browser Storage**: Credentials stored in your browser, not the tool
- **Session Reuse**: Tool reuses existing browser sessions
- **No Credential Storage**: Tool never stores passwords or tokens
- **Local Processing**: All data processed locally on your machine
- **No Network Transmission**: Login data never sent to external servers

#### **Q: Does the tool send data to external servers?**

**A:** No, the tool is completely local:

- **Local Processing**: All scraping happens on your machine
- **No Cloud Services**: No external APIs or services
- **No Data Collection**: Tool doesn't collect usage statistics
- **Privacy First**: Designed with privacy as a priority
- **Offline Capable**: Works without internet connection (after setup)

#### **Q: Can I use this tool in a corporate environment?**

**A:** Yes, with some considerations:

- **Network Policies**: May need to configure corporate proxies
- **Firewall Rules**: Port 9222 may need to be opened
- **Browser Policies**: Corporate browser restrictions may apply
- **Data Policies**: Ensure compliance with corporate data policies
- **IT Support**: May need IT assistance for initial setup

### **Updates & Maintenance**

#### **Q: How often should I update the tool?**

**A:** Regular updates are recommended:

- **Security Updates**: As soon as available
- **Feature Updates**: Monthly or as needed
- **Instagram Changes**: When scraping stops working
- **Dependency Updates**: With each major release
- **Bug Fixes**: As they become available

#### **Q: What happens when Instagram updates their website?**

**A:** The tool includes several strategies:

- **Graceful Degradation**: Continues working with partial data
- **Error Reporting**: Detailed logs for debugging
- **Community Updates**: Regular updates based on Instagram changes
- **Fallback Strategies**: Multiple approaches for data extraction
- **Quick Fixes**: Most issues resolved within days

#### **Q: Can I contribute to the tool's development?**

**A:** Yes, contributions are welcome:

- **GitHub Repository**: Open source project
- **Issue Reporting**: Report bugs and request features
- **Code Contributions**: Submit pull requests
- **Documentation**: Help improve documentation
- **Testing**: Test on different platforms and configurations

### **Tips & Best Practices**

#### **Q: What are the best practices for using this tool?**

**A:** Follow these guidelines for optimal results:

- **Start Small**: Begin with few accounts to test configuration
- **Monitor Performance**: Watch for rate limiting and errors
- **Regular Updates**: Keep the tool and dependencies updated
- **Backup Configuration**: Save your .env file and settings
- **Test Regularly**: Verify functionality before important operations

#### **Q: How can I optimize scraping performance?**

**A:** Several strategies can improve performance:

- **Network Optimization**: Use fast, stable internet connection
- **Browser Optimization**: Close unnecessary browser tabs and extensions
- **System Resources**: Ensure adequate RAM and CPU availability
- **Configuration Tuning**: Adjust timeouts and post limits based on performance
- **Batch Processing**: Process accounts in optimal group sizes

#### **Q: What should I do if something goes wrong?**

**A:** Follow this troubleshooting sequence:

1. **Check Logs**: Review application logs for error details
2. **Verify Configuration**: Ensure .env file is properly configured
3. **Test Connectivity**: Verify internet and Instagram access
4. **Restart Application**: Close and restart the tool
5. **Check Resources**: Ensure adequate system resources
6. **Report Issues**: Submit detailed bug reports if problems persist

## Important Notes

**CRITICAL**: Do not modify the caption selectors in `instagram_scraper.py`. These selectors are fragile and changes will break the tool's functionality.

**Instagram Dependencies**: The tool's success depends on Instagram's HTML structure remaining consistent. The tool may need updates if Instagram makes significant changes to their pages.

**Rate Limiting**: Instagram may block requests if too many are made too quickly. The default settings are conservative to avoid this.

**WSL2 Optimization**: This tool is specifically designed for Windows Subsystem for Linux 2 environments and may not work optimally in other setups.

**Browser Management**: The tool always launches a new browser instance to ensure reliable operation. If you encounter connection errors, close any existing browser instances and try again.

**Account Management**: Instagram accounts are now managed directly through the GUI text area, making it easier to customize without editing external files.

## Implementation Details & Design Decisions

This section explains the "why" behind key implementation decisions and architectural choices that may not be immediately obvious.

### **Configuration Management Architecture**

**Why a frozen dataclass with `__post_init__` validation?**

- **Immutability**: The `Settings` class is frozen to prevent runtime modification, ensuring configuration consistency
- **Validation timing**: `__post_init__` validates settings after all fields are set, allowing for complex validation logic
- **Environment detection**: The configuration automatically detects testing environments (`CI=true` or `PYTEST_CURRENT_TEST`) and provides fallback values to prevent import-time errors

**Why `object.__setattr__` for frozen dataclass updates?**

- **Frozen constraint bypass**: Since the dataclass is frozen, we use `object.__setattr__` to update values during initialization
- **Type safety**: This approach maintains type checking while allowing necessary post-initialization modifications

### **WSL2 Browser Integration Strategy**

**Why complex WSL2 detection and handling?**

- **Cross-platform compatibility**: WSL2 runs Linux but often needs to launch Windows browsers
- **Path translation**: The tool automatically detects WSL2 environments and handles Windows/Linux path differences
- **Process management**: Different process killing strategies are needed for Windows vs Linux environments

**Key WSL2 detection logic:**

```python
is_wsl2 = (
    os.name == "posix"  # Linux shell
    and "microsoft" in os.uname().release.lower()  # WSL2 kernel
    and ("win" in str(browser_path).lower() or ".exe" in str(browser_path).lower())  # Windows browser
)
```

### **Instagram Caption Extraction Design**

**Why hardcoded XPath instead of CSS selectors?**

- **Fragility**: Instagram's HTML structure changes frequently, making CSS selectors unreliable
- **Specificity**: The exact XPath `/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/span` targets the specific caption element
- **Maintenance**: When Instagram changes their structure, only this one XPath needs updating

**CRITICAL WARNING**: Do not modify this XPath selector. Instagram's HTML structure is fragile and changes will break caption extraction.

### **GUI Account Management Implementation**

**Why text area instead of listbox with buttons?**

- **Simplicity**: Direct text input eliminates the need for complex add/remove dialog logic
- **Bulk operations**: Users can paste multiple accounts at once or edit the entire list
- **No file dependencies**: Eliminates the need for external text files that could be misplaced
- **Immediate feedback**: Changes are visible immediately without needing to save files

**Account parsing logic:**

```python
# Each line becomes an account, empty lines are automatically filtered
return [line.strip() for line in self.account_text.get(1.0, tk.END).splitlines() if line.strip()]
```

### **Timezone Handling Strategy**

**Why timezone conversion in the scraper?**

- **Instagram's UTC timestamps**: Instagram provides all dates in UTC
- **User preference**: Users can configure their local timezone via `TIMEZONE_OFFSET`
- **Consistent reporting**: All dates in reports are converted to the user's local timezone

**Timezone conversion flow:**

1. Instagram provides UTC timestamp
2. Parse as UTC datetime: `datetime.fromisoformat(dt_attr.replace("Z", "+00:00"))`
3. Convert to user's timezone: `utc_dt.astimezone(self.settings.TIMEZONE)`

### **Browser Process Management**

**Why kill existing browser processes?**

- **Port conflicts**: Only one browser can use port 9222 for remote debugging
- **Session conflicts**: Existing browser instances may have different debugging configurations
- **Clean state**: Ensures the tool starts with a known browser state

**Process killing strategy:**

- **WSL2/Windows**: Uses `taskkill.exe /f /im brave.exe`
- **Linux/macOS**: Uses `pkill -f brave`
- **Fallback handling**: Gracefully handles missing process management tools

### **Threading Architecture**

**Why separate scraping thread?**

- **GUI responsiveness**: Prevents the GUI from freezing during long scraping operations
- **Progress updates**: Allows real-time progress updates and log streaming
- **Cancellation support**: Users can stop scraping without killing the entire application

**Thread safety considerations:**

- **Queue-based logging**: Log messages are sent via a thread-safe queue
- **GUI updates**: All GUI updates are scheduled on the main thread using `root.after()`
- **State management**: Thread-safe event flags for stopping operations

### Error Handling Philosophy

**Why graceful degradation over strict validation?**

- **User experience**: The tool continues working even if some posts fail to scrape
- **Instagram volatility**: Instagram's structure changes frequently, so partial failures are expected
- **Logging strategy**: Comprehensive logging allows users to understand what failed and why

**Error handling patterns:**

- **Try-catch blocks**: Around all Instagram-specific operations
- **Fallback values**: Default values when environment variables are missing
- **User feedback**: Clear error messages and status updates in the GUI

## Architecture Decision Records (ADR)

This section documents the key architectural decisions made during the development of Instagram Helper, including the rationale behind each choice and the alternatives considered.

### **ADR-001: Multi-Threaded GUI Architecture**

**Status**: Accepted  
**Date**: 2024  
**Context**: The application needs to perform long-running Instagram scraping operations while maintaining a responsive GUI.

**Decision**: Implement a multi-threaded architecture with the main thread handling GUI events and a worker thread executing scraping operations.

**Rationale**:

- **GUI Responsiveness**: Prevents the GUI from freezing during long operations
- **User Experience**: Users can interact with the application while scraping runs
- **Progress Monitoring**: Real-time progress updates and log streaming
- **Cancellation Support**: Users can stop operations without killing the application

**Alternatives Considered**:

- **Single-threaded with async**: Would require significant refactoring of existing code
- **Process-based**: Higher resource overhead and complexity
- **Event-driven only**: Limited control over long-running operations

**Consequences**:

- **Complexity**: Requires careful thread safety considerations
- **Resource Management**: Must ensure proper cleanup of browser resources
- **Debugging**: Threading issues can be harder to diagnose

### **ADR-002: Frozen Dataclass Configuration**

**Status**: Accepted  
**Date**: 2024  
**Context**: Need a robust configuration system that prevents runtime modification while supporting complex validation logic.

**Decision**: Use frozen dataclasses with `__post_init__` validation and `object.__setattr__` for post-initialization updates.

**Rationale**:

- **Immutability**: Prevents accidental configuration changes during runtime
- **Type Safety**: Maintains full type checking and IDE support
- **Validation**: Complex validation logic can be implemented in post-init
- **Testing**: Environment detection and fallback values for testing

**Alternatives Considered**:

- **Mutable dataclass**: Would allow runtime modification, reducing safety
- **Configuration files**: Less flexible and harder to validate
- **Environment variables only**: Limited validation and type safety

**Consequences**:

- **Complexity**: Requires understanding of frozen dataclass constraints
- **Initialization**: More complex initialization logic
- **Flexibility**: Runtime configuration changes require special handling

### **ADR-003: Hardcoded XPath for Caption Extraction**

**Status**: Accepted  
**Date**: 2024  
**Context**: Instagram's HTML structure is highly volatile, making CSS selectors unreliable for caption extraction.

**Decision**: Use hardcoded XPath selectors for caption extraction with comprehensive documentation and warnings.

**Rationale**:

- **Reliability**: XPath provides precise targeting of specific DOM elements
- **Maintainability**: Single point of update when Instagram changes structure
- **Performance**: Direct XPath evaluation is faster than complex CSS selectors
- **Debugging**: Easier to identify and fix selector issues

**Alternatives Considered**:

- **CSS Selectors**: Too fragile for Instagram's changing structure
- **Multiple Selector Strategies**: Would increase complexity and maintenance
- **AI-based Extraction**: Unreliable and resource-intensive

**Consequences**:

- **Fragility**: Single point of failure when Instagram updates
- **Maintenance**: Requires manual updates when structure changes
- **Documentation**: Critical warnings must be prominently displayed

### **ADR-004: WSL2-Specific Browser Integration**

**Status**: Accepted  
**Date**: 2024  
**Context**: Windows Subsystem for Linux 2 presents unique challenges for browser integration, requiring special handling.

**Decision**: Implement automatic WSL2 detection and specialized browser management for Windows/Linux hybrid environments.

**Rationale**:

- **User Experience**: Seamless operation in WSL2 environments
- **Cross-Platform**: Supports both native Linux and WSL2 scenarios
- **Process Management**: Different strategies needed for Windows vs Linux processes
- **Path Translation**: Automatic handling of Windows/Linux path differences

**Alternatives Considered**:

- **WSL2-only**: Would limit cross-platform compatibility
- **Native Linux only**: Would exclude WSL2 users
- **Manual configuration**: Would require user intervention

**Consequences**:

- **Complexity**: More complex detection and handling logic
- **Testing**: Requires testing in multiple environments
- **Maintenance**: Must track changes in WSL2 behavior

### **ADR-005: Text Area Account Management**

**Status**: Accepted  
**Date**: 2024  
**Context**: Need a simple, user-friendly way to manage Instagram accounts without external file dependencies.

**Decision**: Replace listbox with buttons with a simple text area where users can type or paste accounts, one per line.

**Rationale**:

- **Simplicity**: Eliminates complex dialog logic and button management
- **User Experience**: More intuitive for users familiar with text editing
- **Bulk Operations**: Users can paste multiple accounts at once
- **No Dependencies**: Removes need for external text files

**Alternatives Considered**:

- **Listbox with buttons**: More complex and harder to use
- **File-based management**: Requires external file maintenance
- **Database storage**: Overkill for simple account lists

**Consequences**:

- **Validation**: Must parse and validate text input
- **User Error**: Users may enter invalid account names
- **No Programmatic Control**: Less control over account management

### **ADR-006: Jinja2 Template System**

**Status**: Accepted  
**Date**: 2024  
**Context**: Need a flexible, secure HTML generation system for Instagram post reports.

**Decision**: Use Jinja2 templating engine with automatic HTML escaping and sandboxed execution.

**Rationale**:

- **Security**: Automatic HTML escaping prevents XSS attacks
- **Flexibility**: Powerful templating capabilities for complex reports
- **Maintainability**: Separation of HTML and Python logic
- **Performance**: Compiled templates for efficient rendering

**Alternatives Considered**:

- **String formatting**: Security risks and maintenance issues
- **HTML generation libraries**: Less flexible and more complex
- **Static templates**: Limited customization options

**Consequences**:

- **Dependencies**: Additional dependency on Jinja2
- **Learning Curve**: Developers must understand Jinja2 syntax
- **Security**: Must ensure proper template sandboxing

### **ADR-007: Graceful Degradation Error Handling**

**Status**: Accepted  
**Date**: 2024  
**Context**: Instagram scraping is inherently fragile due to frequent HTML structure changes and rate limiting.

**Decision**: Implement graceful degradation that continues operation despite partial failures, with comprehensive logging and user feedback.

**Rationale**:

- **User Experience**: Users get partial results rather than complete failure
- **Reliability**: Application continues working even when some operations fail
- **Debugging**: Comprehensive logging helps identify and fix issues
- **Instagram Volatility**: Partial failures are expected and normal

**Alternatives Considered**:

- **Fail-fast**: Would result in frequent complete failures
- **Retry Logic**: Could trigger rate limiting and make issues worse
- **Silent Failures**: Would hide problems from users

**Consequences**:

- **Complexity**: More complex error handling and recovery logic
- **Partial Results**: Users may get incomplete data
- **Debugging**: Must distinguish between expected and unexpected failures

## Development Workflow & Architecture

This section provides comprehensive guidance for developers working with the codebase, including architectural decisions, development patterns, and troubleshooting strategies.

### **Code Organization & Module Structure**

The application follows a modular architecture with clear separation of concerns:

```text
instagram-helper/
├── gui_app.py              # Main GUI application and threading logic
├── instagram_scraper.py    # Instagram scraping engine and data extraction
├── browser_manager.py      # Browser integration and WSL2 handling
├── report_generator.py     # HTML report generation and templating
├── config.py               # Configuration management and environment handling
├── utils.py                # Utility functions and logging setup
├── run.py                  # Application entry point and error handling
├── templates/              # HTML templates for reports
│   └── template.html      # Main report template with responsive design
└── tests/                  # Comprehensive test suite
    ├── test_gui_app.py    # GUI application tests
    ├── test_config.py     # Configuration tests
    ├── test_instagram_scraper.py  # Scraping logic tests
    └── test_browser_manager.py    # Browser management tests
```

### **Development Environment Setup**

**Prerequisites:**

- Python 3.12+ (strict requirement for type hints and modern features)
- Virtual environment (venv) for dependency isolation
- Git for version control and collaboration

**Setup Commands:**

```bash
# Clone and setup
git clone <repository>
cd instagram-helper
make setup-dev
source venv/bin/activate

# Verify installation
make check-all
```

### **Code Quality & Testing Workflow**

**Recommended Development Cycle:**

1. **Code Changes**: Make modifications to source files
2. **Format & Lint**: `make format && make lint`
3. **Type Checking**: `make type-check`
4. **Testing**: `make test`
5. **Full Validation**: `make check-all`
6. **Manual Testing**: Run the application to verify functionality

**Quality Tools Configuration:**

- **Ruff**: Fast Python linter and formatter (configured in pyproject.toml)
- **MyPy**: Static type checking with strict settings
- **Pytest**: Testing framework with coverage reporting
- **EditorConfig**: Consistent coding style across editors

### **Architectural Patterns & Design Decisions**

**1. Threading Model**

- **Main Thread**: GUI event loop and user interactions
- **Worker Thread**: Long-running scraping operations
- **Communication**: Thread-safe queues and event flags
- **GUI Updates**: All updates scheduled via `root.after()`

**2. Configuration Management**

- **Frozen Dataclass**: Immutable settings with post-init validation
- **Environment Detection**: Automatic testing environment detection
- **Fallback Values**: Graceful degradation for missing configuration
- **Type Safety**: Full type annotations and validation

**3. Error Handling Strategy**

- **Graceful Degradation**: Continue operation despite partial failures
- **Comprehensive Logging**: Detailed error tracking and debugging
- **User Feedback**: Clear error messages and status updates
- **Resource Cleanup**: Proper cleanup in finally blocks

**4. Browser Integration**

- **WSL2 Support**: Automatic detection and handling
- **Cross-Platform**: Windows, Linux, and macOS compatibility
- **Process Management**: Proper cleanup and conflict resolution
- **Fallback Strategies**: Multiple approaches for reliability

### **Testing Strategy & Coverage**

**Test Categories:**

- **Unit Tests**: Individual function and method testing
- **Integration Tests**: Module interaction testing
- **GUI Tests**: User interface behavior validation
- **Browser Tests**: Browser integration testing (with mocks)

**Coverage Goals:**

- **Minimum Coverage**: 90%+ code coverage
- **Critical Paths**: 100% coverage for core functionality
- **Edge Cases**: Comprehensive error condition testing
- **Platform Variations**: WSL2, Windows, and Linux testing

**Testing Best Practices:**

- **Mock External Dependencies**: Browser, Instagram, file system
- **Environment Isolation**: Clean environment for each test
- **Data Validation**: Verify output format and content
- **Performance Testing**: Ensure acceptable response times

### **Debugging & Troubleshooting**

**Common Issues & Solutions:**

**1. Browser Connection Failures**

```bash
# Check browser process status
ps aux | grep brave
# Kill existing processes
pkill -f brave
# Verify port availability
netstat -tlnp | grep 9222
```

**2. Instagram Scraping Failures**

- **Selector Issues**: Instagram may have changed HTML structure
- **Rate Limiting**: Reduce post count or increase delays
- **Session Expiration**: Clear browser cookies and re-authenticate
- **Network Issues**: Check internet connectivity and Instagram availability

**3. WSL2 Integration Problems**

- **Path Translation**: Ensure Windows paths are correctly formatted
- **Process Management**: Verify wsl.exe availability and permissions
- **Browser Launch**: Check Windows browser installation and paths

**4. Configuration Issues**

- **Environment Variables**: Verify .env file format and values
- **Path Permissions**: Ensure output and log directories are writable
- **Python Version**: Confirm Python 3.12+ is being used

**Debug Mode Activation:**

```bash
# Set debug logging
export LOG_LEVEL=DEBUG
# Run with verbose output
python run.py --debug
```

### Performance Optimization

Scraping Performance:

- **Post Limits**: Adjust `INSTAGRAM_MAX_POSTS_PER_ACCOUNT` based on needs
- **Timeout Settings**: Optimize `INSTAGRAM_POST_LOAD_TIMEOUT` for network conditions
- **Batch Processing**: Process multiple accounts efficiently
- **Memory Management**: Avoid accumulating large datasets in memory

GUI Responsiveness:

- **Threading**: Keep GUI responsive during long operations
- **Progress Updates**: Real-time feedback for user operations
- **Resource Management**: Proper cleanup to prevent memory leaks
- **Event Handling**: Efficient event processing and UI updates

### Deployment & Distribution

Local Development:

- **Virtual Environment**: Isolated dependency management
- **Configuration**: Environment-specific .env files
- **Testing**: Comprehensive local testing before deployment

CI/CD Pipeline:

- **Automated Testing**: GitHub Actions with multiple Python versions
- **Quality Checks**: Automated linting, formatting, and type checking
- **Executable Build**: Windows .exe generation for distribution
- **Release Management**: Automated versioning and release creation

Distribution Options:

- **Source Distribution**: Direct Python package installation
- **Executable Build**: PyInstaller-based standalone executables
- **Container Deployment**: Docker containers for consistent environments
- **Cloud Deployment**: Cloud-based execution environments

### Contributing Guidelines

Code Standards:

- **Style Guide**: Follow PEP 8 and project-specific conventions
- **Type Hints**: Full type annotations for all functions and methods
- **Documentation**: Comprehensive docstrings and inline comments
- **Testing**: New features must include corresponding tests

Pull Request Process:

1. **Feature Branch**: Create feature-specific branches
2. **Quality Checks**: Ensure all quality checks pass
3. **Test Coverage**: Maintain or improve test coverage
4. **Documentation**: Update relevant documentation
5. **Review Process**: Code review and approval workflow

Issue Reporting:

- **Bug Reports**: Include steps to reproduce and error details
- **Feature Requests**: Describe use case and expected behavior
- **Environment Details**: Specify OS, Python version, and configuration
- **Log Files**: Attach relevant log files for debugging

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

## License

This project is licensed under the MIT License.
