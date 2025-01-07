"""Optimized bot module"""

import logging
import asyncio
from typing import Optional
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from cachetools import TTLCache

from .config import BotConfig
from .notion_service import NotionService

logger = logging.getLogger(__name__)

class NotionBot:
    def __init__(self, config: BotConfig):
        self.notion = NotionService(config.notion_token, config.database_id)
        self.config = config
        
        # Simple cache with 5 minute TTL
        self.cache = TTLCache(maxsize=100, ttl=300)
        
        # Rate limiting
        self.user_timestamps = {}
        self.rate_limit = 3  # requests per second
        
    async def _rate_limit_check(self, user_id: int) -> bool:
        """Simple rate limiting"""
        now = time.time()
        if user_id in self.user_timestamps:
            last_request = self.user_timestamps[user_id]
            if now - last_request < 1/self.rate_limit:
                return False
        self.user_timestamps[user_id] = now
        return True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Optimized start command handler"""
        if not update.effective_user:
            return
            
        if not await self._rate_limit_check(update.effective_user.id):
            await update.message.reply_text("Пожалуйста, подождите немного...")
            return

        keyboard = [
            [
                InlineKeyboardButton("📋 Задачи", callback_data="tasks"),
                InlineKeyboardButton("➕ Новая", callback_data="new_task")
            ]
        ]
        
        await update.message.reply_text(
            "Привет! Я помогу вам управлять задачами в Notion",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Optimized task listing with caching"""
        if not update.callback_query or not update.effective_user:
            return
            
        if not await self._rate_limit_check(update.effective_user.id):
            await update.callback_query.answer("Пожалуйста, подождите...")
            return

        # Try cache first
        cache_key = f"tasks_{update.effective_user.id}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            await update.callback_query.message.reply_text(cached_result)
            return

        # If not in cache, fetch with pagination
        try:
            tasks = await self.notion.query_database(limit=10)
            
            if not tasks:
                await update.callback_query.message.reply_text("Задач пока нет")
                return
                
            text = "📋 Последние задачи:\n\n"
            for task in tasks:
                status = task.get("properties", {}).get("Status", {}).get("status", {}).get("name", "Новая")
                title = task.get("properties", {}).get("Title", {}).get("title", [{}])[0].get("text", {}).get("content", "Без названия")
                text += f"- {title} [{status}]\n"
                
            # Cache the result
            self.cache[cache_key] = text
            
            await update.callback_query.message.reply_text(text)
            
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")
            await update.callback_query.message.reply_text("Произошла ошибка при получении задач")

    def run(self):
        """Run the bot with optimizations"""
        # Configure application with optimized settings
        app = (
            Application.builder()
            .token(self.config.telegram_token)
            .concurrent_updates(True)  # Enable concurrent updates
            .build()
        )

        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CallbackQueryHandler(self.list_tasks, pattern="^tasks$"))
        
        # Set up error handling
        app.add_error_handler(self._error_handler)
        
        # Run the bot
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Log errors"""
        logger.error(f"Error: {context.error} with update {update}")
