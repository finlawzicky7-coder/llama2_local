#!/bin/bash
# Stop the autonomous assistant
PIDFILE="/home/user/llama2_local/assistant.pid"

if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm "$PIDFILE"
        echo "Assistant stopped (PID $PID)"
    else
        rm "$PIDFILE"
        echo "Assistant was not running (stale PID file removed)"
    fi
else
    echo "No PID file found. Assistant is not running."
fi
