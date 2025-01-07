"""Configuration module with user management"""

import os
from typing import Set
from dataclasses import dataclass

@dataclass
class BotConfig:
    telegram_token: str
    notion_token: str
    database_id: str
    admin_id: int

    @classmethod
    def from_env(cls):
        return cls(
            telegram_token=os.getenv('TELEGRAM_TOKEN'),
            notion_token=os.getenv('NOTION_TOKEN'),
            database_id=os.getenv('DATABASE_ID'),
            admin_id=int(os.getenv('ADMIN_ID', 0))
        )

class UserManager:
    def __init__(self, allowed_users_file: str = 'allowed_users.txt'):
        self.allowed_users_file = allowed_users_file
        self._allowed_users: Set[int] = set()
        self.load_users()
    
    def load_users(self):
        try:
            with open(self.allowed_users_file, 'r') as f:
                self._allowed_users = set(int(line.strip()) for line in f)
        except FileNotFoundError:
            with open(self.allowed_users_file, 'w') as f:
                f.write('')
    
    def is_allowed(self, user_id: int) -> bool:
        return user_id in self._allowed_users

    def add_user(self, user_id: int):
        self._allowed_users.add(user_id)
        self._save_users()
    
    def remove_user(self, user_id: int):
        self._allowed_users.discard(user_id)
        self._save_users()
    
    def _save_users(self):
        with open(self.allowed_users_file, 'w') as f:
            for user_id in self._allowed_users:
                f.write(f"{user_id}\n")