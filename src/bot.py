"""Main bot module"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from .config import BotConfig
from .notion_service import NotionService
from .constants import MESSAGES

class NotionBot:
    def __init__(self, config: BotConfig):
        self.notion = NotionService(config.notion_token)
        self.config = config

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        keyboard = [
            [
                InlineKeyboardButton("📋 Задачи", callback_data="tasks"),
                InlineKeyboardButton("➕ Новая", callback_data="new_task")
            ],
            [
                InlineKeyboardButton("🔄 В работе", callback_data="in_progress"),
                InlineKeyboardButton("✅ Готово", callback_data="completed")
            ]
        ]
        await update.message.reply_text(
            MESSAGES["welcome"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List tasks"""
        tasks = await self.notion.query_database(self.config.database_id)
        if not tasks:
            await update.callback_query.message.reply_text(MESSAGES["no_tasks"])
            return
            
        text = "📋 Ваши задачи:\n\n"
        for task in tasks:
            status = task["properties"]["Status"]["select"]["name"]
            title = task["properties"]["Title"]["title"][0]["text"]["content"]
            text += f"- {title} [{status}]\n"
            
        await update.callback_query.message.reply_text(text)

    def run(self):
        """Run the bot"""
        application = Application.builder().token(self.config.telegram_token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.list_tasks, pattern="^tasks$"))

        # Start bot
        application.run_polling()