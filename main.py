"""Entry point for the bot"""

import logging
from src.config import BotConfig
from src.bot import NotionBot

def main():
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Initialize and run bot
    config = BotConfig.from_env()
    bot = NotionBot(config)
    bot.run()

if __name__ == '__main__':
    main()