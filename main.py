"""Entry point for the bot"""

import logging
import os
from fastapi import FastAPI
from src.config import BotConfig
from src.bot import NotionBot
from src.api.monitoring import router as monitoring_router
from src.services.backup_service import BackupService
from src.utils.logging_config import setup_logging
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
    # Setup logging
    setup_logging(LOG_DIR)

    # Initialize backup service
    backup_service = BackupService(DB_PATH, BACKUP_DIR)
    
    # Initialize scheduler
    scheduler = AsyncIOScheduler()
    
    # Schedule daily backup at 3 AM
    @scheduler.scheduled_job('cron', hour=3)
    async def scheduled_backup():
        backup_service.create_backup()
    
    scheduler.start()

    # Initialize and run bot
    config = BotConfig.from_env()
    bot = NotionBot(config)
    bot.run()

if __name__ == '__main__':
    main()