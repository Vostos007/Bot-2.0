import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_dir: str):
    """Sets up logging with file rotation"""
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Main log file
    main_log = os.path.join(log_dir, 'bot.log')
    
    # Formatting setup
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Rotation setup (10 files, 10MB each)
    handler = RotatingFileHandler(
        main_log,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    handler.setFormatter(formatter)
    
    # Root logger setup
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    
    # Separate handler for errors
    error_log = os.path.join(log_dir, 'error.log')
    error_handler = RotatingFileHandler(
        error_log,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)