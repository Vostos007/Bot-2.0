"""Entry point for the bot"""

import logging
import os
from fastapi import FastAPI
from config import BotConfig
from bot import NotionBot
from api.monitoring import router as monitoring_router
from services.backup_service import BackupService
from utils.logging_config import setup_logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Initialize FastAPI
app = FastAPI()

# Add monitoring router
app.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
DB_PATH = os.path.join(BASE_DIR, 'bot.db')

def main():
    # Create required directories
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Setup logging
    setup_logging(LOG_DIR)
    logger = logging.getLogger(__name__)
    logger.info("Starting bot...")

    try:
        # Initialize backup service
        backup_service = BackupService(DB_PATH, BACKUP_DIR)
        
        # Initialize scheduler
        scheduler = AsyncIOScheduler()
        
        # Schedule daily backup at 3 AM
        @scheduler.scheduled_job('cron', hour=3)
        async def scheduled_backup():
            try:
                backup_service.create_backup()
                logger.info("Backup created successfully")
            except Exception as e:
                logger.error(f"Backup failed: {e}")
        
        scheduler.start()
        logger.info("Scheduler started")

        # Initialize and run bot
        config = BotConfig.from_env()
        bot = NotionBot(config)
        logger.info("Bot initialized")
        bot.run()

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
