#!/usr/bin/env python3
"""Test script to verify WSL2 detection and configuration."""

import sys
import os

# Add the parent directory to the path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import is_wsl2, get_wsl_host_ip, WSL2_MODE, WSL_HOST_IP, BROWSER_PATH

def main():
    """Test WSL2 detection and configuration."""
    print("=== WSL2 Detection Test ===\n")
    
    # Test WSL2 detection
    print(f"WSL2 Detection: {is_wsl2()}")
    print(f"WSL2 Mode: {WSL2_MODE}")
    
    # Test host IP detection
    try:
        host_ip = get_wsl_host_ip()
        print(f"Detected Host IP: {host_ip}")
        print(f"Configured Host IP: {WSL_HOST_IP}")
    except Exception as e:
        print(f"Error getting host IP: {e}")
    
    # Test browser path
    print(f"Browser Path: {BROWSER_PATH}")
    
    # Test if browser exists
    if os.path.exists(BROWSER_PATH):
        print(f"✓ Browser found at: {BROWSER_PATH}")
    else:
        print(f"✗ Browser not found at: {BROWSER_PATH}")
    
    # Show environment info
    print(f"\nEnvironment Variables:")
    print(f"  WSL2_MODE: {os.getenv('WSL2_MODE', 'not set')}")
    print(f"  WSL_HOST_IP: {os.getenv('WSL_HOST_IP', 'not set')}")
    print(f"  BROWSER_PATH: {os.getenv('BROWSER_PATH', 'not set')}")
    
    # Show system info
    print(f"\nSystem Info:")
    try:
        with open('/proc/version', 'r') as f:
            version = f.read().strip()
            print(f"  Kernel: {version}")
    except Exception as e:
        print(f"  Error reading /proc/version: {e}")
    
    try:
        with open('/etc/resolv.conf', 'r') as f:
            resolv = f.read().strip()
            print(f"  Resolv.conf: {resolv}")
    except Exception as e:
        print(f"  Error reading /etc/resolv.conf: {e}")
    
    print(f"\n=== Test Complete ===")

if __name__ == "__main__":
    main()
