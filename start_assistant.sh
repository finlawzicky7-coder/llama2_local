#!/bin/bash
# Start the autonomous assistant with auto-restart
# Usage: ./start_assistant.sh
# Stop:  kill $(cat /home/user/llama2_local/assistant.pid)

WORKDIR="/home/user/llama2_local"
PIDFILE="$WORKDIR/assistant.pid"
LOGFILE="$WORKDIR/logs/assistant.log"

mkdir -p "$WORKDIR/logs"

# Check if already running
if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Assistant already running (PID $OLD_PID)"
        exit 1
    fi
fi

# Start with auto-restart loop
(
    while true; do
        echo "[$(date)] Starting assistant scheduler..." >> "$LOGFILE"
        cd "$WORKDIR"
        python3 -m assistant.scheduler >> "$LOGFILE" 2>&1
        echo "[$(date)] Scheduler exited. Restarting in 10s..." >> "$LOGFILE"
        sleep 10
    done
) &

echo $! > "$PIDFILE"
echo "Assistant started (PID $!). Logs: $LOGFILE"
