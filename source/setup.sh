#!/bin/bash

# Создаем директории
mkdir -p /var/log/telegram-bot /opt/backups
chmod 755 /var/log/telegram-bot /opt/backups

# Делаем скрипты исполняемыми
chmod +x /opt/bot-control.sh /opt/update.sh

# Копируем systemd сервис
cp telegram-bot.service /etc/systemd/system/

# Перезагружаем systemd и запускаем сервис
systemctl daemon-reload
systemctl enable telegram-bot
systemctl start telegram-bot

# Проверяем статус
/opt/bot-control.sh status