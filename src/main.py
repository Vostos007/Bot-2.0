"""Entry point for the bot with proper async handling"""

import logging
import os
import asyncio
import signal
from fastapi import FastAPI
from src.config import BotConfig
from src.bot import NotionBot
from src.api.monitoring import router as monitoring_router
from src.services.backup_service import BackupService
from src.utils.logging_config import setup_logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# Setup paths first
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
DB_PATH = os.path.join(BASE_DIR, 'bot.db')

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Initialize logging after LOG_DIR is defined
setup_logging(LOG_DIR)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Add monitoring router
app.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])

# Load environment variables
load_dotenv()

# Check required variables
required_vars = ['TELEGRAM_TOKEN', 'NOTION_TOKEN', 'DATABASE_ID', 'ADMIN_ID']
for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    logger.info(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    
    logger.info("Cancelling outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def main():
    """Main application entry point"""
    config = BotConfig.from_env()
    bot = NotionBot(config)
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s, loop))
        )
    
    try:
        logger.info("Starting NotionBot...")
        await bot.run()
    except asyncio.CancelledError:
        logger.info("Bot shutdown complete")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise