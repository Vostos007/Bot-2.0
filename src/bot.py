"""Main bot module with CPU usage optimization"""

import logging
import asyncio
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from .config import BotConfig
from .notion_service import NotionService
from .constants import MESSAGES
from .utils.error_handler import handle_errors
from .utils.monitoring import ResourceMonitor
from .utils.rate_limiter import RateLimiter

class NotionBot:
    def __init__(self, config: BotConfig):
        self.notion = NotionService(config.notion_token, config.database_id)
        self.config = config
        self.monitor = ResourceMonitor(warning_threshold=40)  # 40% CPU threshold
        self.rate_limiter = RateLimiter(max_requests=30, time_window=60)
        
        # Start monitoring task
        self.monitor_task = None

    async def _check_resources(self):
        """Periodic resource check"""
        while True:
            self.monitor.check_resources()
            await asyncio.sleep(60)  # Check every minute

    @handle_errors
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler with rate limiting"""
        user_id = update.effective_user.id
        
        # Check rate limit
        if not self.rate_limiter.can_make_request(user_id):
            await update.message.reply_text(
                "⚠️ Пожалуйста, подождите немного перед следующим запросом."
            )
            return
        
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
        """List tasks handler with rate limiting"""
        user_id = update.effective_user.id
        
        if not self.rate_limiter.can_make_request(user_id):
            await update.callback_query.message.reply_text(
                "⚠️ Пожалуйста, подождите немного перед следующим запросом."
            )
            return
            
        tasks = await self.notion.query_database()
        
        if not tasks:
            await update.callback_query.message.reply_text(MESSAGES["no_tasks"])
            return
            
        text = "📋 Ваши задачи:\n\n"
        for task in tasks:
            status = task["properties"]["Status"]["status"]["name"]
            title = task["properties"]["Title"]["title"][0]["text"]["content"]
            text += f"- {title} [{status}]\n"
            await asyncio.sleep(0)  # Prevent blocking
            
        await update.callback_query.message.reply_text(text)

    def run(self):
        """Run the bot with resource monitoring"""
        application = Application.builder().token(self.config.telegram_token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.list_tasks, pattern="^tasks$"))

        # Start monitoring
        self.monitor_task = application.create_task(self._check_resources())

        # Run bot
        application.run_polling()
        
    async def stop(self):
        """Graceful shutdown"""
        if self.monitor_task:
            self.monitor_task.cancel()
        # Cleanup code here if needed