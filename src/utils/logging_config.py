import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logging(log_dir: str, log_level: int = logging.INFO) -> None:
    """Configure logging with file rotation and console output.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (default: INFO)
    """
    try:
        # Create log directory if not exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Main logger configuration
        logger = logging.getLogger()
        logger.setLevel(log_level)
        
        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # File handler with rotation
        log_file = os.path.join(log_dir, 'bot.log')
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Special handler for errors
        error_log = os.path.join(log_dir, 'errors.log')
        error_handler = RotatingFileHandler(
            filename=error_log,
            maxBytes=2*1024*1024,  # 2 MB
            backupCount=1,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(error_handler)
        
        logger.info("Logging configured successfully")
        
    except Exception as e:
        print(f"Failed to configure logging: {e}")
        raise