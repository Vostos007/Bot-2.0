#!/bin/bash

# Create logs directory
LOG_DIR="logs"
mkdir -p $LOG_DIR

# Log file with timestamp
LOG_FILE="$LOG_DIR/bot_$(date +%Y%m%d_%H%M%S).log"

# Function to check status and restart
check_and_restart() {
    if ! pgrep -f "python main.py" > /dev/null; then
        echo "$(date): Bot stopped, restarting..." >> "$LOG_FILE"
        python main.py >> "$LOG_FILE" 2>&1 &
    fi
}

# Start bot
echo "$(date): Starting bot..." >> "$LOG_FILE"
python main.py >> "$LOG_FILE" 2>&1 &

# Monitor every minute
while true; do
    check_and_restart
    sleep 60
done