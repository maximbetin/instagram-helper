#!/usr/bin/env python3
"""Demonstration script showing WSL2 integration features."""

import sys
import os

# Add the parent directory to the path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    is_wsl2, 
    get_wsl_host_ip, 
    WSL2_MODE, 
    WSL_HOST_IP, 
    BROWSER_PATH,
    BROWSER_DEBUG_PORT
)

def demo_wsl2_integration():
    """Demonstrate WSL2 integration features."""
    print("🚀 Instagram Helper - WSL2 Integration Demo")
    print("=" * 50)
    
    # Environment detection
    print("\n🔍 Environment Detection:")
    print(f"  Running in WSL2: {'✅ Yes' if is_wsl2() else '❌ No'}")
    print(f"  WSL2 Mode enabled: {'✅ Yes' if WSL2_MODE else '❌ No'}")
    
    if is_wsl2():
        print(f"  Windows Host IP: {WSL_HOST_IP}")
        print(f"  Debug Port: {BROWSER_DEBUG_PORT}")
        print(f"  Browser Path: {BROWSER_PATH}")
        
        # Check if browser exists
        if os.path.exists(BROWSER_PATH):
            print(f"  Browser Status: ✅ Found")
        else:
            print(f"  Browser Status: ❌ Not found")
    
    # Configuration options
    print("\n⚙️  Configuration Options:")
    print("  Set WSL2_MODE=disabled to force Linux mode")
    print("  Set WSL_HOST_IP to override auto-detection")
    print("  Set BROWSER_PATH to specify custom browser location")
    
    # Usage instructions
    print("\n📖 Usage Instructions:")
    if is_wsl2():
        print("  1. Launch Windows Brave with remote debugging:")
        print(f"     ./scripts/launch_brave_wsl2.sh")
        print("")
        print("  2. Or manually launch Brave with:")
        print(f"     {BROWSER_PATH} --remote-debugging-port={BROWSER_DEBUG_PORT} --remote-debugging-address=0.0.0.0")
        print("")
        print("  3. Run your Instagram Helper script:")
        print("     python cli.py")
        print("")
        print("  The tool will automatically connect to Windows Brave!")
    else:
        print("  You're not running in WSL2, so the tool will use Linux mode.")
        print("  To test WSL2 features, run this script from WSL2.")
    
    # Security notes
    if is_wsl2():
        print("\n⚠️  Security Notes:")
        print("  - Remote debugging port is exposed on Windows host network")
        print("  - Consider using Windows Firewall to restrict access")
        print("  - Only use on trusted networks")
    
    print("\n🎯 Ready to use Instagram Helper with WSL2!")

if __name__ == "__main__":
    demo_wsl2_integration()
