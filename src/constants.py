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

AVAILABLE_TAGS = [
    "Mobile",
    "Website",
    "Improvement",
    "ETSY",
    "срочно"
]

MESSAGES = {
    "welcome": "Привет! Я помогу управлять задачами в Notion.",
    "no_tasks": "Задач не найдено",
    "task_created": "✅ Задача создана",
    "task_updated": "✅ Задача обновлена",
    "error": "❌ Произошла ошибка: {error}"
}