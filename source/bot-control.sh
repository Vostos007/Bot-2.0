#!/bin/bash

LOG_DIR="/var/log/telegram-bot"
mkdir -p $LOG_DIR

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_DIR/control.log"
    echo "$1"
}

check_status() {
    if systemctl is-active --quiet telegram-bot; then
        log "Bot service is running"
        return 0
    else
        log "Bot service is not running"
        return 1
    fi
}

case "$1" in
    start)
        if ! check_status; then
            log "Starting bot service..."
            systemctl start telegram-bot || {
                log "Failed to start service"
                exit 1
            }
            log "Bot service started successfully"
        else
            log "Bot service is already running"
        fi
        ;;
    stop)
        if check_status; then
            log "Stopping bot service..."
            systemctl stop telegram-bot || {
                log "Failed to stop service"
                exit 1
            }
            log "Bot service stopped successfully"
        else
            log "Bot service is not running"
        fi
        ;;
    restart)
        log "Restarting bot service..."
        systemctl restart telegram-bot || {
            log "Failed to restart service"
            exit 1
        }
        log "Bot service restarted successfully"
        ;;
    status)
        check_status
        systemctl status telegram-bot
        ;;
    logs)
        journalctl -u telegram-bot -f
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
esac