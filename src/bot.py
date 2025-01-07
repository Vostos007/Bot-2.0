"""Main bot module with user isolation"""

import logging
import asyncio
from typing import Dict, Optional
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from cachetools import TTLCache

from .config import BotConfig, UserManager
from .notion_service import NotionService

logger = logging.getLogger(__name__)

class NotionBot:
    def __init__(self, config: BotConfig):
        self.notion = NotionService(config.notion_token, config.database_id)
        self.config = config
        self.user_manager = UserManager()
        
        # Per-user caches
        self.user_caches: Dict[int, TTLCache] = {}
        
        # Rate limiting
        self.user_timestamps = {}
        self.rate_limit = 3  # requests per second
        
    def get_user_cache(self, user_id: int) -> TTLCache:
        if user_id not in self.user_caches:
            self.user_caches[user_id] = TTLCache(maxsize=100, ttl=300)
        return self.user_caches[user_id]
        
    async def check_access(self, update: Update) -> bool:
        if not update.effective_user:
            return False
            
        user_id = update.effective_user.id
        if not self.user_manager.is_allowed(user_id):
            await update.message.reply_text(
                "У вас нет доступа к этому боту. "
                "Обратитесь к администратору."
            )
            return False
        return True

    async def _rate_limit_check(self, user_id: int) -> bool:
        """Per-user rate limiting"""
        now = time.time()
        if user_id in self.user_timestamps:
            last_request = self.user_timestamps[user_id]
            if now - last_request < 1/self.rate_limit:
                return False
        self.user_timestamps[user_id] = now
        return True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command with access check"""
        if not await self.check_access(update):
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

    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin commands handler"""
        if not update.effective_user or update.effective_user.id != self.config.admin_id:
            return
            
        command = update.message.text.split()
        if len(command) < 2:
            await update.message.reply_text("Использование: /admin [add_user|remove_user] [user_id]")
            return
            
        action, *args = command[1:]
        
        if action == "add_user" and args:
            try:
                user_id = int(args[0])
                self.user_manager.add_user(user_id)
                await update.message.reply_text(f"Пользователь {user_id} добавлен")
                logger.info(f"Admin added user {user_id}")
            except ValueError:
                await update.message.reply_text("Неверный формат ID")
                
        elif action == "remove_user" and args:
            try:
                user_id = int(args[0])
                self.user_manager.remove_user(user_id)
                await update.message.reply_text(f"Пользователь {user_id} удален")
                logger.info(f"Admin removed user {user_id}")
            except ValueError:
                await update.message.reply_text("Неверный формат ID")