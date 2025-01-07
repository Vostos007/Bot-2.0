#!/bin/bash

# Настройки
REPO_NAME="Bot-2.0"
BRANCH_NAME="auto-sync-$(date +%Y%m%d-%H%M%S)"
COMMIT_MESSAGE="Автоматическая синхронизация $(date +'%Y-%m-%d %H:%M:%S')"
PR_TITLE="Автоматическая синхронизация"
PR_BODY="Автоматически созданный PR для синхронизации изменений"

# Переход в папку проекта
cd /path/to/sync-project/$REPO_NAME || { echo "Ошибка: не удалось перейти в папку проекта"; exit 1; }

# Создание новой ветки
git checkout -b $BRANCH_NAME || { echo "Ошибка: не удалось создать ветку"; exit 1; }

# Добавление всех изменений
git add . || { echo "Ошибка: не удалось добавить изменения"; exit 1; }

# Создание коммита
git commit -m "$COMMIT_MESSAGE" || { echo "Ошибка: не удалось создать коммит"; exit 1; }

# Отправка изменений на сервер
git push origin $BRANCH_NAME || { echo "Ошибка: не удалось отправить изменения"; exit 1; }

# Создание Pull Request
gh pr create \
  --title "$PR_TITLE" \
  --body "$PR_BODY" \
  --base main \
  --head $BRANCH_NAME \
  --reviewer Vostos007 \
  --assignee Vostos007 \
  --label "automation" || { echo "Ошибка: не удалось создать Pull Request"; exit 1; }

echo "Процесс завершен успешно!" 