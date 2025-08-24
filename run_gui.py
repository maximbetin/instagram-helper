#!/usr/bin/env python3
"""Launcher script for Instagram Helper GUI."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui_app import main
    main()
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error starting GUI: {e}")
    sys.exit(1)
