"""Main bot module with user isolation"""

import logging
import asyncio
from typing import Dict, Optional
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from cachetools import TTLCache

from src.config import BotConfig, UserManager
from src.notion_service import NotionService

logger = logging.getLogger(__name__)

class NotionBot:
    def __init__(self, config: BotConfig):
        try:
            if not config.notion_token or not config.database_id:
                raise ValueError("Notion token and database ID must be provided")
                
            self.notion = NotionService(
                token=config.notion_token,
                database_id=config.database_id
            )
            logger.info("NotionService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NotionService: {e}")
            raise
            
        self.config = config
        self.user_manager = UserManager()
        
        # Initialize caches
        self.user_caches: Dict[int, TTLCache] = {}
        self._last_cache_cleanup = time.time()
        
        # Rate limiting
        self.user_timestamps = {}
        self._last_rate_limit_cleanup = time.time()
        self.rate_limit = 3
        self.cleanup_interval = 3600
        
    async def run(self):
        """Run the bot with error handling"""
        try:
            self.application = Application.builder().token(self.config.telegram_token).build()
            
            # Добавляем обработчики
            await self.setup_handlers()
            
            logger.info("Starting bot polling...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # Main loop with error handling
            while True:
                try:
                    await asyncio.sleep(1)
                    self._cleanup_old_entries()
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    await asyncio.sleep(5)
                    
        except asyncio.CancelledError:
            logger.info("Shutting down bot...")
            try:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
            finally:
                logger.info("Bot shutdown complete")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise

    def _cleanup_old_entries(self):
        """Cleanup old cache and rate limit entries"""
        now = time.time()
        if now - self._last_cache_cleanup > self.cleanup_interval:
            # Cleanup user caches
            for user_id in list(self.user_caches.keys()):
                if not self.user_caches[user_id]:
                    del self.user_caches[user_id]
            self._last_cache_cleanup = now
            
        if now - self._last_rate_limit_cleanup > self.cleanup_interval:
            # Cleanup rate limit timestamps
            cutoff = now - 3600  # 1 hour
            self.user_timestamps = {
                user_id: timestamp 
                for user_id, timestamp in self.user_timestamps.items()
                if timestamp > cutoff
            }
            self._last_rate_limit_cleanup = now

    def get_user_cache(self, user_id: int) -> TTLCache:
        """Get user cache with automatic cleanup"""
        self._cleanup_old_entries()
        if user_id not in self.user_caches:
            self.user_caches[user_id] = TTLCache(maxsize=100, ttl=300)
        return self.user_caches[user_id]
        
    async def check_access(self, update: Update) -> bool:
        """Check if user has access"""
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
        """Per-user rate limiting with cleanup"""
        self._cleanup_old_entries()
        now = time.time()
        if user_id in self.user_timestamps:
            last_request = self.user_timestamps[user_id]
            if now - last_request < 1/self.rate_limit:
                return False
        self.user_timestamps[user_id] = now
        return True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        if not update.effective_user:
            return
        
        user_id = update.effective_user.id
        
        if not self.user_manager.is_allowed(user_id):
            await update.message.reply_text("У вас нет доступа к этому боту. Обратитесь к администратору.")
            return
        
        keyboard = [
            [InlineKeyboardButton("Мои задачи", callback_data='show_tasks')],
            [InlineKeyboardButton("Новая задача", callback_data='new_task')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Привет! Я помогу вам управлять задачами в Notion",
            reply_markup=reply_markup
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

    async def setup_handlers(self):
        """Setup command handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("tasks", self.show_tasks_command))
        self.application.add_handler(CommandHandler("new_task", self.new_task_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        
        # Добавляем обработчик кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Добавляем обработчик ошибок
        self.application.add_error_handler(self.error_handler)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button presses"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not self.user_manager.is_allowed(user_id):
            await query.edit_message_text("У вас нет доступа к этому боту. Обратитесь к администратору.")
            return
        
        if query.data == 'show_tasks':
            await self.show_tasks(update, context)
        elif query.data == 'new_task':
            await self.new_task(update, context)

    async def show_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's tasks"""
        try:
            tasks = await self.notion.get_tasks()
            if tasks:
                await update.callback_query.edit_message_text("\n".join(tasks))
            else:
                await update.callback_query.edit_message_text("У вас пока нет задач")
        except Exception as e:
            logger.error(f"Failed to show tasks: {e}")
            await update.callback_query.edit_message_text("Ошибка при получении задач")

    async def new_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create new task"""
        try:
            await update.callback_query.edit_message_text("Функция создания задачи пока не реализована")
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            await update.callback_query.edit_message_text("Ошибка при создании задачи")

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log errors and send user-friendly message"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and hasattr(update, 'callback_query'):
            await update.callback_query.edit_message_text("Произошла ошибка. Попробуйте позже.")
        elif update and hasattr(update, 'message'):
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

    async def show_tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command handler for /tasks"""
        if not await self.check_access(update):
            return
        
        try:
            tasks = await self.notion.get_tasks()
            if tasks:
                await update.message.reply_text("\n".join(tasks))
            else:
                await update.message.reply_text("У вас пока нет задач")
        except Exception as e:
            logger.error(f"Failed to show tasks: {e}")
            await update.message.reply_text("Ошибка при получении задач")

    async def new_task_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command handler for /new_task"""
        if not await self.check_access(update):
            return
        
        try:
            # Здесь будет логика создания задачи
            await update.message.reply_text("Функция создания задачи пока не реализована")
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            await update.message.reply_text("Ошибка при создании задачи")