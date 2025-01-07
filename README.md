# Bot-2.0

Telegram бот для управления задачами в Notion с оптимизированным потреблением ресурсов.

🚀 **Тестирование автоматического деплоя**

## Особенности
- Низкое потребление CPU
- Кэширование запросов
- Защита от перегрузок
- Простой интерфейс
- Автоматический деплой

## Установка

```bash
git clone https://github.com/Vostos007/Bot-2.0.git
cd Bot-2.0
pip install -r requirements.txt
```

## Настройка Notion API

1. Создайте новую интеграцию:
   - Перейдите на https://www.notion.so/my-integrations
   - Нажмите "New integration"
   - Заполните необходимые поля
   - Скопируйте токен интеграции

2. Настройте базу данных:
   - Создайте новую базу данных в Notion или используйте существующую
   - В настройках базы данных (⋮) выберите "Add connections"
   - Добавьте созданную интеграцию
   - Скопируйте ID базы данных из URL

3. Установите переменные окружения:
```bash
export NOTION_TOKEN='your_integration_token'
export DATABASE_ID='your_database_id'
```

### Структура базы данных Notion
База данных должна содержать следующие поля:
- Title (type: title) - название задачи
- Status (type: status) - статус задачи

## Запуск

```bash
python main.py
```

## Использование

1. Начало работы:
   - Отправьте `/start` боту
   - Используйте кнопки меню для навигации

2. Основные команды:
   - 📋 Задачи - просмотр списка задач
   - ➕ Новая - создание новой задачи

## Техническая документация

- [API References](docs/API_REFERENCES.md) - документация по API
- Rate limits и другие ограничения
- Форматы данных

## Оптимизация

- Кэширование (TTL = 5 минут)
- Rate limiting (3 req/sec)
- Пагинация (10 задач)
- Асинхронная обработка

## Логирование

Логи сохраняются с информацией о времени, уровне и сообщении:
```
2024-01-07 12:34:56 - INFO - Bot started
```

## Решение проблем

Если возникают ошибки:
1. Проверьте токены и права доступа
2. Убедитесь в правильной структуре базы данных
3. Проверьте логи ошибок

## Лицензия

MIT