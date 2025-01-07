# Deployment Scripts

Эти скрипты предназначены для развертывания и управления Telegram ботом на сервере.

## Установка

1. Скопируйте содержимое папки deploy на сервер
2. Запустите install.sh:
```bash
cd /path/to/deploy
chmod +x install.sh
./install.sh
```

## Управление ботом

После установки доступны следующие команды:

```bash
# Запуск бота
/opt/bot-control.sh start

# Остановка бота
/opt/bot-control.sh stop

# Перезапуск бота
/opt/bot-control.sh restart

# Проверка статуса
/opt/bot-control.sh status

# Просмотр логов
/opt/bot-control.sh logs
```

## Обновление

Для обновления бота используйте:

```bash
/opt/update.sh
```

Скрипт создаст резервную копию, обновит код из репозитория и перезапустит сервис.

## Логи

Логи доступны в следующих местах:
- `/var/log/telegram-bot/bot.log` - основной лог бота
- `/var/log/telegram-bot/error.log` - лог ошибок
- `/var/log/telegram-bot/control.log` - лог управления сервисом
- `/var/log/telegram-bot/update.log` - лог обновлений

## Бэкапы

Резервные копии хранятся в `/opt/backups` и создаются автоматически перед каждым обновлением.
Сохраняются последние 5 бэкапов.