#!/bin/bash

# Создаем необходимые директории
mkdir -p /var/log/telegram-bot /opt/backups
chmod 755 /var/log/telegram-bot /opt/backups

# Копируем файлы
cp bot-control.sh /opt/
cp update.sh /opt/
cp telegram-bot.service /etc/systemd/system/

# Делаем скрипты исполняемыми
chmod +x /opt/bot-control.sh /opt/update.sh

# Перезагружаем systemd и запускаем сервис
systemctl daemon-reload
systemctl enable telegram-bot
systemctl start telegram-bot

# Проверяем статус
/opt/bot-control.sh status