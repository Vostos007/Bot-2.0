"""Main bot module with improved error handling and monitoring"""

import logging
import time
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from .config import BotConfig
from .notion_service import NotionService
from .constants import MESSAGES
from .utils.error_handler import handle_errors

class NotionBot:
    def __init__(self, config: BotConfig):
        self.notion = NotionService(config.notion_token, config.database_id)
        self.config = config
        self.start_time = time.time()

    @handle_errors
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
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

    @handle_errors
    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List tasks handler"""
        tasks = await self.notion.query_database(
            filter_conditions={
                "property": "Status",
                "status": {
                    "does_not_equal": "Completed"
                }
            }
        )
        
        if not tasks:
            await update.callback_query.message.reply_text(MESSAGES["no_tasks"])
            return
            
        text = "📋 Ваши задачи:\n\n"
        for task in tasks:
            status = task["properties"]["Status"]["status"]["name"]
            title = task["properties"]["Title"]["title"][0]["text"]["content"]
            text += f"- {title} [{status}]\n"
            
        await update.callback_query.message.reply_text(text)

    def run(self):
        """Run the bot"""
        application = Application.builder().token(self.config.telegram_token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.list_tasks, pattern="^tasks$"))

        application.run_polling()