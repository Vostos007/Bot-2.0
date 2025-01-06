from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes, ConversationHandler
from telegram_calendar_keyboard import CallbackData, create_calendar
from datetime import datetime
import os

from ..notion_service import NotionService
from ..constants import MESSAGES, TASK_STATUSES

# States for conversation handler
TITLE, ASSIGNEE, DUE_DATE, STATUS, PRIORITY, CONFIRM = range(6)

class CommandHandlers:
    def __init__(self, notion_service: NotionService):
        self.notion = notion_service
        self.calendar_callback = CallbackData("calendar", "action", "year", "month", "day")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles /start command"""
        keyboard = [
            [InlineKeyboardButton("📋 Задачи", callback_data="view_tasks"),
             InlineKeyboardButton("➕ Новая задача", callback_data="new_task")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        await update.message.reply_text(
            MESSAGES["welcome"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles /help command"""
        help_text = """📚 Доступные команды:

/start - Начать работу с ботом
/new - Создать новую задачу
/tasks - Просмотр задач
/help - Показать эту справку
/restart - Перезапустить бота
/cancel - Отменить текущее действие

🔹 При создании задачи:
- Можно пропускать поля, нажимая 'Пропустить'
- Можно отменить создание командой /cancel
"""
        await update.message.reply_text(help_text)
        return ConversationHandler.END

    async def restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles /restart command"""
        await update.message.reply_text("🔄 Перезапуск бота...")
        os.system('systemctl restart telegram-bot.service')
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles /cancel command"""
        await update.message.reply_text("❌ Действие отменено", reply_markup=None)
        return ConversationHandler.END

    async def start_new_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start new task creation"""
        await update.message.reply_text("📝 Введите название задачи:")
        return TITLE

    async def handle_task_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle task title input"""
        context.user_data['title'] = update.message.text
        
        # Get workspace members
        members = await self.notion.get_workspace_members()
        keyboard = [
            [InlineKeyboardButton(member['name'], callback_data=f"assign_{member['id']}")] 
            for member in members
            if member['type'] in ['member', 'guest']
        ]
        keyboard.append([InlineKeyboardButton("Пропустить", callback_data="skip_assignee")])
        
        await update.message.reply_text(
            "👤 Выберите ответственного:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ASSIGNEE

    async def handle_assignee(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle assignee selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data != "skip_assignee":
            context.user_data['assignee_id'] = query.data.split('_')[1]
            
        # Show calendar for due date
        calendar, step = create_calendar()
        await query.message.reply_text(
            "📅 Выберите срок выполнения:",
            reply_markup=calendar
        )
        return DUE_DATE