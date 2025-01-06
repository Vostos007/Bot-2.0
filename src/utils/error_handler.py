"""Error handling utilities"""

import logging
from functools import wraps
from telegram import Update

def handle_errors(f):
    """Decorator for handling errors in handlers"""
    @wraps(f)
    async def wrapper(self, update: Update, *args, **kwargs):
        try:
            return await f(self, update, *args, **kwargs)
        except Exception as e:
            await self._handle_error(update, str(e))
            logging.error(f"Error in {f.__name__}: {e}")
        return None
    return wrapper

async def _handle_error(update: Update, error_msg: str):
    """Send error message to user"""
    message = f"⚠️ Произошла ошибка: {error_msg}\nПожалуйста, попробуйте позже."
    if update.callback_query:
        await update.callback_query.message.reply_text(message)
    else:
        await update.message.reply_text(message)