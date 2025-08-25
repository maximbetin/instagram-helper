#!/usr/bin/env python3
"""Instagram Helper - Simple GUI Launcher"""

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
