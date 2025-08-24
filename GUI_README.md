# Instagram Helper GUI Interface

The Instagram Helper now includes a user-friendly graphical user interface (GUI) built with Tkinter, providing an intuitive way to manage Instagram scraping operations.

## Features

### 🖥️ **Real-Time Monitoring**

- **Live Log Display**: See scraping progress and status updates in real-time
- **Progress Bar**: Visual progress indicator showing completion percentage
- **Status Updates**: Current operation status displayed prominently

### ⚙️ **Configurable Settings**

- **Max Post Age**: Set how many days back to scrape (default: 7 days)
- **Max Posts per Account**: Limit posts collected per Instagram account (default: 5)
- **Post Load Timeout**: Adjust timeout for page loading (default: 10000ms)

### 👥 **Account Management**

- **Dynamic Account List**: Add, remove, or modify Instagram accounts on the fly
- **Load from Config**: Restore default accounts from configuration file
- **Multi-Selection**: Select multiple accounts for removal

### 🎮 **Control Interface**

- **Start/Stop Controls**: Begin or halt scraping operations
- **Thread-Safe**: Responsive UI that doesn't freeze during scraping
- **Graceful Shutdown**: Clean termination of running operations

## Installation

### Prerequisites

- **Python 3.12+** (required)
- **Tkinter**: Usually included with Python, but may need installation on some systems

### Tkinter Installation (if needed)

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# macOS
# Usually included with Python

# Windows
# Usually included with Python
```

### Dependencies

```bash
# Install main project dependencies
pip install -r requirements.txt

# Install GUI-specific dependencies (if needed)
pip install -r requirements_gui.txt
```

## Usage

### Launching the GUI

#### Option 1: Direct Python execution

```bash
python gui_app.py
```

#### Option 2: Using the launcher script

```bash
python run_gui.py
```

#### Option 3: Demo mode (for testing)

```bash
python demo_gui.py
```

### Basic Workflow

1. **Configure Settings**
   - Adjust max post age (how many days back to scrape)
   - Set max posts per account
   - Configure timeout values

2. **Manage Accounts**
   - Add new Instagram accounts: Click "Add Account" and enter username
   - Remove accounts: Select accounts and click "Remove Selected"
   - Reset to defaults: Click "Load from Config"

3. **Start Scraping**
   - Click "Start Scraping" to begin the process
   - Monitor progress in the logs and progress bar
   - Use "Stop Scraping" to halt operations if needed

4. **View Results**
   - HTML reports are automatically generated
   - Check the output directory for generated reports
   - Logs show detailed operation information

## Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    Instagram Helper                         │
├─────────────────────────────────────────────────────────────┤
│ [Start Scraping] [Stop Scraping]                           │
├─────────────────────────────────────────────────────────────┤
│ Max Post Age: [7] Max Posts: [5] Timeout: [10000]         │
├─────────────────────────────────────────────────────────────┤
│ Instagram Accounts:                                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ @gijon                                                  │ │
│ │ @aytoviedo                                              │ │
│ │ @cultura.gijon                                          │ │
│ └─────────────────────────────────────────────────────────┘ │
│ [Add Account] [Remove Selected] [Load from Config]         │
├─────────────────────────────────────────────────────────────┤
│ Logs:                                                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 2024-01-01 12:00:00 - Starting scraping...            │ │
│ │ 2024-01-01 12:00:05 - Processing @gijon...            │ │
│ │ 2024-01-01 12:00:10 - Found 3 posts for @gijon        │ │
│ └─────────────────────────────────────────────────────────┘ │
│ [Clear Logs]                                               │
├─────────────────────────────────────────────────────────────┤
│ Progress: ████████████████████████████████████████ 100%   │
│ Status: Complete - 15 posts found                          │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

The GUI respects all existing environment variables from your `.env` file:

- `BROWSER_PATH`: Path to your browser executable
- `BROWSER_USER_DATA_DIR`: Browser user data directory
- `OUTPUT_DIR`: Directory for generated reports
- `TIMEZONE_OFFSET`: Timezone configuration

### Settings Persistence

- **Account List**: Changes are not automatically saved to config files
- **Settings**: Values are reset to defaults on each launch
- **Reports**: Generated reports are saved to the configured output directory

## Troubleshooting

### Common Issues

#### GUI Won't Launch

```bash
# Check Tkinter installation
python -c "import tkinter; print('Tkinter available')"

# Install Tkinter if missing
sudo apt-get install python3-tk  # Ubuntu/Debian
```

#### Import Errors

```bash
# Ensure you're in the project directory
cd /path/to/instagram-helper

# Activate virtual environment
source venv/bin/activate

# Check dependencies
pip list | grep playwright
```

#### Browser Issues

- Ensure your browser supports remote debugging
- Check that `BROWSER_PATH` is correctly set in `.env`
- Verify no other browser instances are using the debug port

### Debug Mode

```bash
# Run with verbose logging
python -u gui_app.py 2>&1 | tee gui_debug.log
```

## Advanced Features

### Custom Account Lists

- Modify accounts in the GUI interface
- Use the "Load from Config" button to restore defaults
- Account changes are session-only (not saved to files)

### Real-Time Monitoring

- Logs update every 100ms for responsive display
- Progress bar shows account-by-account completion
- Status messages provide current operation details

### Multi-Threading

- Scraping runs in background thread
- UI remains responsive during operations
- Clean shutdown with proper resource cleanup

## Integration

### With Existing CLI

- GUI and CLI can coexist
- Same configuration files and settings
- Compatible output formats

### With Existing Scripts

- All existing Python modules work unchanged
- Browser management follows same patterns
- Report generation uses identical templates

## Performance

### Memory Usage

- Minimal memory overhead for GUI components
- Efficient log handling with queue-based system
- Clean resource management

### Responsiveness

- Non-blocking UI during scraping operations
- Smooth progress updates
- Immediate response to user controls

## Future Enhancements

Potential improvements for future versions:

- Settings persistence across sessions
- Account list export/import functionality
- Customizable log levels
- Dark/light theme options
- Keyboard shortcuts
- Batch operation scheduling

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the main project README.md
3. Check that all dependencies are properly installed
4. Verify your environment configuration

---

**Note**: The GUI provides the same functionality as the command-line interface but with a user-friendly interface. All scraping operations, browser management, and report generation work identically to the CLI version.
