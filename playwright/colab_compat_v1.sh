#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values - now relative to script location
PROFILES_DIR="$SCRIPT_DIR/../profiles"
PROFILE_NAME=${1}
USER_DATA_DIR="$PROFILES_DIR/$PROFILE_NAME" # Use first argument, fallback to env var
DEBUG_PORT="${2}" # Use second argument, fallback to env var
HEADLESS="${3:-false}" # Use third argument, default to false
BINARY_PATH="$SCRIPT_DIR/../chrome_binary_setup/chrome/linux-116.0.5793.0/chrome-linux64/chrome"

# Create the user data dir if it doesn't exist
mkdir -p "$USER_DATA_DIR"

echo "debug port: $DEBUG_PORT"
echo "headless mode: $HEADLESS"

if [ -z "$DEBUG_PORT" ]; then
  echo "Error: DEBUG_PORT is not set. Please provide it as an argument or set the environment variable."
  echo "Usage: $0 <user_data_dir> <debug_port> [headless]"
  exit 1
fi

# Kill any existing Chrome processes using this debug port
echo "Cleaning up existing Chrome processes on port $DEBUG_PORT..."
pkill -f "remote-debugging-port=$DEBUG_PORT" 2>/dev/null || true

# Wait a moment for processes to terminate
sleep 2

# Double-check and force kill if necessary
if pgrep -f "remote-debugging-port=$DEBUG_PORT" > /dev/null; then
  echo "Force killing remaining processes..."
  pkill -9 -f "remote-debugging-port=$DEBUG_PORT" 2>/dev/null || true
  sleep 1
fi

# Build Chrome command with minimal, Colab-compatible arguments
CHROME_ARGS=(
  --remote-debugging-port=$DEBUG_PORT
  --user-data-dir="$USER_DATA_DIR"
  --no-first-run
  --no-default-browser-check
  --disable-default-apps
  --disable-component-update
  --disable-popup-blocking
  --disable-dev-shm-usage
  --no-sandbox
  --disable-setuid-sandbox
  --disable-gpu
  --disable-software-rasterizer
  --disable-background-timer-throttling
  --disable-backgrounding-occluded-windows
  --disable-renderer-backgrounding
  --disable-features=TranslateUI,VizDisplayCompositor
  --disable-extensions
  --disable-background-networking
  --password-store=basic
  --use-mock-keychain
  --disable-logging
  --log-level=3
  --remote-debugging-address=0.0.0.0
  --disable-hang-monitor
  --disable-prompt-on-repost
  --disable-client-side-phishing-detection
  --disable-sync
  --disable-translate
  --disable-ipc-flooding-protection
)

# Add headless-specific flags
if [ "$HEADLESS" = "true" ]; then
  CHROME_ARGS+=(
    --headless=new
    --disable-process-singleton-dialog
    --run-all-compositor-stages-before-draw
    --disable-background-timer-throttling
  )
  echo "Starting Chrome in headless mode... Port: $DEBUG_PORT, Profile: $PROFILE_NAME"
else
  echo "Starting Chrome with GUI... Port: $DEBUG_PORT, Profile: $PROFILE_NAME"
fi

# Test Chrome binary first
echo "Testing Chrome binary..."
if ! "$BINARY_PATH" --version >/dev/null 2>&1; then
    echo "Chrome binary test failed. Installing dependencies..."
    apt-get update >/dev/null 2>&1
    apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2 >/dev/null 2>&1
fi

# Start Chrome with the configured arguments
echo "Executing: $BINARY_PATH ${CHROME_ARGS[@]}"
"$BINARY_PATH" "${CHROME_ARGS[@]}" > /tmp/chrome_output.log 2>&1 &
CHROME_PID=$!
echo "Chrome PID: $CHROME_PID"

# Wait for Chrome to fully start
sleep 5

# Check if Chrome is running and the port is available
if kill -0 $CHROME_PID 2>/dev/null; then
    echo "Chrome is running successfully on port $DEBUG_PORT"
    if netstat -tlnp 2>/dev/null | grep -q ":$DEBUG_PORT "; then
        echo "Chrome debug port $DEBUG_PORT is listening"
        echo "DevTools URL: http://localhost:$DEBUG_PORT"
        echo "To connect: curl -s http://localhost:$DEBUG_PORT/json/version"
    else
        echo "Warning: Chrome is running but port $DEBUG_PORT is not listening yet"
        sleep 3
        if netstat -tlnp 2>/dev/null | grep -q ":$DEBUG_PORT "; then
            echo "Chrome debug port $DEBUG_PORT is now listening"
            echo "DevTools URL: http://localhost:$DEBUG_PORT"
        else
            echo "Port still not listening. Check Chrome output:"
            cat /tmp/chrome_output.log 2>/dev/null
        fi
    fi
else
    echo "Chrome process has exited"
    wait $CHROME_PID 2>/dev/null
    echo "Exit code: $?"
    echo "Chrome output:"
    cat /tmp/chrome_output.log 2>/dev/null || echo "No output log found"
fi

# Keep the script running to maintain Chrome and show final status
if kill -0 $CHROME_PID 2>/dev/null; then
    echo "Chrome is running successfully in background."
    echo "Process ID: $CHROME_PID"
    echo "Debug port: $DEBUG_PORT"
    echo "Profile: $PROFILE_NAME"
    echo ""
    echo "To stop Chrome: kill $CHROME_PID"
    echo "To check status: ps aux | grep $CHROME_PID"
    echo "To test connection: curl -s http://localhost:$DEBUG_PORT/json/version"
else
    echo "Failed to start Chrome. Check the output above for errors."
fi