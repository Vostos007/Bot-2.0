#!/bin/bash

LOG_DIR="/var/log/telegram-bot"
BACKUP_DIR="/opt/backups"
mkdir -p $LOG_DIR $BACKUP_DIR

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_DIR/update.log"
    echo "$1"
}

# Создаем бэкап
create_backup() {
    local backup_name="bot_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    log "Creating backup..."
    tar -czf "$BACKUP_DIR/$backup_name" /opt/*.py /opt/requirements.txt .env 2>/dev/null || {
        log "Failed to create backup"
        return 1
    }
    log "Backup created: $backup_name"
    
    # Удаляем старые бэкапы (оставляем последние 5)
    find $BACKUP_DIR -name "bot_backup_*.tar.gz" -type f -printf '%T+ %p\n' | \
        sort -r | tail -n +6 | cut -d' ' -f2- | xargs -r rm
    
    return 0
}

# Проверка зависимостей
check_dependencies() {
    log "Checking dependencies..."
    pip3 freeze > current_requirements.txt
    if ! diff -q requirements.txt current_requirements.txt >/dev/null 2>&1; then
        log "Dependencies need to be updated"
        return 1
    fi
    rm current_requirements.txt
    log "Dependencies are up to date"
    return 0
}

# Основной процесс обновления
main() {
    log "Starting update process..."
    
    # Создаем бэкап
    create_backup || {
        log "Update aborted due to backup failure"
        return 1
    }
    
    # Получаем обновления из git
    log "Pulling updates from git..."
    git pull || {
        log "Failed to pull updates from git"
        return 1
    }
    
    # Проверяем и обновляем зависимости если нужно
    if ! check_dependencies; then
        log "Installing dependencies..."
        pip3 install -r requirements.txt || {
            log "Failed to install dependencies"
            return 1
        }
    fi
    
    # Перезапускаем сервис
    log "Restarting bot service..."
    systemctl restart telegram-bot || {
        log "Failed to restart service"
        return 1
    }
    
    # Проверяем статус
    sleep 2
    if systemctl is-active --quiet telegram-bot; then
        log "Update completed successfully"
        return 0
    else
        log "Service failed to start after update"
        return 1
    fi
}

# Запускаем основной процесс
main || {
    log "Update failed. Check logs for details"
    exit 1
}