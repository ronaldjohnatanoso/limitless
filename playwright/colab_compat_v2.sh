#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILES_DIR="$SCRIPT_DIR/../profiles"
PROFILE_NAME=${1}
USER_DATA_DIR="$PROFILES_DIR/$PROFILE_NAME"
DEBUG_PORT="${2}"
HEADLESS="${3:-false}"
BINARY_PATH="$SCRIPT_DIR/../chrome_binary_setup/chrome/linux-116.0.5793.0/chrome-linux64/chrome"

# Clean up existing Chrome processes on this port (but preserve profile data)
pkill -f "remote-debugging-port=$DEBUG_PORT" 2>/dev/null || true
sleep 2

# Ensure binary is executable
chmod +x "$BINARY_PATH"

# Create profile directory only if it doesn't exist (preserve existing profiles)
if [ ! -d "$USER_DATA_DIR" ]; then
    echo "Creating new profile directory: $USER_DATA_DIR"
    mkdir -p "$USER_DATA_DIR"
else
    echo "Using existing profile directory: $USER_DATA_DIR"
    
    # Remove singleton lock files that prevent Chrome from starting
    echo "Cleaning singleton lock files..."
    rm -f "$USER_DATA_DIR/SingletonLock" 2>/dev/null || true
    rm -f "$USER_DATA_DIR/SingletonSocket" 2>/dev/null || true
    rm -f "$USER_DATA_DIR/SingletonCookie" 2>/dev/null || true
fi

# Minimal Chrome arguments that work reliably in Colab
CHROME_ARGS=(
  --remote-debugging-port=$DEBUG_PORT
  --user-data-dir="$USER_DATA_DIR"
  --no-sandbox
  --disable-setuid-sandbox
  --disable-dev-shm-usage
  --disable-gpu
  --no-first-run
  --disable-default-apps
  --disable-popup-blocking
  --remote-debugging-address=0.0.0.0
)

if [ "$HEADLESS" = "true" ]; then
  CHROME_ARGS+=(--headless=new)
fi

echo "Starting Chrome with profile: $PROFILE_NAME"
echo "Profile directory: $USER_DATA_DIR"
echo "Command: $BINARY_PATH ${CHROME_ARGS[@]}"

# Start Chrome and capture detailed output
"$BINARY_PATH" "${CHROME_ARGS[@]}" > /tmp/chrome_minimal.log 2>&1 &
CHROME_PID=$!

echo "Chrome PID: $CHROME_PID"
sleep 5

if kill -0 $CHROME_PID 2>/dev/null; then
    echo "✓ Chrome is running successfully"
    if netstat -tlnp 2>/dev/null | grep -q ":$DEBUG_PORT "; then
        echo "✓ Debug port $DEBUG_PORT is listening"
        echo "DevTools: http://localhost:$DEBUG_PORT"
    else
        echo "⚠ Chrome running but port not ready yet"
    fi
else
    echo "✗ Chrome failed to start"
    wait $CHROME_PID 2>/dev/null
    echo "Exit code: $?"
    echo "Chrome output:"
    cat /tmp/chrome_minimal.log
fi