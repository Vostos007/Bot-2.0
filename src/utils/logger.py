"""Logging configuration for the bot"""

import logging
import os
from datetime import datetime

def setup_logging(log_dir: str = 'logs'):
    """Setup logging with file and console handlers"""
    # Create logs directory if not exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with daily rotation
    log_file = os.path.join(
        log_dir,
        f'bot_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create special loggers
    access_logger = logging.getLogger('access')
    error_logger = logging.getLogger('error')
    
    return {
        'root': root_logger,
        'access': access_logger,
        'error': error_logger
    }

def log_user_action(logger: logging.Logger, user_id: int, action: str):
    """Log user action with standardized format"""
    logger.info(f"User {user_id} - {action}")

def log_error(logger: logging.Logger, error: Exception, context: str = None):
    """Log error with full context"""
    error_msg = f"Error: {type(error).__name__} - {str(error)}"
    if context:
        error_msg = f"{context} - {error_msg}"
    logger.error(error_msg, exc_info=True)