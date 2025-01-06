"""Constants for the bot"""

TASK_STATUSES = {
    "TODO": "Сделать",
    "TASK_ACCEPTED": "Задача принята",
    "IN_REVISION": "В доработке",
    "IN_PROGRESS": "В работе",
    "REVIEW": "Проверить",
    "COMPLETED": "Выполнена",
    "ARCHIVED": "Archived"
}

TASK_PRIORITIES = {
    "LOW": "Low",
    "MEDIUM": "Medium",
    "HIGH": "High",
    "MEDIUM_RU": "Средний",
    "HIGH_RU": "Высокий"
}

MESSAGES = {
    "welcome": "Добро пожаловать в систему управления задачами!",
    "task_created": "✅ Задача успешно создана",
    "task_updated": "✅ Задача обновлена",
    "error": "❌ Произошла ошибка: {error}",
    "rate_limit": "⚠️ Превышен лимит запросов к API.\nПожалуйста, подождите немного.",
    "no_tasks": "📝 Список задач пуст"
}