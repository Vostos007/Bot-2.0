"""Configuration management"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfig:
    """Bot configuration container"""
    telegram_token: str
    notion_token: str
    database_id: str
    admin_id: int

    @classmethod
    def from_env(cls) -> 'BotConfig':
        """Create configuration from environment variables"""
        return cls(
            telegram_token=os.getenv('TELEGRAM_TOKEN'),
            notion_token=os.getenv('NOTION_TOKEN'),
            database_id=os.getenv('DATABASE_ID'),
            admin_id=int(os.getenv('ADMIN_ID'))
        )