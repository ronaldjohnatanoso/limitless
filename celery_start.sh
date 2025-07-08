#!/bin/bash
# filepath: /media/ronald/Kingston Shared/limitless/celery_start.sh

echo "Starting Airflow with Celery using tmux..."

# Stop any existing Airflow processes (exclude this script)
echo "🛑 Stopping existing Airflow processes..."
pkill -f "airflow celery" 2>/dev/null || true
pkill -f "airflow scheduler" 2>/dev/null || true  
pkill -f "airflow api-server" 2>/dev/null || true
pkill -f "api_server" 2>/dev/null || true

# Kill any existing tmux sessions
echo "🛑 Killing existing tmux sessions..."
tmux kill-server 2>/dev/null || true

# Wait longer for processes to fully stop
sleep 3

# Check if port 8080 is still in use and force kill if needed
if lsof -i :8080 &>/dev/null; then
    echo "🔥 Port 8080 still in use, force killing..."
    sudo kill -9 $(sudo lsof -t -i:8080) 2>/dev/null || true
    sleep 2
fi

# Start Redis
echo "🚀 Starting Redis..."
sudo systemctl start redis-server

# Wait for Redis to start
sleep 2

# Verify Redis is running
if ! redis-cli ping &>/dev/null; then
    echo "❌ Redis failed to start"
    exit 1
fi
echo "✅ Redis is running"

# Change to airflow directory
cd "/media/ronald/Kingston Shared/limitless/airflow"

# Create ONE tmux session with multiple windows
echo "🚀 Creating tmux session with multiple windows..."

# Create session and first window (worker)
tmux new-session -d -s airflow -n worker 'airflow celery worker'

# Add more windows to the same session
tmux new-window -t airflow -n flower 'airflow celery flower'
tmux new-window -t airflow -n scheduler 'airflow scheduler'
tmux new-window -t airflow -n webserver 'airflow api-server'

sleep 3

# Show session info
echo "📋 Tmux session created:"
tmux list-windows -t airflow

echo ""
echo "✅ All services started!"
echo ""
echo "🔗 URLs:"
echo "   Airflow UI: http://localhost:8080"
echo "   Flower UI: http://localhost:5555"
echo ""
echo "📺 Access all services:"
echo "   tmux attach -t airflow"
echo ""
echo "🎮 Navigation (inside tmux):"
echo "   Ctrl+B then 0-3  # Switch to window 0,1,2,3"
echo "   Ctrl+B then n    # Next window"
echo "   Ctrl+B then p    # Previous window"
echo "   Ctrl+B then w    # List windows"
echo "   Ctrl+B then d    # Detach from session"