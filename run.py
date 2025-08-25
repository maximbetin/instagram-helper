#!/usr/bin/env python3
"""Instagram Helper - Simple GUI Launcher

APPLICATION ENTRY POINT STRATEGY:

This module serves as the main entry point for the Instagram Helper application.
The design focuses on robust error handling, clear user feedback, and graceful
degradation when startup fails.

ARCHITECTURE OVERVIEW:

1. MAIN FUNCTION: Centralized entry point that handles all startup logic
2. ERROR HANDLING: Comprehensive error catching with user-friendly messages
3. DEPENDENCY VALIDATION: Checks for required modules before launching the GUI
4. GRACEFUL EXIT: Proper exit codes and error reporting for different failure modes

CRITICAL IMPLEMENTATION DETAILS:

- IMPORT VALIDATION: The application checks for required dependencies before
  attempting to launch the GUI, providing clear error messages if modules
  are missing or corrupted.

- ERROR CATEGORIZATION: Different types of errors (ImportError vs general
  exceptions) are handled separately to provide appropriate user guidance.

- EXIT CODE MANAGEMENT: Proper exit codes (1 for errors) enable integration
  with other tools and scripts that may launch the application.

- USER FEEDBACK: Clear error messages guide users to resolve common issues
  like missing dependencies or installation problems.

STARTUP SEQUENCE:

1. Module Import Check: Validates that all required modules can be imported
2. GUI Initialization: Creates the main GUI application instance
3. Application Launch: Starts the main event loop
4. Error Handling: Catches and reports any startup failures

ERROR RECOVERY STRATEGIES:

- MISSING DEPENDENCIES: Provides installation instructions for missing packages
- GUI INITIALIZATION FAILURES: Reports specific errors that prevent GUI startup
- UNEXPECTED ERRORS: Catches and reports unexpected issues with helpful context

INTEGRATION CONSIDERATIONS:

- COMMAND LINE USAGE: Designed to work with make commands and shell scripts
- AUTOMATION FRIENDLY: Proper exit codes enable automated testing and deployment
- DEBUGGING SUPPORT: Clear error messages help developers identify startup issues
"""

import sys

from gui_app import InstagramHelperGUI


def main() -> None:
    """Launch the Instagram Helper GUI application."""
    try:
        app = InstagramHelperGUI()
        app.run()
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure all dependencies are installed: pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
