#!/bin/bash

# Launch Windows Brave with remote debugging enabled for WSL2 access
# This script helps launch Brave from WSL2 with the correct flags

set -e

# Default values
DEBUG_PORT=9222
INSTAGRAM_URL="https://www.instagram.com/"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            DEBUG_PORT="$2"
            shift 2
            ;;
        -u|--url)
            INSTAGRAM_URL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Launch Windows Brave with remote debugging for WSL2 access"
            echo ""
            echo "Options:"
            echo "  -p, --port PORT    Debug port (default: 9222)"
            echo "  -u, --url URL      URL to open (default: https://www.instagram.com/)"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Launching Windows Brave with remote debugging..."
echo "Debug port: $DEBUG_PORT"
echo "URL: $INSTAGRAM_URL"
echo ""

# Check if we're in WSL2
if ! grep -q microsoft /proc/version 2>/dev/null; then
    echo "Warning: This script is designed for WSL2. You may not be running in WSL2."
fi

# Try different Brave paths
BRAVE_PATHS=(
    "/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    "/mnt/c/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe"
    "/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    "/c/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe"
)

BRAVE_PATH=""
for path in "${BRAVE_PATHS[@]}"; do
    if [ -f "$path" ]; then
        BRAVE_PATH="$path"
        break
    fi
done

if [ -z "$BRAVE_PATH" ]; then
    echo "Error: Brave browser not found in common locations."
    echo "Please install Brave or set BROWSER_PATH environment variable."
    exit 1
fi

echo "Found Brave at: $BRAVE_PATH"

# Launch Brave with remote debugging
echo "Starting Brave with remote debugging enabled..."
"$BRAVE_PATH" \
    --remote-debugging-port="$DEBUG_PORT" \
    --remote-debugging-address=0.0.0.0 \
    "$INSTAGRAM_URL" &

echo ""
echo "Brave launched successfully!"
echo "Remote debugging available at: http://localhost:$DEBUG_PORT"
echo ""
echo "Security note: This exposes the debugging port on your Windows host network."
echo "Consider using Windows Firewall to restrict access if needed."
echo ""
echo "You can now run your Python script from WSL2."
