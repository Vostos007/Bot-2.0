"""Error handling utilities"""

import logging
import functools
from typing import Callable, Any
from telegram import Update
from telegram.ext import ContextTypes
from notion_client.errors import APIResponseError

logger = logging.getLogger(__name__)

def handle_telegram_error(func: Callable) -> Callable:
    """Decorator for handling Telegram API errors"""
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(self, update, context, *args, **kwargs)
        except Exception as e:
            user_id = update.effective_user.id if update.effective_user else 'Unknown'
            logger.error(f"Error in {func.__name__} for user {user_id}: {e}", exc_info=True)
            
            try:
                if update.callback_query:
                    await update.callback_query.answer(
                        "Произошла ошибка. Попробуйте позже."
                    )
                else:
                    await update.message.reply_text(
                        "Произошла ошибка. Попробуйте позже."
                    )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
                
    return wrapper

def handle_notion_error(func: Callable) -> Callable:
    """Decorator for handling Notion API errors"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except APIResponseError as e:
            if e.code == 'unauthorized':
                logger.error("Notion API unauthorized. Check your token.")
                raise
            elif e.code == 'rate_limited':
                logger.warning("Notion API rate limit reached. Waiting...")
                # Можно добавить здесь логику ожидания
                raise
            else:
                logger.error(f"Notion API error: {e}")
                raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
            
    return wrapper

def setup_error_handling(application):
    """Setup global error handlers for the application"""
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
        
        try:
            if update and isinstance(update, Update) and update.effective_message:
                await update.effective_message.reply_text(
                    "Произошла ошибка. Попробуйте позже."
                )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
            
    application.add_error_handler(error_handler)
